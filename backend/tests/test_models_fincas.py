"""
Unit tests for fincas_app models (Finca, Lote).
Tests cover model creation, properties, methods, constraints, and relationships.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from fincas_app.models import Finca, Lote
from core.models import TimeStampedModel


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def finca(user):
    """Create a test finca."""
    return Finca.objects.create(
        nombre='Finca Test',
        ubicacion='Vereda El Cacao',
        municipio='Medellín',
        departamento='Antioquia',
        hectareas=Decimal('10.50'),
        agricultor=user,
        descripcion='Finca de prueba',
        coordenadas_lat=Decimal('6.244203'),
        coordenadas_lng=Decimal('-75.581215'),
        activa=True
    )


@pytest.fixture
def lote(finca):
    """Create a test lote."""
    return Lote.objects.create(
        finca=finca,
        identificador='LOTE-001',
        variedad='Criollo',
        fecha_plantacion=date(2020, 1, 15),
        fecha_cosecha=date(2023, 6, 20),
        area_hectareas=Decimal('2.50'),
        estado='activo',
        descripcion='Lote de prueba',
        coordenadas_lat=Decimal('6.244203'),
        coordenadas_lng=Decimal('-75.581215'),
        activo=True
    )


class TestFinca:
    """Tests for Finca model."""
    
    def test_finca_creation(self, user):
        """Test basic finca creation."""
        finca = Finca.objects.create(
            nombre='Finca Nueva',
            ubicacion='Vereda Test',
            municipio='Bogotá',
            departamento='Cundinamarca',
            hectareas=Decimal('5.00'),
            agricultor=user
        )
        
        assert finca.nombre == 'Finca Nueva'
        assert finca.ubicacion == 'Vereda Test'
        assert finca.municipio == 'Bogotá'
        assert finca.departamento == 'Cundinamarca'
        assert finca.hectareas == Decimal('5.00')
        assert finca.agricultor == user
        assert finca.activa is True
        assert finca.created_at is not None
        assert finca.updated_at is not None
    
    def test_finca_str_representation(self, finca):
        """Test string representation of finca."""
        expected = f"{finca.nombre} - {finca.municipio}, {finca.departamento}"
        assert str(finca) == expected
    
    def test_finca_inherits_timestamped_model(self, finca):
        """Test that Finca inherits from TimeStampedModel."""
        assert isinstance(finca, TimeStampedModel)
        assert hasattr(finca, 'created_at')
        assert hasattr(finca, 'updated_at')
    
    def test_finca_total_lotes_property_empty(self, finca):
        """Test total_lotes property when no lotes exist."""
        assert finca.total_lotes == 0
    
    def test_finca_total_lotes_property_with_lotes(self, finca):
        """Test total_lotes property with multiple lotes."""
        Lote.objects.create(
            finca=finca,
            identificador='LOTE-001',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 15),
            area_hectareas=Decimal('2.50'),
            estado='activo'
        )
        Lote.objects.create(
            finca=finca,
            identificador='LOTE-002',
            variedad='Forastero',
            fecha_plantacion=date(2021, 3, 10),
            area_hectareas=Decimal('3.00'),
            estado='activo'
        )
        
        assert finca.total_lotes == 2
    
    def test_finca_lotes_activos_property(self, finca):
        """Test lotes_activos property."""
        Lote.objects.create(
            finca=finca,
            identificador='LOTE-001',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 15),
            area_hectareas=Decimal('2.50'),
            estado='activo',
            activo=True
        )
        Lote.objects.create(
            finca=finca,
            identificador='LOTE-002',
            variedad='Forastero',
            fecha_plantacion=date(2021, 3, 10),
            area_hectareas=Decimal('3.00'),
            estado='inactivo',
            activo=False
        )
        
        assert finca.lotes_activos == 1
    
    def test_finca_total_analisis_property_no_predictions(self, finca):
        """Test total_analisis property when no predictions exist."""
        assert finca.total_analisis == 0
    
    def test_finca_total_analisis_property_with_predictions(self, finca, user):
        """Test total_analisis property with predictions."""
        from images_app.models import CacaoImage, CacaoPrediction
        
        lote = Lote.objects.create(
            finca=finca,
            identificador='LOTE-001',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 15),
            area_hectareas=Decimal('2.50'),
            estado='activo'
        )
        
        # Create images and predictions
        image1 = CacaoImage.objects.create(
            user=user,
            finca=finca,
            lote=lote,
            processed=True
        )
        CacaoPrediction.objects.create(
            image=image1,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        image2 = CacaoImage.objects.create(
            user=user,
            finca=finca,
            lote=lote,
            processed=True
        )
        CacaoPrediction.objects.create(
            image=image2,
            alto_mm=Decimal('21.0'),
            ancho_mm=Decimal('15.5'),
            grosor_mm=Decimal('10.3'),
            peso_g=Decimal('5.6'),
            processing_time_ms=110
        )
        
        assert finca.total_analisis == 2
    
    def test_finca_total_analisis_property_exception_handling(self, finca):
        """Test total_analisis property handles exceptions gracefully."""
        # This should not raise an exception even if related objects don't exist properly
        result = finca.total_analisis
        assert isinstance(result, int)
        assert result >= 0
    
    def test_finca_calidad_promedio_property_no_predictions(self, finca):
        """Test calidad_promedio property when no predictions exist."""
        assert finca.calidad_promedio == 0.0
    
    def test_finca_calidad_promedio_property_with_predictions(self, finca, user):
        """Test calidad_promedio property with predictions."""
        from images_app.models import CacaoImage, CacaoPrediction
        
        lote = Lote.objects.create(
            finca=finca,
            identificador='LOTE-001',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 15),
            area_hectareas=Decimal('2.50'),
            estado='activo'
        )
        
        image = CacaoImage.objects.create(
            user=user,
            finca=finca,
            lote=lote,
            processed=True
        )
        CacaoPrediction.objects.create(
            image=image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            confidence_alto=Decimal('0.85'),
            confidence_ancho=Decimal('0.90'),
            confidence_grosor=Decimal('0.88'),
            confidence_peso=Decimal('0.92'),
            processing_time_ms=100
        )
        
        calidad = finca.calidad_promedio
        assert isinstance(calidad, float)
        assert 0.0 <= calidad <= 100.0
    
    def test_finca_calidad_promedio_property_exception_handling(self, finca):
        """Test calidad_promedio property handles exceptions gracefully."""
        result = finca.calidad_promedio
        assert isinstance(result, float)
        assert result >= 0.0
    
    def test_finca_ubicacion_completa_property(self, finca):
        """Test ubicacion_completa property."""
        expected = f"{finca.ubicacion}, {finca.municipio}, {finca.departamento}"
        assert finca.ubicacion_completa == expected
    
    def test_finca_get_estadisticas_method(self, finca):
        """Test get_estadisticas method."""
        stats = finca.get_estadisticas()
        
        assert isinstance(stats, dict)
        assert 'total_lotes' in stats
        assert 'lotes_activos' in stats
        assert 'total_analisis' in stats
        assert 'calidad_promedio' in stats
        assert 'hectareas' in stats
        assert 'fecha_registro' in stats
        assert 'activa' in stats
        
        assert stats['total_lotes'] == 0
        assert stats['lotes_activos'] == 0
        assert stats['total_analisis'] == 0
        assert stats['calidad_promedio'] == 0.0
        assert stats['hectareas'] == float(finca.hectareas)
        assert stats['activa'] is True
    
    def test_finca_constraint_hectareas_positivas(self, user):
        """Test constraint that hectareas must be positive."""
        with pytest.raises(IntegrityError):
            Finca.objects.create(
                nombre='Finca Test',
                ubicacion='Test',
                municipio='Test',
                departamento='Test',
                hectareas=Decimal('0.00'),
                agricultor=user
            )
    
    def test_finca_constraint_hectareas_negative(self, user):
        """Test constraint that hectareas cannot be negative."""
        with pytest.raises(IntegrityError):
            Finca.objects.create(
                nombre='Finca Test',
                ubicacion='Test',
                municipio='Test',
                departamento='Test',
                hectareas=Decimal('-1.00'),
                agricultor=user
            )
    
    def test_finca_cascade_delete_with_user(self, user):
        """Test that fincas are deleted when user is deleted."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Test',
            municipio='Test',
            departamento='Test',
            hectareas=Decimal('5.00'),
            agricultor=user
        )
        finca_id = finca.id
        
        user.delete()
        
        assert not Finca.objects.filter(id=finca_id).exists()
    
    def test_finca_ordering(self, user):
        """Test that fincas are ordered by created_at descending."""
        finca1 = Finca.objects.create(
            nombre='Finca 1',
            ubicacion='Test',
            municipio='Test',
            departamento='Test',
            hectareas=Decimal('5.00'),
            agricultor=user
        )
        
        # Small delay to ensure different timestamps
        import time
        time.sleep(0.01)
        
        finca2 = Finca.objects.create(
            nombre='Finca 2',
            ubicacion='Test',
            municipio='Test',
            departamento='Test',
            hectareas=Decimal('5.00'),
            agricultor=user
        )
        
        fincas = list(Finca.objects.filter(agricultor=user))
        assert fincas[0].id == finca2.id
        assert fincas[1].id == finca1.id


