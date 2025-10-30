"""
Vistas para la app personas.

INTEGRACIÓN:
- Los catálogos están disponibles en /api/temas/ y /api/parametros/
- Las ubicaciones están disponibles en /api/departamentos/ y /api/municipios/
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from catalogos.models import Parametro, Departamento, Municipio
from .serializers import (
    PersonaRegistroSerializer, 
    PersonaSerializer
)
from .models import Persona


class PersonaRegistroView(APIView):
    """Inicia flujo de verificación por OTP. No crea usuario/persona aquí."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Dispara envío de OTP guardando el formulario en temp_data sin reenviar la request."""
        try:
            email = request.data.get('email')
            if not email:
                return Response({'detail': 'Email es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

            # Prevenir si ya existe usuario
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if User.objects.filter(email=email).exists():
                return Response({'detail': 'El email ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

            # Rate limit y creación/actualización del pending
            from auth_app.models import PendingEmailVerification
            existing = PendingEmailVerification.objects.filter(email=email).first()
            if existing:
                elapsed = (timezone.now() - existing.last_sent).total_seconds()
                if elapsed < 60:
                    return Response({
                        'detail': f'Espera {int(60 - elapsed)} segundos antes de reenviar el código.'
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            code = PendingEmailVerification.generate_code()
            PendingEmailVerification.objects.update_or_create(
                email=email,
                defaults={'otp_code': code, 'temp_data': request.data}
            )

            # Enviar email con servicio centralizado
            from api.email_service import email_service
            email_service.send_email(
                to_emails=[email],
                subject='Verificación de cuenta CacaoScan',
                html_content=f"""
                <html>
                <body style=\"font-family: Arial, sans-serif; line-height: 1.6; color: #333;\">
                    <div style=\"max-width: 600px; margin: 0 auto; padding: 20px;\">
                        <h2 style=\"color: #22c55e;\">Verificación de cuenta CacaoScan</h2>
                        <p>Hola 👋,</p>
                        <p>Tu código de verificación es:</p>
                        <div style=\"background-color: #f3f4f6; border: 2px solid #22c55e; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;\">
                            <h1 style=\"color: #22c55e; font-size: 32px; margin: 0; letter-spacing: 5px;\">{code}</h1>
                        </div>
                        <p>Este código expirará en <strong>10 minutos</strong>.</p>
                        <p style=\"color: #6b7280; font-size: 14px;\">Si no solicitaste este código, puedes ignorar este email.</p>
                        <hr style=\"border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;\">
                        <p style=\"color: #6b7280; font-size: 12px;\">© {timezone.now().year} CacaoScan - Sistema de análisis de cacao</p>
                    </div>
                </body>
                </html>
                """,
                text_content=f"Hola, tu código de verificación es: {code}. Este código expirará en 10 minutos."
            )

            return Response({'message': 'Código enviado con éxito al correo.', 'email': email}, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response({'detail': f'Error iniciando verificación: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PersonaListaView(APIView):
    """Vista para listar todas las personas."""
    
    def get(self, request):
        """Listar todas las personas."""
        personas = Persona.objects.select_related(
            'tipo_documento__tema',
            'genero__tema',
            'departamento',
            'municipio'
        ).all()
        serializer = PersonaSerializer(personas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PersonaDetalleView(APIView):
    """Vista para obtener, actualizar o eliminar una persona específica."""
    
    def get(self, request, persona_id):
        """Obtener una persona específica."""
        try:
            persona = Persona.objects.select_related(
                'tipo_documento__tema',
                'genero__tema',
                'departamento',
                'municipio'
            ).get(id=persona_id)
            serializer = PersonaSerializer(persona)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Persona.DoesNotExist:
            return Response(
                {'error': 'Persona no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )