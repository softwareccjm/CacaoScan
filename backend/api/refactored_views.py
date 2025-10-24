"""
Vistas refactorizadas para CacaoScan usando servicios.
Estas vistas utilizan la capa de servicios para separar la lógica de negocio.
"""
import logging
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import login, logout
from django.contrib.auth.models import User

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    ScanMeasureResponseSerializer, 
    ErrorResponseSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
)
from .utils import create_error_response, create_success_response
from .services import (
    auth_service, analysis_service, image_service, 
    finca_service, lote_service, report_service,
    ValidationServiceError, PermissionServiceError, NotFoundServiceError, ServiceError
)

logger = logging.getLogger("cacaoscan.api")


class LoginView(APIView):
    """
    Endpoint para login de usuario.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Autentica un usuario y devuelve un token de acceso",
        operation_summary="Login de usuario",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login exitoso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': UserSerializer,
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Autentica un usuario y devuelve tokens JWT.
        """
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Usar servicio de autenticación
                user, tokens = auth_service().authenticate_user(
                    username_or_email=serializer.validated_data['username'],
                    password=serializer.validated_data['password']
                )
                
                # Login en la sesión
                login(request, user)
                
                return create_success_response(
                    message='Login exitoso',
                    data={
                        **tokens,
                        'user': UserSerializer(user).data
                    }
                )
                
            except ValidationServiceError as e:
                return create_error_response(
                    message=e.message,
                    error_type=e.error_code or 'invalid_credentials',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    details=e.details
                )
            except PermissionServiceError as e:
                return create_error_response(
                    message=e.message,
                    error_type=e.error_code or 'account_disabled',
                    status_code=status.HTTP_403_FORBIDDEN,
                    details=e.details
                )
            except ServiceError as e:
                return create_error_response(
                    message='Error interno en autenticación',
                    error_type=e.error_code or 'authentication_error',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details=e.details
                )
        
        return create_error_response(
            message='Credenciales inválidas',
            error_type='invalid_credentials',
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=serializer.errors
        )


class RegisterView(APIView):
    """
    Endpoint para registro de usuario.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Registra un nuevo usuario en el sistema",
        operation_summary="Registro de usuario",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Usuario creado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': UserSerializer,
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Registra un nuevo usuario y genera tokens JWT automáticamente.
        """
        # Crear una copia de los datos y eliminar el campo 'role' si viene del frontend
        data = request.data.copy()
        data.pop('role', None)  # Elimina si viene en la solicitud
        
        serializer = RegisterSerializer(data=data)
        
        if serializer.is_valid():
            try:
                # Usar servicio de registro
                user, tokens = auth_service().register_user(data)
                
                # Login en la sesión
                login(request, user)
                
                return create_success_response(
                    message='Usuario registrado exitosamente',
                    data={
                        **tokens,
                        'user': UserSerializer(user).data
                    },
                    status_code=status.HTTP_201_CREATED
                )
                
            except ValidationServiceError as e:
                return create_error_response(
                    message=e.message,
                    error_type=e.error_code or 'validation_error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details=e.details
                )
            except ServiceError as e:
                return create_error_response(
                    message='Error interno en registro',
                    error_type=e.error_code or 'registration_error',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details=e.details
                )
        
        return create_error_response(
            message='Error en los datos proporcionados',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
        )


class LogoutView(APIView):
    """
    Endpoint para logout de usuario.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Cierra la sesión del usuario actual",
        operation_summary="Logout de usuario",
        responses={
            200: openapi.Response(
                description="Logout exitoso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Cierra la sesión del usuario.
        """
        try:
            # Usar servicio de logout
            auth_service().logout_user(request.user)
            
            # Logout de la sesión
            logout(request)
            
            return create_success_response(
                message='Logout exitoso'
            )
            
        except ServiceError as e:
            return create_error_response(
                message='Error interno en logout',
                error_type=e.error_code or 'logout_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=e.details
            )


