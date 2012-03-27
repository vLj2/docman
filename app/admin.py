from django.contrib import admin
from app.models import *

## introducing in django 1.4
"""
from django.contrib.admin import SimpleListFilter
class ScopeFilter(SimpleListFilter):
	title = 'Scopes'
	parameter_name = 'scope'

	def lookups(self, request, model_admin):
		return Scope.objects.all()

	def queryset(self, request, queryset):
		#return Scope.objects.
		print queryset
		#return queryset.filter()
"""

def reset_password(self, request, queryset):
	for u in queryset:
		rows_updated = u.get_profile().reset_password()
	self.message_user(request, 'A new password has been sent!')
reset_password.short_description = 'Send new password'

class UserAdmin(admin.ModelAdmin):
	list_display = ['username', 'first_name', 'last_name', 'email', 'is_active','last_login',]
	search_fields = ['username', 'first_name', 'last_name', 'email']
	list_filter = ['is_active']

	actions = [reset_password]

class UserProfileAdmin(admin.ModelAdmin):
	pass

class DocentAdmin(admin.ModelAdmin):
	pass

class ScopeAdmin(admin.ModelAdmin):
	filter_horizontal = ('users',)
	
class CategoryAdmin(admin.ModelAdmin):
	pass
	
class CourseAdmin(admin.ModelAdmin):
	prepopulated_fields = {"shell_name": ("name",)}
	filter_horizontal = ('subscribers', 'scopes',)

class NewsAdmin(admin.ModelAdmin):
	pass
	
class DocumentAdmin(admin.ModelAdmin):
	pass
	
class DocumentRevisionAdmin(admin.ModelAdmin):
	pass

class OrganisationAdmin(admin.ModelAdmin):
	pass	

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Docent, DocentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentRevision, DocumentRevisionAdmin)
admin.site.register(Scope, ScopeAdmin)
