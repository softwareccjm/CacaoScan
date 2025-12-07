"""
Tests for measurement calibration module.
"""
import pytest
import numpy as np
import cv2
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from ml.measurement.calibration import (
    CalibrationMethod,
    ReferenceObject,
    CalibrationResult,
    CalibrationParams,
    CoinDetector,
    RulerDetector,
    CalibrationManager,
    get_calibration_manager,
    calibrate_image,
    convert_pixels_to_mm,
    convert_mm_to_pixels
)


class TestCalibrationMethod:
    """Tests for CalibrationMethod enum."""
    
    def test_coin_detection(self):
        """Test coin detection method."""
        assert CalibrationMethod.COIN_DETECTION.value == "coin_detection"
    
    def test_ruler_detection(self):
        """Test ruler detection method."""
        assert CalibrationMethod.RULER_DETECTION.value == "ruler_detection"


class TestReferenceObject:
    """Tests for ReferenceObject enum."""
    
    def test_coin_1000_cop(self):
        """Test 1000 COP coin reference."""
        coin = ReferenceObject.COIN_1000_COP.value
        assert coin['diameter_mm'] == 23.0
        assert coin['name'] == "Moneda 1000 COP"
    
    def test_ruler_1cm(self):
        """Test 1cm ruler reference."""
        ruler = ReferenceObject.RULER_1CM.value
        assert ruler['length_mm'] == 10.0
        assert ruler['name'] == "Regla 1cm"


class TestCoinDetector:
    """Tests for CoinDetector class."""
    
    def test_init(self):
        """Test CoinDetector initialization."""
        detector = CoinDetector()
        
        assert detector.min_coin_area == 100
        assert detector.max_coin_area == 10000
    
    def test_load_coin_templates(self):
        """Test loading coin templates."""
        detector = CoinDetector()
        
        templates = detector._load_coin_templates()
        
        assert isinstance(templates, dict)
        assert "1000_cop" in templates
    
    @patch('ml.measurement.calibration.cv2.HoughCircles')
    @patch('ml.measurement.calibration.cv2.cvtColor')
    @patch('ml.measurement.calibration.cv2.GaussianBlur')
    def test_detect_coins(self, mock_blur, mock_cvt, mock_hough):
        """Test detecting coins."""
        detector = CoinDetector()
        
        # Create test image
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cvt.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_blur.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_hough.return_value = np.array([[[50, 50, 20]]])
        
        coins = detector.detect_coins(image)
        
        assert isinstance(coins, list)
    
    @patch('ml.measurement.calibration.cv2.HoughCircles')
    def test_detect_coins_no_circles(self, mock_hough):
        """Test detecting coins when no circles found."""
        detector = CoinDetector()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_hough.return_value = None
        
        coins = detector.detect_coins(image)
        
        assert coins == []
    
    def test_classify_coin_by_size_1000(self):
        """Test classifying 1000 COP coin."""
        detector = CoinDetector()
        
        result = detector._classify_coin_by_size(25)  # Diameter ~50
        
        assert result == ReferenceObject.COIN_1000_COP
    
    def test_classify_coin_by_size_unknown(self):
        """Test classifying unknown coin size."""
        detector = CoinDetector()
        
        result = detector._classify_coin_by_size(5)  # Too small
        
        assert result is None


class TestRulerDetector:
    """Tests for RulerDetector class."""
    
    def test_init(self):
        """Test RulerDetector initialization."""
        detector = RulerDetector()
        
        assert detector.min_line_length == 50
        assert detector.max_line_length == 500
    
    @patch('ml.measurement.calibration.cv2.HoughLinesP')
    @patch('ml.measurement.calibration.cv2.Canny')
    @patch('ml.measurement.calibration.cv2.cvtColor')
    def test_detect_rulers(self, mock_cvt, mock_canny, mock_hough):
        """Test detecting rulers."""
        detector = RulerDetector()
        
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cvt.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_canny.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_hough.return_value = np.array([[[10, 10, 60, 10]]])
        
        rulers = detector.detect_rulers(image)
        
        assert isinstance(rulers, list)
    
    @patch('ml.measurement.calibration.cv2.HoughLinesP')
    def test_detect_rulers_no_lines(self, mock_hough):
        """Test detecting rulers when no lines found."""
        detector = RulerDetector()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_hough.return_value = None
        
        rulers = detector.detect_rulers(image)
        
        assert rulers == []
    
    def test_classify_ruler_by_length_5cm(self):
        """Test classifying 5cm ruler."""
        detector = RulerDetector()
        
        result = detector._classify_ruler_by_length(250)  # ~50mm
        
        assert result == ReferenceObject.RULER_5CM
    
    def test_classify_ruler_by_length_unknown(self):
        """Test classifying unknown ruler length."""
        detector = RulerDetector()
        
        result = detector._classify_ruler_by_length(10)  # Too short
        
        assert result is None


