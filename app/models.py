from django.db import models
from django.contrib.auth.models import User, UserManager
import datetime
from django.db.models import Q, Count, Sum
from django.utils.safestring import mark_safe
from docman.settings import APP_URL, MEDIA_ROOT, DOMAIN, MEDIA_URL
from tagging.models import Tag
from djangoratings.fields import RatingField
import tagging.fields
from django.utils.encoding import smart_str, smart_unicode
import re
from app import docmail
from django.template import Context
from django.utils import simplejson
# SIGNALS AND LISTENERS
from django.contrib.auth.models import User
from django.db.models import signals
from django.dispatch import dispatcher, receiver
# Internationalization
from django.utils.translation import ugettext as _
import subprocess
import os.path

# cache
from django.core.cache import cache

def get_upload_path(instance, filename):
	if instance.document.course.shell_name:
		return smart_str(u'hdd/%s/%s' % (instance.document.course.shell_name, filename))
	else:
		return 'hdd/%s' % filename

class Docent(models.Model):
	name = models.CharField(max_length=255)
	email = models.EmailField()
	
	def __unicode__(self):
		return self.name

	def getUser(self):
		try:
			return User.objects.get(Q(userprofile__is_lecturer=True, userprofile__lecturer_id=self.pk))
		except:
			return False

	def getCourses(self):
		return Course.objects.filter(Q(docent=self.pk))

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	welcome_email = models.BooleanField(default=False)
	semester = models.IntegerField(default=-1)
	show_feed = models.BooleanField(default=True)
	survey = models.BooleanField(default=True)
	
	#api
	api_key = models.CharField(max_length=40, null=True, blank=True)
	etherpad_user_id = models.CharField(max_length=255, null=True, blank=True)

	#lecturer profile
	is_lecturer = models.BooleanField(default=False)
	lecturer_id = models.ForeignKey(Docent, unique=True, null=True, blank=True)
	
	#facebook
	about_me = models.TextField(blank=True, null=True)
	facebook_id = models.BigIntegerField(blank=True, null=True)
	facebook_name = models.CharField(max_length=255, blank=True, null=True)
	facebook_profile_url = models.TextField(blank=True, null=True)
	website_url = models.TextField(blank=True, null=True)
	blog_url = models.TextField(blank=True, null=True)
	image = models.ImageField(blank=True, null=True,
		upload_to='profile_images', max_length=255)
	date_of_birth = models.DateField(blank=True, null=True)
	raw_data = models.TextField(blank=True, null=True)	

	def __unicode__(self):
		return self.user.username
		
	def profile(self):
		if self.user.is_staff:
			icon = 'staff'
		else:
			icon = 'student'
		return '<span class="profileLink %s"><a href="/user/%d/">%s %s</a></span>' % (icon, self.user.pk, self.user.first_name, self.user.last_name)
		
	def facebook_profile_picture_thumbnail(self):
		if not self.facebook_id:
			return False
		return 'https://graph.facebook.com/%s/picture' % simplejson.loads(self.raw_data)['username']

	@staticmethod
	@receiver(models.signals.post_save, sender=User)
	def user_post_save(sender, instance, created, **kwargs):
		user = instance
		# check for profile
		try:
			p = user.get_profile()
			## user already has a profile
		except:
			## user has no profile - create it
			p = UserProfile.create(user)
		if not p.welcome_email and user.email and user.first_name:
			## write welcome email
			password = User.objects.make_random_password(10)
			docmail.docmail(user.email, _("Welcome to DocMan!"), "welcome", Context({ 'user': user, 'password': password, 'domain': DOMAIN }));
			p.welcome_email=True
			p.save()
			user.set_password(password)
			user.save()
	
	@staticmethod
	def create(user):
		try:
			p = user.get_profile()
		except:
			print "user has no profile - create it"
			p = UserProfile(user=user)
			p.save()
		return p
		
	def reset_password(profile):
		user = User.objects.get(pk=profile.user.pk)
		password = User.objects.make_random_password(10)
		docmail.docmail(user.email, _("New DocMan Password"), "reset_password", Context({ 'user': user, 'password': password, 'domain': DOMAIN }));
		user.set_password(password)
		user.save()

	def is_organisation_manager(self):
		if Organisation.objects.filter(managers__id=self.user.pk):
			return True
		else:
			return False

class Category(models.Model):
	name = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.name
		
	def getCourses(self, user):
		semester_id = user.get_profile().semester

		if type(semester_id) == str: semester_id=-1
		if (semester_id > 0):
			return Course.objects.filter(Q(category=self), Q(scopes__users__id=user.pk), Q(semester=semester_id) | Q(semester=-1)).order_by('name').distinct('pk')
		else:
			return Course.objects.filter(Q(category=self), Q(scopes__users__id=user.pk)).order_by('name').distinct('pk')
			
