from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.http import Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpRequest
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
from docman.settings import APP_URL, MEDIA_ROOT, CONTENT_TYPES, MAX_UPLOAD_SIZE, DOMAIN, DEFAULT_FROM_EMAIL, IMPRINT
from dateutil import relativedelta
from docman.app.models import *
from django.utils.translation import ugettext as _
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
# Internationalization
from django.utils.translation import ugettext as _


def is_valid_email(email):
	return True if email_re.match(email) else False
	
def get_directory_size(directory):
	print directory
	dir_size = 0
	for (path, dirs, files) in os.walk(directory):
		for file in files:
			filename = os.path.join(path, file)
			dir_size += os.path.getsize(filename)
	return dir_size
  
@login_required
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

@login_required
def about_view(request):
	stats = { 'space' : get_directory_size(MEDIA_ROOT+'/hdd'), 'count': len(Document.objects.all()) }
	print stats
	imprint = IMPRINT
	return render_to_response("about.html", locals(), context_instance=RequestContext(request))	
	
@login_required
def user_view(request, user_id):
	user = get_object_or_404(User, Q(pk=user_id))
	documents = Document.objects.filter(Q(author=user_id)).order_by('-pub_date')[:10]
	cdocuments = DocumentComment.objects.filter(Q(author=user_id)).order_by('-pub_date')[:10]
	return render_to_response("user.html", locals(), context_instance=RequestContext(request))	

@login_required
def subscribe_course_view(request, course_id):
	course = get_object_or_404(Course, Q(pk=course_id))
	course.subscribers.add(request.user)
	course.save()
	messages.add_message(request, messages.SUCCESS, _('Successfully subscribed to notifications for this course.'))
	return HttpResponseRedirect(reverse("course", args=[course.pk]))	
	
@login_required
def unsubscribe_course_view(request, course_id):
	course = get_object_or_404(Course, Q(pk=course_id))
	course.subscribers.remove(request.user)
	course.save()
	messages.add_message(request, messages.SUCCESS, _('You unsubscribed from notifications for this course.'))
	return HttpResponseRedirect(reverse("course", args=[course.pk]))	

@login_required
def subscribe_document_view(request, document_id):
	document = get_object_or_404(Document, Q(pk=document_id))
	document.subscribers.add(request.user)
	document.save()
	messages.add_message(request, messages.SUCCESS, _('Successfully subscribed to notifications for this document.'))
	return HttpResponseRedirect(reverse("document", args=[document.pk]))	
	
@login_required
def unsubscribe_document_view(request, document_id):
	document = get_object_or_404(Document, Q(pk=document_id))
	document.subscribers.remove(request.user)
	document.save()
	messages.add_message(request, messages.SUCCESS, _('You unsubscribed from notifications for this document.'))
	return HttpResponseRedirect(reverse("document", args=[document.pk]))	
 
@login_required
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
def account_view(request):
	if not request.POST:
		return render_to_response("account.html", locals(), context_instance=RequestContext(request))
	else:
		password = request.POST.get("password")
		repeat = request.POST.get("password_repeat")
		
		if len(password) > 0 and (password != repeat):
			messages.add_message(request, messages.ERROR, _("The passwords don't match."))
			return HttpResponseRedirect(reverse("account", args=[]))
			
		if len(password) < 6:
			messages.add_message(request, messages.ERROR, _("Your password must be at least 5 characters long!"))
			return HttpResponseRedirect(reverse("account", args=[]))
			
		request.user.set_password(password)
		request.user.save()

		messages.add_message(request, messages.SUCCESS, _('Your password has been changed!'))
		return HttpResponseRedirect(reverse("account", args=[]))
		
	
@login_required
def logout_view(reqeust):
	logout(reqeust)
	return HttpResponseRedirect(reverse("default", args=[]))

@csrf_protect
def login_view(request):
	redirect_to = request.REQUEST.get('next', '')
	if request.POST.get("username") and request.POST.get("password"):
		username = request.POST.get("username")
		password = request.POST.get("password")
		error = False
		
		print redirect_to
		
		if redirect_to.find('.') > 0:
			redirect_to = '/'
			
		print redirect_to
		
		user = authenticate(username=username, password=password)
	
		if user is None:
			error = _("Username or password invalid.")
		else:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(redirect_to)
			else:
				error = _("This account has been deactivated.")
	
	next = redirect_to
	return render_to_response("login.html", locals(), context_instance=RequestContext(request))

@login_required
def search_view(request):
	pass
	
	return render_to_response("search.html", locals(), context_instance=RequestContext(request))

@login_required
def tag_cloud_view(request):
	tags = Tag.objects.usage_for_model(Document, counts=True)
	cloud = calculate_cloud(tags, steps=2)
	return render_to_response("tag-cloud.html", locals(), context_instance=RequestContext(request))

