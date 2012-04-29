from django.core.mail import mail_admins
from django.core import mail
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.http import Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpRequest
from urllib import unquote
from django.template import RequestContext
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.utils import simplejson
import urlparse
from datetime import datetime
import os
import socket
from docman.settings import APP_URL, MEDIA_ROOT, CONTENT_TYPES, MAX_UPLOAD_SIZE, DOMAIN, DEFAULT_FROM_EMAIL, IMPRINT, SUPPORT_EMAIL, FACEBOOK_APP_ID, DEBUG
from dateutil import relativedelta
from docman.app.models import *
import re
from django.core.validators import email_re
from django.utils import simplejson
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.template.defaultfilters import filesizeformat
from os import popen
import pyPdf
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os, tempfile, zipfile
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.core.files import File
from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud, get_tag_list
from django.template.defaultfilters import slugify
from StringIO import StringIO  
from zipfile import ZipFile 
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.utils.html import escape, linebreaks, urlize
from django.utils.encoding import smart_str, smart_unicode
from django.contrib.auth import logout
from app import docmail
from django.template import Context
from operator import itemgetter
from heapq import nlargest
# Internationalization
from django.utils.translation import ugettext as _

# testing
from base64 import b64decode
from django.core.files.base import ContentFile

# Etherpad API
from py_etherpad import EtherpadLiteClient

#lecturer decorator
from decorators import is_no_lecturer, is_lecturer

#organisation required
from decorators import has_organisation

#cache
from django.views.decorators.cache import cache_page
from django.core.cache import cache


def is_valid_email(email):
	return True if email_re.match(email) else False

def get_directory_size(directory):
	dir_size = 0
	for (path, dirs, files) in os.walk(directory):
		for file in files:
			filename = os.path.join(path, file)
			dir_size += os.path.getsize(filename)
	return dir_size

def get_most_common_word(iterable, n=None, min_length=5):
	bag = {}
	bag_get = bag.get
	for elem in iterable:
		if (len(elem) >= min_length):
			bag[elem] = bag_get(elem, 0) + 1
	if n is None:
		return sorted(bag.iteritems(), key=itemgetter(1), reverse=True)
	it = enumerate(bag.iteritems())
	nl = nlargest(n, ((cnt, i, elem) for (i, (elem, cnt)) in it))
	return [elem for cnt, i, elem in nl]

@login_required
@is_no_lecturer
@has_organisation
# facebook
def facebook_deconnect_view(request):
	request.user.get_profile().facebook_id = 0
	request.user.get_profile().facebook_name = 0
	request.user.get_profile().facebook_profile_url = ''
	request.user.get_profile().website_url = ''
	request.user.get_profile().blog_url = ''
	request.user.get_profile().raw_data = ''
	request.user.get_profile().save()

	messages.add_message(request, messages.SUCCESS, _('Your Facebook connection has been deleted!'))
	return HttpResponseRedirect(reverse("account", args=[]))
	
	#return HttpResponseRedirect('https://www.facebook.com/settings/?tab=applications&app_id=%s' % FACEBOOK_APP_ID)

@login_required
@is_lecturer
@has_organisation
def scope_info_view(request, scope_id):
	scope = get_object_or_404(Scope, Q(pk=scope_id), Q(users__pk=request.user.pk))

	return render_to_response("scope_info.html", locals(), context_instance=RequestContext(request))

