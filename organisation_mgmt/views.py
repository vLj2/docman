from django.core.mail import mail_admins
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpRequest
from django.template import RequestContext
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from datetime import datetime
from docman.settings import APP_URL, MEDIA_ROOT, CONTENT_TYPES, MAX_UPLOAD_SIZE, DOMAIN, DEFAULT_FROM_EMAIL, IMPRINT, SUPPORT_EMAIL, FACEBOOK_APP_ID
from docman.app.models import *
from django.core.validators import email_re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.simple import direct_to_template
from django.utils.encoding import smart_str, smart_unicode
from app import docmail
from django.template import Context
from django.utils import simplejson
import re
from django.core.validators import email_re
from django.template.defaultfilters import slugify
from django.core import serializers


# Internationalization
from django.utils.translation import ugettext as _

# tools
def is_valid_email(email):
	return True if email_re.match(email) else False

@login_required
def default_view(request):
	organisations = Organisation.objects.filter(Q(managers__id=request.user.pk))

	if not organisations:
		raise Http404

	return render_to_response("organisation/default.html", locals(), context_instance=RequestContext(request))

@login_required
def organisation_lecturer_mgmt_filter(request, organisation_id):
	term = request.GET.get('term')

	try:
		organisation = Organisation.objects.get(Q(pk=organisation_id), Q(managers__id=request.user.pk))
	except Organisation.DoesNotExist:
		organisation = False

	response = []

	if organisation and term:
		lecturers = organisation.docents.filter(Q(name__icontains=term) | Q(email__icontains=term))
	
		if lecturers:
			for lecturer in lecturers:
				is_active = False
				has_account = False
				last_login = "Never"
				if lecturer.getUser():
					last_login = lecturer.getUser().last_login.strftime('%Y-%m-%d %H:%M:%S')
					has_account = True
					if lecturer.getUser().is_active:
						is_active = True
					
				response.append({'pk':lecturer.pk, 'id':lecturer.pk, 'name': lecturer.name, 'email':lecturer.email, 'is_active': is_active, 'has_account': has_account, 'last_login': last_login})

	return HttpResponse(simplejson.dumps(response))

@login_required
def organisation_user_mgmt_filter(request, organisation_id):
	term = request.GET.get('term')

	try:
		organisation = Organisation.objects.get(Q(pk=organisation_id), Q(managers__id=request.user.pk))
	except Organisation.DoesNotExist:
		organisation = False

	response = []

	if organisation and term:
		users = organisation.users.filter(Q(userprofile__is_lecturer=False) & (Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(username__icontains=term) | Q(email__icontains=term)))
	
		if users:
			for user in users:
				response.append({'pk':user.pk, 'id':user.pk, 'first_name': user.first_name, 'last_name': user.last_name, 'username': user.username, 'is_active': user.is_active, 'email':user.email, 'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S')})


	return HttpResponse(simplejson.dumps(response))

@login_required
def organisation_scope_mgmt_filter(request, organisation_id):
	term = request.GET.get('term')

	try:
		organisation = Organisation.objects.get(Q(pk=organisation_id), Q(managers__id=request.user.pk))
	except Organisation.DoesNotExist:
		organisation = False

	response = []

	if organisation and term:
		scopes = organisation.scopes.filter(Q(name__icontains=term))

		if scopes:
			for scope in scopes:
				users = scope.getUsersAssigned()
				courses = scope.getCourses()
				courses_string = ''
				if courses.count() == 0:
					courses_string = ''
				else:
					for course in courses:
						courses_string+= course.name+', '
					courses_string = re.sub(", $", "", courses_string)
				response.append({'pk':scope.pk, 'id':scope.pk, 'name': scope.name, 'courses': courses_string, 'users': users})

	return HttpResponse(simplejson.dumps(response))	

@login_required
def organisation_course_mgmt_filter(request, organisation_id):
	term = request.GET.get('term')

	try:
		organisation = Organisation.objects.get(Q(pk=organisation_id), Q(managers__id=request.user.pk))
	except Organisation.DoesNotExist:
		organisation = False

	response = []

	if organisation and term:
		courses = organisation.courses.filter(Q(name__icontains=term) | Q(category__name__icontains=term) | Q(scopes__name__icontains=term))
	
		if courses:
			for course in courses:
				scopes = course.get_scopes()
				scope_string = ''
				if scopes.count() == 0:
					scope_string = '-'
				else:
					for scope in course.get_scopes():
						scope_string+=scope.name+', '
				scope_string = re.sub(", $", "", scope_string)
				response.append({'pk':course.pk, 'id':course.pk, 'semester': course.getSemester(), 'category': course.category.name, 'name': course.name, 'lecturer': course.docent.name, 'scopes': scope_string})


	return HttpResponse(simplejson.dumps(response))

