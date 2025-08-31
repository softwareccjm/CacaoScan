"""
Modelos de usuario para CacaoScan.

Incluye modelo User extendido con roles y perfil de usuario
para gestión de agricultores y administradores.
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Modelo de usuario extendido para CacaoScan.
    
    Extiende el modelo User de Django para incluir roles específicos
    (agricultor/administrador) y campos adicionales necesarios para el sistema.
    """
    
    # Opciones de roles
    ROLE_CHOICES = [
        ('farmer', 'Agricultor'),
        ('admin', 'Administrador'),
        ('analyst', 'Analista'),
    ]
    
    # Campos básicos adicionales
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del usuario"
    )
    
    # Email como campo único y requerido
    email = models.EmailField(
        unique=True,
        verbose_name="Correo electrónico",
        help_text="Dirección de correo electrónico (será el username)"
    )
    
    # Rol del usuario
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='farmer',
        verbose_name="Rol",
        help_text="Rol del usuario en el sistema"
    )
    
    # Información personal adicional
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Número de teléfono debe tener formato: '+999999999'. Hasta 15 dígitos."
            )
        ],
        verbose_name="Teléfono",
        help_text="Número de teléfono de contacto"
    )
    
    # Estado del usuario
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Email verificado",
        help_text="Indica si el email del usuario ha sido verificado"
    )
    
    # Configuración de autenticación
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        db_table = 'auth_user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active', 'role']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username
    
    def get_short_name(self):
        """Retorna el nombre corto del usuario."""
        return self.first_name or self.username
    
    @property
    def is_farmer(self):
        """Verifica si el usuario es agricultor."""
        return self.role == 'farmer'
    
    @property
    def is_admin_user(self):
        """Verifica si el usuario es administrador."""
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_analyst(self):
        """Verifica si el usuario es analista."""
        return self.role == 'analyst'
    
    def can_manage_all_images(self):
        """Verifica si el usuario puede gestionar todas las imágenes."""
        return self.is_admin_user or self.is_analyst
    
    def get_role_display_verbose(self):
        """Retorna descripción detallada del rol."""
        role_descriptions = {
            'farmer': 'Agricultor - Puede subir imágenes y ver predicciones',
            'admin': 'Administrador - Acceso completo al sistema',
            'analyst': 'Analista - Puede ver y analizar todos los datos',
        }
        return role_descriptions.get(self.role, self.get_role_display())


class UserProfile(models.Model):
    """
    Perfil extendido de usuario para información adicional.
    
    Contiene información específica del contexto agrícola y de ubicación
    que no está en el modelo User base.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Usuario"
    )
    
    # Información de ubicación
    region = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Región",
        help_text="Región geográfica del usuario"
    )
    
    municipality = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Municipio",
        help_text="Municipio donde se encuentra el usuario"
    )
    
    farm_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre de la finca",
        help_text="Nombre de la finca (solo para agricultores)"
    )
    
    # Información agrícola
    years_experience = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Años de experiencia",
        help_text="Años de experiencia en cultivo de cacao"
    )
    
    farm_size_hectares = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Tamaño de finca (hectáreas)",
        help_text="Tamaño de la finca en hectáreas"
    )
    
    # Configuraciones del usuario
    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('es', 'Español'),
            ('en', 'English'),
        ],
        default='es',
        verbose_name="Idioma preferido"
    )
    
    # Notificaciones
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Notificaciones por email",
        help_text="Recibir notificaciones por correo electrónico"
    )
    
    # Fechas
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        indexes = [
            models.Index(fields=['region']),
            models.Index(fields=['municipality']),
        ]
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"
    
    @property
    def location_display(self):
        """Retorna la ubicación en formato legible."""
        location_parts = []
        if self.municipality:
            location_parts.append(self.municipality)
        if self.region:
            location_parts.append(self.region)
        return ", ".join(location_parts) if location_parts else "No especificada"
    
    def get_experience_level(self):
        """Retorna el nivel de experiencia categorizado."""
        if not self.years_experience:
            return "No especificado"
        
        if self.years_experience < 2:
            return "Principiante"
        elif self.years_experience < 5:
            return "Intermedio"
        elif self.years_experience < 10:
            return "Avanzado"
        else:
            return "Experto"


# Signal para crear perfil automáticamente
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea automáticamente un perfil cuando se crea un usuario."""
    if created:
        UserProfile.objects.create(user=instance)