@login_required
@has_organisation
def ie_upload_view(request):
	if request.POST.get('document_id'):
		document_id = request.POST.get('document_id')
	else:
		document_id = False

	if request.POST.get('course_id'):
		course_id = request.POST.get('course_id')
	else:
		messages.add_message(request, messages.ERROR, _('An unknown error occurred while trying to upload your file. Please try again later!'))
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	try:
		contentFile = request.FILES['file']
	except:
		messages.add_message(request, messages.ERROR, _('No File selected!'))
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	if not document_id:
		u_name = request.POST.get('name')
		u_tags = request.POST.get('tags')
		u_desc = request.POST.get('desc')
		if not request.user.get_profile().is_lecturer:
			is_lecturer_visible = request.POST.get("is_lecturer_visible")	
	
	"""try:
		contentFile.name = unicode(contentFile.name, 'ascii')
	except UnicodeError:
		contentFile.name = unicode(contentFile.name, 'utf-8')
	else:
		pass"""

	if not document_id:
		try:
			course = get_object_or_404(Course.objects.distinct('pk'), Q(pk=course_id), Q(scopes__users__id=request.user.pk))
		except:
			messages.add_message(request, messages.ERROR, _("Course couldn't be loaded - please try again!"))
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		try:
			document = Document.objects.get(Q(pk=document_id))
			if document.is_etherpad:
				raise
		except:
			messages.add_message(request, messages.ERROR, _("Document couln't be loaded - please try again!"))
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		
	try:
		if int(contentFile.size) > MAX_UPLOAD_SIZE:
			messages.add_message(request, messages.ERROR, _("The file is too big!"))
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	except:
		messages.add_message(request, messages.ERROR, _("An unexpected error occured while uploading the file."))
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	if not document_id:
		try:
			document = Document(name=contentFile.name, pub_date=datetime.datetime.now(), author=request.user, course=course)			
			document.save()
			# auto-subscribe to document
			document.subscribers.add(request.user)			
			revision = DocumentRevision(document=document, pub_date=datetime.datetime.now(), uploaded_by=request.user)
			revision.file.save(slugify(document.name) + '.' + document.name.rpartition('.')[len(document.name.rpartition('.'))-1], contentFile)
					
			for subscriber in course.subscribers.all():
				if subscriber.pk != request.user.pk:
					docmail.docmail(subscriber.email, "[%s] Neues Dokument" % course.name, "course_new_document", Context({ 'user': subscriber, 'document': document, 'author' : request.user, 'course' : course, 'domain': settings.DOMAIN }));
			
		except:
			raise
			messages.add_message(request, messages.ERROR, _("An unexpected error occured while uploading the file."))
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		try:
			#document.name = contentFile.name
			document.pub_date = datetime.datetime.now()
			document.save()
			revision = DocumentRevision(document=document, pub_date=datetime.datetime.now(), uploaded_by=request.user)
			revision.file.save(slugify(contentFile.name) + '.' + contentFile.name.rpartition('.')[len(contentFile.name.rpartition('.'))-1], contentFile)
			for subscriber in document.subscribers.all():
				if subscriber.pk != request.user.pk:
					docmail.docmail(subscriber.email, "[%s] Neue Revision" % document.name, "document_new_revision", Context({ 'user': subscriber, 'document': document, 'author' : request.user, 'domain': settings.DOMAIN }));
		except:
			messages.add_message(request, messages.ERROR, _("An unexpected error occured while uploading the file."))
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))				

	if not document_id:
		# filter tags
		tags = u_tags.lower().strip()
		tags = re.sub("[^a-z0-9-, ]", "", tags)
	
		document.desc = u_desc
		if u_name:
			document.name = u_name
		document.tags = tags

		if not request.user.get_profile().is_lecturer:
			if is_lecturer_visible:
				document.is_lecturer_visible = True
			else:
				document.is_lecturer_visible = False

		document.save()
	
	# we do really want to know what the mime type is
	command = smart_str(u'file %s' % revision.file.path)
	mime = os.popen(command).read()

	if mime.find('PDF document') > 0:
		revision.type = 'pdf'
	elif mime.find('text') > 0:
		revision.type = 'txt'
	elif mime.find('image') > 0:
		revision.type = 'image'
	elif mime.find('Rich Text') > 0:
		revision.type = 'rtf'
	elif mime.find('Excel') > 0:
		revision.type = 'xls'
	elif mime.find('PowerPoint') > 0:
		revision.type = 'ppt'		
	elif mime.find('Word') > 0:
		revision.type = 'doc'			
	elif mime.find('MPEG') > 0:
		revision.type = 'audio'
	#elif mime.find('Zip archive') > 0:
	#	revision.type = 'zip'		
	else:
		if revision.file.name.find('pages') > 0:
			revision.type = 'doc'
		elif revision.file.name.find('key') > 0:
			revision.type = 'ppt'			
		elif revision.file.name.find('ppt') > 0:
			revision.type = 'ppt'						
		elif revision.file.name.find('xls') > 0:
			revision.type = 'xls'
		elif revision.file.name.find('xlsx') > 0:
			revision.type = 'xls'			
		elif revision.file.name.find('doc') > 0:
			revision.type = 'doc'
		elif revision.file.name.find('docx') > 0:
			revision.type = 'doc'
		elif revision.file.name.find('odp') > 0:
			revision.type = 'ppt'
		elif revision.file.name.find('rar') > 0:
			revision.type = 'zip'
		elif revision.file.name.find('zip') > 0:
			revision.type = 'zip'
		else:
			# default type: file ending
			revision.type = document.name.rpartition('.')[len(document.name.rpartition('.'))-1]

	try:
		raw_formats = settings.RAW_FORMATS

		if document.name.rpartition('.')[len(document.name.rpartition('.'))-1] == 'pdf':
			print "detected pdf, opening.."
			try:
				pdf = pyPdf.PdfFileReader(open(revision.file.path, "rb"))
				raw = ""
				for page in pdf.pages:
					raw = "%s %s" % (raw, page.extractText())
				revision.raw = raw
			except:
				pass
		
		elif document.name.rpartition('.')[len(document.name.rpartition('.'))-1] in raw_formats:
			revision.raw = revision.file.read()
	except:
		pass
		
	revision.save()

	# create preview if pdf or image file
	# we need a pk to do this, so call this after .save()
	if revision.type == "image" or revision.type == "pdf":
		revision.create_preview()
		
	print "upload done!"

	# clear cache
	cache.clear()	
	
	if document_id:
		messages.add_message(request, messages.SUCCESS, _("The new revision <strong>%s</strong> has been uploaded successfully." % document.name))
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		messages.add_message(request, messages.SUCCESS, _("The Document <strong>%s</strong> has been uploaded successfully.") % document.name)
	
	return HttpResponseRedirect(reverse("document", args=[document.pk]))