@login_required
def organisation_autocomplete_course_scope_view(request, organisation_id, course_id):
	term = request.GET.get('term')

	try:
		organisation = Organisation.objects.get(Q(pk=organisation_id), Q(managers__id=request.user.pk))
	except Organisation.DoesNotExist:
		organisation = False

	response = []

	if organisation:
		course = Course.objects.get(Q(pk=course_id))
		if course:
			scopes = Scope.objects.filter(Q(pk__in=organisation.scopes.all()), Q(name__icontains=term)).exclude(pk__in=course.scopes.all())
			if scopes:
				for scope in scopes:
					response.append({'id': scope.pk, 'value': scope.name, 'label': scope.name})

	return HttpResponse(simplejson.dumps(response))

@login_required
def organisation_autocomplete_scope_course_view(request, organisation_id, scope_id):
	term = request.GET.get('term')
	
	try:
		organisation = Organisation.objects.get(Q(pk=organisation_id), Q(managers__id=request.user.pk))
	except Organisation.DoesNotExist:
		organisation = False

	response = []

	if organisation:
		scope = Scope.objects.get(Q(pk=scope_id))
		
		if organisation.scopes.filter(Q(pk=scope_id)):
			courses = organisation.courses.filter(Q(name__icontains=term)).exclude(scopes__pk=scope.pk)

			if courses:
				for course in courses:
					response.append({'id': course.pk, 'value': course.name, 'label': course.name+' <span style=font-size:x-small>('+course.category.name+')</span>'})

	return HttpResponse(simplejson.dumps(response))

@login_required
def organisation_autocomplete_scope_user_view(request, organisation_id, scope_id):
	term = request.GET.get('term')
	
	try:
		organisation = Organisation.objects.get(Q(pk=organisation_id), Q(managers__id=request.user.pk))
	except Organisation.DoesNotExist:
		organisation = False

	response = []

	if organisation:
		scope = Scope.objects.get(Q(pk=scope_id))
		
		if organisation.scopes.filter(Q(pk=scope_id)):
			users = organisation.users.filter(Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(username__contains=term)).exclude(pk__in=scope.users.all())

			if users:
				for user in users:
					response.append({'id': user.pk, 'value': user.username, 'label': user.first_name+' '+user.last_name})

	return HttpResponse(simplejson.dumps(response))

@login_required
def organisation_autocomplete_view(request, organisation_id, user_id):
	term = request.GET.get('term')
	user = User.objects.get(Q(pk=user_id))

	if user:
		organisation = Organisation.objects.get(Q(pk=organisation_id), Q(managers__id=request.user.pk), Q(users__id=user_id))

	if organisation:
		scopes = organisation.scopes.filter(Q(name__icontains=term)).exclude(users__id=user.pk).order_by('name')

	response = []
	if scopes:
		for scope in scopes:
			courses = scope.getCourses()[:3]
			coursesString = ''
			if not courses:
				coursesString = _('No courses')
			else:
				for course in courses:
					coursesString = '%s%s, ' % (coursesString, course.name)
			
			coursesString = re.sub(", $", "", coursesString)
			response.append({'id': scope.pk, 'value': scope.name, 'label': scope.name + ' <span style=font-size:x-small>('+coursesString+')</span>'})
	
	return HttpResponse(simplejson.dumps(response))

@login_required
def organisation_view(request, organisation_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))

	active_page = 'overview'
	return render_to_response("organisation/organisation.html", locals(), context_instance=RequestContext(request))

