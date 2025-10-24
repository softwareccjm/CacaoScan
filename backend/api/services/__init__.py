"""
Servicios base para CacaoScan.
Contiene clases base y utilidades comunes para todos los servicios.
"""
import logging
from typing import Dict, Any, Optional, List, Tuple
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger("cacaoscan.services")


class ServiceError(Exception):
    """
    Excepción base para errores de servicios.
    """
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationServiceError(ServiceError):
    """
    Error de validación en servicios.
    """
    pass


class PermissionServiceError(ServiceError):
    """
    Error de permisos en servicios.
    """
    pass


class NotFoundServiceError(ServiceError):
    """
    Error de recurso no encontrado en servicios.
    """
    pass


class BaseService:
    """
    Clase base para todos los servicios de CacaoScan.
    Proporciona funcionalidades comunes y utilidades.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"cacaoscan.services.{self.__class__.__name__}")
    
    def log_info(self, message: str, **kwargs):
        """Log de información."""
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log de advertencia."""
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log de error."""
        self.logger.error(message, extra=kwargs)
    
    def validate_user_permission(self, user: User, permission: str, resource: Any = None) -> bool:
        """
        Valida si un usuario tiene permisos para realizar una acción.
        
        Args:
            user: Usuario a validar
            permission: Tipo de permiso (read, write, delete, admin)
            resource: Recurso específico (opcional)
            
        Returns:
            True si tiene permisos
            
        Raises:
            PermissionServiceError: Si no tiene permisos
        """
        if not user or not user.is_authenticated:
            raise PermissionServiceError("Usuario no autenticado", "not_authenticated")
        
        # Administradores tienen todos los permisos
        if user.is_superuser:
            return True
        
        # Validaciones específicas por tipo de permiso
        if permission == "admin":
            if not user.is_staff:
                raise PermissionServiceError("Se requieren permisos de administrador", "admin_required")
        
        return True
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Valida que los campos requeridos estén presentes en los datos.
        
        Args:
            data: Diccionario de datos a validar
            required_fields: Lista de campos requeridos
            
        Raises:
            ValidationServiceError: Si faltan campos requeridos
        """
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            raise ValidationServiceError(
                f"Campos requeridos faltantes: {', '.join(missing_fields)}",
                "missing_required_fields",
                {"missing_fields": missing_fields}
            )
    
    def validate_email(self, email: str) -> bool:
        """
        Valida formato de email.
        
        Args:
            email: Email a validar
            
        Returns:
            True si es válido
            
        Raises:
            ValidationServiceError: Si el email no es válido
        """
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_regex, email):
            raise ValidationServiceError("Formato de email inválido", "invalid_email_format")
        
        return True
    
    def get_user_by_id(self, user_id: int) -> User:
        """
        Obtiene un usuario por ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario encontrado
            
        Raises:
            NotFoundServiceError: Si el usuario no existe
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFoundServiceError(f"Usuario con ID {user_id} no encontrado", "user_not_found")
    
    def get_user_by_email(self, email: str) -> User:
        """
        Obtiene un usuario por email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario encontrado
            
        Raises:
            NotFoundServiceError: Si el usuario no existe
        """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotFoundServiceError(f"Usuario con email {email} no encontrado", "user_not_found")
    
    def create_audit_log(self, user: User, action: str, resource_type: str, 
                        resource_id: int = None, details: Dict[str, Any] = None) -> None:
        """
        Crea un log de auditoría.
        
        Args:
            user: Usuario que realiza la acción
            action: Acción realizada
            resource_type: Tipo de recurso
            resource_id: ID del recurso (opcional)
            details: Detalles adicionales (opcional)
        """
        try:
            from ..models import ActivityLog
            
            ActivityLog.objects.create(
                user=user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                timestamp=timezone.now()
            )
            
            self.log_info(f"Log de auditoría creado: {action} en {resource_type}", 
                         user_id=user.id, resource_id=resource_id)
            
        except Exception as e:
            self.log_error(f"Error creando log de auditoría: {e}")
    
    def send_notification(self, user: User, tipo: str, titulo: str, mensaje: str, 
                         datos_extra: Dict[str, Any] = None) -> None:
        """
        Envía una notificación al usuario.
        
        Args:
            user: Usuario destinatario
            tipo: Tipo de notificación
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            datos_extra: Datos adicionales (opcional)
        """
        try:
            from ..models import Notification
            
            Notification.create_notification(
                user=user,
                tipo=tipo,
                titulo=titulo,
                mensaje=mensaje,
                datos_extra=datos_extra or {}
            )
            
            self.log_info(f"Notificación enviada: {titulo}", user_id=user.id, tipo=tipo)
            
        except Exception as e:
            self.log_error(f"Error enviando notificación: {e}")
    
    def send_email_notification(self, user: User, notification_type: str, 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Envía una notificación por email.
        
        Args:
            user: Usuario destinatario
            notification_type: Tipo de notificación por email
            context: Contexto para el template
            
        Returns:
            Resultado del envío de email
        """
        try:
            from ..email_service import send_email_notification
            
            email_context = {
                'user_name': user.get_full_name() or user.username,
                'user_email': user.email,
                **(context or {})
            }
            
            result = send_email_notification(
                user_email=user.email,
                notification_type=notification_type,
                context=email_context
            )
            
            if result['success']:
                self.log_info(f"Email enviado: {notification_type}", user_id=user.id)
            else:
                self.log_warning(f"Error enviando email: {result.get('error')}", user_id=user.id)
            
            return result
            
        except Exception as e:
            self.log_error(f"Error en envío de email: {e}")
            return {'success': False, 'error': str(e)}


