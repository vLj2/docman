from django.db import models
from django.contrib.auth.models import User, UserManager
import datetime
from django.db.models import Q, Count, Sum
from django.utils.safestring import mark_safe
from docman.settings import APP_URL, MEDIA_ROOT, DOMAIN
from tagging.models import Tag
from djangoratings.fields import RatingField
import tagging.fields
from django.utils.encoding import smart_str, smart_unicode
import re
from app import docmail
from django.template import Context
# SIGNALS AND LISTENERS
from django.contrib.auth.models import User
from django.db.models import signals
from django.dispatch import dispatcher, receiver
# Internationalization
from django.utils.translation import ugettext as _


def get_upload_path(instance, filename):
	if instance.document.course.shell_name:
		return smart_str(u'hdd/%s/%s' % (instance.document.course.shell_name, filename))
	else:
		return 'hdd/%s' % filename

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	welcome_email = models.BooleanField(default=False)
	semester = models.IntegerField(default=-1)
	
	def profile(self):
		if self.user.is_staff:
			icon = 'staff'
		else:
			icon = 'student'
		return '<span class="profileLink %s"><a href="/user/%d/">%s %s</a></span>' % (icon, self.user.pk, self.user.first_name, self.user.last_name)

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


class Docent(models.Model):
	name = models.CharField(max_length=255)
	email = models.EmailField()
	
	def __unicode__(self):
		return self.name	

class Category(models.Model):
	name = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.name
		
	def getCourses(self, semester_id=-1):
		if type(semester_id) == str: semester_id=-1
		if (semester_id > 0):
			return Course.objects.filter(Q(category=self), Q(semester=semester_id) | Q(semester=-1)).order_by('name')
		else:
			return Course.objects.filter(Q(category=self)).order_by('name')
		
class Course(models.Model):
	category = models.ForeignKey(Category)
	name = models.CharField(max_length=255)	
	docent = models.ForeignKey(Docent)
	shell_name = models.SlugField(max_length=255)
	subscribers = models.ManyToManyField(User, related_name='course_subscriber')
	semester = models.IntegerField()
	
	def getSemester(self):
		if self.semester >= 1:
			return _("%d. Term") % self.semester
		else:
			return _("All Terms")

	def get_subscription(self, subscriber):
		try:
			return self.subscribers.get(pk=subscriber)
		except:
			return False	
	
	def __unicode__(self):
		return self.name	
		
	def getDocuments(self):
		return Document.objects.filter(Q(course=self)).order_by('-pub_date')

	def getLastDocuments(self):
		return Document.objects.filter(Q(course=self)).order_by('-pub_date')[:5]
				
class Document(models.Model):
	name = models.CharField(max_length=255)	
	pub_date = models.DateTimeField()	
	author = models.ForeignKey(User)
	course = models.ForeignKey(Course)
	tags = tagging.fields.TagField(null=True, blank=True)
	desc = models.TextField(null=True, blank=True)
	rating = RatingField(range=5, can_change_vote=True, allow_anonymous=False)
	subscribers = models.ManyToManyField(User, related_name='subscriber')
	
	def get_subscription(self, subscriber):
		try:
			return self.subscribers.get(pk=subscriber)
		except:
			return False
	
	def get_tags(self):
		return Tag.objects.get_for_object(self)
		
	def getLatestRevision(self):
		return DocumentRevision.objects.filter(Q(document=self)).order_by('-pub_date')[:1][0]
		
	def get_raw(self):
		return self.getLatestRevision().raw
		
	def __unicode__(self):
		return self.name

class DocumentRevision(models.Model):
	document = models.ForeignKey(Document)
	file = models.FileField(upload_to=get_upload_path, max_length=255)
	pub_date = models.DateTimeField()
	raw = models.TextField(null=True, blank=True)
	type = models.CharField(max_length=255)
	
	def get_extension(self):
		return self.file.path.rpartition('.')[len(self.file.path.rpartition('.'))-1]
	
class DocumentComment(models.Model):
	pub_date = models.DateTimeField()
	author = models.ForeignKey(User)
	text = models.TextField()
	document = models.ForeignKey(Document)