@login_required
def organisation_course_mgmt_view(request, organisation_id, course_id=False):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))
	active_page = 'course_management'

	if course_id:
		course = get_object_or_404(Course, Q(pk=course_id))
		if not organisation.courses.filter(Q(pk=course_id)):
			raise Http404

		categories = Category.objects.all().order_by('-name')
		lecturers = organisation.docents.all()
		semesters = [1,2,3,4,5,6,-1]

		if request.POST:
			name = request.POST.get('name')
			category_id = request.POST.get('category')
			lecturer_id = request.POST.get('lecturer')
			semester = request.POST.get('semester')
			category = get_object_or_404(Category, Q(pk=category_id))
			lecturer = get_object_or_404(organisation.docents.all(), Q(pk=lecturer_id))

			error = False

			if len(name) < 5:
				error = True
				messages.add_message(request, messages.ERROR, _('Minimum length for course names: 5 characters.'))
			
			if category not in categories:
				error = True
				messages.add_message(request, messages.ERROR, _('Please select a valid category.'))

			if lecturer not in lecturers:
				error = True
				messages.add_message(request, messages.ERROR, _('Please select a valid lecturer.'))
		
			if int(semester) not in semesters:
				error = True
				messages.add_message(request, messages.ERROR, _('Please select a valid semester.'))

			if not error:
				course.category = category
				course.docent = lecturer
				course.semester = int(semester)
				course.name = name
				course.save()

				messages.add_message(request, messages.SUCCESS, _('The course has been successfully amended.'))

		return render_to_response("organisation/course_mgmt_edit.html", locals(), context_instance=RequestContext(request))

	courses = organisation.courses.all()
	json_array = []
	for course in courses:
		scope_string = ''
		scopes = course.get_scopes()
		if scopes.count() == 0:
			scope_string = '-'
		else:
			for scope in course.get_scopes():
				scope_string+=scope.name+', '
			scope_string = re.sub(", $", "", scope_string)
		json_array.append({'name':course.name, 'pk':course.pk, 'id':course.pk, 'semester': course.getSemester(), 'category': course.category.name, 'lecturer': course.docent.name, 'scopes': scope_string})

	json_cache = simplejson.dumps(json_array)
	return render_to_response("organisation/course_mgmt.html", locals(), context_instance=RequestContext(request))

@login_required
def organisation_course_mgmt_create_view(request, organisation_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))

	categories = Category.objects.all().order_by('-name')
	lecturers = organisation.docents.all()
	semesters = [1,2,3,4,5,6,-1]

	active_page = 'course_management'
	if request.POST:
		name = request.POST.get('name')
		category_id = request.POST.get('category')
		lecturer_id = request.POST.get('lecturer')
		semester = request.POST.get('semester')

		error = False

		try:
			category = Category.objects.get(Q(pk=category_id))
			lecturer = organisation.docents.get(Q(pk=lecturer_id))
		except:
			messages.add_message(request, messages.ERROR, _('Please select a category and lecturer.'))
			return render_to_response("organisation/course_mgmt_create.html", locals(), context_instance=RequestContext(request))

		if len(name) < 5:
			error = True
			messages.add_message(request, messages.ERROR, _('Minimum length for course names: 5 characters.'))
			
		if category not in categories:
			error = True
			messages.add_message(request, messages.ERROR, _('Please select a valid category.'))

		if lecturer not in lecturers:
			error = True
			messages.add_message(request, messages.ERROR, _('Please select a valid lecturer.'))
		
		if semester:
			if int(semester) not in semesters:
				error = True
				messages.add_message(request, messages.ERROR, _('Please select a valid semester.'))
		else:
			error = True
			messages.add_message(request, messages.ERROR, _('Please select a valid semester.'))
				

		if not error:
			course = Course(name=name, category=category, docent=lecturer, semester=semester, shell_name=slugify(name))
			course.save()
			organisation.courses.add(course)
			messages.add_message(request, messages.SUCCESS, _('The course has been successfully created.'))
		
			return HttpResponseRedirect(reverse("organisation-course-mgmt-edit", args=[organisation_id, course.pk]))

	return render_to_response("organisation/course_mgmt_create.html", locals(), context_instance=RequestContext(request))

@login_required
def organisation_course_mgmt_deletescope_view(request, organisation_id, course_id, scope_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))	
	course = get_object_or_404(Course, Q(pk=course_id), Q(pk__in=organisation.courses.all())) #course does exist

	try:
		scope = Scope.objects.get(pk=scope_id, pk__in=organisation.scopes.all())
	except:
		messages.add_message(request, messages.ERROR, _('This scope does not exist!'))
		return HttpResponseRedirect(reverse("organisation-course-mgmt-edit", args=[organisation_id, course_id]))	

	if scope in course.scopes.all():
		course.scopes.remove(scope)
		messages.add_message(request, messages.SUCCESS, _('The scope has been removed from this course.'))
		return HttpResponseRedirect(reverse("organisation-course-mgmt-edit", args=[organisation_id, course_id]))
	else:
		messages.add_message(request, messages.INFO, _('The scope is not connected to this course.'))
		return HttpResponseRedirect(reverse("organisation-course-mgmt-edit", args=[organisation_id, course_id]))

