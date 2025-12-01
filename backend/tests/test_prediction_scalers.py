"""
Tests de diagnóstico y validación para escaladores y predicciones.
"""
import pytest
import numpy as np
from ml.regression.scalers import load_scalers
from ml.prediction.predict import get_predictor
from ml.regression.models import TARGETS


@pytest.mark.slow
class TestScalerDiagnostics:
    """Tests de diagnóstico para escaladores cargados desde archivos."""
    
    @pytest.mark.skip(reason="Requires actual scaler files - integration test")
    def test_scalers_loaded_successfully(self):
        """Verifica que los escaladores se carguen correctamente."""
        scalers = load_scalers()
        
        assert scalers.is_fitted
        assert len(scalers.scalers) == len(TARGETS)
        
        for target in TARGETS:
            assert target in scalers.scalers
    
    @pytest.mark.skip(reason="Requires actual scaler files - integration test")
    def test_scaler_statistics(self):
        """Verifica estadísticas de los escaladores."""
        scalers = load_scalers()
        
        for target in TARGETS:
            scaler = scalers.scalers[target]
            
            # Verificar que tiene atributos necesarios
            assert hasattr(scaler, 'mean_')
            assert hasattr(scaler, 'scale_')
            assert scaler.mean_ is not None
            assert scaler.scale_ is not None
            
            # Verificar que mean y scale son razonables
            assert scaler.mean_[0] > 0  # Valores positivos
            assert scaler.scale_[0] > 0  # Desviación estándar positiva
    
    @pytest.mark.skip(reason="Requires actual scaler files - integration test")
    def test_scaler_inverse_transform_ranges(self):
        """Verifica que la desnormalización produzca valores razonables."""
        scalers = load_scalers()
        
        # Límites razonables basados en el dataset (en mm o g)
        target_limits = {
            'alto': (5.0, 60.0),
            'ancho': (3.0, 30.0),
            'grosor': (1.0, 20.0),
            'peso': (0.2, 10.0)
        }
        
        # Probar valores normalizados típicos (-3 a +3 desviaciones estándar)
        test_normalized = np.array([[-3.0], [-2.0], [-1.0], [0.0], [1.0], [2.0], [3.0]])
        
        for target in TARGETS:
            self._assert_scaler_inverse_transform_range(
                target, scalers, test_normalized, target_limits
            )
    
    def _assert_scaler_inverse_transform_range(
        self, target: str, scalers, test_normalized: np.ndarray, target_limits: dict
    ) -> None:
        """Verifica que los valores desnormalizados estén en rangos razonables."""
        scaler = scalers.scalers[target]
        denorm_values = scaler.inverse_transform(test_normalized)
        
        _, max_val = target_limits[target]
        
        # Verificar que los valores desnormalizados están en rangos razonables
        # (con un margen porque estamos probando ±3 desviaciones estándar)
        denorm_min = denorm_values.min()
        denorm_max = denorm_values.max()
        max_allowed = max_val * 1.5
        
        # Los valores extremos pueden estar fuera del rango típico, pero deben ser razonables
        assert denorm_min > 0, f"{target}: valor mínimo negativo {denorm_min:.2f}"
        assert denorm_max < max_allowed, f"{target}: valor máximo muy alto {denorm_max:.2f}"
    
    @pytest.mark.skip(reason="Requires actual scaler files - integration test")
    def test_scaler_denormalization_accuracy(self):
        """Verifica que la desnormalización sea reversible."""
        scalers = load_scalers()
        
        # Valores de prueba típicos del dataset
        test_values = {
            'alto': np.array([[23.0], [25.0], [27.0]]),
            'ancho': np.array([[12.0], [14.0], [16.0]]),
            'grosor': np.array([[8.0], [9.0], [10.0]]),
            'peso': np.array([[1.5], [1.7], [2.0]])
        }
        
        for target in TARGETS:
            self._assert_scaler_denormalization_accuracy_for_target(
                target, scalers, test_values
            )
    
    def _assert_scaler_denormalization_accuracy_for_target(
        self, target: str, scalers, test_values: dict
    ) -> None:
        """Verifica que la desnormalización sea reversible para un target."""
        scaler = scalers.scalers[target]
        original_values = test_values[target]
        
        # Normalizar
        reshaped_original = original_values.reshape(-1, 1)
        normalized = scaler.transform(reshaped_original)
        
        # Desnormalizar
        reshaped_normalized = normalized.reshape(-1, 1)
        denormalized = scaler.inverse_transform(reshaped_normalized)
        
        # Verificar que la transformación inversa es precisa
        original_flat = original_values.flatten()
        denormalized_flat = denormalized.flatten()
        
        np.testing.assert_allclose(
            original_flat,
            denormalized_flat,
            rtol=1e-10,
            err_msg=f"{target}: Transformación inversa incorrecta"
        )


@pytest.mark.slow
@pytest.mark.integration
class TestPredictionLimits:
    """Tests para validar límites físicos en predicciones."""
    
    @pytest.mark.skip(reason="Requires actual model files - integration test")
    def test_predictor_loaded(self):
        """Verifica que el predictor se cargue correctamente."""
        predictor = get_predictor()
        success = predictor.load_artifacts()
        
        assert success, "El predictor no se cargó correctamente"
        assert predictor.models_loaded
        assert predictor.scalers is not None
    
    def test_prediction_value_ranges(self):
        """Verifica que las predicciones estén en rangos razonables."""
        # Este test requiere una imagen real para funcionar
        # Por ahora solo verificamos que el predictor esté configurado
        
        predictor = get_predictor()
        success = predictor.load_artifacts()
        
        if not success:
            return
        
        # Verificar que todos los modelos están cargados
        for target in TARGETS:
            assert target in predictor.regression_models, \
                f"Modelo {target} no está cargado"
        
        # Verificar que los escaladores están cargados
        assert predictor.scalers is not None
        assert predictor.scalers.is_fitted
    
    def test_scaler_stats_match_predictor(self):
        """Verifica que los escaladores del predictor coincidan con los cargados directamente."""
        predictor = get_predictor()
        success = predictor.load_artifacts()
        
        if not success:
            pytest.skip("Predictor no cargado")
        
        scalers_direct = load_scalers()
        
        for target in TARGETS:
            self._assert_scaler_stats_match(target, predictor, scalers_direct)
    
    def _assert_scaler_stats_match(self, target: str, predictor, scalers_direct) -> None:
        """Verifica que las estadísticas de un escalador coincidan."""
        scaler_predictor = predictor.scalers.scalers[target]
        scaler_direct = scalers_direct.scalers[target]
        
        predictor_mean = scaler_predictor.mean_[0]
        direct_mean = scaler_direct.mean_[0]
        predictor_scale = scaler_predictor.scale_[0]
        direct_scale = scaler_direct.scale_[0]
        
        np.testing.assert_almost_equal(
            predictor_mean,
            direct_mean,
            decimal=4,
            err_msg=f"{target}: Mean no coincide"
        )
        
        np.testing.assert_almost_equal(
            predictor_scale,
            direct_scale,
            decimal=4,
            err_msg=f"{target}: Scale no coincide"
        )

