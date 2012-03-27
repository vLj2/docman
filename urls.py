from django.conf.urls.defaults import *
from django.contrib import auth
from django.conf import settings
from django_facebook import views as facebook_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': False }),
	)

# DocMan Organisation Mgmt
urlpatterns +=patterns('docman.organisation_mgmt.views',
	url(r'^_/', include('docman.organisation_mgmt.urls'))
)

# DocMan app
urlpatterns += patterns('docman.app.views',
	# login logout
	url(r'^login/$', 'login_view', name='login'),
	url(r'^logout/$', 'logout_view', name='logout'),	

	# basic views
	url(r'^$', 'default_view', name='default'),	
	url(r'^course/(?P<course_id>(\w+))/$', 'course_view', name='course'),	
	url(r'^account/$', 'account_view', name="account"),	
	url(r'^document/(?P<document_id>(\w+))/', 'document_view', name='document'),
	url(r'^about/$', 'about_view', name="about"),
	url(r'^press/$', 'press_view', name="press"),
	url(r'^get/$', 'get_view', name='get'),
	url(r'^get/(?P<success>(\w+))/$', 'get_view', name='get-param'),
	
	# survey
	url(r'^survey/', 'save_survey_view', name='survey-save'),

	# subscriptions
	url(r'^subscribe/(?P<document_id>(\w+))/', 'subscribe_document_view', name='subscribe'),
	url(r'^unsubscribe/(?P<document_id>(\w+))/', 'unsubscribe_document_view', name='unsubscribe'),
	url(r'^subscribe-course/(?P<course_id>(\w+))/', 'subscribe_course_view', name='subscribe-course'),	
	url(r'^unsubscribe-course/(?P<course_id>(\w+))/', 'unsubscribe_course_view', name='unsubscribe-course'),
	
	# modifiers
	url(r'^account-ajax/$', 'account_ajax_view', name="account-ajax"),	
	url(r'^semester/(?P<semester_id>(\w+))/', 'semester_view', name='semester'),	
	url(r'^delete/(?P<document_id>(\w+))/', 'document_delete_view', name='delete-doc'),	
	url(r'^delete-revision/(?P<revision_id>(\w+))/', 'revision_delete_view', name='delete-rev'),	
	url(r'^file-info/$', 'file_info_view'),	

	# download
	url(r'^download/(?P<document_id>(\w+))/', 'download_view', name='download'),	
	url(r'^download-course/(?P<course_id>(\w+))/', 'download_course_view', name='download-all'),	
	
	# search
	(r'^search/', include('haystack.urls')),
	
	# profiles
	url(r'^docent/(?P<docent_id>(\w+))/', 'docent_view', name='docent'),		
	url(r'^user/(?P<user_id>(\w+))/$', 'user_view', name='user-profile'),		
	
	# comments
	url(r'^save-comment/(?P<document_id>(\w+))/', 'save_comment_view', name='comment-save'),		
	url(r'^delete-comment/(?P<comment_id>(\w+))/', 'delete_comment_view', name='comment-delete'),		
	
	# rate
	url(r'^rate/(?P<document_id>(\w+))/', 'rate_document_view', name='rate-document'),
	
	# upload
	url(r'^test-upload/', 'test_upload_view'),
	url(r'^ie-upload/', 'ie_upload_view', name="ie-upload"),

	# i18n
	(r'^i18n/', include('django.conf.urls.i18n')),
	
	# tags 
	url(r'^tags/(?P<tag_name>([a-z0-9- ]+))/', 'tag_view', name='tags'),	
	url(r'^cloud/', 'tag_cloud_view', name='tags-cloud'),		

	# scope info
	url(r'^scope-info/(?P<scope_id>(\w+))/', 'scope_info_view', name='scope-info'),

	# error-no-organisation
	url(r'^error-no-organisation/$', 'error_no_organisation_view', name='error-no-organisation'),
	
	# facebook 
	url(r'^facebook/connect/$', facebook_views.connect, name='facebook_connect'),
	url(r'^facebook/deconnect/$', 'facebook_deconnect_view', name='facebook-deconnect'),
)

urlpatterns += patterns('django.contrib.auth.views',
	url(r'^password_reset/$', 'password_reset', {'template_name':'registration/password_reset.html'}, name='password_reset'),
	(r'^password_reset/done/$', 'password_reset_done'),
	url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', name='password_reset_confirm'),
	(r'^reset/done/$', 'password_reset_complete'),
)
