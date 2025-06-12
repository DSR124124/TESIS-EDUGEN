from django.contrib import admin
from .models import SCORMPackage

@admin.register(SCORMPackage)
class SCORMPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_content_title', 'standard', 'version', 'is_published', 'created_at')
    list_filter = ('standard', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'generated_content__title')
    date_hierarchy = 'created_at'
    readonly_fields = ('package_file', 'manifest_file')
    
    def get_content_title(self, obj):
        return obj.generated_content.title
    get_content_title.short_description = 'Contenido origen'
    get_content_title.admin_order_field = 'generated_content__title' 