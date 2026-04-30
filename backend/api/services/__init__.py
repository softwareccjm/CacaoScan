"""
Servicios para CacaoScan API.

Solo se exportan aqui los servicios definidos dentro de api.services.
Los servicios cross-app (fincas, reports, images, training) deben
importarse directamente desde su modulo de origen para evitar ciclos.
"""

from .base import (
    BaseService,
    ServiceResult,
    ServiceError,
    ValidationServiceError,
    PermissionServiceError,
    NotFoundServiceError,
)

from .auth import (
    LoginService,
    RegistrationService,
    PasswordService,
    VerificationService,
    ProfileService,
)
from .analysis_service import AnalysisService


login_service = LoginService()
registration_service = RegistrationService()
password_service = PasswordService()
verification_service = VerificationService()
profile_service = ProfileService()
# analysis_service se crea lazy para evitar imports circulares.
analysis_service = None


__all__ = [
    'BaseService',
    'ServiceResult',
    'ServiceError',
    'ValidationServiceError',
    'PermissionServiceError',
    'NotFoundServiceError',
    'LoginService',
    'RegistrationService',
    'PasswordService',
    'VerificationService',
    'ProfileService',
    'AnalysisService',
    'login_service',
    'registration_service',
    'password_service',
    'verification_service',
    'profile_service',
    'analysis_service',
]


def __getattr__(name: str):
    """Lazy creation de analysis_service para evitar import circular."""
    global analysis_service
    if name == 'analysis_service':
        if analysis_service is None:
            analysis_service = AnalysisService()
        return analysis_service
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
