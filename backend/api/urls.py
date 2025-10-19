"""
URLs para la API de CacaoScan.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Endpoints principales
    path('scan/measure/', views.ScanMeasureView.as_view(), name='scan-measure'),
    path('models/status/', views.ModelsStatusView.as_view(), name='models-status'),
    path('models/load/', views.LoadModelsView.as_view(), name='load-models'),
    path('dataset/validation/', views.DatasetValidationView.as_view(), name='dataset-validation'),
    
    # Inicialización automática
    path('auto-initialize/', views.AutoInitializeView.as_view(), name='auto-initialize'),
]
