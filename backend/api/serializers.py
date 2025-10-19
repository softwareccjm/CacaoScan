"""
Serializers para la API de CacaoScan.
"""
from rest_framework import serializers


class ScanMeasureResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de medición."""
    alto_mm = serializers.FloatField()
    ancho_mm = serializers.FloatField()
    grosor_mm = serializers.FloatField()
    peso_g = serializers.FloatField()
    confianza_modelos = serializers.DictField()
    urls_recortes = serializers.ListField(child=serializers.URLField())
    procesamiento_info = serializers.DictField()


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
    status = serializers.CharField()
