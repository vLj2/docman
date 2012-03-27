from django.http import Http404, HttpResponse, HttpResponseRedirect
from functools import wraps
from app.models import Organisation
from django.core.urlresolvers import reverse

def is_no_lecturer(func):
	def _checklogin(request, *args, **kwargs):
		if request.user.get_profile().is_lecturer:
			raise Http404
		else:
			return func(request, *args, **kwargs)

	return wraps(func)(_checklogin)

def is_lecturer(func):
	def _checklogin(request, *args, **kwargs):
		if not request.user.get_profile().is_lecturer:
			raise Http404
		else:
			return func(request, *args, **kwargs)

	return wraps(func)(_checklogin)

def has_organisation(func):
	def _checklogin(request, *args, **kwargs):
		if not Organisation.objects.filter(users__pk=request.user.pk):
			return HttpResponseRedirect(reverse("error-no-organisation"))
		else:
			return func(request, *args, **kwargs)

	return wraps(func)(_checklogin)