from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Institution, Director
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'domain', 'email', 'is_active')
    search_fields = ('name', 'code', 'domain', 'email')
    list_filter = ('is_active',)
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'domain')
        }),
        ('Información de contacto', {
            'fields': ('email', 'phone', 'address', 'website')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'institution', 'dni', 'phone', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'dni')
    list_filter = ('is_active', 'institution')
    ordering = ('user__first_name',)
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Nombre completo'

    fieldsets = (
        (None, {
            'fields': ('user', 'institution')
        }),
        ('Información personal', {
            'fields': ('dni', 'phone')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si es una nueva creación
            # Asegurarse que el usuario tenga los permisos necesarios
            obj.user.is_staff = True
            obj.user.save()
        super().save_model(request, obj, form, change)