class TestCalibrationManager:
    """Tests for CalibrationManager class."""
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    @patch('ml.measurement.calibration.ensure_dir_exists')
    def test_init(self, mock_ensure_dir, mock_get_dir):
        """Test CalibrationManager initialization."""
        mock_dir = Mock()
        mock_get_dir.return_value = mock_dir
        
        manager = CalibrationManager()
        
        assert manager.coin_detector is not None
        assert manager.ruler_detector is not None
        assert manager.current_calibration is None
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    @patch('ml.measurement.calibration.CalibrationManager._calibrate_with_coins')
    def test_calibrate_image_coin_detection(self, mock_calibrate_coins, mock_get_dir):
        """Test calibrating image with coin detection."""
        mock_result = CalibrationResult(
            success=True,
            pixels_per_mm=0.2,
            confidence=0.9,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=ReferenceObject.COIN_1000_COP,
            detected_points=[(50, 50)]
        )
        mock_calibrate_coins.return_value = mock_result
        
        manager = CalibrationManager()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = manager.calibrate_image(image, CalibrationMethod.COIN_DETECTION)
        
        assert result.success is True
        mock_calibrate_coins.assert_called_once()
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    @patch('ml.measurement.calibration.CalibrationManager._calibrate_with_rulers')
    def test_calibrate_image_ruler_detection(self, mock_calibrate_rulers, mock_get_dir):
        """Test calibrating image with ruler detection."""
        mock_result = CalibrationResult(
            success=True,
            pixels_per_mm=0.2,
            confidence=0.8,
            method=CalibrationMethod.RULER_DETECTION,
            reference_object=ReferenceObject.RULER_1CM,
            detected_points=[(10, 10), (60, 10)]
        )
        mock_calibrate_rulers.return_value = mock_result
        
        manager = CalibrationManager()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = manager.calibrate_image(image, CalibrationMethod.RULER_DETECTION)
        
        assert result.success is True
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_calibrate_image_error(self, mock_get_dir):
        """Test calibrating image with error."""
        manager = CalibrationManager()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch.object(manager, '_calibrate_with_coins', side_effect=Exception("Error")):
            result = manager.calibrate_image(image, CalibrationMethod.COIN_DETECTION)
            
            assert result.success is False
            assert result.error_message is not None
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    @patch('ml.measurement.calibration.CoinDetector.detect_coins')
    def test_calibrate_with_coins_no_coins(self, mock_detect, mock_get_dir):
        """Test calibrating with coins when none found."""
        mock_detect.return_value = []
        
        manager = CalibrationManager()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = manager._calibrate_with_coins(image)
        
        assert result.success is False
        assert "No se detectaron monedas" in result.error_message
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    @patch('ml.measurement.calibration.CoinDetector.detect_coins')
    @patch('ml.measurement.calibration.CalibrationManager._create_calibration_image')
    @patch('ml.measurement.calibration.CalibrationManager._save_calibration_image')
    def test_calibrate_with_coins_success(self, mock_save, mock_create, mock_detect, mock_get_dir):
        """Test calibrating with coins successfully."""
        mock_coin = {
            'center': (50, 50),
            'radius': 25,
            'diameter_pixels': 50,
            'coin_type': ReferenceObject.COIN_1000_COP,
            'confidence': 0.9
        }
        mock_detect.return_value = [mock_coin]
        mock_create.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_save.return_value = Path("calibration.jpg")
        
        manager = CalibrationManager()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = manager._calibrate_with_coins(image)
        
        assert result.success is True
        assert result.pixels_per_mm > 0
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_convert_pixels_to_mm_no_calibration(self, mock_get_dir):
        """Test converting pixels to mm without calibration."""
        manager = CalibrationManager()
        
        with pytest.raises(ValueError, match="No hay calibración"):
            manager.convert_pixels_to_mm(100.0)
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_convert_pixels_to_mm_with_calibration(self, mock_get_dir):
        """Test converting pixels to mm with calibration."""
        manager = CalibrationManager()
        manager.current_calibration = CalibrationParams(
            pixels_per_mm=0.2,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=ReferenceObject.COIN_1000_COP,
            confidence=0.9,
            timestamp="1234567890",
            image_dimensions=(100, 100)
        )
        
        result = manager.convert_pixels_to_mm(100.0)
        
        assert result == 500.0  # 100 / 0.2
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_convert_mm_to_pixels(self, mock_get_dir):
        """Test converting mm to pixels."""
        manager = CalibrationManager()
        manager.current_calibration = CalibrationParams(
            pixels_per_mm=0.2,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=ReferenceObject.COIN_1000_COP,
            confidence=0.9,
            timestamp="1234567890",
            image_dimensions=(100, 100)
        )
        
        result = manager.convert_mm_to_pixels(50.0)
        
        assert result == 10.0  # 50 * 0.2
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    @patch('ml.measurement.calibration.save_json')
    def test_save_calibration(self, mock_save_json, mock_get_dir):
        """Test saving calibration."""
        manager = CalibrationManager()
        
        calibration_result = CalibrationResult(
            success=True,
            pixels_per_mm=0.2,
            confidence=0.9,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=ReferenceObject.COIN_1000_COP,
            detected_points=[(50, 50)]
        )
        
        manager.save_calibration(calibration_result)
        
        assert manager.current_calibration is not None
        assert manager.current_calibration.pixels_per_mm == 0.2
        mock_save_json.assert_called_once()
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_save_calibration_failed(self, mock_get_dir):
        """Test saving failed calibration."""
        manager = CalibrationManager()
        
        calibration_result = CalibrationResult(
            success=False,
            pixels_per_mm=0.0,
            confidence=0.0,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=None,
            detected_points=[],
            error_message="Error"
        )
        
        with pytest.raises(ValueError, match="No se puede guardar"):
            manager.save_calibration(calibration_result)
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    @patch('ml.measurement.calibration.load_json')
    def test_load_calibration_success(self, mock_load_json, mock_get_dir):
        """Test loading calibration successfully."""
        mock_get_dir.return_value = Path("/tmp")
        mock_load_json.return_value = {
            'pixels_per_mm': 0.2,
            'method': 'coin_detection',
            'reference_object': None,
            'confidence': 0.9,
            'timestamp': '1234567890',
            'image_dimensions': [100, 100],
            'validation_score': None
        }
        
        manager = CalibrationManager()
        calibration_file = manager.calibration_dir / "current_calibration.json"
        calibration_file.parent.mkdir(parents=True, exist_ok=True)
        calibration_file.write_text('{}')
        
        result = manager.load_calibration()
        
        assert result is not None
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_load_calibration_not_found(self, mock_get_dir):
        """Test loading calibration when file not found."""
        manager = CalibrationManager()
        
        result = manager.load_calibration()
        
        assert result is None