@login_required
def organisation_course_mgmt_addscope_view(request, organisation_id, course_id):
	scope_name = request.POST.get("scope")
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))	
	course = get_object_or_404(Course, Q(pk=course_id), Q(pk__in=organisation.courses.all())) #course does exist

	try:
		scope = Scope.objects.get(name=scope_name, pk__in=organisation.scopes.all())
	except:
		messages.add_message(request, messages.ERROR, _('This scope does not exist!'))
		return HttpResponseRedirect(reverse("organisation-course-mgmt-edit", args=[organisation_id, course_id]))	

	if scope not in course.scopes.all():
		course.scopes.add(scope)
		messages.add_message(request, messages.SUCCESS, _('The scope has been added to this course.'))
		return HttpResponseRedirect(reverse("organisation-course-mgmt-edit", args=[organisation_id, course_id]))
	else:
		messages.add_message(request, messages.INFO, _('The scope is already connected to this course.'))
		return HttpResponseRedirect(reverse("organisation-course-mgmt-edit", args=[organisation_id, course_id]))

@login_required
def organisation_course_mgmt_delete_view(request, organisation_id, course_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))
	course = get_object_or_404(Course, Q(pk=course_id), Q(pk__in=organisation.courses.all()))
	sure_flag = request.POST.get('sure_flag')

	if not sure_flag:
		messages.add_message(request, messages.ERROR, _('You need to tick the checkbox in case to delete the course.'))
		return HttpResponseRedirect(reverse("organisation-course-mgmt-edit", args=[organisation_id, course_id]))
	else:
		course.delete()
		messages.add_message(request, messages.SUCCESS, _('The course has been successfully deleted.'))
		return HttpResponseRedirect(reverse("organisation-course-mgmt", args=[organisation_id]))

@login_required
def organisation_lecturer_mgmt_view(request, organisation_id, lecturer_id=False):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))

	active_page = 'lecturer_management'

	if lecturer_id:
		lecturer = get_object_or_404(Docent, Q(pk=lecturer_id))
		if not organisation.docents.filter(Q(pk=lecturer_id)):
			raise Http404

		if lecturer.getUser():
			scopes = Scope.objects.filter(Q(users__id=lecturer.getUser().pk), Q(pk__in=organisation.scopes.all())).order_by('name')

		if request.POST:
			messages.add_message(request, messages.SUCCESS, _('The lecturer has been successfully amended.'))

		return render_to_response("organisation/lecturer_mgmt_edit.html", locals(), context_instance=RequestContext(request))

	lecturers = organisation.docents.all()
	json_array = []
	for lecturer in lecturers:
		is_active = False
		has_account = False
		last_login = "Never"
		if lecturer.getUser():
			has_account = True
			last_login = lecturer.getUser().last_login.strftime('%Y-%m-%d %H:%M:%S')
			if lecturer.getUser().is_active:
				is_active = True
		lecturer.last_login = last_login
		lecturer.is_active = is_active
		lecturer.has_account = has_account
		json_array.append({'id': lecturer.pk, 'pk': lecturer.pk, 'name': lecturer.name, 'email': lecturer.email, 'is_active': is_active, 'has_account': has_account, 'last_login': last_login});

	json_cache = simplejson.dumps(json_array)
	return render_to_response("organisation/lecturer_mgmt.html", locals(), context_instance=RequestContext(request))	

@login_required
def organisation_lecturer_mgmt_create_view(request, organisation_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))

	active_page = 'lecturer_management'
	if request.POST:
		name = request.POST.get('name')
		email = request.POST.get('email')

		error = False

		# check name
		if len(name) < 1:
			error = True
			messages.add_message(request, messages.ERROR, _('Name is a required field.'))

		# check email
		if not is_valid_email(email):
			error = True
			messages.add_message(request, messages.ERROR, _('The email address has an invalid format.'))
		if Docent.objects.filter(Q(email__iexact=email)):
			error = True
			messages.add_message(request, messages.ERROR, _('This email adress has already been taken!'))

		if not error:
			lecturer = Docent(name=name, email=email)
			lecturer.save()
			organisation.docents.add(lecturer)
			messages.add_message(request, messages.SUCCESS, _('The lecturer has been successfully created.'))
			
			return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, lecturer.pk]))

		return render_to_response("organisation/lecturer_mgmt_create.html", locals(), context_instance=RequestContext(request))
	else:
		return render_to_response("organisation/lecturer_mgmt_create.html", locals(), context_instance=RequestContext(request))