@login_required
@has_organisation
#thanks to sven <33311!!
def test_upload_view(request):
	# we find these in our request header
	if 'HTTP_DOCUMENTID' in request.META:
		document_id = request.META["HTTP_DOCUMENTID"]
	else:
		document_id = False
		
	if 'HTTP_COURSEID' in request.META:
		course_id = request.META["HTTP_COURSEID"]
	else:
		course_id = False

	# we always expect base64-encoded data
	
	content = request.raw_post_data
	#content = b64decode(request.raw_post_data)

	if not content:
		return # whooops - something went wrong!
		
	contentFile = ContentFile(content)
	contentFile.name = request.META['HTTP_UP_FILENAME']
	
	try:
		contentFile.name = unicode(contentFile.name, 'ascii')
	except UnicodeError:
		contentFile.name = unicode(contentFile.name, 'utf-8')
	else:
		pass

	if not document_id:
		try:
			course = get_object_or_404(Course.objects.distinct('pk'), Q(pk=course_id), Q(scopes__users__id=request.user.pk))
		except:
			response = {'success' : False, 'error' : _("Course couldn't be loaded - please try again!")}
			return HttpResponse(simplejson.dumps(response))
	else:
		try:
			document = Document.objects.get(Q(pk=document_id))
			if document.is_etherpad:
				raise
		except:
			response = {'success' : False, 'error' : _("Document couln't be loaded - please try again!")}
			return HttpResponse(simplejson.dumps(response))		
		
	try:
		if int(contentFile.size) > MAX_UPLOAD_SIZE:
			response = {'success' : False, 'error' : _('The file is too big!')}
			return HttpResponse(simplejson.dumps(response))	
		# we do not want a filetype restriction any longer	
		#content_type = request.META['HTTP_UP_TYPE']
		#if content_type in CONTENT_TYPES:
		#else:
		#		response = {'success' : False, 'error' : _('The file type %s is not supported.') % content_type}
		#		return HttpResponse(simplejson.dumps(response))
	except:
		response = {'success' : False, 'error' : _("An unexpected error occured while uploading the file.")}
		return HttpResponse(simplejson.dumps(response))
	
	if not document_id:
		try:
			document = Document(name=contentFile.name, pub_date=datetime.datetime.now(), author=request.user, course=course)			
			document.save()
			# auto-subscribe to document
			document.subscribers.add(request.user)			
			revision = DocumentRevision(document=document, pub_date=datetime.datetime.now(), uploaded_by=request.user)
			revision.file.save(slugify(document.name) + '.' + document.name.rpartition('.')[len(document.name.rpartition('.'))-1], contentFile)
					
			for subscriber in course.subscribers.all():
				if subscriber.pk != request.user.pk:
					docmail.docmail(subscriber.email, "[%s] Neues Dokument" % course.name, "course_new_document", Context({ 'user': subscriber, 'document': document, 'author' : request.user, 'course' : course, 'domain': settings.DOMAIN }));
			
		except:
			raise
			response = {'success' : False, 'error' : _("An unexpected error occured while uploading the file.")}
			return HttpResponse(simplejson.dumps(response))		
	else:
		try:
			#document.name = contentFile.name
			document.pub_date = datetime.datetime.now()
			document.save()
			revision = DocumentRevision(document=document, pub_date=datetime.datetime.now(), uploaded_by=request.user)
			revision.file.save(slugify(contentFile.name) + '.' + contentFile.name.rpartition('.')[len(contentFile.name.rpartition('.'))-1], contentFile)
			for subscriber in document.subscribers.all():
				if subscriber.pk != request.user.pk:
					docmail.docmail(subscriber.email, "[%s] Neue Revision" % document.name, "document_new_revision", Context({ 'user': subscriber, 'document': document, 'author' : request.user, 'domain': settings.DOMAIN }));
		except:
			response = {'success' : False, 'error' : _("An unexpected error occured while uploading the file.")}
			return HttpResponse(simplejson.dumps(response))				
	
	# we do really want to know what the mime type is
	command = smart_str(u'file %s' % revision.file.path)
	mime = os.popen(command).read()

	if mime.find('PDF document') > 0:
		revision.type = 'pdf'
	elif mime.find('text') > 0:
		revision.type = 'txt'
	elif mime.find('image') > 0:
		revision.type = 'image'
	elif mime.find('Rich Text') > 0:
		revision.type = 'rtf'
	elif mime.find('Excel') > 0:
		revision.type = 'xls'
	elif mime.find('PowerPoint') > 0:
		revision.type = 'ppt'		
	elif mime.find('Word') > 0:
		revision.type = 'doc'			
	elif mime.find('MPEG') > 0:
		revision.type = 'audio'
	#elif mime.find('Zip archive') > 0:
	#	revision.type = 'zip'		
	else:
		if revision.file.name.find('pages') > 0:
			revision.type = 'doc'
		elif revision.file.name.find('key') > 0:
			revision.type = 'ppt'			
		elif revision.file.name.find('ppt') > 0:
			revision.type = 'ppt'						
		elif revision.file.name.find('xls') > 0:
			revision.type = 'xls'
		elif revision.file.name.find('xlsx') > 0:
			revision.type = 'xls'			
		elif revision.file.name.find('doc') > 0:
			revision.type = 'doc'
		elif revision.file.name.find('docx') > 0:
			revision.type = 'doc'
		elif revision.file.name.find('odp') > 0:
			revision.type = 'ppt'
		elif revision.file.name.find('rar') > 0:
			revision.type = 'zip'
		elif revision.file.name.find('zip') > 0:
			revision.type = 'zip'
		else:
			# default type: file ending
			revision.type = document.name.rpartition('.')[len(document.name.rpartition('.'))-1]

	try:
		raw_formats = settings.RAW_FORMATS

		if document.name.rpartition('.')[len(document.name.rpartition('.'))-1] == 'pdf':
			print "detected pdf, opening.."
			try:
				pdf = pyPdf.PdfFileReader(open(revision.file.path, "rb"))
				raw = ""
				for page in pdf.pages:
					raw = "%s %s" % (raw, page.extractText())
				revision.raw = raw
			except:
				pass
		
		elif document.name.rpartition('.')[len(document.name.rpartition('.'))-1] in raw_formats:
			revision.raw = revision.file.read()
	except:
		pass
		
	"""if revision.raw:
		#tags = [slugify(word) for word in set(revision.raw.split(" ")) if len(word) > 10]
		#tags = tags[:5]
		
		# get most common words from raw text
		try:
			tags = get_most_common_word(revision.raw.split(), n=10, min_length=10)
		except:"""

	tags = {}
		
	revision.save()

	# create preview if pdf or image file
	# we need a pk to do this, so call this after .save()
	if revision.type == "image" or revision.type == "pdf":
		revision.create_preview()
		
	print "upload done!"

	# clear cache
	cache.clear()	
	
	if document_id:
		messages.add_message(request, messages.SUCCESS, _("The new revision <strong>%s</strong> has been uploaded successfully." % document.name))
		response = {'revision': True, 'success' : True, 'ok' : _("The new revision <strong>%s</strong> has been uploaded successfully." % document.name), 'tags': ' '.join(tags),}	
	else:
		response = {'documentName' : document.name, 'documentId' : document.pk, 'success' : True, 'ok' : _("The Document <strong>%s</strong> has been uploaded successfully.") % document.name, 'tags': ' '.join(tags),}
	return HttpResponse(simplejson.dumps(response))