@login_required
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
	
	return render_to_response("tag.html", locals(), context_instance=RequestContext(request))

@login_required
def default_view(request):
	categories = Category.objects.all().order_by('-name')
	return render_to_response("default.html", locals(), context_instance=RequestContext(request))
	
@login_required
def document_edit_view(request, document_id):
	tags = request.POST.get("tags")
	desc = request.POST.get("desc")
	doEdit = request.POST.get('doEdit')
	
	try:
		document = Document.objects.get(Q(pk=document_id))
	except:
		response = {'success' : False, 'error' : _("Couln't load the document!")}
		return HttpResponse(simplejson.dumps(response))	
		
	if (request.user.is_staff == False and document.author != request.user):
		response = {'success' : False, 'error' : _("You aren't the owner of this document!")}
		return HttpResponse(simplejson.dumps(response))	
	
	if doEdit == 'tags':
		# filter tags
		tags = tags.lower().strip()
		tags = re.sub("[^a-z0-9- ]", "", tags)
		document.tags = tags
	elif doEdit == 'desc':
		document.desc = desc
	else:
		response = {'success' : False, 'error' : _('Data is missing!')}
		return HttpResponse(simplejson.dumps(response))
		
	document.save()
	
	response = {'success' : True, 'desc_clean' : escape(desc), 'desc' : '<div class="desc">%s</p>' % (linebreaks(urlize(escape(desc)))) }
	return HttpResponse(simplejson.dumps(response))	
	
@login_required
def download_view(request, document_id):
	document = get_object_or_404(Document, Q(pk=document_id))
	revisionId = request.GET.get('rev')
	zipped = request.GET.get('zipped')
	
	if not revisionId:
		filename = document.getLatestRevision().file.path
		ffile = document.getLatestRevision().file
	else:
		revision = get_object_or_404(DocumentRevision, Q(pk=revisionId))
		filename = revision.file.path
		ffile = revision.file
		
	print filename
	
	output_name = re.sub('hdd/%s' % document.course.shell_name, '', ffile.name)
		
	if not zipped:
		wrapper = FileWrapper(file(filename))
		response = HttpResponse(wrapper, content_type='text/plain')
		response['Content-Length'] = os.path.getsize(filename)
		response['Content-Type'] = 'application/force-download';
		response['Content-disposition'] = 'attachment; filename=%s' % output_name
		response['Pragma'] = 'no-cache'
		response['Expires'] = 0
	else:
		in_memory = StringIO()
		zip = ZipFile(in_memory, "a")
		zip.write(filename, output_name)
		for f in zip.filelist:
			f.create_system = 0
		zip.close()
		in_memory.seek(0)
		response = HttpResponse(mimetype="application/zip")
		response['Content-Disposition'] = 'attachment; filename=%s.zip' % output_name
		response.write(in_memory.read())
		in_memory.close()
	return response

@login_required
def docent_view(request, docent_id):
	docent = get_object_or_404(Docent, Q(pk=docent_id))
	courses = Course.objects.filter(Q(docent=docent_id))
	return render_to_response("docent.html", locals(), context_instance=RequestContext(request))
	
@login_required
def course_view(request, course_id):
	page = request.GET.get('p')
	course = get_object_or_404(Course, Q(pk=course_id))
	category = Category.objects.get(Q(pk=course.category.pk))
	documents_raw = course.getDocuments()
	documents_paginator = Paginator(documents_raw, 20)
	
	try:
		documents = documents_paginator.page(page)
	except TypeError:
		documents = documents_paginator.page(1)
	except PageNotAnInteger:
		documents = documents_paginator.page(1)
	except EmptyPage:
		documents = documents_paginator.page(documents_paginator.num_pages)
	
	return render_to_response("course.html", locals(), context_instance=RequestContext(request))
	
def upload_test_view(request):
	uploadFile = request.FILES['fileUpload']
	
	course = Course.objects.get(Q(pk=1))
	
	document = Document(name="Test", pub_date=datetime.datetime.now(), author=request.user, course=course)
	document.save()
	revision = DocumentRevision(document=document, pub_date=datetime.datetime.now())
	revision.file.save(request.FILES['fileUpload'].name, request.FILES['fileUpload'], False)

	print revision.file.path
	
	pdf = pyPdf.PdfFileReader(open(revision.file.path, "rb"))
	for page in pdf.pages:
		print page.extractText()

