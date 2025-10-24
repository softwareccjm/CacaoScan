"""
Servicio de reportes para CacaoScan.
Maneja la generación y gestión de reportes de análisis.
"""
import logging
import os
import uuid
from typing import Dict, Any, Optional, Tuple, List
from django.contrib.auth.models import User
from django.db import transaction
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .base import BaseService, ServiceError, ValidationServiceError, PermissionServiceError, NotFoundServiceError, PaginationService

logger = logging.getLogger("cacaoscan.services.reports")


class ReportService(BaseService):
    """
    Servicio para manejo de reportes de análisis.
    """
    
    def __init__(self):
        super().__init__()
    
    def generate_analysis_report(self, user: User, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera un reporte de análisis de granos de cacao.
        
        Args:
            user: Usuario que solicita el reporte
            report_data: Datos del reporte a generar
            
        Returns:
            Diccionario con información del reporte generado
            
        Raises:
            ValidationServiceError: Si los datos son inválidos
            ServiceError: Si hay error en la generación
        """
        try:
            # Validar campos requeridos
            required_fields = ['tipo_reporte', 'periodo_inicio', 'periodo_fin']
            self.validate_required_fields(report_data, required_fields)
            
            # Validar fechas
            try:
                fecha_inicio = datetime.fromisoformat(report_data['periodo_inicio'].replace('Z', '+00:00'))
                fecha_fin = datetime.fromisoformat(report_data['periodo_fin'].replace('Z', '+00:00'))
                
                if fecha_inicio >= fecha_fin:
                    raise ValidationServiceError("La fecha de inicio debe ser anterior a la fecha de fin", "invalid_date_range")
                
                # Verificar que el rango no sea muy amplio (máximo 1 año)
                if (fecha_fin - fecha_inicio).days > 365:
                    raise ValidationServiceError("El rango de fechas no puede ser mayor a 1 año", "date_range_too_large")
                    
            except ValueError:
                raise ValidationServiceError("Formato de fecha inválido", "invalid_date_format")
            
            with transaction.atomic():
                from ..models import Reporte
                
                # Generar nombre único para el archivo
                report_id = str(uuid.uuid4())
                filename = f"reporte_{report_data['tipo_reporte']}_{report_id}.pdf"
                
                # Crear objeto Reporte
                reporte = Reporte.objects.create(
                    usuario=user,
                    tipo_reporte=report_data['tipo_reporte'],
                    titulo=report_data.get('titulo', f"Reporte de {report_data['tipo_reporte']}"),
                    descripcion=report_data.get('descripcion', ''),
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    parametros=report_data.get('parametros', {}),
                    estado='generando',
                    archivo_path='',  # Se actualizará cuando se genere el archivo
                    metadata={'report_id': report_id}
                )
                
                # Generar contenido del reporte
                report_content = self._generate_report_content(user, reporte, report_data)
                
                # Guardar archivo del reporte
                file_path = self._save_report_file(reporte, report_content, filename)
                
                # Actualizar reporte con la ruta del archivo
                reporte.archivo_path = file_path
                reporte.estado = 'completado'
                reporte.save()
                
                # Enviar notificación por email
                self._send_report_notification(user, reporte)
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="report_generated",
                    resource_type="reporte",
                    resource_id=reporte.id,
                    details={
                        'tipo_reporte': reporte.tipo_reporte,
                        'fecha_inicio': fecha_inicio.isoformat(),
                        'fecha_fin': fecha_fin.isoformat(),
                        'archivo_path': file_path
                    }
                )
                
                self.log_info(f"Reporte generado: {reporte.titulo}", user_id=user.id, reporte_id=reporte.id)
                
                return self._serialize_reporte(reporte)
                
        except ValidationServiceError:
            raise
        except Exception as e:
            self.log_error(f"Error generando reporte: {e}")
            raise ServiceError("Error interno generando reporte", "generation_error")
    
    def _generate_report_content(self, user: User, reporte, report_data: Dict[str, Any]) -> bytes:
        """
        Genera el contenido del reporte en formato PDF.
        
        Args:
            user: Usuario del reporte
            reporte: Objeto Reporte
            report_data: Datos del reporte
            
        Returns:
            Contenido del reporte en bytes
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            import io
            
            # Crear buffer para el PDF
            buffer = io.BytesIO()
            
            # Crear documento PDF
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            
            # Obtener estilos
            styles = getSampleStyleSheet()
            
            # Crear estilos personalizados
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkblue
            )
            
            # Obtener datos del reporte
            report_data_content = self._get_report_data(user, reporte, report_data)
            
            # Construir contenido del PDF
            story = []
            
            # Título
            story.append(Paragraph("CacaoScan - Reporte de Análisis", title_style))
            story.append(Spacer(1, 12))
            
            # Información del reporte
            story.append(Paragraph(f"<b>Título:</b> {reporte.titulo}", styles['Normal']))
            story.append(Paragraph(f"<b>Tipo:</b> {reporte.tipo_reporte}", styles['Normal']))
            story.append(Paragraph(f"<b>Período:</b> {reporte.fecha_inicio.strftime('%d/%m/%Y')} - {reporte.fecha_fin.strftime('%d/%m/%Y')}", styles['Normal']))
            story.append(Paragraph(f"<b>Generado por:</b> {user.get_full_name() or user.username}", styles['Normal']))
            story.append(Paragraph(f"<b>Fecha de generación:</b> {timezone.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Resumen ejecutivo
            story.append(Paragraph("Resumen Ejecutivo", heading_style))
            story.append(Paragraph(report_data_content.get('resumen_ejecutivo', 'No hay datos disponibles para el período seleccionado.'), styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Estadísticas generales
            if 'estadisticas_generales' in report_data_content:
                story.append(Paragraph("Estadísticas Generales", heading_style))
                
                stats_data = report_data_content['estadisticas_generales']
                stats_table_data = [
                    ['Métrica', 'Valor'],
                    ['Total de Análisis', str(stats_data.get('total_analisis', 0))],
                    ['Promedio de Confianza', f"{stats_data.get('promedio_confianza', 0):.1%}"],
                    ['Tiempo Promedio de Procesamiento', f"{stats_data.get('tiempo_promedio_ms', 0):.0f} ms"],
                    ['Análisis de Alta Calidad', str(stats_data.get('analisis_alta_calidad', 0))],
                    ['Análisis de Calidad Media', str(stats_data.get('analisis_calidad_media', 0))],
                    ['Análisis de Baja Calidad', str(stats_data.get('analisis_baja_calidad', 0))]
                ]
                
                stats_table = Table(stats_table_data, colWidths=[2*inch, 1.5*inch])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(stats_table)
                story.append(Spacer(1, 20))
            
            # Análisis de dimensiones
            if 'analisis_dimensiones' in report_data_content:
                story.append(Paragraph("Análisis de Dimensiones", heading_style))
                
                dims_data = report_data_content['analisis_dimensiones']
                dims_table_data = [
                    ['Dimensión', 'Promedio (mm)', 'Mínimo (mm)', 'Máximo (mm)', 'Desviación Estándar'],
                    ['Alto', f"{dims_data.get('alto_promedio', 0):.2f}", f"{dims_data.get('alto_minimo', 0):.2f}", f"{dims_data.get('alto_maximo', 0):.2f}", f"{dims_data.get('alto_desviacion', 0):.2f}"],
                    ['Ancho', f"{dims_data.get('ancho_promedio', 0):.2f}", f"{dims_data.get('ancho_minimo', 0):.2f}", f"{dims_data.get('ancho_maximo', 0):.2f}", f"{dims_data.get('ancho_desviacion', 0):.2f}"],
                    ['Grosor', f"{dims_data.get('grosor_promedio', 0):.2f}", f"{dims_data.get('grosor_minimo', 0):.2f}", f"{dims_data.get('grosor_maximo', 0):.2f}", f"{dims_data.get('grosor_desviacion', 0):.2f}"],
                    ['Peso', f"{dims_data.get('peso_promedio', 0):.2f}g", f"{dims_data.get('peso_minimo', 0):.2f}g", f"{dims_data.get('peso_maximo', 0):.2f}g", f"{dims_data.get('peso_desviacion', 0):.2f}g"]
                ]
                
                dims_table = Table(dims_table_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
                dims_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(dims_table)
                story.append(Spacer(1, 20))
            
            # Recomendaciones
            if 'recomendaciones' in report_data_content:
                story.append(Paragraph("Recomendaciones", heading_style))
                for i, recomendacion in enumerate(report_data_content['recomendaciones'], 1):
                    story.append(Paragraph(f"{i}. {recomendacion}", styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Pie de página
            story.append(Spacer(1, 30))
            story.append(Paragraph(f"Reporte generado el {timezone.now().strftime('%d/%m/%Y a las %H:%M')} por CacaoScan", 
                                 ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)))
            
            # Construir PDF
            doc.build(story)
            
            # Obtener contenido del buffer
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except Exception as e:
            self.log_error(f"Error generando contenido del reporte: {e}")
            raise ServiceError("Error interno generando contenido", "content_generation_error")
    
    def _get_report_data(self, user: User, reporte, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtiene los datos necesarios para generar el reporte.
        
        Args:
            user: Usuario del reporte
            reporte: Objeto Reporte
            report_data: Datos del reporte
            
        Returns:
            Diccionario con datos del reporte
        """
        try:
            from ..models import CacaoPrediction
            
            # Construir queryset de predicciones
            queryset = CacaoPrediction.objects.filter(
                user=user,
                created_at__gte=reporte.fecha_inicio,
                created_at__lte=reporte.fecha_fin
            )
            
            # Estadísticas generales
            total_analisis = queryset.count()
            if total_analisis == 0:
                return {
                    'resumen_ejecutivo': 'No se encontraron análisis en el período seleccionado.',
                    'estadisticas_generales': {},
                    'analisis_dimensiones': {},
                    'recomendaciones': ['No hay datos suficientes para generar recomendaciones.']
                }
            
            # Calcular estadísticas
            stats = queryset.aggregate(
                promedio_confianza=Avg('average_confidence'),
                tiempo_promedio_ms=Avg('processing_time_ms'),
                alto_promedio=Avg('alto_mm'),
                alto_minimo=Min('alto_mm'),
                alto_maximo=Max('alto_mm'),
                ancho_promedio=Avg('ancho_mm'),
                ancho_minimo=Min('ancho_mm'),
                ancho_maximo=Max('ancho_mm'),
                grosor_promedio=Avg('grosor_mm'),
                grosor_minimo=Min('grosor_mm'),
                grosor_maximo=Max('grosor_mm'),
                peso_promedio=Avg('peso_g'),
                peso_minimo=Min('peso_g'),
                peso_maximo=Max('peso_g')
            )
            
            # Contar por calidad
            analisis_alta_calidad = queryset.filter(average_confidence__gte=0.8).count()
            analisis_calidad_media = queryset.filter(average_confidence__gte=0.6, average_confidence__lt=0.8).count()
            analisis_baja_calidad = queryset.filter(average_confidence__lt=0.6).count()
            
            # Generar resumen ejecutivo
            resumen_ejecutivo = f"""
            Durante el período de {reporte.fecha_inicio.strftime('%d/%m/%Y')} a {reporte.fecha_fin.strftime('%d/%m/%Y')}, 
            se realizaron {total_analisis} análisis de granos de cacao. El promedio de confianza fue del 
            {stats['promedio_confianza']:.1%}, con {analisis_alta_calidad} análisis de alta calidad, 
            {analisis_calidad_media} de calidad media y {analisis_baja_calidad} de baja calidad.
            """
            
            # Generar recomendaciones
            recomendaciones = []
            if analisis_baja_calidad > total_analisis * 0.3:
                recomendaciones.append("Se recomienda mejorar las condiciones de captura de imágenes para reducir el porcentaje de análisis de baja calidad.")
            
            if stats['promedio_confianza'] < 0.7:
                recomendaciones.append("Considerar recalibrar los modelos de análisis para mejorar la precisión general.")
            
            if stats['tiempo_promedio_ms'] > 5000:
                recomendaciones.append("El tiempo de procesamiento es elevado. Se sugiere optimizar el sistema de análisis.")
            
            if not recomendaciones:
                recomendaciones.append("Los análisis muestran buenos resultados. Mantener las condiciones actuales de procesamiento.")
            
            return {
                'resumen_ejecutivo': resumen_ejecutivo.strip(),
                'estadisticas_generales': {
                    'total_analisis': total_analisis,
                    'promedio_confianza': stats['promedio_confianza'] or 0,
                    'tiempo_promedio_ms': stats['tiempo_promedio_ms'] or 0,
                    'analisis_alta_calidad': analisis_alta_calidad,
                    'analisis_calidad_media': analisis_calidad_media,
                    'analisis_baja_calidad': analisis_baja_calidad
                },
                'analisis_dimensiones': {
                    'alto_promedio': stats['alto_promedio'] or 0,
                    'alto_minimo': stats['alto_minimo'] or 0,
                    'alto_maximo': stats['alto_maximo'] or 0,
                    'alto_desviacion': 0,  # TODO: Calcular desviación estándar
                    'ancho_promedio': stats['ancho_promedio'] or 0,
                    'ancho_minimo': stats['ancho_minimo'] or 0,
                    'ancho_maximo': stats['ancho_maximo'] or 0,
                    'ancho_desviacion': 0,
                    'grosor_promedio': stats['grosor_promedio'] or 0,
                    'grosor_minimo': stats['grosor_minimo'] or 0,
                    'grosor_maximo': stats['grosor_maximo'] or 0,
                    'grosor_desviacion': 0,
                    'peso_promedio': stats['peso_promedio'] or 0,
                    'peso_minimo': stats['peso_minimo'] or 0,
                    'peso_maximo': stats['peso_maximo'] or 0,
                    'peso_desviacion': 0
                },
                'recomendaciones': recomendaciones
            }
            
        except Exception as e:
            self.log_error(f"Error obteniendo datos del reporte: {e}")
            raise ServiceError("Error interno obteniendo datos", "data_error")
    
    def _save_report_file(self, reporte, content: bytes, filename: str) -> str:
        """
        Guarda el archivo del reporte en el sistema de archivos.
        
        Args:
            reporte: Objeto Reporte
            content: Contenido del archivo
            filename: Nombre del archivo
            
        Returns:
            Ruta del archivo guardado
        """
        try:
            from django.core.files.storage import default_storage
            
            # Crear directorio de reportes si no existe
            reports_dir = 'media/reportes'
            os.makedirs(reports_dir, exist_ok=True)
            
            # Ruta completa del archivo
            file_path = f"{reports_dir}/{filename}"
            
            # Guardar archivo
            default_storage.save(file_path, ContentFile(content))
            
            return file_path
            
        except Exception as e:
            self.log_error(f"Error guardando archivo del reporte: {e}")
            raise ServiceError("Error interno guardando archivo", "file_save_error")
    
    def _send_report_notification(self, user: User, reporte) -> None:
        """
        Envía notificación por email del reporte generado.
        
        Args:
            user: Usuario destinatario
            reporte: Objeto Reporte
        """
        try:
            email_context = {
                'report_type': reporte.tipo_reporte,
                'period_start': reporte.fecha_inicio.strftime('%d/%m/%Y'),
                'period_end': reporte.fecha_fin.strftime('%d/%m/%Y'),
                'generation_date': reporte.created_at.strftime('%d/%m/%Y %H:%M'),
                'file_size': f"{len(reporte.archivo_path)} bytes",  # TODO: Calcular tamaño real
                'file_format': 'PDF',
                'download_url': f"/api/v1/reportes/{reporte.id}/download/",
                'download_expiry_days': 7,
                'report_id': str(reporte.id),
                'summary_stats': [],  # TODO: Agregar estadísticas resumidas
                'report_sections': [
                    'Resumen Ejecutivo',
                    'Estadísticas Generales',
                    'Análisis de Dimensiones',
                    'Recomendaciones'
                ],
                'recommendations': ['Mantener las condiciones actuales de procesamiento.']
            }
            
            email_result = self.send_email_notification(
                user=user,
                notification_type='report_ready',
                context=email_context
            )
            
            if email_result['success']:
                self.log_info(f"Email de reporte enviado a {user.email}", user_id=user.id)
            else:
                self.log_warning(f"Error enviando email de reporte: {email_result.get('error')}", user_id=user.id)
                
        except Exception as e:
            self.log_error(f"Error enviando notificación de reporte: {e}")
    
    def get_user_reports(self, user: User, page: int = 1, page_size: int = 20, 
                        filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Obtiene los reportes de un usuario con paginación.
        
        Args:
            user: Usuario del cual obtener reportes
            page: Número de página
            page_size: Tamaño de página
            filters: Filtros adicionales
            
        Returns:
            Diccionario con reportes paginados
        """
        try:
            from ..models import Reporte
            
            # Construir queryset base
            if user.is_superuser:
                # Administradores ven todos los reportes
                queryset = Reporte.objects.all().select_related('usuario')
            else:
                # Usuarios normales solo ven sus reportes
                queryset = Reporte.objects.filter(usuario=user)
            
            # Aplicar filtros
            if filters:
                if 'tipo_reporte' in filters:
                    queryset = queryset.filter(tipo_reporte=filters['tipo_reporte'])
                if 'estado' in filters:
                    queryset = queryset.filter(estado=filters['estado'])
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            # Ordenar por fecha de creación descendente
            queryset = queryset.order_by('-created_at')
            
            # Paginar resultados
            paginated_data = PaginationService.paginate_queryset(queryset, page, page_size)
            
            # Serializar resultados
            results = []
            for reporte in paginated_data['results']:
                results.append(self._serialize_reporte(reporte))
            
            return {
                'results': results,
                'pagination': paginated_data['pagination']
            }
            
        except Exception as e:
            self.log_error(f"Error obteniendo reportes: {e}")
            raise ServiceError("Error interno obteniendo reportes", "list_error")
    
    def get_report_detail(self, user: User, report_id: int) -> Dict[str, Any]:
        """
        Obtiene los detalles de un reporte específico.
        
        Args:
            user: Usuario que solicita los detalles
            report_id: ID del reporte
            
        Returns:
            Diccionario con detalles del reporte
            
        Raises:
            NotFoundServiceError: Si el reporte no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import Reporte
            
            # Obtener reporte
            try:
                reporte = Reporte.objects.select_related('usuario').get(id=report_id)
            except Reporte.DoesNotExist:
                raise NotFoundServiceError(f"Reporte con ID {report_id} no encontrado", "report_not_found")
            
            # Verificar permisos
            if reporte.usuario != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para ver este reporte", "no_permission")
            
            return self._serialize_reporte(reporte)
            
        except (NotFoundServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error obteniendo detalles de reporte: {e}")
            raise ServiceError("Error interno obteniendo detalles", "detail_error")
    
    def download_report(self, user: User, report_id: int) -> Tuple[bytes, str, str]:
        """
        Descarga un reporte específico.
        
        Args:
            user: Usuario que solicita la descarga
            report_id: ID del reporte
            
        Returns:
            Tupla con (contenido_archivo, nombre_archivo, tipo_mime)
            
        Raises:
            NotFoundServiceError: Si el reporte no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import Reporte
            from django.core.files.storage import default_storage
            
            # Obtener reporte
            try:
                reporte = Reporte.objects.get(id=report_id)
            except Reporte.DoesNotExist:
                raise NotFoundServiceError(f"Reporte con ID {report_id} no encontrado", "report_not_found")
            
            # Verificar permisos
            if reporte.usuario != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para descargar este reporte", "no_permission")
            
            # Verificar que el reporte esté completado
            if reporte.estado != 'completado':
                raise ValidationServiceError("El reporte aún no está listo para descarga", "report_not_ready")
            
            # Leer contenido del archivo
            if not reporte.archivo_path:
                raise NotFoundServiceError("Archivo de reporte no encontrado", "file_not_found")
            
            try:
                file_content = default_storage.open(reporte.archivo_path).read()
            except Exception as e:
                raise NotFoundServiceError(f"Error leyendo archivo: {str(e)}", "file_read_error")
            
            # Generar nombre de archivo para descarga
            filename = f"reporte_{reporte.tipo_reporte}_{reporte.created_at.strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="report_downloaded",
                resource_type="reporte",
                resource_id=report_id
            )
            
            self.log_info(f"Reporte descargado: {report_id}", user_id=user.id)
            
            return file_content, filename, 'application/pdf'
            
        except (NotFoundServiceError, PermissionServiceError, ValidationServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error descargando reporte: {e}")
            raise ServiceError("Error interno descargando reporte", "download_error")
    
    def delete_report(self, user: User, report_id: int) -> bool:
        """
        Elimina un reporte del sistema.
        
        Args:
            user: Usuario que solicita la eliminación
            report_id: ID del reporte
            
        Returns:
            True si se eliminó exitosamente
            
        Raises:
            NotFoundServiceError: Si el reporte no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import Reporte
            from django.core.files.storage import default_storage
            
            # Obtener reporte
            try:
                reporte = Reporte.objects.get(id=report_id)
            except Reporte.DoesNotExist:
                raise NotFoundServiceError(f"Reporte con ID {report_id} no encontrado", "report_not_found")
            
            # Verificar permisos
            if reporte.usuario != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para eliminar este reporte", "no_permission")
            
            with transaction.atomic():
                # Eliminar archivo físico si existe
                if reporte.archivo_path:
                    try:
                        default_storage.delete(reporte.archivo_path)
                    except Exception as e:
                        self.log_warning(f"Error eliminando archivo físico: {e}")
                
                # Eliminar reporte de BD
                reporte.delete()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="report_deleted",
                    resource_type="reporte",
                    resource_id=report_id
                )
                
                self.log_info(f"Reporte eliminado: {report_id}", user_id=user.id)
                
                return True
                
        except (NotFoundServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error eliminando reporte: {e}")
            raise ServiceError("Error interno eliminando reporte", "delete_error")
    
    def get_report_statistics(self, user: User) -> Dict[str, Any]:
        """
        Obtiene estadísticas de reportes de un usuario.
        
        Args:
            user: Usuario del cual obtener estadísticas
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            from ..models import Reporte
            from django.db.models import Count
            
            # Construir queryset base
            if user.is_superuser:
                queryset = Reporte.objects.all()
            else:
                queryset = Reporte.objects.filter(usuario=user)
            
            # Estadísticas básicas
            total_reports = queryset.count()
            completed_reports = queryset.filter(estado='completado').count()
            generating_reports = queryset.filter(estado='generando').count()
            failed_reports = queryset.filter(estado='error').count()
            
            # Estadísticas por tipo
            tipo_stats = queryset.values('tipo_reporte').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Estadísticas por mes (últimos 12 meses)
            from django.db.models.functions import TruncMonth
            monthly_stats = queryset.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')[:12]
            
            return {
                'total_reports': total_reports,
                'completed_reports': completed_reports,
                'generating_reports': generating_reports,
                'failed_reports': failed_reports,
                'success_rate': round((completed_reports / total_reports * 100) if total_reports > 0 else 0, 2),
                'tipo_distribution': list(tipo_stats),
                'monthly_distribution': list(monthly_stats)
            }
            
        except Exception as e:
            self.log_error(f"Error obteniendo estadísticas de reportes: {e}")
            raise ServiceError("Error interno obteniendo estadísticas", "stats_error")
    
    def cleanup_old_reports(self, user: User, days_old: int = 30) -> Dict[str, Any]:
        """
        Limpia reportes antiguos del sistema.
        
        Args:
            user: Usuario que solicita la limpieza
            days_old: Días de antigüedad para considerar reportes como antiguos
            
        Returns:
            Diccionario con resultados de la limpieza
            
        Raises:
            PermissionServiceError: Si el usuario no es administrador
        """
        try:
            # Solo administradores pueden limpiar reportes
            if not user.is_superuser:
                raise PermissionServiceError("Solo administradores pueden limpiar reportes", "admin_required")
            
            from ..models import Reporte
            from django.core.files.storage import default_storage
            from django.utils import timezone
            
            # Calcular fecha límite
            cutoff_date = timezone.now() - timedelta(days=days_old)
            
            # Obtener reportes antiguos
            old_reports = Reporte.objects.filter(
                created_at__lt=cutoff_date,
                estado='completado'
            )
            
            deleted_count = 0
            errors = []
            
            for reporte in old_reports:
                try:
                    # Eliminar archivo físico si existe
                    if reporte.archivo_path:
                        try:
                            default_storage.delete(reporte.archivo_path)
                        except Exception as e:
                            self.log_warning(f"Error eliminando archivo físico: {e}")
                    
                    # Eliminar reporte de BD
                    reporte.delete()
                    deleted_count += 1
                    
                except Exception as e:
                    errors.append({'id': reporte.id, 'error': str(e)})
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="reports_cleanup",
                resource_type="system",
                details={
                    'days_old': days_old,
                    'deleted_count': deleted_count,
                    'errors_count': len(errors)
                }
            )
            
            self.log_info(f"Limpieza de reportes completada: {deleted_count} eliminados", user_id=user.id)
            
            return {
                'total_old_reports': old_reports.count(),
                'deleted_count': deleted_count,
                'errors': errors,
                'success_rate': round((deleted_count / old_reports.count()) * 100) if old_reports.count() > 0 else 100
            }
            
        except PermissionServiceError:
            raise
        except Exception as e:
            self.log_error(f"Error en limpieza de reportes: {e}")
            raise ServiceError("Error interno en limpieza", "cleanup_error")
    
    def _serialize_reporte(self, reporte) -> Dict[str, Any]:
        """
        Serializa un reporte a diccionario.
        
        Args:
            reporte: Objeto Reporte
            
        Returns:
            Diccionario serializado
        """
        return {
            'id': reporte.id,
            'tipo_reporte': reporte.tipo_reporte,
            'titulo': reporte.titulo,
            'descripcion': reporte.descripcion,
            'fecha_inicio': reporte.fecha_inicio.isoformat(),
            'fecha_fin': reporte.fecha_fin.isoformat(),
            'parametros': reporte.parametros,
            'estado': reporte.estado,
            'archivo_path': reporte.archivo_path,
            'metadata': reporte.metadata,
            'created_at': reporte.created_at.isoformat(),
            'updated_at': reporte.updated_at.isoformat(),
            'usuario': {
                'id': reporte.usuario.id,
                'username': reporte.usuario.username,
                'email': reporte.usuario.email,
                'full_name': reporte.usuario.get_full_name()
            }
        }
