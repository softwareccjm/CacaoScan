"""
API module for CacaoScan.

This module re-exports views from api.views for backward compatibility.
All new code should import directly from api.views instead.
"""
# Re-export views from api.views module for backward compatibility
# NOTE: These re-exports are maintained for compatibility with urls.py
# New code should import from api.views or specific view modules directly
from .views.auth import (
    SendOtpView,
    VerifyOtpView,
)
from .views.finca import (
    FincaListCreateView, FincaDetailView, FincaUpdateView,
    FincaDeleteView, FincaActivateView, FincaStatsView,
    LoteListCreateView, LoteDetailView, LoteUpdateView,
    LoteDeleteView, LoteStatsView, LotesPorFincaView,
)
from .views.notifications import (
    NotificationListCreateView, NotificationDetailView,
    NotificationMarkReadView, NotificationMarkAllReadView,
    NotificationUnreadCountView, NotificationStatsView,
    NotificationCreateView,
)
from .views.admin import (
    ActivityLogListView, LoginHistoryListView, AuditStatsView,
    SystemSettingsView, SystemGeneralConfigView, SystemSecurityConfigView,
    SystemMLConfigView, SystemInfoView,
)
from .views.reports import (
    ReporteListCreateView, ReporteDetailView, ReporteDownloadView,
    ReporteDeleteView, ReporteStatsView, ReporteCleanupView,
    ReporteAgricultoresView, ReporteUsuariosView,
)
from .views.ml import (
    CalibrationStatusView, CalibrationView, CalibratedScanMeasureView,
    IncrementalTrainingStatusView, IncrementalTrainingView,
    IncrementalDataUploadView, IncrementalModelVersionsView,
    IncrementalDataVersionsView,
    ModelMetricsListView, ModelMetricsDetailView, ModelMetricsCreateView,
    ModelMetricsUpdateView, ModelMetricsDeleteView, ModelMetricsStatsView,
    ModelPerformanceTrendView, ModelComparisonView, BestModelsView,
    ProductionModelsView,
)
from .views.image import BatchAnalysisView

__all__ = [
    # OTP views
    'SendOtpView', 'VerifyOtpView',
    # Finca views
    'FincaListCreateView', 'FincaDetailView', 'FincaUpdateView',
    'FincaDeleteView', 'FincaActivateView', 'FincaStatsView',
    # Lote views
    'LoteListCreateView', 'LoteDetailView', 'LoteUpdateView',
    'LoteDeleteView', 'LoteStatsView', 'LotesPorFincaView',
    # Notification views
    'NotificationListCreateView', 'NotificationDetailView',
    'NotificationMarkReadView', 'NotificationMarkAllReadView',
    'NotificationUnreadCountView', 'NotificationStatsView',
    'NotificationCreateView',
    # Audit views
    'ActivityLogListView', 'LoginHistoryListView', 'AuditStatsView',
    # Report views
    'ReporteListCreateView', 'ReporteDetailView', 'ReporteDownloadView',
    'ReporteDeleteView', 'ReporteStatsView', 'ReporteCleanupView',
    'ReporteAgricultoresView', 'ReporteUsuariosView',
    # Calibration views
    'CalibrationStatusView', 'CalibrationView', 'CalibratedScanMeasureView',
    # Incremental views
    'IncrementalTrainingStatusView', 'IncrementalTrainingView',
    'IncrementalDataUploadView', 'IncrementalModelVersionsView',
    'IncrementalDataVersionsView',
    # Model metrics views
    'ModelMetricsListView', 'ModelMetricsDetailView', 'ModelMetricsCreateView',
    'ModelMetricsUpdateView', 'ModelMetricsDeleteView', 'ModelMetricsStatsView',
    'ModelPerformanceTrendView', 'ModelComparisonView', 'BestModelsView',
    'ProductionModelsView',
    # Batch analysis views
    'BatchAnalysisView',
    # Config views
    'SystemSettingsView', 'SystemGeneralConfigView', 'SystemSecurityConfigView',
    'SystemMLConfigView', 'SystemInfoView',
]

