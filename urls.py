from django.conf.urls.defaults import *
from django.contrib import auth
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': False }),    
    (r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('docman.app.views',
	url(r'^$', 'default_view', name='default'),
	url(r'^login/$', 'login_view', name='login'),
	url(r'^logout/$', 'logout_view', name='logout'),	
	url(r'^course/(?P<course_id>(\w+))/$', 'course_view', name='course'),
	url(r'^user/(?P<user_id>(\w+))/$', 'user_view'),	
	url(r'^upload/$', 'upload_view'),
	url(r'^file-info/$', 'file_info_view'),
	url(r'^account/$', 'account_view', name="account"),
	url(r'^about/$', 'about_view', name="about"),
	url(r'^upload-test/$', 'upload_test_view'),
	url(r'^document/(?P<document_id>(\w+))/', 'document_view', name='document'),
	url(r'^semester/(?P<semester_id>(\w+))/', 'semester_view', name='semester'),
	url(r'^subscribe-course/(?P<course_id>(\w+))/', 'subscribe_course_view', name='subscribe-course'),	
	url(r'^unsubscribe-course/(?P<course_id>(\w+))/', 'unsubscribe_course_view', name='unsubscribe-course'),
	url(r'^subscribe/(?P<document_id>(\w+))/', 'subscribe_document_view', name='subscribe'),
	url(r'^unsubscribe/(?P<document_id>(\w+))/', 'unsubscribe_document_view', name='unsubscribe'),
	url(r'^delete/(?P<document_id>(\w+))/', 'document_delete_view', name='delete-doc'),
	url(r'^edit/(?P<document_id>(\w+))/', 'document_edit_view', name='edit-doc'),
	url(r'^download/(?P<document_id>(\w+))/', 'download_view', name='download'),	
	url(r'^download-course/(?P<course_id>(\w+))/', 'download_course_view', name='download-all'),	
	(r'^search/', include('haystack.urls')),
	url(r'^tags/(?P<tag_name>(\w+))/', 'tag_view', name='tags'),	
	url(r'^cloud/', 'tag_cloud_view', name='tags-cloud'),	
	url(r'^docent/(?P<docent_id>(\w+))/', 'docent_view', name='docent'),		
	url(r'^save-comment/(?P<document_id>(\w+))/', 'save_comment_view', name='comment-save'),		
	url(r'^delete-comment/(?P<comment_id>(\w+))/', 'delete_comment_view', name='comment-delete'),		
	url(r'^rate/(?P<document_id>(\w+))/', 'rate_document_view', name='rate-document'),		
)

urlpatterns += patterns('django.contrib.auth.views',
	#url(r'^logout/$', 'logout', {'template_name':'login.html'}, name='logout'),	
)