class Scope(models.Model):
	name = models.CharField(max_length=255)
	users = models.ManyToManyField(User, related_name='scope_user', blank=True)
	
	def __unicode__(self):
		return self.name

	def getCourses(self):
		return Course.objects.filter(Q(scopes__pk=self.pk)).order_by('name')

	def getUsersAssigned(self):
		return self.users.count()
		
class Course(models.Model):
	category = models.ForeignKey(Category)
	name = models.CharField(max_length=255)	
	docent = models.ForeignKey(Docent)
	shell_name = models.SlugField(max_length=255)
	subscribers = models.ManyToManyField(User, related_name='course_subscriber', blank=True)
	scopes = models.ManyToManyField(Scope, related_name='course_scope', blank=True)
	semester = models.IntegerField()
	
	def getSemester(self):
		if self.semester >= 1:
			return _("%d. Term") % self.semester
		else:
			return _("All Terms")

	def get_subscription(self, subscriber):
		try:
			if cache.get('Course(%d)get_subscription(%d)' % (self.pk, subscriber)):
				retval = cache.get('Course(%d)get_subscription(%d)' % (self.pk, subscriber))
			else:
				retval = self.subscribers.get(pk=subscriber)
				cache.set('Course(%d)get_subscription(%d)' % (self.pk, subscriber), retval)
			return retval
		except:
			return False	

	def get_scopes(self):
		return self.scopes.all()
	
	def __unicode__(self):
		return self.name	
		
	def getDocuments(self, user=None):
		if user:
			if user.get_profile().is_lecturer:
				return Document.objects.filter(Q(is_etherpad=False,is_lecturer_visible=True,course=self)).order_by('-pub_date')

		return Document.objects.filter(Q(course=self)).order_by('-pub_date')

	def getLastDocuments(self, user=None):
		if user:
			if user.get_profile().is_lecturer:
				if cache.get('Course(%d)getLatestDocuments_lecturer' % self.pk):
					retval = cache.get('Course(%d)getLatestDocuments_lecturer' % self.pk)
				else:
					retval = Document.objects.filter(Q(is_etherpad=False,is_lecturer_visible=True,course=self)).order_by('-pub_date')[:5]
					cache.set('Course(%d)getLatestDocuments_lecturer' % self.pk, retval)
				return retval

		
		if cache.get('Course(%d)getLatestDocuments' % self.pk):
			retval = cache.get('Course(%d)getLatestDocuments' % self.pk)
		else:
			retval = Document.objects.filter(Q(course=self)).order_by('-pub_date')[:5]
			cache.set('Course(%d)getLatestDocuments' % self.pk, retval)
		return retval
		
	def hasMatchingScope(self, user):
		return Course.objects.filter(Q(pk=self.pk), Q(scopes__users__id=user.pk)).distinct('pk')
				
class Document(models.Model):
	name = models.CharField(max_length=255)	
	pub_date = models.DateTimeField()	
	author = models.ForeignKey(User)
	course = models.ForeignKey(Course)
	tags = tagging.fields.TagField(null=True, blank=True)
	desc = models.TextField(null=True, blank=True)
	rating = RatingField(range=5, can_change_vote=True, allow_anonymous=False)
	subscribers = models.ManyToManyField(User, related_name='subscriber')
	is_etherpad = models.BooleanField(default=False)
	etherpad_document_id = models.CharField(max_length=255, null=True, blank=True)
	etherpad_group_id = models.CharField(max_length=255, null=True, blank=True)
	etherpad_raw = models.TextField(null=True, blank=True)
	is_lecturer_visible = models.BooleanField(default=True, null=False)
	
	def get_subscription(self, subscriber):
		try:
			if cache.get('Document(%d)get_subscription(%d)' % (self.pk, subscriber)):
				retval = cache.get('Document(%d)get_subscription(%d)' % (self.pk, subscriber))
			else:
				retval = self.subscribers.get(pk=subscriber)
				cache.set('Document(%d)get_subscription(%d)' % (self.pk, subscriber), retval)
			return retval
		except:
			return False
	
	def get_tags(self):
		return Tag.objects.get_for_object(self)
		
	def getLatestRevision(self):
		if not self.is_etherpad:
			if cache.get('Document(%d)getLatestRevision' % self.pk):
				retval = cache.get('Document(%d)getLatestRevision' % self.pk)
			else:
				retval = DocumentRevision.objects.filter(Q(document=self)).order_by('-pub_date')[:1][0]
				cache.set('Document(%d)getLatestRevision' % self.pk, retval)
			return retval
		else:
			return DocumentRevision(document=self, file=False, pub_date=self.pub_date, type='etherpad')
		
	def get_raw(self):
		if self.is_etherpad:
			return self.etherpad_raw
		else:
			return self.getLatestRevision().raw
		
	def get_comments_count(self):
		if cache.get('Document(%d)get_comments_count' % self.pk) >= 0: # this entry can also be 0 and so be cached as 0
			retval = cache.get('Document(%d)get_comments_count' % self.pk)
		else:
			retval = DocumentComment.objects.filter(Q(document=self)).order_by('-pub_date').count()
			cache.set('Document(%d)get_comments_count' % self.pk, retval)
		return retval

	def __unicode__(self):
		return self.name

