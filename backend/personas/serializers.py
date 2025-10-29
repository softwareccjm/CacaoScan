"""
Serializers para la app personas.

INTEGRACIÓN CON MÓDULOS:
- Usa Parametro (catálogos) para tipo_documento y genero
- Usa Departamento y Municipio (ubicaciones) para ubicación
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from catalogos.models import Parametro, Departamento, Municipio
from .models import Persona


class PersonaSerializer(serializers.ModelSerializer):
    """Serializer estándar para Persona con información completa de catálogos."""
    # Campos anidados de catálogos
    tipo_documento_info = serializers.SerializerMethodField()
    genero_info = serializers.SerializerMethodField()
    departamento_info = serializers.SerializerMethodField()
    municipio_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Persona
        fields = [
            'id', 'user', 'tipo_documento', 'tipo_documento_info', 
            'numero_documento', 'primer_nombre', 'segundo_nombre',
            'primer_apellido', 'segundo_apellido', 'telefono', 'direccion',
            'genero', 'genero_info', 'fecha_nacimiento',
            'departamento', 'departamento_info', 'municipio', 'municipio_info',
            'fecha_creacion'
        ]
        read_only_fields = ['user', 'fecha_creacion']
    
    def get_tipo_documento_info(self, obj):
        """Devuelve información del tipo de documento."""
        if obj.tipo_documento:
            return {
                'id': obj.tipo_documento.id,
                'codigo': obj.tipo_documento.codigo,
                'nombre': obj.tipo_documento.nombre
            }
        return None
    
    def get_genero_info(self, obj):
        """Devuelve información del género."""
        if obj.genero:
            return {
                'id': obj.genero.id,
                'codigo': obj.genero.codigo,
                'nombre': obj.genero.nombre
            }
        return None
    
    def get_departamento_info(self, obj):
        """Devuelve información del departamento."""
        if obj.departamento:
            return {
                'id': obj.departamento.id,
                'codigo': obj.departamento.codigo,
                'nombre': obj.departamento.nombre
            }
        return None
    
    def get_municipio_info(self, obj):
        """Devuelve información del municipio."""
        if obj.municipio:
            return {
                'id': obj.municipio.id,
                'codigo': obj.municipio.codigo,
                'nombre': obj.municipio.nombre
            }
        return None


class PersonaRegistroSerializer(serializers.Serializer):
    """
    Serializer para registro de usuario y persona en una sola petición.
    
    INTEGRACIÓN CON CATÁLOGOS:
    - tipo_documento: Código del parámetro del tema TIPO_DOC (ej: 'CC', 'CE')
    - genero: Código del parámetro del tema SEXO (ej: 'M', 'F')
    - departamento: ID del departamento
    - municipio: ID del municipio
    """
    # Campos para crear el usuario
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    
    # Campos para crear la persona
    tipo_documento = serializers.CharField(required=True, help_text="Código del parámetro TIPO_DOC (ej: CC, CE)")
    numero_documento = serializers.CharField(required=True, max_length=20)
    primer_nombre = serializers.CharField(required=True, max_length=50)
    segundo_nombre = serializers.CharField(required=False, allow_blank=True, max_length=50)
    primer_apellido = serializers.CharField(required=True, max_length=50)
    segundo_apellido = serializers.CharField(required=False, allow_blank=True, max_length=50)
    telefono = serializers.CharField(required=True, max_length=15)
    direccion = serializers.CharField(required=False, allow_blank=True, max_length=255)
    genero = serializers.CharField(required=True, help_text="Código del parámetro SEXO (ej: M, F, O)")
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    
    # Ubicación (IDs de departamento y municipio)
    departamento = serializers.IntegerField(required=False, allow_null=True)
    municipio = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_email(self, value):
        """Validar que el email no exista."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
    
    def validate_numero_documento(self, value):
        """Validar que el número de documento sea único."""
        if Persona.objects.filter(numero_documento=value).exists():
            raise serializers.ValidationError("Este número de documento ya está registrado.")
        return value
    
    def validate(self, data):
        """Validar referencias a catálogos y ubicaciones."""
        # Validar tipo_documento (debe ser un Parametro con tema TIPO_DOC)
        tipo_doc_codigo = data.get('tipo_documento')
        tipo_doc = Parametro.objects.filter(
            codigo=tipo_doc_codigo,
            tema__codigo='TIPO_DOC',
            activo=True
        ).first()
        
        if not tipo_doc:
            raise serializers.ValidationError({
                'tipo_documento': f"Tipo de documento '{tipo_doc_codigo}' no existe o no está activo."
            })
        data['tipo_documento_obj'] = tipo_doc
        
        # Validar genero (debe ser un Parametro con tema SEXO)
        genero_codigo = data.get('genero')
        genero = Parametro.objects.filter(
            codigo=genero_codigo,
            tema__codigo='SEXO',
            activo=True
        ).first()
        
        if not genero:
            raise serializers.ValidationError({
                'genero': f"Género '{genero_codigo}' no existe o no está activo."
            })
        data['genero_obj'] = genero
        
        # Validar municipio (debe existir y pertenecer al departamento)
        municipio_id = data.get('municipio')
        departamento_id = data.get('departamento')
        
        if municipio_id:
            municipio = Municipio.objects.filter(id=municipio_id).first()
            if not municipio:
                raise serializers.ValidationError({
                    'municipio': f"Municipio con ID '{municipio_id}' no existe."
                })
            
            # Si se especifica departamento, validar que coincida
            if departamento_id and municipio.departamento.id != departamento_id:
                raise serializers.ValidationError({
                    'municipio': f"El municipio no pertenece al departamento especificado."
                })
            data['municipio_obj'] = municipio
        else:
            data['municipio_obj'] = None
        
        if departamento_id:
            departamento = Departamento.objects.filter(id=departamento_id).first()
            if not departamento:
                raise serializers.ValidationError({
                    'departamento': f"Departamento con ID '{departamento_id}' no existe."
                })
            data['departamento_obj'] = departamento
        else:
            data['departamento_obj'] = None
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """Crear el usuario y la persona en una sola transacción."""
        # Extraer datos del usuario
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        # Extraer objetos de catálogos ya validados
        tipo_documento = validated_data.pop('tipo_documento_obj')
        genero = validated_data.pop('genero_obj')
        departamento = validated_data.pop('departamento_obj', None)
        municipio = validated_data.pop('municipio_obj', None)
        
        # Crear el usuario (username será el email)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=validated_data.get('primer_nombre', ''),
            last_name=validated_data.get('primer_apellido', ''),
            is_active=True
        )
        
        # Crear la persona asociada al usuario con catálogos y ubicaciones normalizadas
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento=validated_data.get('numero_documento'),
            primer_nombre=validated_data.get('primer_nombre'),
            segundo_nombre=validated_data.get('segundo_nombre', None),
            primer_apellido=validated_data.get('primer_apellido'),
            segundo_apellido=validated_data.get('segundo_apellido', None),
            telefono=validated_data.get('telefono'),
            direccion=validated_data.get('direccion', None),
            genero=genero,
            fecha_nacimiento=validated_data.get('fecha_nacimiento', None),
            departamento=departamento,
            municipio=municipio
        )
        
        return persona
    
    def to_representation(self, instance):
        """Personalizar la representación de la respuesta."""
        return {
            'id': instance.id,
            'user': {
                'id': instance.user.id,
                'email': instance.user.email
            },
            'primer_nombre': instance.primer_nombre,
            'segundo_nombre': instance.segundo_nombre,
            'primer_apellido': instance.primer_apellido,
            'segundo_apellido': instance.segundo_apellido,
            'numero_documento': instance.numero_documento,
            'telefono': instance.telefono,
            'tipo_documento': instance.tipo_documento.codigo,
            'genero': instance.genero.codigo,
            'departamento': instance.departamento.nombre if instance.departamento else None,
            'municipio': instance.municipio.nombre if instance.municipio else None,
        }