@login_required
def organisation_lecturer_mgmt_delete_view(request, organisation_id, lecturer_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))
	lecturer = get_object_or_404(Docent, Q(pk=lecturer_id), Q(pk__in=organisation.docents.all()))
	sure_flag = request.POST.get('sure_flag')

	if lecturer.getUser().pk == request.user.pk:
		raise Http404

	if not sure_flag:
		messages.add_message(request, messages.ERROR, _('You need to tick the checkbox in case to delete the lecturer.'))
		return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, user.pk]))
	else:
		lecturer.delete()

		messages.add_message(request, messages.SUCCESS, _('The lecturer has been successfully deleted.'))
		return HttpResponseRedirect(reverse("organisation-lecturer-mgmt", args=[organisation_id]))

@login_required
def organisation_scope_mgmt_delete_view(request, organisation_id, scope_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))
	scope = get_object_or_404(Scope, Q(pk=scope_id), Q(pk__in=organisation.scopes.all()))
	sure_flag = request.POST.get('sure_flag')

	if not sure_flag:
		messages.add_message(request, messages.ERROR, _('You need to tick the checkbox in case to delete the scope.'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope.pk]))
	else:
		scope.delete()
		messages.add_message(request, messages.SUCCESS, _('The scope has been successfully deleted.'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt", args=[organisation_id]))

@login_required
def organisation_scope_mgmt_create_view(request, organisation_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))

	active_page = 'scope_management'
	if request.POST:
		name = request.POST.get('name')

		error = False

		if len(name) < 2:
			error = True
			messages.add_message(request, messages.ERROR, _('Minimum length for scope names: 2 characters'))

		if Scope.objects.filter(Q(name__iexact=name), Q(pk__in=organisation.scopes.all())):
			error = True
			messages.add_message(request, messages.ERROR, _('This scope name has already been taken!'))

		if not error:
			scope = Scope(name=name)
			scope.save()
			organisation.scopes.add(scope)
			messages.add_message(request, messages.SUCCESS, _('The scope has been successfully created.'))
		
			return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope.pk]))

	return render_to_response("organisation/scope_mgmt_create.html", locals(), context_instance=RequestContext(request))
		
@login_required
def organisation_scope_mgmt_view(request, organisation_id, scope_id=False):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))

	active_page = 'scope_management'
	
	if scope_id:
		scope = get_object_or_404(Scope, Q(pk=scope_id))
		if not organisation.scopes.filter(Q(pk=scope_id)):
			raise Http404

		if request.POST:
			name = request.POST.get('name')

			error = False

			if len(name) < 2:
				error = True
				messages.add_message(request, messages.ERROR, _('Minimum length for scope names: 2 characters'))

			if Scope.objects.filter(Q(name__iexact=name), Q(pk__in=organisation.scopes.all())).exclude(pk=scope.pk):
				error = True
				messages.add_message(request, messages.ERROR, _('This scope name has already been taken!'))

			if not error:
				scope.name = name
				scope.save()
				messages.add_message(request, messages.SUCCESS, _('The scope has been successfully amended.'))

		return render_to_response("organisation/scope_mgmt_edit.html", locals(), context_instance=RequestContext(request))

	else:
		scopes = organisation.scopes.all()

		json_array = []
		for scope in scopes:
			users = scope.getUsersAssigned()
			courses = scope.getCourses()
			courses_string = ''
			if courses.count() == 0:
				courses_string = ''
			else:
				for course in courses:
					courses_string+= course.name+', '
				courses_string = re.sub(", $", "", courses_string)
			json_array.append({'pk':scope.pk, 'id':scope.pk, 'name': scope.name, 'courses': courses_string, 'users': users})
		json_cache = simplejson.dumps(json_array)
		return render_to_response("organisation/scope_mgmt.html", locals(), context_instance=RequestContext(request))