@login_required
def file_info_view(request):
	documentId = request.POST.get("documentId")
	name = request.POST.get("name")
	tags = request.POST.get("tags")
	desc = request.POST.get("desc")
	
	try:
		document = Document.objects.get(Q(pk=documentId))
	except:
		response = {'success' : False, 'error' : _("Couln't load the document!")}
		return HttpResponse(simplejson.dumps(response))	
	
	if not name:
		response = {'success' : False, 'error' : _("Please enter a name!")}
		return HttpResponse(simplejson.dumps(response))
		
	if document.author.pk != request.user.pk:
		response = {'success' : False, 'error' : _("You aren't the owner of this document!")}
		return HttpResponse(simplejson.dumps(response))	
	
	# filter tags
	tags = tags.lower().strip()
	tags = re.sub("[^a-z0-9- ]", "", tags)
	
	document.desc = desc
	document.name = name
	document.tags = tags
	document.save()
	
	response = {'success' : True}
	return HttpResponse(simplejson.dumps(response))	

@login_required
def document_delete_view(request, document_id):
	document = get_object_or_404(Document, Q(pk=document_id))
	course = Course.objects.get(Q(pk=document.course.pk))

	if not request.user.is_staff and request.user != document.author:
		return HttpResponseRedirect(reverse("document", args=[document.pk]))
	
	revisions = DocumentRevision.objects.filter(Q(document=document.pk))
	for revision in revisions:
		revision.file.delete()
		revision.delete()
				
	document.delete()
	
	messages.add_message(request, messages.SUCCESS, _('The document has been deleted successfully!'))
	return HttpResponseRedirect(reverse("course", args=[course.pk]))

@login_required
def document_view(request, document_id):
	document = get_object_or_404(Document, Q(pk=document_id))
	course = Course.objects.get(Q(pk=document.course.pk))
	category = Category.objects.get(Q(pk=course.category.pk))
	comments = DocumentComment.objects.filter(document=document).order_by('-pub_date')
	revisions = DocumentRevision.objects.filter(document=document).order_by('-pub_date')[1:]
	tags_raw = Tag.objects.usage_for_model(Document, counts=True)
	cloud_raw = calculate_cloud(tags_raw, steps=2)	
	tags = document.get_tags()
	cloud = [] 
	
	for tag in tags_raw:
		if tag in tags:
			cloud.insert(len(cloud) + 1, tag)
	
	return render_to_response("document.html", locals(), context_instance=RequestContext(request))

@login_required
def delete_comment_view(request, comment_id):
	comment = get_object_or_404(DocumentComment, Q(pk=comment_id))
	document_id = comment.document.pk
	
	if (request.user.is_staff == True or comment.author == request.user):
		comment.delete()
		messages.add_message(request, messages.SUCCESS, _("The comment has been deleted."))
		return HttpResponseRedirect(reverse("document", args=[document_id]))				
	else:
		messages.add_message(request, messages.ERROR, _("You aren't the author of this comment!"))
		return HttpResponseRedirect(reverse("document", args=[document_id]))				

@login_required
def download_course_view(request, course_id):
	documents = Document.objects.filter(Q(course=course_id))
	course = get_object_or_404(Course, Q(pk=course_id))

	if len(documents) == 0:
		messages.add_message(request, messages.INFO, _("There are no documents in this category."))
		return HttpResponseRedirect(reverse("course", args=[course_id]))				

	in_memory = StringIO()
	zip = ZipFile(in_memory, "a")

	for document in documents:
		filename = document.getLatestRevision().file.path
		output_name = re.sub('hdd/%s' % document.course.shell_name, '', document.getLatestRevision().file.name)
		output_name = smart_str(u'%s/%s' % (course.name, output_name))

		zip.write(filename, output_name)

	for f in zip.filelist:
		f.create_system = 0
	zip.close()
	
	in_memory.seek(0)
	response = HttpResponse(mimetype="application/zip")
	response['Content-Disposition'] = smart_str(u'attachment; filename=%s.zip' % course.name)
	response.write(in_memory.read())
	in_memory.close()

	return response