class TestLote:
    """Tests for Lote model."""
    
    def test_lote_creation(self, finca):
        """Test basic lote creation."""
        lote = Lote.objects.create(
            finca=finca,
            identificador='LOTE-003',
            variedad='Trinitario',
            fecha_plantacion=date(2021, 5, 10),
            fecha_cosecha=date(2024, 8, 15),
            area_hectareas=Decimal('1.50'),
            estado='activo'
        )
        
        assert lote.finca == finca
        assert lote.identificador == 'LOTE-003'
        assert lote.variedad == 'Trinitario'
        assert lote.fecha_plantacion == date(2021, 5, 10)
        assert lote.fecha_cosecha == date(2024, 8, 15)
        assert lote.area_hectareas == Decimal('1.50')
        assert lote.estado == 'activo'
        assert lote.activo is True
        assert lote.created_at is not None
        assert lote.updated_at is not None
    
    def test_lote_str_representation(self, lote):
        """Test string representation of lote."""
        expected = f"{lote.identificador} - {lote.variedad} ({lote.finca.nombre})"
        assert str(lote) == expected
    
    def test_lote_inherits_timestamped_model(self, lote):
        """Test that Lote inherits from TimeStampedModel."""
        assert isinstance(lote, TimeStampedModel)
        assert hasattr(lote, 'created_at')
        assert hasattr(lote, 'updated_at')
    
    def test_lote_total_analisis_property_empty(self, lote):
        """Test total_analisis property when no images exist."""
        assert lote.total_analisis == 0
    
    def test_lote_total_analisis_property_with_images(self, lote, user):
        """Test total_analisis property with images."""
        from images_app.models import CacaoImage
        
        CacaoImage.objects.create(
            user=user,
            finca=lote.finca,
            lote=lote
        )
        CacaoImage.objects.create(
            user=user,
            finca=lote.finca,
            lote=lote
        )
        
        assert lote.total_analisis == 2
    
    def test_lote_total_analisis_property_exception_handling(self, lote):
        """Test total_analisis property handles exceptions gracefully."""
        result = lote.total_analisis
        assert isinstance(result, int)
        assert result >= 0
    
    def test_lote_analisis_procesados_property(self, lote, user):
        """Test analisis_procesados property."""
        from images_app.models import CacaoImage
        
        CacaoImage.objects.create(
            user=user,
            finca=lote.finca,
            lote=lote,
            processed=True
        )
        CacaoImage.objects.create(
            user=user,
            finca=lote.finca,
            lote=lote,
            processed=False
        )
        
        assert lote.analisis_procesados == 1
    
    def test_lote_calidad_promedio_property_no_predictions(self, lote):
        """Test calidad_promedio property when no predictions exist."""
        assert lote.calidad_promedio == 0.0
    
    def test_lote_calidad_promedio_property_with_predictions(self, lote, user):
        """Test calidad_promedio property with predictions."""
        from images_app.models import CacaoImage, CacaoPrediction
        
        image = CacaoImage.objects.create(
            user=user,
            finca=lote.finca,
            lote=lote,
            processed=True
        )
        CacaoPrediction.objects.create(
            image=image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            confidence_alto=Decimal('0.85'),
            confidence_ancho=Decimal('0.90'),
            confidence_grosor=Decimal('0.88'),
            confidence_peso=Decimal('0.92'),
            processing_time_ms=100
        )
        
        calidad = lote.calidad_promedio
        assert isinstance(calidad, float)
        assert 0.0 <= calidad <= 100.0
    
    def test_lote_calidad_promedio_property_exception_handling(self, lote):
        """Test calidad_promedio property handles exceptions gracefully."""
        result = lote.calidad_promedio
        assert isinstance(result, float)
        assert result >= 0.0
    
    def test_lote_edad_meses_property(self, finca):
        """Test edad_meses property."""
        from datetime import date
        today = date.today()
        plant_date = date(today.year - 2, today.month, today.day)
        
        lote = Lote.objects.create(
            finca=finca,
            identificador='LOTE-AGE',
            variedad='Criollo',
            fecha_plantacion=plant_date,
            area_hectareas=Decimal('2.50'),
            estado='activo'
        )
        
        edad = lote.edad_meses
        assert isinstance(edad, int)
        assert edad >= 20  # Approximately 2 years
    
    def test_lote_ubicacion_completa_property(self, lote):
        """Test ubicacion_completa property."""
        expected = f"{lote.finca.ubicacion}, {lote.finca.municipio}, {lote.finca.departamento}"
        assert lote.ubicacion_completa == expected
    
    def test_lote_get_estadisticas_method(self, lote):
        """Test get_estadisticas method."""
        stats = lote.get_estadisticas()
        
        assert isinstance(stats, dict)
        assert 'total_analisis' in stats
        assert 'analisis_procesados' in stats
        assert 'calidad_promedio' in stats
        assert 'area_hectareas' in stats
        assert 'edad_meses' in stats
        assert 'estado' in stats
        assert 'activo' in stats
        assert 'fecha_plantacion' in stats
        assert 'fecha_cosecha' in stats
        
        assert stats['total_analisis'] == 0
        assert stats['analisis_procesados'] == 0
        assert stats['calidad_promedio'] == 0.0
        assert stats['area_hectareas'] == float(lote.area_hectareas)
        assert stats['estado'] == 'activo'
        assert stats['activo'] is True
    
    def test_lote_get_estadisticas_with_fecha_cosecha(self, finca):
        """Test get_estadisticas method with fecha_cosecha."""
        lote = Lote.objects.create(
            finca=finca,
            identificador='LOTE-COSECHA',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 15),
            fecha_cosecha=date(2023, 6, 20),
            area_hectareas=Decimal('2.50'),
            estado='cosechado'
        )
        
        stats = lote.get_estadisticas()
        assert stats['fecha_cosecha'] == '20/06/2023'
    
    def test_lote_get_estadisticas_without_fecha_cosecha(self, finca):
        """Test get_estadisticas method without fecha_cosecha."""
        lote = Lote.objects.create(
            finca=finca,
            identificador='LOTE-NO-COSECHA',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 15),
            area_hectareas=Decimal('2.50'),
            estado='activo'
        )
        
        stats = lote.get_estadisticas()
        assert stats['fecha_cosecha'] is None
    
    def test_lote_constraint_area_positiva(self, finca):
        """Test constraint that area_hectareas must be positive."""
        with pytest.raises(IntegrityError):
            Lote.objects.create(
                finca=finca,
                identificador='LOTE-001',
                variedad='Criollo',
                fecha_plantacion=date(2020, 1, 15),
                area_hectareas=Decimal('0.00'),
                estado='activo'
            )
    
    def test_lote_constraint_fecha_cosecha_valida(self, finca):
        """Test constraint that fecha_cosecha must be >= fecha_plantacion."""
        with pytest.raises(IntegrityError):
            Lote.objects.create(
                finca=finca,
                identificador='LOTE-001',
                variedad='Criollo',
                fecha_plantacion=date(2020, 1, 15),
                fecha_cosecha=date(2019, 1, 15),  # Before plantacion
                area_hectareas=Decimal('2.50'),
                estado='activo'
            )
    
    def test_lote_constraint_fecha_cosecha_null_allowed(self, finca):
        """Test that fecha_cosecha can be null."""
        lote = Lote.objects.create(
            finca=finca,
            identificador='LOTE-NULL',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 15),
            fecha_cosecha=None,
            area_hectareas=Decimal('2.50'),
            estado='activo'
        )
        
        assert lote.fecha_cosecha is None
    
    def test_lote_unique_constraint_identificador_por_finca(self, finca):
        """Test unique constraint on (finca, identificador)."""
        Lote.objects.create(
            finca=finca,
            identificador='LOTE-UNIQUE',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 15),
            area_hectareas=Decimal('2.50'),
            estado='activo'
        )
        
        # Should raise IntegrityError when trying to create duplicate
        with pytest.raises(IntegrityError):
            Lote.objects.create(
                finca=finca,
                identificador='LOTE-UNIQUE',
                variedad='Forastero',
                fecha_plantacion=date(2021, 1, 15),
                area_hectareas=Decimal('3.00'),
                estado='activo'
            )
    
    def test_lote_same_identificador_different_finca(self, user):
        """Test that same identificador can exist in different fincas."""
        finca1 = Finca.objects.create(
            nombre='Finca 1',
            ubicacion='Test',
            municipio='Test',
            departamento='Test',
            hectareas=Decimal('5.00'),
            agricultor=user
        )
        finca2 = Finca.objects.create(
            nombre='Finca 2',
            ubicacion='Test',
            municipio='Test',
            departamento='Test',
            hectareas=Decimal('5.00'),
            agricultor=user
        )
        
        lote1 = Lote.objects.create(
            finca=finca1,
            identificador='LOTE-001',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 15),
            area_hectareas=Decimal('2.50'),
            estado='activo'
        )
        
        lote2 = Lote.objects.create(
            finca=finca2,
            identificador='LOTE-001',
            variedad='Forastero',
            fecha_plantacion=date(2021, 1, 15),
            area_hectareas=Decimal('3.00'),
            estado='activo'
        )
        
        assert lote1.identificador == lote2.identificador
        assert lote1.finca != lote2.finca
    
    def test_lote_cascade_delete_with_finca(self, finca):
        """Test that lotes are deleted when finca is deleted."""
        lote = Lote.objects.create(
            finca=finca,
            identificador='LOTE-CASCADE',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 15),
            area_hectareas=Decimal('2.50'),
            estado='activo'
        )
        lote_id = lote.id
        
        finca.delete()
        
        assert not Lote.objects.filter(id=lote_id).exists()
    
    def test_lote_estado_choices(self, finca):
        """Test that estado field accepts valid choices."""
        valid_estados = ['activo', 'inactivo', 'cosechado', 'renovado']
        
        for estado in valid_estados:
            lote = Lote.objects.create(
                finca=finca,
                identificador=f'LOTE-{estado}',
                variedad='Criollo',
                fecha_plantacion=date(2020, 1, 15),
                area_hectareas=Decimal('2.50'),
                estado=estado
            )
            assert lote.estado == estado
    
    def test_lote_ordering(self, finca):
        """Test that lotes are ordered by created_at descending."""
        lote1 = Lote.objects.create(
            finca=finca,
            identificador='LOTE-1',
            variedad='Criollo',
            fecha_plantacion=date(2020, 1, 15),
            area_hectareas=Decimal('2.50'),
            estado='activo'
        )
        
        # Small delay to ensure different timestamps
        import time
        time.sleep(0.01)
        
        lote2 = Lote.objects.create(
            finca=finca,
            identificador='LOTE-2',
            variedad='Forastero',
            fecha_plantacion=date(2021, 1, 15),
            area_hectareas=Decimal('3.00'),
            estado='activo'
        )
        
        lotes = list(Lote.objects.filter(finca=finca))
        assert lotes[0].id == lote2.id
        assert lotes[1].id == lote1.id