@login_required
@has_organisation
def semester_view(request, semester_id):
	try:
		profile = request.user.get_profile()
	except:
		profile = UserProfile.create(request.user)
	if (str(semester_id) == 'all'):
		profile.semester = -1
		profile.save()
	elif (int(semester_id) <= 6 and int(semester_id) >= 1):
		profile.semester = int(semester_id)
		profile.save()
	else:
		messages.add_message(request, messages.ERROR, _('Invalid Term selected.') )
		return HttpResponseRedirect(reverse("default"))				
	return HttpResponseRedirect(reverse("default"))				

def get_view(request, success=False):
	if request.GET.get('email'):
		if not is_valid_email(request.GET.get('email')):
			messages.add_message(request, messages.ERROR, _("This is not a valid email address!"))
			mail_sent = 0
		else:
			text = "%s\n\nE-Mail: %s" % (str(request.META['REMOTE_ADDR']), request.GET.get('email'))
			mail_admins('DocMan Closed Beta', text)
			mail_sent = 1
		return HttpResponseRedirect(reverse("get-param", args=[mail_sent]))

	return render_to_response("get.html", locals(), context_instance=RequestContext(request))

@cache_page(60*15)
def about_view(request):
	stats = { 'space' : get_directory_size(MEDIA_ROOT+'/hdd'), 'count': len(Document.objects.all()) }
	imprint = IMPRINT
	return render_to_response("about.html", locals(), context_instance=RequestContext(request))

@cache_page(60*15)
def press_view(request):
	return render_to_response("press.html", locals(), context_instance=RequestContext(request))	
	
@login_required
@has_organisation
def user_view(request, user_id):
	user = get_object_or_404(User, Q(pk=user_id))

	# we need to check if this is an lecturer and if he has connected an lecturer profile
	if user.get_profile().is_lecturer:
		if user.get_profile().lecturer_id:
			return HttpResponseRedirect(reverse('docent', args=[user.get_profile().lecturer_id.pk]))
		else:
			raise Http404

	# we need to check if we have mathing scopes with this user - otherwise,
	# we cannot see his profile
	my_scopes = Scope.objects.filter(Q(users__pk=request.user.pk))
	users_scopes = Scope.objects.filter(Q(users__pk=user.pk))
	match = False
	
	for scope in my_scopes:
		if scope in users_scopes:
			match = True
			
	if not match:
		raise Http404
	
	documents = Document.objects.filter(Q(author=user_id)).order_by('-pub_date')[:10]
	cdocuments = DocumentComment.objects.filter(Q(author=user_id)).order_by('-pub_date')[:10]
	return render_to_response("user.html", locals(), context_instance=RequestContext(request))	

@login_required
@is_no_lecturer
@has_organisation
def subscribe_course_view(request, course_id):
	course = get_object_or_404(Course.objects.distinct('pk'), Q(pk=course_id), Q(scopes__users__id=request.user.pk))
	course.subscribers.add(request.user)
	course.save()
	messages.add_message(request, messages.SUCCESS, _('Successfully subscribed to notifications for this course.'))
	return HttpResponseRedirect(reverse("course", args=[course.pk]))	
	
@login_required
@is_no_lecturer
@has_organisation
def unsubscribe_course_view(request, course_id):
	course = get_object_or_404(Course.objects.distinct('pk'), Q(pk=course_id), Q(scopes__users__id=request.user.pk))
	course.subscribers.remove(request.user)
	course.save()
	messages.add_message(request, messages.SUCCESS, _('You unsubscribed from notifications for this course.'))
	return HttpResponseRedirect(reverse("course", args=[course.pk]))	

