from django.conf.urls.defaults import *
from django.contrib import auth
from django.conf import settings
from django_facebook import views as facebook_views

# DocMan organisation mgmt
urlpatterns = patterns('docman.organisation_mgmt.views',
	url(r'^organisation/$', 'default_view', name="organisation-default"),
	url(r'^organisation/(?P<organisation_id>(\w+))/$', 'organisation_view', name="organisation-organisation"),

	url(r'^organisation/(?P<organisation_id>(\w+))/user_mgmt/filter/$', 'organisation_user_mgmt_filter', name="organisation-user-mgmt-filter"),
	url(r'^organisation/(?P<organisation_id>(\w+))/user_mgmt/(?P<user_id>(\w+))/newpassword/$', 'organisation_user_mgmt_newpassword_view', name="organisation-user-mgmt-newpassword"),
	url(r'^organisation/(?P<organisation_id>(\w+))/user_mgmt/create/$', 'organisation_user_mgmt_create_view', name="organisation-user-mgmt-create"),
	url(r'^organisation/(?P<organisation_id>(\w+))/user_mgmt/(?P<user_id>(\w+))/delete/$', 'organisation_user_mgmt_delete_view', name="organisation-user-mgmt-delete"),
	url(r'^organisation/(?P<organisation_id>(\w+))/user_mgmt/(?P<user_id>(\w+))/disable/$', 'organisation_user_mgmt_disable_view', name="organisation-user-mgmt-disable"),
	url(r'^organisation/(?P<organisation_id>(\w+))/user_mgmt/(?P<user_id>(\w+))/enable/$', 'organisation_user_mgmt_enable_view', name="organisation-user-mgmt-enable"),	
	url(r'^organisation/(?P<organisation_id>(\w+))/user_mgmt/$', 'organisation_user_mgmt_view', name="organisation-user-mgmt"),
	url(r'^organisation/(?P<organisation_id>(\w+))/user_mgmt/(?P<user_id>(\w+))/$', 'organisation_user_mgmt_view', name="organisation-user-mgmt-edit"),
	url(r'^organisation/(?P<organisation_id>(\w+))/user_mgmt/addscope/(?P<user_id>(\w+))/$', 'organisation_user_addscope_view', name="organisation-user-mgmt-addscope"),
	url(r'^organisation/(?P<organisation_id>(\w+))/user_mgmt/deletescope/(?P<user_id>(\w+))/(?P<scope_id>(\w+))/$', 'organisation_user_deletescope_view', name="organisation-user-mgmt-deletescope"),

	url(r'^organisation/(?P<organisation_id>(\w+))/lecturer_mgmt/filter/$', 'organisation_lecturer_mgmt_filter', name="organisation-lecturer-mgmt-filter"),
	url(r'^organisation/(?P<organisation_id>(\w+))/lecturer_mgmt/create/$', 'organisation_lecturer_mgmt_create_view', name="organisation-lecturer-mgmt-create"),
	url(r'^organisation/(?P<organisation_id>(\w+))/lecturer_mgmt/$', 'organisation_lecturer_mgmt_view', name="organisation-lecturer-mgmt"),
	url(r'^organisation/(?P<organisation_id>(\w+))/lecturer_mgmt/(?P<lecturer_id>(\w+))/$', 'organisation_lecturer_mgmt_view', name="organisation-lecturer-mgmt-edit"),
	url(r'^organisation/(?P<organisation_id>(\w+))/lecturer_mgmt/(?P<lecturer_id>(\w+))/delete/$', 'organisation_lecturer_mgmt_delete_view', name="organisation-lecturer-mgmt-delete"),

	url(r'^organisation/(?P<organisation_id>(\w+))/course_mgmt/filter/$', 'organisation_course_mgmt_filter', name="organisation-course-mgmt-filter"),
	url(r'^organisation/(?P<organisation_id>(\w+))/course_mgmt/create$', 'organisation_course_mgmt_create_view', name="organisation-course-mgmt-create"),
	url(r'^organisation/(?P<organisation_id>(\w+))/course_mgmt/$', 'organisation_course_mgmt_view', name="organisation-course-mgmt"),
	url(r'^organisation/(?P<organisation_id>(\w+))/course_mgmt/(?P<course_id>(\w+))/edit/$', 'organisation_course_mgmt_view', name="organisation-course-mgmt-edit"),
	url(r'^organisation/(?P<organisation_id>(\w+))/course_mgmt/(?P<course_id>(\w+))/delete$', 'organisation_course_mgmt_delete_view', name="organisation-course-mgmt-delete"),
	url(r'^organisation/(?P<organisation_id>(\w+))/course_mgmt/addscope/(?P<course_id>(\w+))/$', 'organisation_course_mgmt_addscope_view', name="organisation-course-mgmt-addscope"),
	url(r'^organisation/(?P<organisation_id>(\w+))/course_mgmt/deletescope/(?P<course_id>(\w+))/(?P<scope_id>(\w+))/$', 'organisation_course_mgmt_deletescope_view', name="organisation-course-mgmt-deletescope"),

	url(r'^organisation/(?P<organisation_id>(\w+))/scope_mgmt/filter/$', 'organisation_scope_mgmt_filter', name="organisation-scope-mgmt-filter"),
	url(r'^organisation/(?P<organisation_id>(\w+))/scope_mgmt/(?P<scope_id>(\w+))/delete/$', 'organisation_scope_mgmt_delete_view', name="organisation-scope-mgmt-delete"),
	url(r'^organisation/(?P<organisation_id>(\w+))/scope_mgmt/create$', 'organisation_scope_mgmt_create_view', name="organisation-scope-mgmt-create"),
	url(r'^organisation/(?P<organisation_id>(\w+))/scope_mgmt/$', 'organisation_scope_mgmt_view', name="organisation-scope-mgmt"),
	url(r'^organisation/(?P<organisation_id>(\w+))/scope_mgmt/(?P<scope_id>(\w+))/$', 'organisation_scope_mgmt_view', name="organisation-scope-mgmt-edit"),
	url(r'^organisation/(?P<organisation_id>(\w+))/scope_mgmt/(?P<scope_id>(\w+))/adduser/$', 'organisation_scope_mgmt_adduser_view', name="organisation-scope-mgmt-adduser"),
	url(r'^organisation/(?P<organisation_id>(\w+))/scope_mgmt/(?P<scope_id>(\w+))/deleteuser/(?P<user_id>(\w+))/$', 'organisation_scope_mgmt_deleteuser_view', name="organisation-scope-mgmt-deleteuser"),
	url(r'^organisation/(?P<organisation_id>(\w+))/scope_mgmt/(?P<scope_id>(\w+))/addcourse/$', 'organisation_scope_mgmt_addcourse_view', name="organisation-scope-mgmt-addcourse"),
url(r'^organisation/(?P<organisation_id>(\w+))/scope_mgmt/(?P<scope_id>(\w+))/deletecourse/(?P<course_id>(\w+))/$', 'organisation_scope_mgmt_deletecourse_view', name="organisation-scope-mgmt-deletecourse"),	

	url(r'^organisation/(?P<organisation_id>(\w+))/autocomplete/(?P<user_id>(\w+))/$', 'organisation_autocomplete_view', name="organisation-autocomplete"),
	url(r'^organisation/(?P<organisation_id>(\w+))/autocomplete/scope/(?P<scope_id>(\w+))/user/$', 'organisation_autocomplete_scope_user_view', name="organisation-autocomplete-scope-user"),
	url(r'^organisation/(?P<organisation_id>(\w+))/autocomplete/scope/(?P<scope_id>(\w+))/course/$', 'organisation_autocomplete_scope_course_view', name="organisation-autocomplete-scope-course"),
	url(r'^organisation/(?P<organisation_id>(\w+))/autocomplete/course/(?P<course_id>(\w+))/scope/$', 'organisation_autocomplete_course_scope_view', name="organisation-autocomplete-course-scope"),
)