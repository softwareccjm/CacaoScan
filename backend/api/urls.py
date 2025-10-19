"""
URLs para la API de CacaoScan.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Endpoints de ML
    path('scan/measure/', views.ScanMeasureView.as_view(), name='scan-measure'),
    path('models/status/', views.ModelsStatusView.as_view(), name='models-status'),
    path('dataset/validation/', views.DatasetValidationView.as_view(), name='dataset-validation'),
]
