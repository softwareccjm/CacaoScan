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
from catalogos.models import Parametro, Departamento, Municipio
from .serializers import (
    PersonaRegistroSerializer, 
    PersonaSerializer
)
from .models import Persona


class PersonaRegistroView(APIView):
    """Vista para registrar usuario y persona en una sola petición."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Crear usuario y persona.
        
        Requiere:
        - tipo_documento: Código del parámetro (ej: 'CC')
        - genero: Código del parámetro (ej: 'M')
        - departamento: ID del departamento (opcional)
        - municipio: ID del municipio (opcional)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"📝 Datos recibidos en registro: {request.data}")
        
        serializer = PersonaRegistroSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                persona = serializer.save()
                logger.info(f"✅ Persona creada exitosamente: {persona.id}")
                return Response(
                    serializer.to_representation(persona),
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                logger.error(f"❌ Error al crear persona: {str(e)}")
                return Response(
                    {'error': f'Error al crear el usuario: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        logger.warning(f"⚠️ Errores de validación: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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