@login_required
def organisation_user_mgmt_newpassword_view(request, organisation_id, user_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))
	user = get_object_or_404(User, Q(pk=user_id), Q(pk__in=organisation.users.all()), ~Q(pk=request.user.pk), ~Q(pk__in=organisation.managers.all()))

	user.get_profile().reset_password()
	
	if request.GET.get('lecturer'):
		messages.add_message(request, messages.SUCCESS, _('An email with a new password has been sent to the lecturer.'))
		return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, user.get_profile().lecturer_id.pk]))
	else:
		messages.add_message(request, messages.SUCCESS, _('An email with a new password has been sent to the user.'))
		return HttpResponseRedirect(reverse("organisation-user-mgmt-edit", args=[organisation_id, user_id]))

@login_required
def organisation_user_mgmt_disable_view(request, organisation_id, user_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))
	user = get_object_or_404(User, Q(pk=user_id), Q(pk__in=organisation.users.all()), ~Q(pk=request.user.pk), ~Q(pk__in=organisation.managers.all()))

	user.is_active = False
	user.save()

	if request.GET.get('lecturer'):
		messages.add_message(request, messages.SUCCESS, _('The lecturer has been successfully disabled.'))
		return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, user.get_profile().lecturer_id.pk]))
	else:
		messages.add_message(request, messages.SUCCESS, _('The user has been successfully disabled.'))
		return HttpResponseRedirect(reverse("organisation-user-mgmt-edit", args=[organisation_id, user_id]))

@login_required
def organisation_user_mgmt_enable_view(request, organisation_id, user_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))
	user = get_object_or_404(User, Q(pk=user_id), Q(pk__in=organisation.users.all()), ~Q(pk=request.user.pk), ~Q(pk__in=organisation.managers.all()))

	user.is_active = True
	user.save()

	if request.GET.get('lecturer'):
		messages.add_message(request, messages.SUCCESS, _('The lecturer has been successfully enabled.'))
		return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, user.get_profile().lecturer_id.pk]))
	else:
		messages.add_message(request, messages.SUCCESS, _('The user has been successfully enabled.'))
		return HttpResponseRedirect(reverse("organisation-user-mgmt-edit", args=[organisation_id, user_id]))

@login_required
def organisation_user_mgmt_delete_view(request, organisation_id, user_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))
	user = get_object_or_404(User, Q(pk=user_id), Q(pk__in=organisation.users.all()), ~Q(pk=request.user.pk), ~Q(pk__in=organisation.managers.all()))
	sure_flag = request.POST.get('sure_flag')

	if not sure_flag:
		messages.add_message(request, messages.ERROR, _('You need to tick the checkbox in case to delete the user.'))
		return HttpResponseRedirect(reverse("organisation-user-mgmt-edit", args=[organisation_id, user.pk]))
	else:
		user.delete()

		messages.add_message(request, messages.SUCCESS, _('The user has been successfully deleted.'))
		return HttpResponseRedirect(reverse("organisation-user-mgmt", args=[organisation_id]))

@login_required
def organisation_user_mgmt_create_view(request, organisation_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))
	lecturer = False
	if request.GET.get('lecturer'):
		lecturer = get_object_or_404(Docent, Q(pk=request.GET.get('lecturer')))
		if not organisation.docents.filter(Q(pk=lecturer.pk)):
			raise Http404	

	active_page = 'user_management'

	if lecturer:
		active_page = 'lecturer_management'

	if request.POST:
		username = request.POST.get('username')
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		email = request.POST.get('email')

		error = False

		# check username
		if len(username) < 2:
			error = True
			messages.add_message(request, messages.ERROR, _('Minimum length for usernames: 2 characters'))
		if User.objects.filter(Q(username__iexact=username)):
			error = True
			messages.add_message(request, messages.ERROR, _('This username has already been taken!'))
		
		# check first_name
		if len(first_name) < 1:
			error = True
			messages.add_message(request, messages.ERROR, _('First name is a required field.'))

		# check last_name
		if len(last_name) < 1:
			error = True
			messages.add_message(request, messages.ERROR, _('Last name is a required field.'))
		
		# check email
		if not is_valid_email(email):
			error = True
			messages.add_message(request, messages.ERROR, _('The email address has an invalid format.'))
		if User.objects.filter(Q(email__iexact=email)):
			error = True
			messages.add_message(request, messages.ERROR, _('This email adress has already been taken!'))

		if not error:
			user = User(username=username, first_name=first_name, last_name=last_name, email=email)
			user.save()
			organisation.users.add(user)
			messages.add_message(request, messages.SUCCESS, _('The user has been successfully created.'))
			
			if lecturer:
				user.get_profile().is_lecturer = True
				user.get_profile().lecturer_id = lecturer
				user.get_profile().save()
				return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, lecturer.pk]))
			else:
				return HttpResponseRedirect(reverse("organisation-user-mgmt-edit", args=[organisation_id, user.pk]))	

		return render_to_response("organisation/user_mgmt_create.html", locals(), context_instance=RequestContext(request))
	else:
		if lecturer:
			email = lecturer.email
		return render_to_response("organisation/user_mgmt_create.html", locals(), context_instance=RequestContext(request))

