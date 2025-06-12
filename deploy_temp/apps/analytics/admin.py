from django.contrib import admin
from .models import UsageMetric, StudentProgress, ContentMetric, ContentInteractionMetric

@admin.register(UsageMetric)
class UsageMetricAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'resource']
    date_hierarchy = 'timestamp'

@admin.register(ContentMetric)
class ContentMetricAdmin(admin.ModelAdmin):
    list_display = ['content', 'tokens_used', 'prompt_tokens', 'completion_tokens', 'generation_time', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['content__title']
    date_hierarchy = 'timestamp'

@admin.register(ContentInteractionMetric)
class ContentInteractionMetricAdmin(admin.ModelAdmin):
    list_display = ['content_object', 'views', 'downloads', 'average_rating', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['content_type', 'object_id', 'content_object', 'views', 'downloads', 'rating_sum', 'rating_count', 'created_at', 'updated_at']

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'content', 'score', 'completed', 'completion_date', 'updated_at']
    list_filter = ['completed', 'course', 'completion_date']
    search_fields = ['student__user__username', 'student__user__first_name', 'student__user__last_name', 'course__name']
    date_hierarchy = 'updated_at'
    readonly_fields = ['created_at', 'updated_at'] 