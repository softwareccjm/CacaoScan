"""
Servicios principales para CacaoScan.
Punto de entrada centralizado para todos los servicios de la aplicación.
"""
from .auth_service import AuthenticationService
from .analysis_service import AnalysisService
from .image_service import ImageService
from .fincas_service import FincaService, LoteService
from .report_service import ReportService
from .base import BaseService, ServiceError, ValidationServiceError, PermissionServiceError, NotFoundServiceError

# Instancias singleton de servicios
_auth_service = None
_analysis_service = None
_image_service = None
_finca_service = None
_lote_service = None
_report_service = None


def get_auth_service() -> AuthenticationService:
    """
    Obtiene la instancia singleton del servicio de autenticación.
    
    Returns:
        Instancia de AuthenticationService
    """
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthenticationService()
    return _auth_service


def get_analysis_service() -> AnalysisService:
    """
    Obtiene la instancia singleton del servicio de análisis.
    
    Returns:
        Instancia de AnalysisService
    """
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service


def get_image_service() -> ImageService:
    """
    Obtiene la instancia singleton del servicio de imágenes.
    
    Returns:
        Instancia de ImageService
    """
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service


def get_finca_service() -> FincaService:
    """
    Obtiene la instancia singleton del servicio de fincas.
    
    Returns:
        Instancia de FincaService
    """
    global _finca_service
    if _finca_service is None:
        _finca_service = FincaService()
    return _finca_service


def get_lote_service() -> LoteService:
    """
    Obtiene la instancia singleton del servicio de lotes.
    
    Returns:
        Instancia de LoteService
    """
    global _lote_service
    if _lote_service is None:
        _lote_service = LoteService()
    return _lote_service


def get_report_service() -> ReportService:
    """
    Obtiene la instancia singleton del servicio de reportes.
    
    Returns:
        Instancia de ReportService
    """
    global _report_service
    if _report_service is None:
        _report_service = ReportService()
    return _report_service


# Clase principal de servicios para facilitar el acceso
class Services:
    """
    Clase principal que proporciona acceso a todos los servicios.
    """
    
    @property
    def auth(self) -> AuthenticationService:
        """Servicio de autenticación."""
        return get_auth_service()
    
    @property
    def analysis(self) -> AnalysisService:
        """Servicio de análisis."""
        return get_analysis_service()
    
    @property
    def image(self) -> ImageService:
        """Servicio de imágenes."""
        return get_image_service()
    
    @property
    def finca(self) -> FincaService:
        """Servicio de fincas."""
        return get_finca_service()
    
    @property
    def lote(self) -> LoteService:
        """Servicio de lotes."""
        return get_lote_service()
    
    @property
    def report(self) -> ReportService:
        """Servicio de reportes."""
        return get_report_service()


# Instancia global de servicios
services = Services()


# Funciones de conveniencia para acceso directo
def auth_service() -> AuthenticationService:
    """Función de conveniencia para obtener el servicio de autenticación."""
    return services.auth


def analysis_service() -> AnalysisService:
    """Función de conveniencia para obtener el servicio de análisis."""
    return services.analysis


def image_service() -> ImageService:
    """Función de conveniencia para obtener el servicio de imágenes."""
    return services.image


def finca_service() -> FincaService:
    """Función de conveniencia para obtener el servicio de fincas."""
    return services.finca


def lote_service() -> LoteService:
    """Función de conveniencia para obtener el servicio de lotes."""
    return services.lote


def report_service() -> ReportService:
    """Función de conveniencia para obtener el servicio de reportes."""
    return services.report


# Exportar todas las clases y funciones principales
__all__ = [
    # Servicios principales
    'AuthenticationService',
    'AnalysisService', 
    'ImageService',
    'FincaService',
    'LoteService',
    'ReportService',
    
    # Clase de servicios
    'Services',
    'services',
    
    # Funciones de acceso
    'get_auth_service',
    'get_analysis_service',
    'get_image_service',
    'get_finca_service',
    'get_lote_service',
    'get_report_service',
    
    # Funciones de conveniencia
    'auth_service',
    'analysis_service',
    'image_service',
    'finca_service',
    'lote_service',
    'report_service',
    
    # Excepciones base
    'ServiceError',
    'ValidationServiceError',
    'PermissionServiceError',
    'NotFoundServiceError',
]
