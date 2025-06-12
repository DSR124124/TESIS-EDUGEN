from django.contrib import admin
from .models import ContentType, ContentRequest, GeneratedContent

@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(ContentRequest)
class ContentRequestAdmin(admin.ModelAdmin):
    list_display = ('topic', 'course', 'content_type', 'teacher', 'status', 'created_at')
    list_filter = ('status', 'content_type', 'created_at')
    search_fields = ('topic', 'teacher__username', 'teacher__first_name', 'teacher__last_name')
    date_hierarchy = 'created_at'

@admin.register(GeneratedContent)
class GeneratedContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_request_topic', 'get_content_type', 'tokens_used', 'created_at')
    list_filter = ('request__status', 'request__content_type', 'created_at')
    search_fields = ('title', 'request__topic', 'request__teacher__username')
    date_hierarchy = 'created_at'
    
    def get_request_topic(self, obj):
        return obj.request.topic
    get_request_topic.short_description = 'Tema'
    get_request_topic.admin_order_field = 'request__topic'
    
    def get_content_type(self, obj):
        return obj.request.content_type.name
    get_content_type.short_description = 'Tipo de Contenido'
    get_content_type.admin_order_field = 'request__content_type__name' 