"""
Configuración del admin de Django para gestión de usuarios.

Proporciona interfaces administrativas para User y UserProfile
con funcionalidades avanzadas de filtrado y edición.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline para editar perfil junto con usuario."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    
    fieldsets = (
        ('Información de Ubicación', {
            'fields': ('region', 'municipality', 'farm_name')
        }),
        ('Información Agrícola', {
            'fields': ('years_experience', 'farm_size_hectares')
        }),
        ('Configuraciones', {
            'fields': ('preferred_language', 'email_notifications')
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personalizado para modelo User extendido."""
    
    inlines = (UserProfileInline,)
    
    # Campos mostrados en la lista
    list_display = (
        'email',
        'username', 
        'get_full_name',
        'role',
        'is_verified',
        'is_active',
        'date_joined',
        'get_location'
    )
    
    # Campos para búsqueda
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    # Filtros laterales
    list_filter = (
        'role',
        'is_verified',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
        'profile__region',
    )
    
    # Campos editables en la lista
    list_editable = ('is_verified', 'is_active')
    
    # Ordenamiento por defecto
    ordering = ('-date_joined',)
    
    # Configuración de fieldsets para el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('username', 'email', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        ('Permisos y Rol', {
            'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
        ('Grupos y Permisos', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
    )
    
    # Configuración para crear usuario
    add_fieldsets = (
        ('Información Requerida', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        ('Configuración Inicial', {
            'fields': ('role', 'is_active')
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('date_joined', 'last_login')
    
    def get_full_name(self, obj):
        """Muestra nombre completo."""
        return obj.get_full_name()
    get_full_name.short_description = 'Nombre Completo'
    
    def get_location(self, obj):
        """Muestra ubicación del perfil."""
        try:
            return obj.profile.location_display
        except UserProfile.DoesNotExist:
            return 'Sin perfil'
    get_location.short_description = 'Ubicación'
    
    def get_queryset(self, request):
        """Optimiza queries con select_related."""
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para gestión de perfiles de usuario."""
    
    list_display = (
        'get_user_name',
        'get_user_email',
        'region',
        'municipality',
        'farm_name',
        'get_experience_level',
        'farm_size_hectares',
        'created_at'
    )
    
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
        'farm_name',
        'region',
        'municipality'
    )
    
    list_filter = (
        'region',
        'municipality',
        'preferred_language',
        'email_notifications',
        'created_at',
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Ubicación', {
            'fields': ('region', 'municipality', 'farm_name')
        }),
        ('Información Agrícola', {
            'fields': ('years_experience', 'farm_size_hectares')
        }),
        ('Configuraciones', {
            'fields': ('preferred_language', 'email_notifications')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_name(self, obj):
        """Muestra nombre del usuario."""
        return obj.user.get_full_name()
    get_user_name.short_description = 'Usuario'
    
    def get_user_email(self, obj):
        """Muestra email del usuario."""
        return obj.user.email
    get_user_email.short_description = 'Email'
    
    def get_queryset(self, request):
        """Optimiza queries con select_related."""
        return super().get_queryset(request).select_related('user')


# Configuración adicional del admin
admin.site.site_header = 'CacaoScan Administración'
admin.site.site_title = 'CacaoScan Admin'
admin.site.index_title = 'Panel de Administración'