@login_required
def organisation_user_mgmt_view(request, organisation_id, user_id = False):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))

	active_page = 'user_management'
	if user_id:
		user = get_object_or_404(User, Q(pk=user_id)) #user does exist
		if not organisation.users.filter(Q(pk=user_id)): # user belongs to this organisation
			raise Http404

		scopes = Scope.objects.filter(Q(users__id=user.pk), Q(pk__in=organisation.scopes.all())).order_by('name')

		if request.POST:
			username = request.POST.get('username')
			first_name = request.POST.get('first_name')
			last_name = request.POST.get('last_name')
			email = request.POST.get('email')

			error = False

			# check username
			if len(username) < 2:
				error = True
				messages.add_message(request, messages.ERROR, _('Minimum length for usernames: 2 characters'))
			if User.objects.filter(Q(username__iexact=username)).exclude(pk=user.pk):
				error = True
				messages.add_message(request, messages.ERROR, _('This username has already been taken!'))
			
			# check first_name
			if len(first_name) < 1:
				error = True
				messages.add_message(request, messages.ERROR, _('First name is a required field.'))

			# check last_name
			if len(last_name) < 1:
				error = True
				messages.add_message(request, messages.ERROR, _('Last name is a required field.'))
			
			# check email
			if not is_valid_email(email):
				error = True
				messages.add_message(request, messages.ERROR, _('The email address has an invalid format.'))
			if User.objects.filter(Q(email__iexact=email)).exclude(pk=user.pk):
				error = True
				messages.add_message(request, messages.ERROR, _('This email adress has already been taken!'))

			if not error:
				user.username = username
				user.first_name = first_name
				user.last_name = last_name
				user.email = email
				user.save()
				messages.add_message(request, messages.SUCCESS, _('The user has been successfully amended.'))

			if request.GET.get('lecturer'):
				return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, user.get_profile().lecturer_id.pk]))

		return render_to_response("organisation/user_mgmt_edit.html", locals(), context_instance=RequestContext(request))
	else:
		users = organisation.users.filter(Q(userprofile__is_lecturer=False))
		json_cache = serializers.serialize('json', users, fields=('id', 'pk', 'username', 'first_name', 'last_name', 'email', 'is_active', 'last_login'))
		return render_to_response("organisation/user_mgmt.html", locals(), context_instance=RequestContext(request))

@login_required
def organisation_user_deletescope_view(request, organisation_id, user_id, scope_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))	
	user = get_object_or_404(User, Q(pk=user_id), Q(pk__in=organisation.users.all())) #user does exist

	try:
		scope = Scope.objects.get(pk=scope_id, pk__in=organisation.scopes.all())
	except:
		messages.add_message(request, messages.ERROR, _('This scope does not exist!'))
		if request.GET.get('lecturer'):
			return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, user.get_profile().lecturer_id.pk]))
		else:
			return HttpResponseRedirect(reverse("organisation-user-mgmt-edit", args=[organisation_id, user_id]))	

	if organisation.scopes.filter(Q(users__id=user.pk), Q(pk=scope.pk)):
		scope.users.remove(user)
		messages.add_message(request, messages.SUCCESS, _('The user has been disconnected from this scope.'))
		if request.GET.get('lecturer'):
			return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, user.get_profile().lecturer_id.pk]))
		else:
			return HttpResponseRedirect(reverse("organisation-user-mgmt-edit", args=[organisation_id, user_id]))
	else:
		messages.add_message(request, messages.INFO, _('The user is not connected to this scope.'))
		if request.GET.get('lecturer'):
			return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, user.get_profile().lecturer_id.pk]))
		else:
			return HttpResponseRedirect(reverse("organisation-user-mgmt-edit", args=[organisation_id, user_id]))