@login_required
@has_organisation
def subscribe_document_view(request, document_id):
	document = get_object_or_404(Document, Q(pk=document_id))
	if document.is_etherpad:
		raise Http404
	document.subscribers.add(request.user)
	document.save()
	messages.add_message(request, messages.SUCCESS, _('Successfully subscribed to notifications for this document.'))
	return HttpResponseRedirect(reverse("document", args=[document.pk]))	
	
@login_required
@has_organisation
def unsubscribe_document_view(request, document_id):
	document = get_object_or_404(Document, Q(pk=document_id))
	if document.is_etherpad:
		raise Http404	
	document.subscribers.remove(request.user)
	document.save()
	messages.add_message(request, messages.SUCCESS, _('You unsubscribed from notifications for this document.'))
	return HttpResponseRedirect(reverse("document", args=[document.pk]))	
 
@login_required
@is_no_lecturer
@has_organisation
def rate_document_view(request, document_id):
	rating = request.POST.get("rating")
	
	try:
		document = Document.objects.get(Q(pk=document_id))
	except:
		response = {'success' : False, 'error' : _("Couldn't load the document")}
		return HttpResponse(simplejson.dumps(response))	

	if int(rating) < 1 or int(rating) > 5:
		response = {'success' : False, 'error' : _('Invalid rating')}
		return HttpResponse(simplejson.dumps(response))			
		
	document.rating.add(score=rating, user=request.user, ip_address=request.META['REMOTE_ADDR'])
	
	response = {'success' : True }
	return HttpResponse(simplejson.dumps(response))

@login_required
@has_organisation
def account_ajax_view(request):
	if not request.POST:
		response = {'success' : False}
	else:
		profile = UserProfile.objects.get(user=request.user.pk)
		show_feed = request.POST.get("show_latest_uploads")

		if show_feed == "yes":
			profile.show_feed = True
		else:
			profile.show_feed = False

		profile.save()
		response = {'success': True}

	return HttpResponse(simplejson.dumps(response))

@login_required
def account_view(request):
	if not request.POST:
		return render_to_response("account.html", locals(), context_instance=RequestContext(request))
	else:
		if request.POST.get("changePasswordForm"):
			current = request.POST.get("current")
			password = request.POST.get("password")
			repeat = request.POST.get("password_repeat")
			
			if not request.user.check_password(current):
				messages.add_message(request, messages.ERROR, _("Your current password is not correct!"))
				return HttpResponseRedirect(reverse("account", args=[]))				

			if len(password) > 0 and (password != repeat):
				messages.add_message(request, messages.ERROR, _("The passwords don't match!"))
				return HttpResponseRedirect(reverse("account", args=[]))

			if len(password) < 6:
				messages.add_message(request, messages.ERROR, _("Your password must be at least 5 characters long!"))
				return HttpResponseRedirect(reverse("account", args=[]))

			request.user.set_password(password)
			request.user.save()

			messages.add_message(request, messages.SUCCESS, _('Your password has been changed!'))
			return HttpResponseRedirect(reverse("account", args=[]))
		elif request.POST.get("settingsForm"):
			show_feed = request.POST.get("show_latest_uploads")
			profile = UserProfile.objects.get(user=request.user.pk)

			if show_feed == "yes":
				profile.show_feed = True
			else:
				profile.show_feed = False
	
			profile.save()

			messages.add_message(request, messages.SUCCESS, _('Your settings have been changed!'))
			return HttpResponseRedirect(reverse("account", args=[]))
		elif request.POST.get("changeEmailForm"):
			email = request.POST.get("email")
			
			if not is_valid_email(email):
				messages.add_message(request, messages.ERROR, _("This is not a valid email address!"))
				return HttpResponseRedirect(reverse("account", args=[]))
				
			request.user.email = email
			request.user.save()
			
			messages.add_message(request, messages.SUCCESS, _('Your email address has been changed!'))
			return HttpResponseRedirect(reverse("account", args=[]))			
		else:
			return HttpResponseRedirect(reverse("account", args=[]))
		
	
@login_required
def logout_view(reqeust):
	logout(reqeust)
	return HttpResponseRedirect(reverse("default", args=[]))

@csrf_protect
def login_view(request):

	if 'HTTP_USER_AGENT' in request.META:
		if request.META['HTTP_USER_AGENT'].find('MSIE') > 0:
			internet_explorer_warning = True
			#return render_to_response("misc/no-sorry.html", locals(), context_instance=RequestContext(request))
		
#		if request.META['HTTP_USER_AGENT'].find('Firefox') > 0:
#			if float(re.sub("(.*)Firefox/", "", request.META['HTTP_USER_AGENT'])) < 4.0: # this is a really evil hack, actually!
#				firefox_warning = True
				
		if request.META['HTTP_USER_AGENT'].find('Chrome') > 0:				
			chrome_warning = True
			
		if request.is_secure():
			is_secure = True
	
	redirect_to = request.REQUEST.get('next', '')
	secure_domain = '<span class="secureURL">%s</span>' % settings.DOMAIN
	if request.POST.get("username") and request.POST.get("password"):
		username = request.POST.get("username")
		password = request.POST.get("password")
		error = False
		
		if redirect_to.find('.') > 0:
			redirect_to = '/'
		
		user = authenticate(username=username, password=password)
	
		if user is None:
			error = _("Username or password invalid.")
		else:
			if user.is_active:
				login(request, user)
				
				# check if user's password already has been converted to bcrypt, if not: convert it!
				if user.password.startswith('sha1'):
					user.set_password(password)
					user.save()
				
				return HttpResponseRedirect(redirect_to)
			else:
				error = _("This account has been deactivated.")
	
	next = redirect_to
	
	latest_news = News.objects.filter(Q(show=True)).order_by('-pub_date')[:1]
	
	if latest_news:
	 	if latest_news[0].language != request.LANGUAGE_CODE:
			latest_news = News.objects.filter(Q(show=True), Q(related=latest_news[0].pk), Q(language=request.LANGUAGE_CODE)).order_by('-pub_date')[:1]
		
	if latest_news:
		latest_news = latest_news[0]
		
	return render_to_response("login.html", locals(), context_instance=RequestContext(request))

