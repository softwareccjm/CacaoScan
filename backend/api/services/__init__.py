"""
Servicios para CacaoScan API.
"""

# Importar clases base
from .base import (
    BaseService, 
    ServiceResult, 
    ServiceError, 
    ValidationServiceError, 
    PermissionServiceError, 
    NotFoundServiceError
)

# Importar servicios específicos
from .auth import LoginService, RegistrationService, PasswordService, VerificationService, ProfileService
from .analysis_service import AnalysisService
from .finca import FincaService
from .lote_service import LoteService
from .report import ReportService

# Importar servicios por dominio
from .ml.prediction_service import PredictionService
from .ml.ml_service import MLService
from .image.processing_service import ImageProcessingService
from .image.storage_service import ImageStorageService
from .image.management_service import ImageManagementService

# Crear instancias de servicios para uso fácil
login_service = LoginService()
registration_service = RegistrationService()
password_service = PasswordService()
verification_service = VerificationService()
profile_service = ProfileService()
analysis_service = AnalysisService()
image_service = ImageManagementService()
finca_service = FincaService()
lote_service = LoteService()
report_service = ReportService()

# Exportar todo
__all__ = [
    # Clases base
    'BaseService',
    'ServiceResult', 
    'ServiceError',
    'ValidationServiceError',
    'PermissionServiceError',
    'NotFoundServiceError',
    
    # Servicios específicos
    'LoginService',
    'RegistrationService',
    'PasswordService',
    'VerificationService',
    'ProfileService',
    'AnalysisService', 
    'ImageManagementService',
    'FincaService',
    'LoteService',
    'ReportService',
    
    # Servicios por dominio
    'PredictionService',
    'MLService',
    'ImageProcessingService',
    'ImageStorageService',
    
    # Instancias de servicios
    'login_service',
    'registration_service',
    'password_service',
    'verification_service',
    'profile_service',
    'analysis_service',
    'image_service', 
    'finca_service',
    'lote_service',
    'report_service'
]


