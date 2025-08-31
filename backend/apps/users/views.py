"""
Vistas para autenticación y gestión de usuarios en CacaoScan.

Incluye endpoints para registro, login, perfil de usuario
y operaciones de autenticación JWT.
"""

import logging
from django.contrib.auth import login
from django.db import transaction
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User, UserProfile
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

# Configurar logging
logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para obtener tokens JWT.
    
    Extiende la vista base para usar nuestro serializer personalizado
    que incluye información adicional del usuario.
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(APIView):
    """
    Vista para registro de nuevos usuarios.
    
    Permite que usuarios nuevos se registren en el sistema
    con validación completa y creación de perfil.
    """
    
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Registrar nuevo usuario en el sistema",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response("Usuario registrado exitosamente"),
            400: openapi.Response("Error de validación")
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """Registra un nuevo usuario."""
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    # Crear usuario
                    user = serializer.save()
                    
                    # Log del registro
                    logger.info(f"Usuario registrado: {user.email} ({user.role})")
                    
                    # Generar tokens JWT
                    refresh = RefreshToken.for_user(user)
                    access = refresh.access_token
                    
                    # Preparar respuesta
                    user_serializer = UserDetailSerializer(user)
                    
                    return Response({
                        'success': True,
                        'message': 'Usuario registrado exitosamente',
                        'user': user_serializer.data,
                        'tokens': {
                            'access': str(access),
                            'refresh': str(refresh),
                        }
                    }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error en registro de usuario: {e}")
            return Response({
                'success': False,
                'error': 'Error interno del servidor',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    """
    Vista para login de usuarios.
    
    Permite autenticación con email o username y contraseña,
    retornando tokens JWT y información del usuario.
    """
    
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Iniciar sesión con email/username y contraseña",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response("Login exitoso"),
            400: openapi.Response("Credenciales inválidas")
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """Autentica usuario y retorna tokens."""
        try:
            serializer = UserLoginSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                user = serializer.validated_data['user']
                
                # Actualizar last_login
                login(request, user)
                
                # Log del login
                logger.info(f"Usuario logueado: {user.email}")
                
                # Generar tokens JWT
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token
                
                # Preparar respuesta
                user_serializer = UserDetailSerializer(user)
                
                return Response({
                    'success': True,
                    'message': 'Login exitoso',
                    'user': user_serializer.data,
                    'tokens': {
                        'access': str(access),
                        'refresh': str(refresh),
                    }
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return Response({
                'success': False,
                'error': 'Error interno del servidor',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(ModelViewSet):
    """
    ViewSet para gestión completa de usuarios.
    
    Proporciona endpoints para CRUD de usuarios y operaciones
    relacionadas como cambio de contraseña y gestión de perfil.
    """
    
    queryset = User.objects.select_related('profile').all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Selecciona el serializer apropiado según la acción."""
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserDetailSerializer
    
    def get_queryset(self):
        """Filtra usuarios según permisos."""
        user = self.request.user
        
        # Administradores pueden ver todos los usuarios
        if user.is_admin_user:
            return self.queryset
        
        # Usuarios normales solo pueden ver su propio perfil
        return self.queryset.filter(id=user.id)
    
    @action(detail=False, methods=['get'], url_path='me')
    def current_user(self, request):
        """Retorna información del usuario autenticado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'], url_path='me/update')
    def update_current_user(self, request):
        """Actualiza información del usuario autenticado."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            user = serializer.save()
            response_serializer = UserDetailSerializer(user)
            
            logger.info(f"Usuario actualizado: {user.email}")
            
            return Response({
                'success': True,
                'message': 'Perfil actualizado exitosamente',
                'user': response_serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """Cambia la contraseña del usuario autenticado."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            logger.info(f"Contraseña cambiada: {request.user.email}")
            
            return Response({
                'success': True,
                'message': 'Contraseña cambiada exitosamente'
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)