@login_required
@is_no_lecturer
@has_organisation
def search_view(request):
	pass
	
	return render_to_response("search.html", locals(), context_instance=RequestContext(request))

@login_required
@is_no_lecturer
@has_organisation
@cache_page(60*15)
def tag_cloud_view(request):
	tags = Tag.objects.usage_for_model(Document, counts=True)
	cloud = calculate_cloud(tags, steps=2)
	return render_to_response("tags/tag-cloud.html", locals(), context_instance=RequestContext(request))

@login_required
@has_organisation
@cache_page(60*15)
def tag_view(request, tag_name):
	tag = get_object_or_404(Tag, Q(name=tag_name))
	documents_raw = TaggedItem.objects.get_by_model(Document, tag).order_by('-pub_date')
	
	page = request.GET.get('p')
	documents_paginator = Paginator(documents_raw, 20)
	
	try:
		documents = documents_paginator.page(page)
	except TypeError:
		documents = documents_paginator.page(1)
	except PageNotAnInteger:
		documents = documents_paginator.page(1)
	except EmptyPage:
		documents = documents_paginator.page(documents_paginator.num_pages)	
	
	return render_to_response("tags/tag.html", locals(), context_instance=RequestContext(request))

@login_required
@has_organisation
def default_view(request):
	categories = Category.objects.all().order_by('-name')

	if request.user.get_profile().show_feed == True and not request.user.get_profile().is_lecturer:
		if request.user.get_profile().semester == -1:
			feed = Document.objects.filter(Q(course__scopes__users__id=request.user.pk)).order_by('-pub_date').distinct('pk')[:5]
		else:
			feed = Document.objects.filter(Q(course__scopes__users__id=request.user.pk), Q(course__semester=request.user.get_profile().semester) | Q(course__semester=-1)).order_by('-pub_date').distinct('pk')[:5]
			
	"""if request.user.get_profile().survey == False and request.user.date_joined + relativedelta.relativedelta(months=1) < datetime.datetime.now():
			show_survey = True"""

	return render_to_response("default.html", locals(), context_instance=RequestContext(request))
	
@login_required
@has_organisation
def download_view(request, document_id):
	if request.user.get_profile().is_lecturer:
		document = get_object_or_404(Document, Q(pk=document_id, is_lecturer_visible=True))
	else:
		document = get_object_or_404(Document, Q(pk=document_id))
	course = get_object_or_404(Course.objects.distinct('pk'), Q(pk=document.course.pk), Q(scopes__users__id=request.user.pk))
	revisionId = request.GET.get('rev')
	zipped = request.GET.get('zipped')

	if document.is_etherpad:
		raise Http404	
	
	if not revisionId:
		filename = document.getLatestRevision().file.path
		ffile = document.getLatestRevision().file
	else:
		revision = get_object_or_404(DocumentRevision, Q(pk=revisionId))
		filename = revision.file.path
		ffile = revision.file


	output_name = re.sub('hdd/%s/' % document.course.shell_name, '', ffile.name)
	# dirty hack: strip ending out of file name
	ending = output_name.rpartition('.')[len(output_name.rpartition('.'))-1]
	output_name = re.sub('(%s(_|-)\d\.%s|%s\.%s)' % (ending, ending, ending, ending), '.%s' % ending, output_name)

	try:	
		if not zipped:
			response = HttpResponse()
			response['Content-Type'] = 'application/force-download';
			response['Content-disposition'] = 'attachment; filename=%s' % output_name

			# making use of X-Sendfile header extension (must be supported by webserver!)
			response['X-Sendfile'] = filename
		else:
			in_memory = StringIO()
			zip = ZipFile(in_memory, "a", zipfile.ZIP_DEFLATED)
			zip.write(filename, output_name)
			for f in zip.filelist:
				f.create_system = 0
			zip.close()
			in_memory.seek(0)
			response = HttpResponse(mimetype="application/zip")
			response['Content-Disposition'] = 'attachment; filename=%s.zip' % output_name
			response['Content-Length'] = in_memory.tell()
			response.write(in_memory.read())
			in_memory.close()
		
		return response
	except:
		raise

@login_required
@has_organisation
def docent_view(request, docent_id):
	docent = get_object_or_404(Docent, Q(pk=docent_id))
	courses = Course.objects.filter(Q(docent=docent_id), Q(scopes__users__id=request.user.pk)).distinct('pk')
	#if courses.count() == 0:
	#	raise Http404
	return render_to_response("docent.html", locals(), context_instance=RequestContext(request))
	
