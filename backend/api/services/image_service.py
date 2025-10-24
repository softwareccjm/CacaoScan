"""
Servicio de imágenes para CacaoScan.
Maneja la gestión de imágenes de granos de cacao.
"""
import logging
from typing import Dict, Any, Optional, Tuple, List
from django.contrib.auth.models import User
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import io

from .base import BaseService, ServiceError, ValidationServiceError, PermissionServiceError, NotFoundServiceError, FileService, PaginationService

logger = logging.getLogger("cacaoscan.services.images")


class ImageService(BaseService):
    """
    Servicio para manejo de imágenes de granos de cacao.
    """
    
    def __init__(self):
        super().__init__()
        self.file_service = FileService()
    
    def upload_image(self, user: User, image_file, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Sube una nueva imagen al sistema.
        
        Args:
            user: Usuario que sube la imagen
            image_file: Archivo de imagen
            metadata: Metadatos adicionales
            
        Returns:
            Diccionario con información de la imagen subida
            
        Raises:
            ValidationServiceError: Si la imagen no es válida
            ServiceError: Si hay error en la subida
        """
        try:
            # Validar archivo de imagen
            validation_result = self.file_service.validate_image_file(image_file)
            self.log_info(f"Imagen validada: {validation_result['size_mb']:.2f}MB", user_id=user.id)
            
            # Generar nombre único para el archivo
            unique_filename = self.file_service.generate_unique_filename(
                image_file.name, 
                f"user_{user.id}"
            )
            
            with transaction.atomic():
                # Crear objeto CacaoImage
                from ..models import CacaoImage
                
                cacao_image = CacaoImage(
                    user=user,
                    image=image_file,
                    file_name=unique_filename,
                    file_size=image_file.size,
                    file_type=image_file.content_type,
                    processed=False,
                    metadata=metadata or {}
                )
                
                # Guardar en BD
                cacao_image.save()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="image_uploaded",
                    resource_type="cacao_image",
                    resource_id=cacao_image.id,
                    details={
                        'file_name': unique_filename,
                        'file_size': image_file.size,
                        'file_type': image_file.content_type
                    }
                )
                
                self.log_info(f"Imagen subida con ID {cacao_image.id}", user_id=user.id)
                
                return {
                    'id': cacao_image.id,
                    'file_name': cacao_image.file_name,
                    'file_size': cacao_image.file_size,
                    'file_type': cacao_image.file_type,
                    'processed': cacao_image.processed,
                    'uploaded_at': cacao_image.created_at.isoformat(),
                    'image_url': cacao_image.image.url if cacao_image.image else None
                }
                
        except ValidationServiceError:
            raise
        except Exception as e:
            self.log_error(f"Error subiendo imagen: {e}")
            raise ServiceError("Error interno subiendo imagen", "upload_error")
    
    def get_user_images(self, user: User, page: int = 1, page_size: int = 20, 
                       filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Obtiene las imágenes de un usuario con paginación.
        
        Args:
            user: Usuario del cual obtener imágenes
            page: Número de página
            page_size: Tamaño de página
            filters: Filtros adicionales
            
        Returns:
            Diccionario con imágenes paginadas
        """
        try:
            from ..models import CacaoImage
            
            # Construir queryset base
            if user.is_superuser:
                # Administradores ven todas las imágenes
                queryset = CacaoImage.objects.all().select_related('user')
            else:
                # Usuarios normales solo ven sus imágenes
                queryset = CacaoImage.objects.filter(user=user)
            
            # Aplicar filtros
            if filters:
                if 'processed' in filters:
                    queryset = queryset.filter(processed=filters['processed'])
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
                if 'file_type' in filters:
                    queryset = queryset.filter(file_type=filters['file_type'])
            
            # Ordenar por fecha de creación descendente
            queryset = queryset.order_by('-created_at')
            
            # Paginar resultados
            paginated_data = PaginationService.paginate_queryset(queryset, page, page_size)
            
            # Serializar resultados
            results = []
            for image in paginated_data['results']:
                results.append({
                    'id': image.id,
                    'file_name': image.file_name,
                    'file_size': image.file_size,
                    'file_type': image.file_type,
                    'processed': image.processed,
                    'uploaded_at': image.created_at.isoformat(),
                    'image_url': image.image.url if image.image else None,
                    'user': {
                        'id': image.user.id,
                        'username': image.user.username,
                        'email': image.user.email
                    } if user.is_superuser else None
                })
            
            return {
                'results': results,
                'pagination': paginated_data['pagination']
            }
            
        except Exception as e:
            self.log_error(f"Error obteniendo imágenes: {e}")
            raise ServiceError("Error interno obteniendo imágenes", "list_error")
    
    def get_image_detail(self, user: User, image_id: int) -> Dict[str, Any]:
        """
        Obtiene los detalles de una imagen específica.
        
        Args:
            user: Usuario que solicita los detalles
            image_id: ID de la imagen
            
        Returns:
            Diccionario con detalles de la imagen
            
        Raises:
            NotFoundServiceError: Si la imagen no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import CacaoImage
            
            # Obtener imagen
            try:
                image = CacaoImage.objects.select_related('user').get(id=image_id)
            except CacaoImage.DoesNotExist:
                raise NotFoundServiceError(f"Imagen con ID {image_id} no encontrada", "image_not_found")
            
            # Verificar permisos
            if image.user != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para ver esta imagen", "no_permission")
            
            # Obtener predicciones asociadas
            predictions = image.predictions.all().order_by('-created_at')
            
            # Serializar imagen
            image_data = {
                'id': image.id,
                'file_name': image.file_name,
                'file_size': image.file_size,
                'file_type': image.file_type,
                'processed': image.processed,
                'uploaded_at': image.created_at.isoformat(),
                'updated_at': image.updated_at.isoformat(),
                'image_url': image.image.url if image.image else None,
                'metadata': image.metadata,
                'user': {
                    'id': image.user.id,
                    'username': image.user.username,
                    'email': image.user.email
                },
                'predictions': [
                    {
                        'id': pred.id,
                        'alto_mm': pred.alto_mm,
                        'ancho_mm': pred.ancho_mm,
                        'grosor_mm': pred.grosor_mm,
                        'peso_g': pred.peso_g,
                        'average_confidence': pred.average_confidence,
                        'processing_time_ms': pred.processing_time_ms,
                        'model_version': pred.model_version,
                        'crop_url': pred.crop_url,
                        'created_at': pred.created_at.isoformat()
                    }
                    for pred in predictions
                ]
            }
            
            return image_data
            
        except (NotFoundServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error obteniendo detalles de imagen: {e}")
            raise ServiceError("Error interno obteniendo detalles", "detail_error")
    
    def update_image_metadata(self, user: User, image_id: int, 
                             metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza los metadatos de una imagen.
        
        Args:
            user: Usuario que actualiza
            image_id: ID de la imagen
            metadata: Nuevos metadatos
            
        Returns:
            Diccionario con imagen actualizada
            
        Raises:
            NotFoundServiceError: Si la imagen no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import CacaoImage
            
            # Obtener imagen
            try:
                image = CacaoImage.objects.get(id=image_id)
            except CacaoImage.DoesNotExist:
                raise NotFoundServiceError(f"Imagen con ID {image_id} no encontrada", "image_not_found")
            
            # Verificar permisos
            if image.user != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para actualizar esta imagen", "no_permission")
            
            with transaction.atomic():
                # Actualizar metadatos
                current_metadata = image.metadata or {}
                current_metadata.update(metadata)
                image.metadata = current_metadata
                image.save()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="image_metadata_updated",
                    resource_type="cacao_image",
                    resource_id=image_id,
                    details={'updated_metadata': list(metadata.keys())}
                )
                
                self.log_info(f"Metadatos de imagen actualizados: {image_id}", user_id=user.id)
                
                return self.get_image_detail(user, image_id)
                
        except (NotFoundServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error actualizando metadatos: {e}")
            raise ServiceError("Error interno actualizando metadatos", "update_error")
    
    def delete_image(self, user: User, image_id: int) -> bool:
        """
        Elimina una imagen del sistema.
        
        Args:
            user: Usuario que solicita la eliminación
            image_id: ID de la imagen
            
        Returns:
            True si se eliminó exitosamente
            
        Raises:
            NotFoundServiceError: Si la imagen no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import CacaoImage
            
            # Obtener imagen
            try:
                image = CacaoImage.objects.get(id=image_id)
            except CacaoImage.DoesNotExist:
                raise NotFoundServiceError(f"Imagen con ID {image_id} no encontrada", "image_not_found")
            
            # Verificar permisos
            if image.user != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para eliminar esta imagen", "no_permission")
            
            with transaction.atomic():
                # Eliminar archivo físico si existe
                if image.image and image.image.name:
                    try:
                        default_storage.delete(image.image.name)
                    except Exception as e:
                        self.log_warning(f"Error eliminando archivo físico: {e}")
                
                # Eliminar imagen de BD (esto también eliminará las predicciones asociadas por CASCADE)
                image.delete()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="image_deleted",
                    resource_type="cacao_image",
                    resource_id=image_id
                )
                
                self.log_info(f"Imagen eliminada: {image_id}", user_id=user.id)
                
                return True
                
        except (NotFoundServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error eliminando imagen: {e}")
            raise ServiceError("Error interno eliminando imagen", "delete_error")
    
    def get_image_statistics(self, user: User, date_from: str = None, 
                           date_to: str = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas de imágenes de un usuario.
        
        Args:
            user: Usuario del cual obtener estadísticas
            date_from: Fecha de inicio (opcional)
            date_to: Fecha de fin (opcional)
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            from ..models import CacaoImage, CacaoPrediction
            from django.db.models import Count, Avg, Sum
            
            # Construir queryset base
            queryset = CacaoImage.objects.filter(user=user)
            
            # Aplicar filtros de fecha
            if date_from:
                queryset = queryset.filter(created_at__gte=date_from)
            if date_to:
                queryset = queryset.filter(created_at__lte=date_to)
            
            # Calcular estadísticas básicas
            total_images = queryset.count()
            processed_images = queryset.filter(processed=True).count()
            unprocessed_images = total_images - processed_images
            
            # Estadísticas por tipo de archivo
            file_type_stats = queryset.values('file_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Estadísticas de tamaño
            size_stats = queryset.aggregate(
                total_size=Sum('file_size'),
                avg_size=Avg('file_size')
            )
            
            # Estadísticas de predicciones
            prediction_stats = CacaoPrediction.objects.filter(
                image__user=user,
                image__created_at__gte=date_from if date_from else '1900-01-01',
                image__created_at__lte=date_to if date_to else '2100-12-31'
            ).aggregate(
                total_predictions=Count('id'),
                avg_confidence=Avg('average_confidence'),
                avg_processing_time=Avg('processing_time_ms')
            )
            
            return {
                'total_images': total_images,
                'processed_images': processed_images,
                'unprocessed_images': unprocessed_images,
                'processing_rate': round((processed_images / total_images * 100) if total_images > 0 else 0, 2),
                'file_type_distribution': list(file_type_stats),
                'size_stats': {
                    'total_size_bytes': size_stats['total_size'] or 0,
                    'total_size_mb': round((size_stats['total_size'] or 0) / (1024 * 1024), 2),
                    'average_size_bytes': round(size_stats['avg_size'] or 0, 0)
                },
                'prediction_stats': {
                    'total_predictions': prediction_stats['total_predictions'] or 0,
                    'average_confidence': round(prediction_stats['avg_confidence'] or 0, 3),
                    'average_processing_time_ms': round(prediction_stats['avg_processing_time'] or 0, 0)
                }
            }
            
        except Exception as e:
            self.log_error(f"Error obteniendo estadísticas de imágenes: {e}")
            raise ServiceError("Error interno obteniendo estadísticas", "stats_error")
    
    def download_image(self, user: User, image_id: int) -> Tuple[bytes, str, str]:
        """
        Descarga una imagen específica.
        
        Args:
            user: Usuario que solicita la descarga
            image_id: ID de la imagen
            
        Returns:
            Tupla con (contenido_archivo, nombre_archivo, tipo_mime)
            
        Raises:
            NotFoundServiceError: Si la imagen no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import CacaoImage
            
            # Obtener imagen
            try:
                image = CacaoImage.objects.get(id=image_id)
            except CacaoImage.DoesNotExist:
                raise NotFoundServiceError(f"Imagen con ID {image_id} no encontrada", "image_not_found")
            
            # Verificar permisos
            if image.user != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para descargar esta imagen", "no_permission")
            
            # Leer contenido del archivo
            if not image.image or not image.image.name:
                raise NotFoundServiceError("Archivo de imagen no encontrado", "file_not_found")
            
            try:
                file_content = default_storage.open(image.image.name).read()
            except Exception as e:
                raise NotFoundServiceError(f"Error leyendo archivo: {str(e)}", "file_read_error")
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="image_downloaded",
                resource_type="cacao_image",
                resource_id=image_id
            )
            
            self.log_info(f"Imagen descargada: {image_id}", user_id=user.id)
            
            return file_content, image.file_name, image.file_type
            
        except (NotFoundServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error descargando imagen: {e}")
            raise ServiceError("Error interno descargando imagen", "download_error")
    
    def bulk_delete_images(self, user: User, image_ids: List[int]) -> Dict[str, Any]:
        """
        Elimina múltiples imágenes en lote.
        
        Args:
            user: Usuario que solicita la eliminación
            image_ids: Lista de IDs de imágenes
            
        Returns:
            Diccionario con resultados de la eliminación
            
        Raises:
            ValidationServiceError: Si la lista está vacía
        """
        try:
            if not image_ids:
                raise ValidationServiceError("Lista de imágenes vacía", "empty_list")
            
            from ..models import CacaoImage
            
            deleted_count = 0
            errors = []
            
            for image_id in image_ids:
                try:
                    # Obtener imagen
                    try:
                        image = CacaoImage.objects.get(id=image_id)
                    except CacaoImage.DoesNotExist:
                        errors.append({'id': image_id, 'error': 'Imagen no encontrada'})
                        continue
                    
                    # Verificar permisos
                    if image.user != user and not user.is_superuser:
                        errors.append({'id': image_id, 'error': 'Sin permisos'})
                        continue
                    
                    with transaction.atomic():
                        # Eliminar archivo físico si existe
                        if image.image and image.image.name:
                            try:
                                default_storage.delete(image.image.name)
                            except Exception as e:
                                self.log_warning(f"Error eliminando archivo físico: {e}")
                        
                        # Eliminar imagen de BD
                        image.delete()
                        deleted_count += 1
                        
                        # Crear log de auditoría
                        self.create_audit_log(
                            user=user,
                            action="image_deleted",
                            resource_type="cacao_image",
                            resource_id=image_id
                        )
                
                except Exception as e:
                    errors.append({'id': image_id, 'error': str(e)})
            
            self.log_info(f"Eliminación masiva completada: {deleted_count}/{len(image_ids)}", user_id=user.id)
            
            return {
                'total_requested': len(image_ids),
                'deleted_count': deleted_count,
                'errors': errors,
                'success_rate': round((deleted_count / len(image_ids)) * 100, 2)
            }
            
        except ValidationServiceError:
            raise
        except Exception as e:
            self.log_error(f"Error en eliminación masiva: {e}")
            raise ServiceError("Error interno en eliminación masiva", "bulk_delete_error")
