from django.contrib import admin
from app.models import *

class DocentAdmin(admin.ModelAdmin):
	pass
	
class CategoryAdmin(admin.ModelAdmin):
	pass
	
class CourseAdmin(admin.ModelAdmin):
	prepopulated_fields = {"shell_name": ("name",)}

	
class DocumentAdmin(admin.ModelAdmin):
	pass
	
class DocumentRevisionAdmin(admin.ModelAdmin):
	pass

admin.site.register(Docent, DocentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentRevision, DocumentRevisionAdmin)
