"""
Views para la API de CacaoScan.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse

from ml.data.dataset_loader import CacaoDatasetLoader


class ScanMeasureView(APIView):
    """
    Endpoint para medición de granos de cacao.
    """
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Procesa una imagen y devuelve mediciones del grano.
        """
        # TODO: Implementar cuando se complete el módulo de regresión
        return Response({
            'message': 'Endpoint en desarrollo',
            'status': 'pending'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class ModelsStatusView(APIView):
    """
    Endpoint para consultar el estado de los modelos.
    """
    
    def get(self, request):
        """
        Devuelve el estado de los modelos entrenados.
        """
        # TODO: Implementar cuando se complete el entrenamiento
        return Response({
            'yolo_segmentation': 'not_trained',
            'regression_models': {
                'alto': 'not_trained',
                'ancho': 'not_trained', 
                'grosor': 'not_trained',
                'peso': 'not_trained'
            },
            'status': 'pending_training'
        })


class DatasetValidationView(APIView):
    """
    Endpoint para validar el dataset.
    """
    
    def get(self, request):
        """
        Valida el dataset y devuelve estadísticas.
        """
        try:
            loader = CacaoDatasetLoader()
            stats = loader.get_dataset_stats()
            
            return Response({
                'valid': len(stats.get('missing_images', [])) == 0,
                'stats': stats,
                'status': 'success'
            })
            
        except Exception as e:
            return Response({
                'valid': False,
                'error': str(e),
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