class PaginationService:
    """
    Servicio para manejo de paginación.
    """
    
    @staticmethod
    def paginate_queryset(queryset, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Pagina un queryset.
        
        Args:
            queryset: Queryset a paginar
            page: Número de página (1-indexed)
            page_size: Tamaño de página
            
        Returns:
            Diccionario con datos paginados
        """
        from django.core.paginator import Paginator
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
        
        return {
            'results': list(page_obj.object_list),
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None
            }
        }


class CacheService:
    """
    Servicio para manejo de caché.
    """
    
    @staticmethod
    def get_cache_key(prefix: str, *args) -> str:
        """
        Genera una clave de caché.
        
        Args:
            prefix: Prefijo de la clave
            *args: Argumentos adicionales
            
        Returns:
            Clave de caché generada
        """
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"
    
    @staticmethod
    def invalidate_pattern(pattern: str) -> None:
        """
        Invalida todas las claves que coincidan con un patrón.
        
        Args:
            pattern: Patrón de claves a invalidar
        """
        try:
            from django.core.cache import cache
            cache.delete_pattern(pattern)
        except Exception as e:
            logger.warning(f"Error invalidando caché con patrón {pattern}: {e}")


class FileService:
    """
    Servicio para manejo de archivos.
    """
    
    @staticmethod
    def validate_image_file(file, max_size_mb: int = 20) -> Dict[str, Any]:
        """
        Valida un archivo de imagen.
        
        Args:
            file: Archivo a validar
            max_size_mb: Tamaño máximo en MB
            
        Returns:
            Diccionario con información de validación
            
        Raises:
            ValidationServiceError: Si el archivo no es válido
        """
        from PIL import Image
        import io
        
        # Validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp']
        if file.content_type not in allowed_types:
            raise ValidationServiceError(
                f"Tipo de archivo no válido: {file.content_type}. Tipos permitidos: {', '.join(allowed_types)}",
                "invalid_file_type"
            )
        
        # Validar tamaño
        max_size_bytes = max_size_mb * 1024 * 1024
        if file.size > max_size_bytes:
            raise ValidationServiceError(
                f"Archivo demasiado grande: {file.size / (1024*1024):.2f}MB. Máximo permitido: {max_size_mb}MB",
                "file_too_large"
            )
        
        # Validar que sea una imagen válida
        try:
            image_data = file.read()
            file.seek(0)  # Resetear posición del archivo
            image = Image.open(io.BytesIO(image_data))
            image.verify()
        except Exception as e:
            raise ValidationServiceError(f"Archivo de imagen inválido: {str(e)}", "invalid_image")
        
        return {
            'valid': True,
            'content_type': file.content_type,
            'size': file.size,
            'size_mb': file.size / (1024 * 1024),
            'dimensions': image.size if 'image' in locals() else None
        }
    
    @staticmethod
    def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
        """
        Genera un nombre de archivo único.
        
        Args:
            original_filename: Nombre original del archivo
            prefix: Prefijo opcional
            
        Returns:
            Nombre de archivo único
        """
        import uuid
        from pathlib import Path
        
        file_path = Path(original_filename)
        extension = file_path.suffix
        unique_id = str(uuid.uuid4())
        
        if prefix:
            return f"{prefix}_{unique_id}{extension}"
        else:
            return f"{unique_id}{extension}"