class DocumentRevision(models.Model):
	document = models.ForeignKey(Document)
	file = models.FileField(upload_to=get_upload_path, max_length=255)
	pub_date = models.DateTimeField()
	raw = models.TextField(null=True, blank=True)
	type = models.CharField(max_length=255)
	uploaded_by = models.ForeignKey(User)

	def __unicode__(self):
		return "%s (%s)" % (self.document.name, self.file.name)

	def get_preview_file_types(self):
		return ["image", "pdf"]

	def get_uploader(self):
		if self.uploaded_by:
			return self.uploaded_by.get_profile().profile()
		else:
			return False
	
	def get_extension(self):
		return self.file.path.rpartition('.')[len(self.file.path.rpartition('.'))-1]

	def get_alternative_preview(self):
		return self.raw[:1000]
		
	def get_preview(self):
		if self.type in self.get_preview_file_types():
			try: 
				if os.path.isfile('%s/preview/%d-%s.png' % (MEDIA_ROOT, self.pk, re.sub('hdd/%s/' % self.document.course.shell_name, '', self.file.name))):
					return '%s/preview/%d-%s.png' % (MEDIA_URL, self.pk, re.sub('hdd/%s/' % self.document.course.shell_name, '', self.file.name))
			except:
				pass
		return False
		
	def get_large_preview(self):
		if self.type in self.get_preview_file_types():
			try:
				if os.path.isfile('%s/preview/%d-%s-large.png' % (MEDIA_ROOT, self.pk, re.sub('hdd/%s/' % self.document.course.shell_name, '', self.file.name))):
					return '%s/preview/%d-%s-large.png' % (MEDIA_URL, self.pk, re.sub('hdd/%s/' % self.document.course.shell_name, '', self.file.name))
			except:
				pass
		return False		
		
	def create_preview(self):
		try:
			#large preview for zooming
			subprocess.call(['convert', "%s[0]" % self.file.path, '-geometry', '600', '%s/preview/%d-%s-large.png' % (MEDIA_ROOT, self.pk, re.sub('hdd/%s/' % self.document.course.shell_name, '', self.file.name))])		
			#small preview
			subprocess.call(['convert', '%s/preview/%d-%s-large.png' % (MEDIA_ROOT, self.pk, re.sub('hdd/%s/' % self.document.course.shell_name, '', self.file.name)), '-geometry', '300', '%s/preview/%d-%s.png' % (MEDIA_ROOT, self.pk, re.sub('hdd/%s/' % self.document.course.shell_name, '', self.file.name))])
		except:
			print "FAIL"
			# if this fails.. well, it fails. we dont care.
			pass

class DocumentComment(models.Model):
	pub_date = models.DateTimeField()
	author = models.ForeignKey(User)
	text = models.TextField()
	document = models.ForeignKey(Document)

class News(models.Model):
	pub_date = models.DateTimeField()
	title = models.CharField(max_length=255, null=False, blank=False)
	text = models.TextField(null=False, blank=False)
	icon = models.CharField(max_length=20, default='newspaper')
	language = models.CharField(max_length=2, default='de', blank=False, null=False)
	related = models.ForeignKey('self', null=True, blank=True)
	show = models.BooleanField(default=True)
	
	class Meta:
		verbose_name_plural = _('News')
		
	def __unicode__(self):
		return self.title

class Organisation(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False)
	users = models.ManyToManyField(User, related_name='organisation_user', blank=True)
	managers = models.ManyToManyField(User, related_name='organisation_manager', blank=True)
	docents = models.ManyToManyField(Docent, related_name='organisation_docents', blank=True)
	scopes = models.ManyToManyField(Scope, related_name='organisation_scope', blank=True)
	courses = models.ManyToManyField(Course, related_name='organisation_course', blank=True)
	
	def __unicode__(self):
		return self.name		