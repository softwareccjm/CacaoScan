"""
Modelos para gestión de personas - App personas.
Modelos normalizados según Tercera Forma Normal (3FN).

INTEGRACIÓN CON MÓDULOS:
- Catálogos (Tema-Parámetro): Para tipo_documento y genero
- Ubicaciones: Para departamento y municipio
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
from catalogos.models import Parametro, Departamento, Municipio


class Persona(models.Model):
    """
    Modelo para información personal complementaria del usuario.
    
    INTEGRACIÓN CON CATÁLOGOS:
    - tipo_documento: Se relaciona con Parametro donde tema__codigo='TIPO_DOC'
    - genero: Se relaciona con Parametro donde tema__codigo='SEXO'
    
    INTEGRACIÓN CON UBICACIONES:
    - departamento: Se relaciona con Departamento (relación 1:N)
    - municipio: Se relaciona con Municipio (relación 1:N)
    
    NORMALIZACIÓN 3FN: Mantiene integridad referencial con catálogos y ubicaciones normalizadas.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="persona",
        help_text="Usuario asociado a la persona"
    )
    
    # CATÁLOGO: Tipo de documento (Parametro del tema TIPO_DOC)
    tipo_documento = models.ForeignKey(
        Parametro, 
        on_delete=models.PROTECT,
        limit_choices_to={'tema__codigo': 'TIPO_DOC'},
        related_name="personas_tipo_doc",
        help_text="Parámetro del catálogo TIPO_DOC (ej: CC, CE, PA, TI, RC)"
    )
    
    numero_documento = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Número de documento de identidad"
    )
    
    # Información personal
    primer_nombre = models.CharField(max_length=50, help_text="Primer nombre")
    segundo_nombre = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        help_text="Segundo nombre (opcional)"
    )
    primer_apellido = models.CharField(max_length=50, help_text="Primer apellido")
    segundo_apellido = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        help_text="Segundo apellido (opcional)"
    )
    
    # Contacto
    telefono = models.CharField(max_length=15, help_text="Número de teléfono")
    direccion = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Dirección de residencia"
    )
    
    # CATÁLOGO: Género (Parametro del tema SEXO)
    genero = models.ForeignKey(
        Parametro, 
        on_delete=models.PROTECT,
        limit_choices_to={'tema__codigo': 'SEXO'},
        related_name="personas_genero",
        help_text="Parámetro del catálogo SEXO (ej: M, F, O)"
    )
    
    # Ubicación geográfica (normalizada)
    fecha_nacimiento = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha de nacimiento"
    )
    
    # UBICACIÓN: Departamento y Municipio normalizados
    departamento = models.ForeignKey(
        Departamento, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personas",
        help_text="Departamento de residencia"
    )
    municipio = models.ForeignKey(
        Municipio, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personas",
        help_text="Municipio de residencia"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del registro")
    
    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ['primer_apellido', 'primer_nombre']
        indexes = [
            models.Index(fields=['numero_documento']),
            models.Index(fields=['user']),
        ]
    
    def clean(self):
        """Validaciones personalizadas a nivel de modelo."""
        errors = {}
        
        # Validar número de documento
        if self.numero_documento:
            # Solo números
            if not self.numero_documento.isdigit():
                errors['numero_documento'] = 'El número de documento solo puede contener números.'
            # Longitud entre 6 y 11 dígitos
            elif len(self.numero_documento) < 6 or len(self.numero_documento) > 11:
                errors['numero_documento'] = 'El número de documento debe tener entre 6 y 11 dígitos.'
        
        # Validar teléfono
        if self.telefono:
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', self.telefono)
            if cleaned_phone.startswith('+'):
                cleaned_phone = cleaned_phone[1:]
            if not cleaned_phone.isdigit():
                errors['telefono'] = 'El teléfono solo puede contener números.'
            elif len(cleaned_phone) < 7 or len(cleaned_phone) > 15:
                errors['telefono'] = 'El teléfono debe tener entre 7 y 15 dígitos.'
        
        # Validar fecha de nacimiento
        if self.fecha_nacimiento:
            hoy = timezone.now().date()
            if self.fecha_nacimiento > hoy:
                errors['fecha_nacimiento'] = 'La fecha de nacimiento no puede ser futura.'
            else:
                edad = hoy.year - self.fecha_nacimiento.year - \
                       ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
                if edad < 14:
                    errors['fecha_nacimiento'] = 'La persona debe tener al menos 14 años.'
                if edad > 120:
                    errors['fecha_nacimiento'] = 'La fecha de nacimiento no es válida.'
        
        # Validar nombres (solo letras y espacios)
        if self.primer_nombre:
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', self.primer_nombre):
                errors['primer_nombre'] = 'El primer nombre solo puede contener letras.'
        
        if self.primer_apellido:
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', self.primer_apellido):
                errors['primer_apellido'] = 'El primer apellido solo puede contener letras.'
        
        # Validar que el municipio pertenezca al departamento
        if self.municipio and self.departamento:
            if self.municipio.departamento != self.departamento:
                errors['municipio'] = 'El municipio no pertenece al departamento seleccionado.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para ejecutar validaciones."""
        self.full_clean()  # Ejecuta clean() y otras validaciones
        super().save(*args, **kwargs)
    
    def __str__(self):
        nombre_completo = f"{self.primer_nombre}"
        if self.segundo_nombre:
            nombre_completo += f" {self.segundo_nombre}"
        nombre_completo += f" {self.primer_apellido}"
        if self.segundo_apellido:
            nombre_completo += f" {self.segundo_apellido}"
        return nombre_completo
    
    @property
    def nombre_completo(self):
        """Devuelve el nombre completo de la persona."""
        return str(self)
    
    @property
    def edad(self):
        """Calcula la edad actual de la persona."""
        if not self.fecha_nacimiento:
            return None
        hoy = timezone.now().date()
        return hoy.year - self.fecha_nacimiento.year - \
               ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
