"""
Serializers para la API de CacaoScan.
"""
from rest_framework import serializers


class ConfidenceSerializer(serializers.Serializer):
    """Serializer para confianzas de los modelos."""
    alto = serializers.FloatField()
    ancho = serializers.FloatField()
    grosor = serializers.FloatField()
    peso = serializers.FloatField()


class DebugInfoSerializer(serializers.Serializer):
    """Serializer para información de debug."""
    segmented = serializers.BooleanField()
    yolo_conf = serializers.FloatField()
    latency_ms = serializers.IntegerField()
    models_version = serializers.CharField()
    device = serializers.CharField(required=False)
    total_time_s = serializers.FloatField(required=False)


class ScanMeasureResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de medición."""
    alto_mm = serializers.FloatField(help_text="Altura del grano en milímetros")
    ancho_mm = serializers.FloatField(help_text="Ancho del grano en milímetros")
    grosor_mm = serializers.FloatField(help_text="Grosor del grano en milímetros")
    peso_g = serializers.FloatField(help_text="Peso del grano en gramos")
    confidences = ConfidenceSerializer(help_text="Niveles de confianza por target")
    crop_url = serializers.URLField(help_text="URL del recorte procesado")
    debug = DebugInfoSerializer(help_text="Información de debug del procesamiento")


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de error."""
    error = serializers.CharField()
    status = serializers.CharField()


class DatasetStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del dataset."""
    total_records = serializers.IntegerField()
    valid_records = serializers.IntegerField()
    missing_images = serializers.IntegerField()
    missing_ids = serializers.ListField(child=serializers.IntegerField())
    dimensions_stats = serializers.DictField()


class ModelsStatusSerializer(serializers.Serializer):
    """Serializer para estado de modelos."""
    yolo_segmentation = serializers.CharField()
    regression_models = serializers.DictField()
    device = serializers.CharField(required=False)
    models_info = serializers.DictField(required=False)
    status = serializers.CharField()


class LoadModelsResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de carga de modelos."""
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    status = serializers.CharField()
