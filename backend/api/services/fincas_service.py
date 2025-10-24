"""
Servicio de fincas y lotes para CacaoScan.
Maneja la gestión de fincas y lotes de cacao.
"""
import logging
from typing import Dict, Any, Optional, Tuple, List
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Count, Avg, Sum
from decimal import Decimal

from .base import BaseService, ServiceError, ValidationServiceError, PermissionServiceError, NotFoundServiceError, PaginationService

logger = logging.getLogger("cacaoscan.services.fincas")


class FincaService(BaseService):
    """
    Servicio para manejo de fincas de cacao.
    """
    
    def __init__(self):
        super().__init__()
    
    def create_finca(self, user: User, finca_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una nueva finca.
        
        Args:
            user: Usuario propietario de la finca
            finca_data: Datos de la finca
            
        Returns:
            Diccionario con información de la finca creada
            
        Raises:
            ValidationServiceError: Si los datos son inválidos
            ServiceError: Si hay error en la creación
        """
        try:
            # Validar campos requeridos
            required_fields = ['nombre', 'ubicacion', 'municipio', 'departamento', 'hectareas']
            self.validate_required_fields(finca_data, required_fields)
            
            # Validar hectáreas
            try:
                hectareas = Decimal(str(finca_data['hectareas']))
                if hectareas <= 0:
                    raise ValidationServiceError("Las hectáreas deben ser mayores a 0", "invalid_hectareas")
            except (ValueError, TypeError):
                raise ValidationServiceError("Formato de hectáreas inválido", "invalid_hectareas_format")
            
            with transaction.atomic():
                from ..models import Finca
                
                # Crear finca
                finca = Finca.objects.create(
                    nombre=finca_data['nombre'],
                    ubicacion=finca_data['ubicacion'],
                    municipio=finca_data['municipio'],
                    departamento=finca_data['departamento'],
                    hectareas=hectareas,
                    agricultor=user,
                    activa=finca_data.get('activa', True),
                    descripcion=finca_data.get('descripcion', ''),
                    coordenadas=finca_data.get('coordenadas', {}),
                    fecha_adquisicion=finca_data.get('fecha_adquisicion'),
                    tipo_suelo=finca_data.get('tipo_suelo', ''),
                    altitud=finca_data.get('altitud'),
                    precipitacion_anual=finca_data.get('precipitacion_anual'),
                    temperatura_promedio=finca_data.get('temperatura_promedio')
                )
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="finca_created",
                    resource_type="finca",
                    resource_id=finca.id,
                    details={
                        'nombre': finca.nombre,
                        'hectareas': float(finca.hectareas),
                        'municipio': finca.municipio,
                        'departamento': finca.departamento
                    }
                )
                
                self.log_info(f"Finca creada: {finca.nombre}", user_id=user.id, finca_id=finca.id)
                
                return self._serialize_finca(finca)
                
        except ValidationServiceError:
            raise
        except Exception as e:
            self.log_error(f"Error creando finca: {e}")
            raise ServiceError("Error interno creando finca", "create_error")
    
    def get_user_fincas(self, user: User, page: int = 1, page_size: int = 20, 
                       filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Obtiene las fincas de un usuario con paginación.
        
        Args:
            user: Usuario del cual obtener fincas
            page: Número de página
            page_size: Tamaño de página
            filters: Filtros adicionales
            
        Returns:
            Diccionario con fincas paginadas
        """
        try:
            from ..models import Finca
            
            # Construir queryset base
            if user.is_superuser:
                # Administradores ven todas las fincas
                queryset = Finca.objects.all().select_related('agricultor')
            else:
                # Usuarios normales solo ven sus fincas
                queryset = Finca.objects.filter(agricultor=user)
            
            # Aplicar filtros
            if filters:
                if 'activa' in filters:
                    queryset = queryset.filter(activa=filters['activa'])
                if 'departamento' in filters:
                    queryset = queryset.filter(departamento__icontains=filters['departamento'])
                if 'municipio' in filters:
                    queryset = queryset.filter(municipio__icontains=filters['municipio'])
                if 'search' in filters:
                    search_term = filters['search']
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_term) |
                        Q(ubicacion__icontains=search_term) |
                        Q(municipio__icontains=search_term) |
                        Q(departamento__icontains=search_term)
                    )
            
            # Ordenar por nombre
            queryset = queryset.order_by('nombre')
            
            # Paginar resultados
            paginated_data = PaginationService.paginate_queryset(queryset, page, page_size)
            
            # Serializar resultados
            results = []
            for finca in paginated_data['results']:
                results.append(self._serialize_finca(finca))
            
            return {
                'results': results,
                'pagination': paginated_data['pagination']
            }
            
        except Exception as e:
            self.log_error(f"Error obteniendo fincas: {e}")
            raise ServiceError("Error interno obteniendo fincas", "list_error")
    
    def get_finca_detail(self, user: User, finca_id: int) -> Dict[str, Any]:
        """
        Obtiene los detalles de una finca específica.
        
        Args:
            user: Usuario que solicita los detalles
            finca_id: ID de la finca
            
        Returns:
            Diccionario con detalles de la finca
            
        Raises:
            NotFoundServiceError: Si la finca no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import Finca
            
            # Obtener finca
            try:
                finca = Finca.objects.select_related('agricultor').prefetch_related('lotes').get(id=finca_id)
            except Finca.DoesNotExist:
                raise NotFoundServiceError(f"Finca con ID {finca_id} no encontrada", "finca_not_found")
            
            # Verificar permisos
            if finca.agricultor != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para ver esta finca", "no_permission")
            
            # Serializar finca con detalles
            finca_data = self._serialize_finca(finca)
            
            # Agregar estadísticas de lotes
            lotes = finca.lotes.all()
            finca_data['estadisticas'] = {
                'total_lotes': lotes.count(),
                'lotes_activos': lotes.filter(activo=True).count(),
                'lotes_inactivos': lotes.filter(activo=False).count(),
                'area_total_lotes': sum(float(lote.area_hectareas) for lote in lotes),
                'variedades': list(set(lote.variedad for lote in lotes if lote.variedad))
            }
            
            # Agregar lotes
            finca_data['lotes'] = [
                {
                    'id': lote.id,
                    'identificador': lote.identificador,
                    'variedad': lote.variedad,
                    'area_hectareas': float(lote.area_hectareas),
                    'fecha_plantacion': lote.fecha_plantacion.isoformat() if lote.fecha_plantacion else None,
                    'activo': lote.activo,
                    'descripcion': lote.descripcion
                }
                for lote in lotes
            ]
            
            return finca_data
            
        except (NotFoundServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error obteniendo detalles de finca: {e}")
            raise ServiceError("Error interno obteniendo detalles", "detail_error")
    
    def update_finca(self, user: User, finca_id: int, finca_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza una finca existente.
        
        Args:
            user: Usuario que actualiza
            finca_id: ID de la finca
            finca_data: Nuevos datos de la finca
            
        Returns:
            Diccionario con finca actualizada
            
        Raises:
            NotFoundServiceError: Si la finca no existe
            PermissionServiceError: Si el usuario no tiene permisos
            ValidationServiceError: Si los datos son inválidos
        """
        try:
            from ..models import Finca
            
            # Obtener finca
            try:
                finca = Finca.objects.get(id=finca_id)
            except Finca.DoesNotExist:
                raise NotFoundServiceError(f"Finca con ID {finca_id} no encontrada", "finca_not_found")
            
            # Verificar permisos
            if finca.agricultor != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para actualizar esta finca", "no_permission")
            
            with transaction.atomic():
                # Actualizar campos
                if 'nombre' in finca_data:
                    finca.nombre = finca_data['nombre']
                if 'ubicacion' in finca_data:
                    finca.ubicacion = finca_data['ubicacion']
                if 'municipio' in finca_data:
                    finca.municipio = finca_data['municipio']
                if 'departamento' in finca_data:
                    finca.departamento = finca_data['departamento']
                if 'hectareas' in finca_data:
                    try:
                        hectareas = Decimal(str(finca_data['hectareas']))
                        if hectareas <= 0:
                            raise ValidationServiceError("Las hectáreas deben ser mayores a 0", "invalid_hectareas")
                        finca.hectareas = hectareas
                    except (ValueError, TypeError):
                        raise ValidationServiceError("Formato de hectáreas inválido", "invalid_hectareas_format")
                
                if 'activa' in finca_data:
                    finca.activa = finca_data['activa']
                if 'descripcion' in finca_data:
                    finca.descripcion = finca_data['descripcion']
                if 'coordenadas' in finca_data:
                    finca.coordenadas = finca_data['coordenadas']
                if 'fecha_adquisicion' in finca_data:
                    finca.fecha_adquisicion = finca_data['fecha_adquisicion']
                if 'tipo_suelo' in finca_data:
                    finca.tipo_suelo = finca_data['tipo_suelo']
                if 'altitud' in finca_data:
                    finca.altitud = finca_data['altitud']
                if 'precipitacion_anual' in finca_data:
                    finca.precipitacion_anual = finca_data['precipitacion_anual']
                if 'temperatura_promedio' in finca_data:
                    finca.temperatura_promedio = finca_data['temperatura_promedio']
                
                finca.save()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="finca_updated",
                    resource_type="finca",
                    resource_id=finca_id,
                    details={'updated_fields': list(finca_data.keys())}
                )
                
                self.log_info(f"Finca actualizada: {finca.nombre}", user_id=user.id, finca_id=finca_id)
                
                return self._serialize_finca(finca)
                
        except (NotFoundServiceError, PermissionServiceError, ValidationServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error actualizando finca: {e}")
            raise ServiceError("Error interno actualizando finca", "update_error")
    
    def delete_finca(self, user: User, finca_id: int) -> bool:
        """
        Elimina una finca del sistema.
        
        Args:
            user: Usuario que solicita la eliminación
            finca_id: ID de la finca
            
        Returns:
            True si se eliminó exitosamente
            
        Raises:
            NotFoundServiceError: Si la finca no existe
            PermissionServiceError: Si el usuario no tiene permisos
            ValidationServiceError: Si la finca tiene lotes asociados
        """
        try:
            from ..models import Finca
            
            # Obtener finca
            try:
                finca = Finca.objects.get(id=finca_id)
            except Finca.DoesNotExist:
                raise NotFoundServiceError(f"Finca con ID {finca_id} no encontrada", "finca_not_found")
            
            # Verificar permisos
            if finca.agricultor != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para eliminar esta finca", "no_permission")
            
            # Verificar si tiene lotes asociados
            if finca.lotes.exists():
                raise ValidationServiceError("No se puede eliminar una finca que tiene lotes asociados", "has_lotes")
            
            with transaction.atomic():
                # Eliminar finca
                finca.delete()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="finca_deleted",
                    resource_type="finca",
                    resource_id=finca_id
                )
                
                self.log_info(f"Finca eliminada: {finca.nombre}", user_id=user.id, finca_id=finca_id)
                
                return True
                
        except (NotFoundServiceError, PermissionServiceError, ValidationServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error eliminando finca: {e}")
            raise ServiceError("Error interno eliminando finca", "delete_error")
    
    def get_finca_statistics(self, user: User, finca_id: int = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas de fincas de un usuario.
        
        Args:
            user: Usuario del cual obtener estadísticas
            finca_id: ID de finca específica (opcional)
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            from ..models import Finca, Lote
            
            # Construir queryset base
            if user.is_superuser:
                fincas_queryset = Finca.objects.all()
            else:
                fincas_queryset = Finca.objects.filter(agricultor=user)
            
            if finca_id:
                fincas_queryset = fincas_queryset.filter(id=finca_id)
            
            # Estadísticas básicas
            total_fincas = fincas_queryset.count()
            fincas_activas = fincas_queryset.filter(activa=True).count()
            fincas_inactivas = total_fincas - fincas_activas
            
            # Estadísticas de área
            area_stats = fincas_queryset.aggregate(
                total_hectareas=Sum('hectareas'),
                promedio_hectareas=Avg('hectareas'),
                min_hectareas=Min('hectareas'),
                max_hectareas=Max('hectareas')
            )
            
            # Estadísticas por departamento
            dept_stats = fincas_queryset.values('departamento').annotate(
                count=Count('id'),
                total_hectareas=Sum('hectareas')
            ).order_by('-count')
            
            # Estadísticas de lotes
            lotes_stats = Lote.objects.filter(finca__in=fincas_queryset).aggregate(
                total_lotes=Count('id'),
                lotes_activos=Count('id', filter=Q(activo=True)),
                area_total_lotes=Sum('area_hectareas')
            )
            
            return {
                'total_fincas': total_fincas,
                'fincas_activas': fincas_activas,
                'fincas_inactivas': fincas_inactivas,
                'area_stats': {
                    'total_hectareas': float(area_stats['total_hectareas'] or 0),
                    'promedio_hectareas': float(area_stats['promedio_hectareas'] or 0),
                    'min_hectareas': float(area_stats['min_hectareas'] or 0),
                    'max_hectareas': float(area_stats['max_hectareas'] or 0)
                },
                'departamento_distribution': list(dept_stats),
                'lotes_stats': {
                    'total_lotes': lotes_stats['total_lotes'] or 0,
                    'lotes_activos': lotes_stats['lotes_activos'] or 0,
                    'area_total_lotes': float(lotes_stats['area_total_lotes'] or 0)
                }
            }
            
        except Exception as e:
            self.log_error(f"Error obteniendo estadísticas de fincas: {e}")
            raise ServiceError("Error interno obteniendo estadísticas", "stats_error")
    
    def _serialize_finca(self, finca) -> Dict[str, Any]:
        """
        Serializa una finca a diccionario.
        
        Args:
            finca: Objeto Finca
            
        Returns:
            Diccionario serializado
        """
        return {
            'id': finca.id,
            'nombre': finca.nombre,
            'ubicacion': finca.ubicacion,
            'municipio': finca.municipio,
            'departamento': finca.departamento,
            'hectareas': float(finca.hectareas),
            'activa': finca.activa,
            'descripcion': finca.descripcion,
            'coordenadas': finca.coordenadas,
            'fecha_adquisicion': finca.fecha_adquisicion.isoformat() if finca.fecha_adquisicion else None,
            'tipo_suelo': finca.tipo_suelo,
            'altitud': finca.altitud,
            'precipitacion_anual': finca.precipitacion_anual,
            'temperatura_promedio': finca.temperatura_promedio,
            'created_at': finca.created_at.isoformat(),
            'updated_at': finca.updated_at.isoformat(),
            'agricultor': {
                'id': finca.agricultor.id,
                'username': finca.agricultor.username,
                'email': finca.agricultor.email,
                'full_name': finca.agricultor.get_full_name()
            }
        }


class LoteService(BaseService):
    """
    Servicio para manejo de lotes de cacao.
    """
    
    def __init__(self):
        super().__init__()
    
    def create_lote(self, user: User, lote_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo lote.
        
        Args:
            user: Usuario propietario del lote
            lote_data: Datos del lote
            
        Returns:
            Diccionario con información del lote creado
            
        Raises:
            ValidationServiceError: Si los datos son inválidos
            ServiceError: Si hay error en la creación
        """
        try:
            # Validar campos requeridos
            required_fields = ['finca_id', 'identificador', 'variedad', 'area_hectareas']
            self.validate_required_fields(lote_data, required_fields)
            
            # Validar área
            try:
                area_hectareas = Decimal(str(lote_data['area_hectareas']))
                if area_hectareas <= 0:
                    raise ValidationServiceError("El área debe ser mayor a 0", "invalid_area")
            except (ValueError, TypeError):
                raise ValidationServiceError("Formato de área inválido", "invalid_area_format")
            
            # Verificar que la finca existe y pertenece al usuario
            from ..models import Finca
            try:
                finca = Finca.objects.get(id=lote_data['finca_id'])
                if finca.agricultor != user and not user.is_superuser:
                    raise PermissionServiceError("No tienes permisos para crear lotes en esta finca", "no_permission")
            except Finca.DoesNotExist:
                raise NotFoundServiceError(f"Finca con ID {lote_data['finca_id']} no encontrada", "finca_not_found")
            
            with transaction.atomic():
                from ..models import Lote
                
                # Crear lote
                lote = Lote.objects.create(
                    finca=finca,
                    identificador=lote_data['identificador'],
                    variedad=lote_data['variedad'],
                    area_hectareas=area_hectareas,
                    fecha_plantacion=lote_data.get('fecha_plantacion'),
                    activo=lote_data.get('activo', True),
                    descripcion=lote_data.get('descripcion', ''),
                    coordenadas=lote_data.get('coordenadas', {}),
                    tipo_suelo=lote_data.get('tipo_suelo', ''),
                    altitud=lote_data.get('altitud'),
                    precipitacion_anual=lote_data.get('precipitacion_anual'),
                    temperatura_promedio=lote_data.get('temperatura_promedio'),
                    numero_arboles=lote_data.get('numero_arboles'),
                    edad_arboles=lote_data.get('edad_arboles'),
                    densidad_plantacion=lote_data.get('densidad_plantacion'),
                    sistema_riego=lote_data.get('sistema_riego', ''),
                    manejo_organico=lote_data.get('manejo_organico', False),
                    certificaciones=lote_data.get('certificaciones', [])
                )
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="lote_created",
                    resource_type="lote",
                    resource_id=lote.id,
                    details={
                        'identificador': lote.identificador,
                        'variedad': lote.variedad,
                        'area_hectareas': float(lote.area_hectareas),
                        'finca_id': finca.id,
                        'finca_nombre': finca.nombre
                    }
                )
                
                self.log_info(f"Lote creado: {lote.identificador}", user_id=user.id, lote_id=lote.id)
                
                return self._serialize_lote(lote)
                
        except (ValidationServiceError, PermissionServiceError, NotFoundServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error creando lote: {e}")
            raise ServiceError("Error interno creando lote", "create_error")
    
    def get_user_lotes(self, user: User, page: int = 1, page_size: int = 20, 
                      filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Obtiene los lotes de un usuario con paginación.
        
        Args:
            user: Usuario del cual obtener lotes
            page: Número de página
            page_size: Tamaño de página
            filters: Filtros adicionales
            
        Returns:
            Diccionario con lotes paginados
        """
        try:
            from ..models import Lote
            
            # Construir queryset base
            if user.is_superuser:
                # Administradores ven todos los lotes
                queryset = Lote.objects.all().select_related('finca', 'finca__agricultor')
            else:
                # Usuarios normales solo ven sus lotes
                queryset = Lote.objects.filter(finca__agricultor=user).select_related('finca')
            
            # Aplicar filtros
            if filters:
                if 'finca_id' in filters:
                    queryset = queryset.filter(finca_id=filters['finca_id'])
                if 'activo' in filters:
                    queryset = queryset.filter(activo=filters['activo'])
                if 'variedad' in filters:
                    queryset = queryset.filter(variedad__icontains=filters['variedad'])
                if 'search' in filters:
                    search_term = filters['search']
                    queryset = queryset.filter(
                        Q(identificador__icontains=search_term) |
                        Q(variedad__icontains=search_term) |
                        Q(finca__nombre__icontains=search_term)
                    )
            
            # Ordenar por identificador
            queryset = queryset.order_by('identificador')
            
            # Paginar resultados
            paginated_data = PaginationService.paginate_queryset(queryset, page, page_size)
            
            # Serializar resultados
            results = []
            for lote in paginated_data['results']:
                results.append(self._serialize_lote(lote))
            
            return {
                'results': results,
                'pagination': paginated_data['pagination']
            }
            
        except Exception as e:
            self.log_error(f"Error obteniendo lotes: {e}")
            raise ServiceError("Error interno obteniendo lotes", "list_error")
    
    def get_lote_detail(self, user: User, lote_id: int) -> Dict[str, Any]:
        """
        Obtiene los detalles de un lote específico.
        
        Args:
            user: Usuario que solicita los detalles
            lote_id: ID del lote
            
        Returns:
            Diccionario con detalles del lote
            
        Raises:
            NotFoundServiceError: Si el lote no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import Lote
            
            # Obtener lote
            try:
                lote = Lote.objects.select_related('finca', 'finca__agricultor').get(id=lote_id)
            except Lote.DoesNotExist:
                raise NotFoundServiceError(f"Lote con ID {lote_id} no encontrado", "lote_not_found")
            
            # Verificar permisos
            if lote.finca.agricultor != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para ver este lote", "no_permission")
            
            # Serializar lote con detalles
            lote_data = self._serialize_lote(lote)
            
            # Agregar información de la finca
            lote_data['finca'] = {
                'id': lote.finca.id,
                'nombre': lote.finca.nombre,
                'ubicacion': lote.finca.ubicacion,
                'municipio': lote.finca.municipio,
                'departamento': lote.finca.departamento,
                'hectareas': float(lote.finca.hectareas)
            }
            
            return lote_data
            
        except (NotFoundServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error obteniendo detalles de lote: {e}")
            raise ServiceError("Error interno obteniendo detalles", "detail_error")
    
    def update_lote(self, user: User, lote_id: int, lote_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza un lote existente.
        
        Args:
            user: Usuario que actualiza
            lote_id: ID del lote
            lote_data: Nuevos datos del lote
            
        Returns:
            Diccionario con lote actualizado
            
        Raises:
            NotFoundServiceError: Si el lote no existe
            PermissionServiceError: Si el usuario no tiene permisos
            ValidationServiceError: Si los datos son inválidos
        """
        try:
            from ..models import Lote
            
            # Obtener lote
            try:
                lote = Lote.objects.get(id=lote_id)
            except Lote.DoesNotExist:
                raise NotFoundServiceError(f"Lote con ID {lote_id} no encontrado", "lote_not_found")
            
            # Verificar permisos
            if lote.finca.agricultor != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para actualizar este lote", "no_permission")
            
            with transaction.atomic():
                # Actualizar campos
                if 'identificador' in lote_data:
                    lote.identificador = lote_data['identificador']
                if 'variedad' in lote_data:
                    lote.variedad = lote_data['variedad']
                if 'area_hectareas' in lote_data:
                    try:
                        area_hectareas = Decimal(str(lote_data['area_hectareas']))
                        if area_hectareas <= 0:
                            raise ValidationServiceError("El área debe ser mayor a 0", "invalid_area")
                        lote.area_hectareas = area_hectareas
                    except (ValueError, TypeError):
                        raise ValidationServiceError("Formato de área inválido", "invalid_area_format")
                
                if 'fecha_plantacion' in lote_data:
                    lote.fecha_plantacion = lote_data['fecha_plantacion']
                if 'activo' in lote_data:
                    lote.activo = lote_data['activo']
                if 'descripcion' in lote_data:
                    lote.descripcion = lote_data['descripcion']
                if 'coordenadas' in lote_data:
                    lote.coordenadas = lote_data['coordenadas']
                if 'tipo_suelo' in lote_data:
                    lote.tipo_suelo = lote_data['tipo_suelo']
                if 'altitud' in lote_data:
                    lote.altitud = lote_data['altitud']
                if 'precipitacion_anual' in lote_data:
                    lote.precipitacion_anual = lote_data['precipitacion_anual']
                if 'temperatura_promedio' in lote_data:
                    lote.temperatura_promedio = lote_data['temperatura_promedio']
                if 'numero_arboles' in lote_data:
                    lote.numero_arboles = lote_data['numero_arboles']
                if 'edad_arboles' in lote_data:
                    lote.edad_arboles = lote_data['edad_arboles']
                if 'densidad_plantacion' in lote_data:
                    lote.densidad_plantacion = lote_data['densidad_plantacion']
                if 'sistema_riego' in lote_data:
                    lote.sistema_riego = lote_data['sistema_riego']
                if 'manejo_organico' in lote_data:
                    lote.manejo_organico = lote_data['manejo_organico']
                if 'certificaciones' in lote_data:
                    lote.certificaciones = lote_data['certificaciones']
                
                lote.save()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="lote_updated",
                    resource_type="lote",
                    resource_id=lote_id,
                    details={'updated_fields': list(lote_data.keys())}
                )
                
                self.log_info(f"Lote actualizado: {lote.identificador}", user_id=user.id, lote_id=lote_id)
                
                return self._serialize_lote(lote)
                
        except (NotFoundServiceError, PermissionServiceError, ValidationServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error actualizando lote: {e}")
            raise ServiceError("Error interno actualizando lote", "update_error")
    
    def delete_lote(self, user: User, lote_id: int) -> bool:
        """
        Elimina un lote del sistema.
        
        Args:
            user: Usuario que solicita la eliminación
            lote_id: ID del lote
            
        Returns:
            True si se eliminó exitosamente
            
        Raises:
            NotFoundServiceError: Si el lote no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import Lote
            
            # Obtener lote
            try:
                lote = Lote.objects.get(id=lote_id)
            except Lote.DoesNotExist:
                raise NotFoundServiceError(f"Lote con ID {lote_id} no encontrado", "lote_not_found")
            
            # Verificar permisos
            if lote.finca.agricultor != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para eliminar este lote", "no_permission")
            
            with transaction.atomic():
                # Eliminar lote
                lote.delete()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="lote_deleted",
                    resource_type="lote",
                    resource_id=lote_id
                )
                
                self.log_info(f"Lote eliminado: {lote.identificador}", user_id=user.id, lote_id=lote_id)
                
                return True
                
        except (NotFoundServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error eliminando lote: {e}")
            raise ServiceError("Error interno eliminando lote", "delete_error")
    
    def get_lotes_by_finca(self, user: User, finca_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los lotes de una finca específica.
        
        Args:
            user: Usuario que solicita los lotes
            finca_id: ID de la finca
            
        Returns:
            Lista de lotes de la finca
            
        Raises:
            NotFoundServiceError: Si la finca no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import Finca, Lote
            
            # Verificar que la finca existe y pertenece al usuario
            try:
                finca = Finca.objects.get(id=finca_id)
                if finca.agricultor != user and not user.is_superuser:
                    raise PermissionServiceError("No tienes permisos para ver los lotes de esta finca", "no_permission")
            except Finca.DoesNotExist:
                raise NotFoundServiceError(f"Finca con ID {finca_id} no encontrada", "finca_not_found")
            
            # Obtener lotes
            lotes = Lote.objects.filter(finca=finca).order_by('identificador')
            
            # Serializar lotes
            results = []
            for lote in lotes:
                results.append(self._serialize_lote(lote))
            
            return results
            
        except (NotFoundServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error obteniendo lotes por finca: {e}")
            raise ServiceError("Error interno obteniendo lotes", "list_error")
    
    def _serialize_lote(self, lote) -> Dict[str, Any]:
        """
        Serializa un lote a diccionario.
        
        Args:
            lote: Objeto Lote
            
        Returns:
            Diccionario serializado
        """
        return {
            'id': lote.id,
            'identificador': lote.identificador,
            'variedad': lote.variedad,
            'area_hectareas': float(lote.area_hectareas),
            'fecha_plantacion': lote.fecha_plantacion.isoformat() if lote.fecha_plantacion else None,
            'activo': lote.activo,
            'descripcion': lote.descripcion,
            'coordenadas': lote.coordenadas,
            'tipo_suelo': lote.tipo_suelo,
            'altitud': lote.altitud,
            'precipitacion_anual': lote.precipitacion_anual,
            'temperatura_promedio': lote.temperatura_promedio,
            'numero_arboles': lote.numero_arboles,
            'edad_arboles': lote.edad_arboles,
            'densidad_plantacion': lote.densidad_plantacion,
            'sistema_riego': lote.sistema_riego,
            'manejo_organico': lote.manejo_organico,
            'certificaciones': lote.certificaciones,
            'created_at': lote.created_at.isoformat(),
            'updated_at': lote.updated_at.isoformat(),
            'finca_id': lote.finca.id,
            'finca_nombre': lote.finca.nombre
        }