@login_required
@has_organisation
def course_view(request, course_id):
	page = request.GET.get('p')
	course = get_object_or_404(Course.objects.distinct('pk'), Q(pk=course_id), Q(scopes__users__id=request.user.pk))
	category = Category.objects.get(Q(pk=course.category.pk))
	documents_raw = course.getDocuments(request.user)
	documents_paginator = Paginator(documents_raw, 20)
	
	try:
		documents = documents_paginator.page(page)
	except TypeError:
		documents = documents_paginator.page(1)
	except PageNotAnInteger:
		documents = documents_paginator.page(1)
	except EmptyPage:
		documents = documents_paginator.page(documents_paginator.num_pages)

	if 'HTTP_USER_AGENT' in request.META:
		if request.META['HTTP_USER_AGENT'].find('MSIE') > 0:
			internet_explorer_warning = True		
	
	return render_to_response("course.html", locals(), context_instance=RequestContext(request))
	
def upload_test_view(request):
	pass
	uploadFile = request.FILES['fileUpload']
	
	course = Course.objects.get(Q(pk=1))
	
	document = Document(name="Test", pub_date=datetime.datetime.now(), author=request.user, course=course)
	document.save()
	revision = DocumentRevision(document=document, pub_date=datetime.datetime.now())
	revision.file.save(request.FILES['fileUpload'].name, request.FILES['fileUpload'], False)
	
	pdf = pyPdf.PdfFileReader(open(revision.file.path, "rb"))
	for page in pdf.pages:
		print page.extractText()

@login_required
@has_organisation
def save_survey_view(request):
	if request.user.get_profile().survey == True:
		response = {'success' : False, 'error' : _("You already voted, mate!")}
		return HttpResponse(simplejson.dumps(response))	

	grade_ = int(request.POST.get("grade"))
	upload_ = int(request.POST.get("upload"))
	layout_ = int(request.POST.get("layout"))
	zip_ = request.POST.get("zip")
	text_ = request.POST.get("text")
		
	text = "What do you think about DocMan in general? Result: %d\nWhat's your opinion about the drop-to-upload thing? Result: %d\nHow's the layout? Result: %d\nDid you sometimes download .zip archives? Result: %s\n\nFree text: %s" % (grade_, upload_, layout_, zip_, text_)
		
	mail_admins("Survey from %s %s" % (request.user.first_name, request.user.last_name), text)
	
	request.user.get_profile().survey = True
	request.user.get_profile().save()

	response = {'success' : True, 'ok' : _("Thanks for your time, mate. You rock!")}
	return HttpResponse(simplejson.dumps(response))	

@login_required
@has_organisation
def file_info_view(request):
	documentId = request.POST.get("documentId")
	name = request.POST.get("name")
	tags = request.POST.get("tags")
	desc = request.POST.get("desc")

	if not request.user.get_profile().is_lecturer:
		is_lecturer_visible = request.POST.get("is_lecturer_visible")
	
	try:
		if request.user.get_profile().is_lecturer:
			document = Document.objects.get(Q(pk=documentId, is_lecturer_visible=True))
		else:
			document = Document.objects.get(Q(pk=documentId))
	except:
		response = {'success' : False, 'error' : _("Couln't load the document!")}
		return HttpResponse(simplejson.dumps(response))	
	
	if not name:
		response = {'success' : False, 'error' : _("Please enter a name!")}
		return HttpResponse(simplejson.dumps(response))
		
	if not request.user.is_staff and document.author.pk != request.user.pk:
		response = {'success' : False, 'error' : _("You aren't the owner of this document!")}
		return HttpResponse(simplejson.dumps(response))	
	
	# filter tags
	tags = tags.lower().strip()
	tags = re.sub("[^a-z0-9-, ]", "", tags)
	
	document.desc = desc
	document.name = name
	document.tags = tags

	if not request.user.get_profile().is_lecturer:
		if is_lecturer_visible:
			document.is_lecturer_visible = True
		else:
			document.is_lecturer_visible = False

	document.save()
	
	messages.add_message(request, messages.SUCCESS, _("The file has been successfully amended!"))
	response = {'success' : True, 'ok' : _("The file has been successfully amended!")}
	
	return HttpResponse(simplejson.dumps(response))	

@login_required
@has_organisation
def document_delete_view(request, document_id):
	document = get_object_or_404(Document, Q(pk=document_id))
	course = get_object_or_404(Course.objects.distinct('pk'), Q(pk=document.course.pk), Q(scopes__users__id=request.user.pk))

	if document.is_etherpad:
		raise Http404	

	if not request.user.is_staff and request.user != document.author:
		return HttpResponseRedirect(reverse("document", args=[document.pk]))

	# delete revisions
	revisions = DocumentRevision.objects.filter(Q(document=document.pk))
	for revision in revisions:
		revision.file.delete()
		revision.delete()

	# delete comments
	DocumentComment.objects.filter(Q(document=document.pk)).delete()

	# delete document
	document.delete()

	# clear cache
	cache.clear()
	
	messages.add_message(request, messages.SUCCESS, _('The document has been deleted successfully!'))
	return HttpResponseRedirect(reverse("course", args=[course.pk]))

@login_required
@has_organisation
def revision_delete_view(request, revision_id):
	revision = get_object_or_404(DocumentRevision, Q(pk=revision_id))
	course = get_object_or_404(Course.objects.distinct('pk'), Q(pk=revision.document.course.pk), Q(scopes__users__id=request.user.pk))
	document_id = revision.document.pk

	if not request.user.is_staff and request.user != revision.uploaded_by:
		return HttpResponseRedirect(reverse("document", args=[document.pk]))

	# delete revision
	revision.delete()

	# clear cache
	cache.clear()
	
	messages.add_message(request, messages.SUCCESS, _('The Revision has been deleted successfully!'))
	return HttpResponseRedirect(reverse("document", args=[document_id]))	