@login_required
def organisation_user_addscope_view(request, organisation_id, user_id):
	scope_name = request.POST.get('scope')

	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))	
	user = get_object_or_404(User, Q(pk=user_id), Q(pk__in=organisation.users.all())) #user does exist

	try:
		scope = Scope.objects.get(name=scope_name, pk__in=organisation.scopes.all())
	except:
		messages.add_message(request, messages.ERROR, _('This scope does not exist!'))
		if request.GET.get('lecturer'):
			return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, user.get_profile().lecturer_id.pk]))
		else:
			return HttpResponseRedirect(reverse("organisation-user-mgmt-edit", args=[organisation_id, user_id]))	

	if organisation.scopes.filter(Q(users__id=user.pk), Q(pk=scope.pk)):
		messages.add_message(request, messages.INFO, _('The user is already connected to this scope.'))
		if request.GET.get('lecturer'):
			return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, user.get_profile().lecturer_id.pk]))
		else:		
			return HttpResponseRedirect(reverse("organisation-user-mgmt-edit", args=[organisation_id, user_id]))
	else:
		scope.users.add(user)
		messages.add_message(request, messages.SUCCESS, _('The user has been connected to this scope.'))
		if request.GET.get('lecturer'):
			return HttpResponseRedirect(reverse("organisation-lecturer-mgmt-edit", args=[organisation_id, user.get_profile().lecturer_id.pk]))
		else:
			return HttpResponseRedirect(reverse("organisation-user-mgmt-edit", args=[organisation_id, user_id]))

@login_required
def organisation_scope_mgmt_adduser_view(request, organisation_id, scope_id):
	user_name = request.POST.get('user')

	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))	
	scope = get_object_or_404(Scope, Q(pk=scope_id), Q(pk__in=organisation.scopes.all())) #user does exist

	try:
		user = User.objects.get(username=user_name, pk__in=organisation.users.all())
	except:
		messages.add_message(request, messages.ERROR, _('This user does not exist!'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope_id]))

	if scope.users.filter(Q(pk=user.pk)):
		messages.add_message(request, messages.INFO, _('The user is already connected to this scope.'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope_id]))
	else:
		scope.users.add(user)
		messages.add_message(request, messages.SUCCESS, _('The user has been connected to this scope.'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope_id]))

@login_required
def organisation_scope_mgmt_deleteuser_view(request, organisation_id, scope_id, user_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))	
	user = get_object_or_404(User, Q(pk=user_id), Q(pk__in=organisation.users.all())) #user does exist
	scope = get_object_or_404(Scope, Q(pk=scope_id), Q(pk__in=organisation.scopes.all()))

	if organisation.scopes.filter(Q(users__id=user.pk), Q(pk=scope.pk)):
		scope.users.remove(user)
		messages.add_message(request, messages.SUCCESS, _('The user has been disconnected from this scope.'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope_id]))
	else:
		messages.add_message(request, messages.INFO, _('The user is not connected to this scope.'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope_id]))

@login_required
def organisation_scope_mgmt_addcourse_view(request, organisation_id, scope_id):
	course_name = request.POST.get('course')

	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))	
	scope = get_object_or_404(Scope, Q(pk=scope_id), Q(pk__in=organisation.scopes.all())) #user does exist

	try:
		course = Course.objects.get(name=course_name, pk__in=organisation.courses.all())
	except:
		messages.add_message(request, messages.ERROR, _('This course does not exist!'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope_id]))

	if course.scopes.filter(Q(pk=scope.pk)):
		messages.add_message(request, messages.INFO, _('The course is already connected to this scope.'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope_id]))
	else:
		course.scopes.add(scope)
		messages.add_message(request, messages.SUCCESS, _('The course has been connected to this scope.'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope_id]))

@login_required
def organisation_scope_mgmt_deletecourse_view(request, organisation_id, scope_id, course_id):
	organisation = get_object_or_404(Organisation, Q(pk=organisation_id), Q(managers__id=request.user.pk))	
	course = get_object_or_404(Course, Q(pk=course_id), Q(pk__in=organisation.courses.all())) #user does exist
	scope = get_object_or_404(Scope, Q(pk=scope_id), Q(pk__in=organisation.scopes.all()))

	if course.scopes.filter(pk=scope.pk):
		course.scopes.remove(scope)
		messages.add_message(request, messages.SUCCESS, _('The course has been disconnected from this scope.'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope_id]))
	else:
		messages.add_message(request, messages.INFO, _('The course is not connected to this scope.'))
		return HttpResponseRedirect(reverse("organisation-scope-mgmt-edit", args=[organisation_id, scope_id]))	