@login_required
def save_comment_view(request, document_id):
	document = get_object_or_404(Document, Q(pk=document_id))
	text = request.POST.get('comment')
	
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
	
		
#@login_required
def upload_view(request):
	courseId = request.POST.get("courseId")
	sessionId = request.POST.get("sessionId") 
	uploadFile = request.FILES['Filedata']
	documentId = request.POST.get("documentId")
	
	try:
		session = Session.objects.get(session_key=sessionId)
		uid = session.get_decoded().get('_auth_user_id')
		request.user = User.objects.get(pk=uid)
	except:
		response = {'success' : False, 'error' : _("There is a problem with the session - please log out and back in!")}
		return HttpResponse(simplejson.dumps(response))
	
	if not documentId:
		try:
			course = Course.objects.get(Q(pk=courseId))
		except:
			response = {'success' : False, 'error' : _("Course couldn't be loaded - please try again!")}
			return HttpResponse(simplejson.dumps(response))
	else:
		try:
			document = Document.objects.get(Q(pk=documentId))
		except:
			response = {'success' : False, 'error' : _("Document couln't be loaded - please try again!")}
			return HttpResponse(simplejson.dumps(response))		
		
	try:
		content_type = uploadFile.content_type
		if content_type in CONTENT_TYPES:
			if uploadFile._size > MAX_UPLOAD_SIZE:
				response = {'success' : False, 'error' : _('The file is too big!')}
				return HttpResponse(simplejson.dumps(response))
		else:
				response = {'success' : False, 'error' : _('The file type %s is not supported.') % content_type}
				return HttpResponse(simplejson.dumps(response))
	except:
		response = {'success' : False, 'error' : _("An unexpected error occured while uploading the file.")}
		return HttpResponse(simplejson.dumps(response))
	
	if not documentId:
		try:
			document = Document(name=uploadFile.name, pub_date=datetime.datetime.now(), author=request.user, course=course)			
			document.save()
			# auto-subscribe to document
			document.subscribers.add(request.user)			
			revision = DocumentRevision(document=document, pub_date=datetime.datetime.now())
			revision.file.save(slugify(uploadFile.name) + '.' + uploadFile.name.rpartition('.')[len(uploadFile.name.rpartition('.'))-1], uploadFile)
					
			for subscriber in course.subscribers.all():
				if subscriber.pk != request.user.pk:
					docmail.docmail(subscriber.email, "[%s] Neues Dokument" % course.name, "course_new_document", Context({ 'user': subscriber, 'document': document, 'author' : request.user, 'course' : course, 'domain': settings.DOMAIN }));
			
		except:
			raise
			response = {'success' : False, 'error' : _("An unexpected error occured while uploading the file.")}
			return HttpResponse(simplejson.dumps(response))		
	else:
		try:
			revision = DocumentRevision(document=document, pub_date=datetime.datetime.now())
			revision.file.save(uploadFile.name, uploadFile)
			for subscriber in document.subscribers.all():
				if subscriber.pk != request.user.pk:
					docmail.docmail(subscriber.email, "[%s] Neue Revision" % document.name, "document_new_revision", Context({ 'user': subscriber, 'document': document, 'author' : request.user, 'domain': settings.DOMAIN }));
		except:
			response = {'success' : False, 'error' : _("An unexpected error occured while uploading the file.")}
			return HttpResponse(simplejson.dumps(response))				
	
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
	else:
		if revision.file.name.find('pages') > 0:
			revision.type = 'doc'
		elif revision.file.name.find('key') > 0:
			revision.type = 'ppt'			
		elif revision.file.name.find('ppt') > 0:
			revision.type = 'ppt'						
		elif revision.file.name.find('xls') > 0:
			revision.type = 'xls'						
		elif revision.file.name.find('doc') > 0:
			revision.type = 'doc'									
		elif revision.file.name.find('odp') > 0:
			revision.type = 'ppt'						
		else:
			revision.type = 'file'
	
	#mime = magic.Magic(mime=True)
	#revision.type = mime.from_file(revision.file.path).split('/')[1]
		
	try:
		print content_type
		print uploadFile.name.rpartition('.')[len(uploadFile.name.rpartition('.'))-1]
		"""(content_type is 'application/pdf' or content_type is 'application/octet-stream') and """
		if uploadFile.name.rpartition('.')[len(uploadFile.name.rpartition('.'))-1] == 'pdf':
			print "detected pdf, opening.."
			try:
				pdf = pyPdf.PdfFileReader(open(revision.file.path, "rb"))
				raw = ""
				for page in pdf.pages:
					raw = "%s %s" % (raw, page.extractText())
				revision.raw = raw
			except:
				pass
		elif uploadFile.name.rpartition('.')[len(uploadFile.name.rpartition('.'))-1] == 'txt': 
			revision.raw = revision.file.read()
		elif uploadFile.name.rpartition('.')[len(uploadFile.name.rpartition('.'))-1] == 'taskpaper': 
			revision.raw = revision.file.read()			
		else:
			print "no pdf, no txt, no taskpaper"
	except:
		pass
		
	#if revision.raw:
	#	tags = [slugify(word) for word in set(revision.raw.split(" ")) if len(word) > 8]
	#	tags = tags[:20]
	#'tags': ' '.join(tags),
		
	revision.save()
	
	response = {'documentName' : document.name, 'documentId' : document.pk, 'success' : True, 'ok' : _("The Document has ben uploaded successfully.")}
	return HttpResponse(simplejson.dumps(response))