@login_required
@has_organisation
def document_view(request, document_id):
	if request.user.get_profile().is_lecturer:
		document = get_object_or_404(Document, Q(pk=document_id, is_lecturer_visible=True))
	else:
		document = get_object_or_404(Document, Q(pk=document_id))
	course = get_object_or_404(Course.objects.distinct('pk'), Q(pk=document.course.pk), Q(scopes__users__id=request.user.pk))
	category = Category.objects.get(Q(pk=course.category.pk))

	if document.is_etherpad:
		return HttpResponseRedirect(reverse("etherpad", args=[document.id]))

	comments = DocumentComment.objects.filter(document=document).order_by('pub_date')
	revisions = DocumentRevision.objects.filter(document=document).order_by('-pub_date')[1:]
	tags_raw = Tag.objects.usage_for_model(Document, counts=True)
	cloud_raw = calculate_cloud(tags_raw, steps=2)	
	tags = document.get_tags()
	cloud = [] 
	
	for tag in tags_raw:
		if tag in tags:
			cloud.insert(len(cloud) + 1, tag)

	if 'HTTP_USER_AGENT' in request.META:
		if request.META['HTTP_USER_AGENT'].find('MSIE') > 0:
			internet_explorer_warning = True
	
	return render_to_response("document.html", locals(), context_instance=RequestContext(request))		

@login_required
@is_no_lecturer
@has_organisation
def delete_comment_view(request, comment_id):
	comment = get_object_or_404(DocumentComment, Q(pk=comment_id))
	document_id = comment.document.pk
	
	if (request.user.is_staff == True or comment.author == request.user):
		comment.delete()
		# clear cache
		cache.clear()
		messages.add_message(request, messages.SUCCESS, _("The comment has been deleted."))
		return HttpResponseRedirect(reverse("document", args=[document_id]))				
	else:
		messages.add_message(request, messages.ERROR, _("You aren't the author of this comment!"))
		return HttpResponseRedirect(reverse("document", args=[document_id]))				

@login_required
@is_no_lecturer
@has_organisation
def download_course_view(request, course_id):
	documents = Document.objects.filter(Q(course=course_id, is_etherpad=False))
	course = get_object_or_404(Course.objects.distinct('pk'), Q(pk=course_id), Q(scopes__users__id=request.user.pk))

	if len(documents) == 0:
		messages.add_message(request, messages.INFO, _("There are no documents in this category."))
		return HttpResponseRedirect(reverse("course", args=[course_id]))				

	in_memory = StringIO()
	zip = ZipFile(in_memory, "a", zipfile.ZIP_DEFLATED)

	for document in documents:
		filename = document.getLatestRevision().file.path

		output_name = re.sub('hdd/%s/' % document.course.shell_name, '', document.getLatestRevision().file.name)

		# dirty hack: strip ending out of file name
		ending = output_name.rpartition('.')[len(output_name.rpartition('.'))-1]
		output_name = re.sub('(%s(_|-)\d\.%s|%s\.%s)' % (ending, ending, ending, ending), '.%s' % ending, output_name)		
		output_name = smart_str(u'%s/%s' % (course.name, output_name))

		zip.write(filename, output_name)

	for f in zip.filelist:
		f.create_system = 0
	zip.close()
	
	in_memory.seek(0)
	response = HttpResponse(mimetype="application/zip")
	response['Content-Disposition'] = smart_str(u'attachment; filename=%s.zip' % slugify(course.name))
	response.write(in_memory.read())
	in_memory.close()

	return response

@login_required
@is_no_lecturer
@has_organisation
def save_comment_view(request, document_id):
	document = get_object_or_404(Document, Q(pk=document_id))
	text = request.POST.get('comment')

	if document.is_etherpad:
		raise Http404	
	
	if len(text) < 5 or len(text) > 2000:
		messages.add_message(request, messages.ERROR, _('Your comment is too short (or far too long).'))
		return HttpResponseRedirect(reverse("document", args=[document.pk]))
	else:
		c = DocumentComment(pub_date=datetime.datetime.now(), author=request.user, text=text, document=document)
		c.save()
		
		for subscriber in document.subscribers.all():
			if subscriber.pk != request.user.pk:		
				docmail.docmail(subscriber.email, "[%s] Neuer Kommentar" % document.name, "document_new_comment", Context({ 'user': subscriber, 'document': document, 'text': text, 'author' : request.user, 'domain': settings.DOMAIN }));
		messages.add_message(request, messages.SUCCESS, _('Your comment has been saved!'))
		return HttpResponseRedirect(reverse("document", args=[document.pk]))		

# error-no-organisation
@login_required
def error_no_organisation_view(request):
	if not Organisation.objects.filter(users__pk=request.user.pk):
		mail_admins('error-no-organisation', "User: %s (ID: %d)\nE-Mail: %s" % (request.user.username, request.user.pk, request.user.email))
		return render_to_response("error-no-organisation.html", locals(), context_instance=RequestContext(request))	
	else:
		return HttpResponseRedirect(reverse("default"))
