"""
Servicio de autenticación para CacaoScan.
Maneja login, registro, verificación de email y recuperación de contraseña.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta

from .base import BaseService, ServiceError, ValidationServiceError, PermissionServiceError, NotFoundServiceError

logger = logging.getLogger("cacaoscan.services.auth")


class AuthenticationService(BaseService):
    """
    Servicio para manejo de autenticación de usuarios.
    """
    
    def __init__(self):
        super().__init__()
    
    def authenticate_user(self, username_or_email: str, password: str) -> Tuple[User, Dict[str, Any]]:
        """
        Autentica un usuario con username/email y contraseña.
        
        Args:
            username_or_email: Username o email del usuario
            password: Contraseña del usuario
            
        Returns:
            Tupla con (usuario, tokens)
            
        Raises:
            ValidationServiceError: Si las credenciales son inválidas
            PermissionServiceError: Si el usuario no está activo
        """
        try:
            # Intentar autenticar con username o email
            user = authenticate(username=username_or_email, password=password)
            
            if not user:
                # Intentar con email si no funcionó con username
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                raise ValidationServiceError("Credenciales inválidas", "invalid_credentials")
            
            if not user.is_active:
                raise PermissionServiceError("Cuenta desactivada", "account_disabled")
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            tokens = {
                'access': str(access_token),
                'refresh': str(refresh),
                'access_expires_at': access_token['exp'],
                'refresh_expires_at': refresh['exp']
            }
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="login",
                resource_type="user",
                resource_id=user.id,
                details={'login_method': 'password'}
            )
            
            self.log_info(f"Usuario autenticado: {user.username}", user_id=user.id)
            
            return user, tokens
            
        except (ValidationServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error en autenticación: {e}")
            raise ServiceError("Error interno en autenticación", "authentication_error")
    
    def register_user(self, user_data: Dict[str, Any]) -> Tuple[User, Dict[str, Any]]:
        """
        Registra un nuevo usuario en el sistema.
        
        Args:
            user_data: Datos del usuario a registrar
            
        Returns:
            Tupla con (usuario, tokens)
            
        Raises:
            ValidationServiceError: Si los datos son inválidos
            ServiceError: Si el usuario ya existe
        """
        try:
            # Validar campos requeridos
            required_fields = ['username', 'email', 'password', 'password_confirm']
            self.validate_required_fields(user_data, required_fields)
            
            # Validar email
            self.validate_email(user_data['email'])
            
            # Validar contraseñas
            if user_data['password'] != user_data['password_confirm']:
                raise ValidationServiceError("Las contraseñas no coinciden", "password_mismatch")
            
            if len(user_data['password']) < 8:
                raise ValidationServiceError("La contraseña debe tener al menos 8 caracteres", "password_too_short")
            
            # Verificar si el usuario ya existe
            if User.objects.filter(username=user_data['username']).exists():
                raise ValidationServiceError("El nombre de usuario ya está en uso", "username_exists")
            
            if User.objects.filter(email=user_data['email']).exists():
                raise ValidationServiceError("El email ya está registrado", "email_exists")
            
            with transaction.atomic():
                # Crear usuario
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    is_active=True
                )
                
                # Crear token de verificación de email
                from ..models import EmailVerificationToken
                verification_token = EmailVerificationToken.create_for_user(user)
                
                # Generar tokens JWT
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                tokens = {
                    'access': str(access_token),
                    'refresh': str(refresh),
                    'access_expires_at': access_token['exp'],
                    'refresh_expires_at': refresh['exp'],
                    'verification_token': str(verification_token.token),
                    'verification_required': True
                }
                
                # Enviar email de bienvenida
                try:
                    email_context = {
                        'verification_token': str(verification_token.token),
                        'verification_url': f"/auth/verify-email/?token={verification_token.token}"
                    }
                    self.send_email_notification(
                        user=user,
                        notification_type='welcome',
                        context=email_context
                    )
                except Exception as e:
                    self.log_warning(f"Error enviando email de bienvenida: {e}")
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="register",
                    resource_type="user",
                    resource_id=user.id,
                    details={'email': user.email}
                )
                
                self.log_info(f"Usuario registrado: {user.username}", user_id=user.id)
                
                return user, tokens
                
        except (ValidationServiceError, ServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error en registro: {e}")
            raise ServiceError("Error interno en registro", "registration_error")
    
    def verify_email(self, token: str) -> User:
        """
        Verifica el email de un usuario usando un token.
        
        Args:
            token: Token de verificación
            
        Returns:
            Usuario verificado
            
        Raises:
            ValidationServiceError: Si el token es inválido o expirado
        """
        try:
            from ..models import EmailVerificationToken
            
            token_obj = EmailVerificationToken.objects.filter(
                token=token,
                is_used=False,
                expires_at__gt=timezone.now()
            ).first()
            
            if not token_obj:
                raise ValidationServiceError("Token inválido o expirado", "invalid_token")
            
            with transaction.atomic():
                # Marcar token como usado
                token_obj.is_used = True
                token_obj.save()
                
                # Marcar usuario como verificado (si tienes campo is_verified)
                user = token_obj.user
                if hasattr(user, 'is_verified'):
                    user.is_verified = True
                    user.save()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="email_verified",
                    resource_type="user",
                    resource_id=user.id
                )
                
                self.log_info(f"Email verificado: {user.email}", user_id=user.id)
                
                return user
                
        except ValidationServiceError:
            raise
        except Exception as e:
            self.log_error(f"Error en verificación de email: {e}")
            raise ServiceError("Error interno en verificación", "verification_error")
    
    def resend_verification(self, email: str) -> Dict[str, Any]:
        """
        Reenvía el token de verificación de email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Información del token reenviado
            
        Raises:
            NotFoundServiceError: Si el usuario no existe
            ValidationServiceError: Si el email ya está verificado
        """
        try:
            self.validate_email(email)
            
            user = self.get_user_by_email(email)
            
            # Verificar si ya está verificado
            if hasattr(user, 'is_verified') and user.is_verified:
                raise ValidationServiceError("El email ya está verificado", "already_verified")
            
            # Crear nuevo token de verificación
            from ..models import EmailVerificationToken
            verification_token = EmailVerificationToken.create_for_user(user)
            
            # Enviar email de verificación
            try:
                email_context = {
                    'verification_token': str(verification_token.token),
                    'verification_url': f"/auth/verify-email/?token={verification_token.token}"
                }
                self.send_email_notification(
                    user=user,
                    notification_type='welcome',  # Reutilizar template de bienvenida
                    context=email_context
                )
            except Exception as e:
                self.log_warning(f"Error enviando email de verificación: {e}")
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="resend_verification",
                resource_type="user",
                resource_id=user.id
            )
            
            self.log_info(f"Token de verificación reenviado: {email}", user_id=user.id)
            
            return {
                'token': str(verification_token.token),
                'expires_at': verification_token.expires_at.isoformat()
            }
            
        except (NotFoundServiceError, ValidationServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error reenviando verificación: {e}")
            raise ServiceError("Error interno reenviando verificación", "resend_error")
    
    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Solicita restablecimiento de contraseña.
        
        Args:
            email: Email del usuario
            
        Returns:
            Información del token de restablecimiento
            
        Raises:
            ValidationServiceError: Si el email no es válido
        """
        try:
            self.validate_email(email)
            
            try:
                user = self.get_user_by_email(email)
                
                # Crear token de restablecimiento
                from ..models import EmailVerificationToken
                reset_token = EmailVerificationToken.create_for_user(user)
                
                # Enviar email de restablecimiento
                try:
                    email_context = {
                        'token': str(reset_token.token),
                        'reset_url': f"/auth/reset-password/?token={reset_token.token}",
                        'token_expiry_hours': 24
                    }
                    self.send_email_notification(
                        user=user,
                        notification_type='password_reset',
                        context=email_context
                    )
                except Exception as e:
                    self.log_warning(f"Error enviando email de restablecimiento: {e}")
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="password_reset_requested",
                    resource_type="user",
                    resource_id=user.id
                )
                
                self.log_info(f"Solicitud de restablecimiento: {email}", user_id=user.id)
                
                return {
                    'token': str(reset_token.token),
                    'expires_at': reset_token.expires_at.isoformat()
                }
                
            except NotFoundServiceError:
                # Por seguridad, no revelar si el email existe o no
                self.log_info(f"Solicitud de restablecimiento para email inexistente: {email}")
                return {'message': 'Si el email existe, recibirás instrucciones de restablecimiento'}
                
        except ValidationServiceError:
            raise
        except Exception as e:
            self.log_error(f"Error en solicitud de restablecimiento: {e}")
            raise ServiceError("Error interno en restablecimiento", "reset_request_error")
    
    def reset_password(self, token: str, new_password: str, confirm_password: str) -> User:
        """
        Restablece la contraseña de un usuario usando un token.
        
        Args:
            token: Token de restablecimiento
            new_password: Nueva contraseña
            confirm_password: Confirmación de contraseña
            
        Returns:
            Usuario con contraseña restablecida
            
        Raises:
            ValidationServiceError: Si los datos son inválidos
        """
        try:
            # Validar contraseñas
            if new_password != confirm_password:
                raise ValidationServiceError("Las contraseñas no coinciden", "password_mismatch")
            
            if len(new_password) < 8:
                raise ValidationServiceError("La contraseña debe tener al menos 8 caracteres", "password_too_short")
            
            from ..models import EmailVerificationToken
            
            token_obj = EmailVerificationToken.objects.filter(
                token=token,
                is_used=False,
                expires_at__gt=timezone.now()
            ).first()
            
            if not token_obj:
                raise ValidationServiceError("Token inválido o expirado", "invalid_token")
            
            with transaction.atomic():
                # Marcar token como usado
                token_obj.is_used = True
                token_obj.save()
                
                # Cambiar contraseña
                user = token_obj.user
                user.set_password(new_password)
                user.save()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="password_reset",
                    resource_type="user",
                    resource_id=user.id
                )
                
                self.log_info(f"Contraseña restablecida: {user.username}", user_id=user.id)
                
                return user
                
        except ValidationServiceError:
            raise
        except Exception as e:
            self.log_error(f"Error en restablecimiento de contraseña: {e}")
            raise ServiceError("Error interno en restablecimiento", "reset_error")
    
    def logout_user(self, user: User) -> None:
        """
        Cierra la sesión de un usuario.
        
        Args:
            user: Usuario a cerrar sesión
        """
        try:
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="logout",
                resource_type="user",
                resource_id=user.id
            )
            
            self.log_info(f"Usuario cerró sesión: {user.username}", user_id=user.id)
            
        except Exception as e:
            self.log_error(f"Error en logout: {e}")
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresca un token de acceso usando un refresh token.
        
        Args:
            refresh_token: Refresh token válido
            
        Returns:
            Nuevos tokens
            
        Raises:
            ValidationServiceError: Si el refresh token es inválido
        """
        try:
            from rest_framework_simplejwt.exceptions import TokenError
            
            try:
                refresh = RefreshToken(refresh_token)
                access_token = refresh.access_token
                
                tokens = {
                    'access': str(access_token),
                    'refresh': str(refresh),
                    'access_expires_at': access_token['exp'],
                    'refresh_expires_at': refresh['exp']
                }
                
                self.log_info(f"Token refrescado para usuario: {refresh.payload.get('user_id')}")
                
                return tokens
                
            except TokenError as e:
                raise ValidationServiceError("Refresh token inválido", "invalid_refresh_token")
                
        except ValidationServiceError:
            raise
        except Exception as e:
            self.log_error(f"Error refrescando token: {e}")
            raise ServiceError("Error interno refrescando token", "refresh_error")
    
    def get_user_profile(self, user: User) -> Dict[str, Any]:
        """
        Obtiene el perfil completo de un usuario.
        
        Args:
            user: Usuario del cual obtener el perfil
            
        Returns:
            Diccionario con información del perfil
        """
        try:
            profile_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
            
            # Agregar información adicional si existe UserProfile
            try:
                from ..models import UserProfile
                profile = UserProfile.objects.get(user=user)
                profile_data.update({
                    'phone': profile.phone,
                    'address': profile.address,
                    'city': profile.city,
                    'country': profile.country,
                    'is_verified': profile.is_verified,
                    'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                })
            except:
                pass
            
            return profile_data
            
        except Exception as e:
            self.log_error(f"Error obteniendo perfil: {e}")
            raise ServiceError("Error interno obteniendo perfil", "profile_error")
    
    def update_user_profile(self, user: User, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza el perfil de un usuario.
        
        Args:
            user: Usuario a actualizar
            profile_data: Datos del perfil a actualizar
            
        Returns:
            Perfil actualizado
            
        Raises:
            ValidationServiceError: Si los datos son inválidos
        """
        try:
            with transaction.atomic():
                # Actualizar campos básicos del usuario
                if 'first_name' in profile_data:
                    user.first_name = profile_data['first_name']
                if 'last_name' in profile_data:
                    user.last_name = profile_data['last_name']
                if 'email' in profile_data:
                    self.validate_email(profile_data['email'])
                    user.email = profile_data['email']
                
                user.save()
                
                # Actualizar UserProfile si existe
                try:
                    from ..models import UserProfile
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    
                    if 'phone' in profile_data:
                        profile.phone = profile_data['phone']
                    if 'address' in profile_data:
                        profile.address = profile_data['address']
                    if 'city' in profile_data:
                        profile.city = profile_data['city']
                    if 'country' in profile_data:
                        profile.country = profile_data['country']
                    
                    profile.save()
                    
                except Exception as e:
                    self.log_warning(f"Error actualizando UserProfile: {e}")
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="profile_updated",
                    resource_type="user",
                    resource_id=user.id,
                    details={'updated_fields': list(profile_data.keys())}
                )
                
                self.log_info(f"Perfil actualizado: {user.username}", user_id=user.id)
                
                return self.get_user_profile(user)
                
        except ValidationServiceError:
            raise
        except Exception as e:
            self.log_error(f"Error actualizando perfil: {e}")
            raise ServiceError("Error interno actualizando perfil", "profile_update_error")