class UserProfileView(APIView):
    """
    Endpoint para obtener y actualizar el perfil del usuario.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene el perfil del usuario actual",
        operation_summary="Obtener perfil",
        responses={
            200: openapi.Response(
                description="Perfil del usuario",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': UserSerializer,
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def get(self, request):
        """
        Obtiene el perfil del usuario actual.
        """
        try:
            profile_data = auth_service().get_user_profile(request.user)
            
            return create_success_response(
                message='Perfil obtenido exitosamente',
                data=profile_data
            )
            
        except ServiceError as e:
            return create_error_response(
                message='Error interno obteniendo perfil',
                error_type=e.error_code or 'profile_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=e.details
            )
    
    @swagger_auto_schema(
        operation_description="Actualiza el perfil del usuario actual",
        operation_summary="Actualizar perfil",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'address': openapi.Schema(type=openapi.TYPE_STRING),
                'city': openapi.Schema(type=openapi.TYPE_STRING),
                'country': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description="Perfil actualizado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': UserSerializer,
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def put(self, request):
        """
        Actualiza el perfil del usuario actual.
        """
        try:
            updated_profile = auth_service().update_user_profile(
                user=request.user,
                profile_data=request.data
            )
            
            return create_success_response(
                message='Perfil actualizado exitosamente',
                data=updated_profile
            )
            
        except ValidationServiceError as e:
            return create_error_response(
                message=e.message,
                error_type=e.error_code or 'validation_error',
                status_code=status.HTTP_400_BAD_REQUEST,
                details=e.details
            )
        except ServiceError as e:
            return create_error_response(
                message='Error interno actualizando perfil',
                error_type=e.error_code or 'profile_update_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=e.details
            )


class RefreshTokenView(APIView):
    """
    Endpoint para refrescar tokens JWT.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Refresca un token de acceso usando un refresh token",
        operation_summary="Refrescar token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token")
            },
            required=['refresh']
        ),
        responses={
            200: openapi.Response(
                description="Token refrescado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Refresca un token de acceso.
        """
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return create_error_response(
                message='Refresh token requerido',
                error_type='missing_refresh_token',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tokens = auth_service().refresh_token(refresh_token)
            
            return create_success_response(
                message='Token refrescado exitosamente',
                data=tokens
            )
            
        except ValidationServiceError as e:
            return create_error_response(
                message=e.message,
                error_type=e.error_code or 'invalid_refresh_token',
                status_code=status.HTTP_401_UNAUTHORIZED,
                details=e.details
            )
        except ServiceError as e:
            return create_error_response(
                message='Error interno refrescando token',
                error_type=e.error_code or 'refresh_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=e.details
            )


class EmailVerificationView(APIView):
    """
    Endpoint para verificar email de usuario.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verifica el email de un usuario usando un token",
        operation_summary="Verificar email",
        request_body=EmailVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Email verificado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Verifica el email de un usuario.
        """
        serializer = EmailVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = auth_service().verify_email(serializer.validated_data['token'])
                
                return create_success_response(
                    message='Email verificado exitosamente',
                    data={'user_id': user.id, 'email': user.email}
                )
                
            except ValidationServiceError as e:
                return create_error_response(
                    message=e.message,
                    error_type=e.error_code or 'invalid_token',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details=e.details
                )
            except ServiceError as e:
                return create_error_response(
                    message='Error interno en verificación',
                    error_type=e.error_code or 'verification_error',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details=e.details
                )
        
        return create_error_response(
            message='Token requerido',
            error_type='missing_token',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
        )


class ResendVerificationView(APIView):
    """
    Endpoint para reenviar verificación de email.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Reenvía el token de verificación de email",
        operation_summary="Reenviar verificación",
        request_body=ResendVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Token reenviado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Reenvía el token de verificación de email.
        """
        serializer = ResendVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = auth_service().resend_verification(serializer.validated_data['email'])
                
                return create_success_response(
                    message='Token de verificación reenviado exitosamente',
                    data=result
                )
                
            except NotFoundServiceError as e:
                return create_error_response(
                    message=e.message,
                    error_type=e.error_code or 'user_not_found',
                    status_code=status.HTTP_404_NOT_FOUND,
                    details=e.details
                )
            except ValidationServiceError as e:
                return create_error_response(
                    message=e.message,
                    error_type=e.error_code or 'validation_error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details=e.details
                )
            except ServiceError as e:
                return create_error_response(
                    message='Error interno reenviando verificación',
                    error_type=e.error_code or 'resend_error',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details=e.details
                )
        
        return create_error_response(
            message='Email requerido',
            error_type='missing_email',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
        )


class ForgotPasswordView(APIView):
    """
    Endpoint para solicitar restablecimiento de contraseña.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Solicita restablecimiento de contraseña",
        operation_summary="Solicitar restablecimiento",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email del usuario")
            },
            required=['email']
        ),
        responses={
            200: openapi.Response(
                description="Instrucciones enviadas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Solicita restablecimiento de contraseña.
        """
        email = request.data.get('email')
        
        if not email:
            return create_error_response(
                message='Email requerido',
                error_type='missing_email',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = auth_service().request_password_reset(email)
            
            return create_success_response(
                message='Si el email existe, recibirás instrucciones de restablecimiento',
                data=result
            )
            
        except ValidationServiceError as e:
            return create_error_response(
                message=e.message,
                error_type=e.error_code or 'invalid_email',
                status_code=status.HTTP_400_BAD_REQUEST,
                details=e.details
            )
        except ServiceError as e:
            return create_error_response(
                message='Error interno en restablecimiento',
                error_type=e.error_code or 'reset_request_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=e.details
            )


class ResetPasswordView(APIView):
    """
    Endpoint para restablecer contraseña usando token.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Restablece la contraseña usando un token",
        operation_summary="Restablecer contraseña",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description="Token de restablecimiento"),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="Nueva contraseña"),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description="Confirmación de contraseña")
            },
            required=['token', 'new_password', 'confirm_password']
        ),
        responses={
            200: openapi.Response(
                description="Contraseña restablecida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Restablece la contraseña usando un token.
        """
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([token, new_password, confirm_password]):
            return create_error_response(
                message='Token, nueva contraseña y confirmación requeridos',
                error_type='missing_fields',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = auth_service().reset_password(token, new_password, confirm_password)
            
            return create_success_response(
                message='Contraseña restablecida exitosamente',
                data={'user_id': user.id, 'username': user.username}
            )
            
        except ValidationServiceError as e:
            return create_error_response(
                message=e.message,
                error_type=e.error_code or 'validation_error',
                status_code=status.HTTP_400_BAD_REQUEST,
                details=e.details
            )
        except ServiceError as e:
            return create_error_response(
                message='Error interno en restablecimiento',
                error_type=e.error_code or 'reset_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=e.details
            )


class ScanMeasureView(APIView):
    """
    Endpoint para medición de granos de cacao.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    @swagger_auto_schema(
        operation_description="Procesa una imagen de grano de cacao y devuelve predicciones de dimensiones y peso",
        operation_summary="Medir grano de cacao",
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="Imagen del grano de cacao (JPG, PNG, BMP)",
                type=openapi.TYPE_FILE,
                required=True
            ),
        ],
        responses={
            200: ScanMeasureResponseSerializer,
            400: ErrorResponseSerializer,
            413: ErrorResponseSerializer,
            503: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['Medición']
    )
    def post(self, request):
        """
        Procesa una imagen y devuelve mediciones del grano.
        
        Request:
            - multipart/form-data con campo 'image' (jpg/png/bmp)
            - Límite de tamaño: 8MB
        
        Response:
            - JSON con predicciones de dimensiones y peso
        """
        try:
            # Validar request
            if 'image' not in request.FILES:
                return create_error_response(
                    message='Campo "image" requerido',
                    error_type='missing_image',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            image_file = request.FILES['image']
            
            # Obtener metadatos adicionales si existen
            metadata = {}
            if 'metadata' in request.data:
                try:
                    import json
                    metadata = json.loads(request.data['metadata'])
                except:
                    pass
            
            # Usar servicio de análisis
            result = analysis_service().process_image_analysis(
                user=request.user,
                image_file=image_file,
                metadata=metadata
            )
            
            return create_success_response(
                message='Análisis completado exitosamente',
                data=result
            )
            
        except ValidationServiceError as e:
            return create_error_response(
                message=e.message,
                error_type=e.error_code or 'validation_error',
                status_code=status.HTTP_400_BAD_REQUEST,
                details=e.details
            )
        except ServiceError as e:
            if e.error_code == 'models_not_available':
                return create_error_response(
                    message='Modelos no disponibles. Ejecutar inicialización automática primero.',
                    error_type='models_not_available',
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    details={'suggestion': 'POST /api/v1/auto-initialize/ para inicializar el sistema'}
                )
            else:
                return create_error_response(
                    message='Error interno en análisis',
                    error_type=e.error_code or 'analysis_error',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details=e.details
                )
        except Exception as e:
            logger.error(f"Error inesperado en ScanMeasureView: {e}")
            return create_error_response(
                message='Error interno del servidor',
                error_type='internal_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