class TestModuleFunctions:
    """Tests for module-level convenience functions."""
    
    @patch('ml.measurement.calibration.get_calibration_manager')
    def test_get_calibration_manager(self, mock_get):
        """Test get_calibration_manager function."""
        mock_manager = Mock()
        mock_get.return_value = mock_manager
        
        result = get_calibration_manager()
        
        assert result == mock_manager
    
    @patch('ml.measurement.calibration.get_calibration_manager')
    def test_calibrate_image_function(self, mock_get):
        """Test calibrate_image convenience function."""
        mock_manager = Mock()
        mock_result = CalibrationResult(
            success=True,
            pixels_per_mm=0.2,
            confidence=0.9,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=ReferenceObject.COIN_1000_COP,
            detected_points=[(50, 50)]
        )
        mock_manager.calibrate_image.return_value = mock_result
        mock_get.return_value = mock_manager
        
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = calibrate_image(image, CalibrationMethod.COIN_DETECTION)
        
        assert result.success is True
    
    @patch('ml.measurement.calibration.get_calibration_manager')
    def test_convert_pixels_to_mm_function(self, mock_get):
        """Test convert_pixels_to_mm convenience function."""
        mock_manager = Mock()
        mock_manager.convert_pixels_to_mm.return_value = 500.0
        mock_get.return_value = mock_manager
        
        result = convert_pixels_to_mm(100.0)
        
        assert result == 500.0
    
    @patch('ml.measurement.calibration.get_calibration_manager')
    def test_convert_mm_to_pixels_function(self, mock_get):
        """Test convert_mm_to_pixels convenience function."""
        mock_manager = Mock()
        mock_manager.convert_mm_to_pixels.return_value = 10.0
        mock_get.return_value = mock_manager
        
        result = convert_mm_to_pixels(50.0)
        
        assert result == 10.0


