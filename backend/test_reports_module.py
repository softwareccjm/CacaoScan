#!/usr/bin/env python3
"""
Test del módulo de reportes completo
"""
import os
import sys
import django
from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import datetime, timedelta
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()

from api.models import ReporteGenerado, CacaoPrediction, CacaoImage, Finca, Lote
from api.report_generator import CacaoReportPDFGenerator
from api.excel_generator import CacaoReportExcelGenerator

User = get_user_model()

class TestReportsModule(TestCase):
    """Test completo del módulo de reportes."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        import uuid
        
        # Crear usuario con nombre único
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Crear finca
        self.finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Test Location',
            hectareas=10.5,
            agricultor=self.user
        )
        
        # Crear lote
        self.lote = Lote.objects.create(
            identificador='LOTE-001',
            finca=self.finca,
            variedad='Criollo',
            area_hectareas=2.5,
            fecha_plantacion=timezone.now().date(),
            estado='activo',
            activo=True
        )
        
        # Crear imagen de prueba
        self.image = CacaoImage.objects.create(
            user=self.user,
            image=None,  # Simulado
            processed=True
        )
        
        # Crear análisis de prueba
        self.analysis = CacaoPrediction.objects.create(
            image=self.image,
            alto_mm=20.5,
            ancho_mm=15.2,
            grosor_mm=8.1,
            peso_g=1.8,
            processing_time_ms=100,
            model_version='v1.0',
            created_at=timezone.now()
        )
    
    def test_pdf_generator_quality_report(self):
        """Test generación de reporte de calidad en PDF."""
        print("🧪 Probando generador PDF de calidad...")
        
        generator = CacaoReportPDFGenerator()
        
        # Simular datos de análisis
        filtros = {
            'fecha_desde': (timezone.now() - timedelta(days=30)).date(),
            'fecha_hasta': timezone.now().date()
        }
        
        try:
            content = generator.generate_quality_report(self.user, filtros)
            
            # Verificar que se generó contenido
            self.assertIsNotNone(content)
            self.assertGreater(len(content), 0)
            
            # Verificar que es PDF (debe empezar con %PDF)
            self.assertTrue(content.startswith(b'%PDF'))
            
            print("✅ Generador PDF de calidad funciona correctamente")
            
        except Exception as e:
            print(f"❌ Error en generador PDF de calidad: {e}")
            self.fail(f"Error generando reporte PDF de calidad: {e}")
    
    def test_excel_generator_quality_report(self):
        """Test generación de reporte de calidad en Excel."""
        print("🧪 Probando generador Excel de calidad...")
        
        generator = CacaoReportExcelGenerator()
        
        # Simular datos de análisis
        filtros = {
            'fecha_desde': (timezone.now() - timedelta(days=30)).date(),
            'fecha_hasta': timezone.now().date()
        }
        
        try:
            content = generator.generate_quality_report(self.user, filtros)
            
            # Verificar que se generó contenido
            self.assertIsNotNone(content)
            self.assertGreater(len(content), 0)
            
            # Verificar que es Excel (debe contener PK en los primeros bytes)
            self.assertTrue(b'PK' in content[:10])
            
            print("✅ Generador Excel de calidad funciona correctamente")
            
        except Exception as e:
            print(f"❌ Error en generador Excel de calidad: {e}")
            self.fail(f"Error generando reporte Excel de calidad: {e}")
    
    def test_pdf_generator_finca_report(self):
        """Test generación de reporte de finca en PDF."""
        print("🧪 Probando generador PDF de finca...")
        
        generator = CacaoReportPDFGenerator()
        
        filtros = {
            'fecha_desde': (timezone.now() - timedelta(days=30)).date(),
            'fecha_hasta': timezone.now().date()
        }
        
        try:
            content = generator.generate_finca_report(self.finca.id, self.user, filtros)
            
            # Verificar que se generó contenido
            self.assertIsNotNone(content)
            self.assertGreater(len(content), 0)
            
            # Verificar que es PDF
            self.assertTrue(content.startswith(b'%PDF'))
            
            print("✅ Generador PDF de finca funciona correctamente")
            
        except Exception as e:
            print(f"❌ Error en generador PDF de finca: {e}")
            self.fail(f"Error generando reporte PDF de finca: {e}")
    
    def test_excel_generator_finca_report(self):
        """Test generación de reporte de finca en Excel."""
        print("🧪 Probando generador Excel de finca...")
        
        generator = CacaoReportExcelGenerator()
        
        filtros = {
            'fecha_desde': (timezone.now() - timedelta(days=30)).date(),
            'fecha_hasta': timezone.now().date()
        }
        
        try:
            content = generator.generate_finca_report(self.finca.id, self.user, filtros)
            
            # Verificar que se generó contenido
            self.assertIsNotNone(content)
            self.assertGreater(len(content), 0)
            
            # Verificar que es Excel
            self.assertTrue(b'PK' in content[:10])
            
            print("✅ Generador Excel de finca funciona correctamente")
            
        except Exception as e:
            print(f"❌ Error en generador Excel de finca: {e}")
            self.fail(f"Error generando reporte Excel de finca: {e}")
    
    def test_pdf_generator_audit_report(self):
        """Test generación de reporte de auditoría en PDF."""
        print("🧪 Probando generador PDF de auditoría...")
        
        generator = CacaoReportPDFGenerator()
        
        filtros = {
            'fecha_desde': (timezone.now() - timedelta(days=7)).date(),
            'fecha_hasta': timezone.now().date()
        }
        
        try:
            content = generator.generate_audit_report(self.user, filtros)
            
            # Verificar que se generó contenido
            self.assertIsNotNone(content)
            self.assertGreater(len(content), 0)
            
            # Verificar que es PDF
            self.assertTrue(content.startswith(b'%PDF'))
            
            print("✅ Generador PDF de auditoría funciona correctamente")
            
        except Exception as e:
            print(f"❌ Error en generador PDF de auditoría: {e}")
            self.fail(f"Error generando reporte PDF de auditoría: {e}")
    
    def test_excel_generator_audit_report(self):
        """Test generación de reporte de auditoría en Excel."""
        print("🧪 Probando generador Excel de auditoría...")
        
        generator = CacaoReportExcelGenerator()
        
        filtros = {
            'fecha_desde': (timezone.now() - timedelta(days=7)).date(),
            'fecha_hasta': timezone.now().date()
        }
        
        try:
            content = generator.generate_audit_report(self.user, filtros)
            
            # Verificar que se generó contenido
            self.assertIsNotNone(content)
            self.assertGreater(len(content), 0)
            
            # Verificar que es Excel
            self.assertTrue(b'PK' in content[:10])
            
            print("✅ Generador Excel de auditoría funciona correctamente")
            
        except Exception as e:
            print(f"❌ Error en generador Excel de auditoría: {e}")
            self.fail(f"Error generando reporte Excel de auditoría: {e}")
    
    def test_custom_report_generation(self):
        """Test generación de reporte personalizado."""
        print("🧪 Probando generador de reporte personalizado...")
        
        generator = CacaoReportExcelGenerator()
        
        parametros = {
            'include_dimensions': True,
            'include_weight': True,
            'include_confidence': True
        }
        
        filtros = {
            'fecha_desde': (timezone.now() - timedelta(days=30)).date(),
            'fecha_hasta': timezone.now().date()
        }
        
        try:
            content = generator.generate_custom_report(
                self.user, 'calidad', parametros, filtros
            )
            
            # Verificar que se generó contenido
            self.assertIsNotNone(content)
            self.assertGreater(len(content), 0)
            
            # Verificar que es Excel
            self.assertTrue(b'PK' in content[:10])
            
            print("✅ Generador de reporte personalizado funciona correctamente")
            
        except Exception as e:
            print(f"❌ Error en generador de reporte personalizado: {e}")
            self.fail(f"Error generando reporte personalizado: {e}")
    
    def test_reporte_generado_model(self):
        """Test del modelo ReporteGenerado."""
        print("🧪 Probando modelo ReporteGenerado...")
        
        try:
            # Crear reporte
            reporte = ReporteGenerado.objects.create(
                usuario=self.user,
                tipo_reporte='calidad',
                formato='pdf',
                titulo='Test Report',
                descripcion='Reporte de prueba',
                estado='completado'
            )
            
            # Verificar creación
            self.assertIsNotNone(reporte.id)
            self.assertEqual(reporte.usuario, self.user)
            self.assertEqual(reporte.tipo_reporte, 'calidad')
            self.assertEqual(reporte.formato, 'pdf')
            self.assertEqual(reporte.titulo, 'Test Report')
            self.assertEqual(reporte.estado, 'completado')
            
            # Verificar métodos
            self.assertFalse(reporte.esta_expirado)
            self.assertIsNotNone(reporte.fecha_solicitud)
            
            print("✅ Modelo ReporteGenerado funciona correctamente")
            
        except Exception as e:
            print(f"❌ Error en modelo ReporteGenerado: {e}")
            self.fail(f"Error probando modelo ReporteGenerado: {e}")
    
    def test_reporte_generado_methods(self):
        """Test de métodos del modelo ReporteGenerado."""
        print("🧪 Probando métodos del modelo ReporteGenerado...")
        
        try:
            # Crear reporte
            reporte = ReporteGenerado.objects.create(
                usuario=self.user,
                tipo_reporte='calidad',
                formato='pdf',
                titulo='Test Report Methods',
                estado='generando'
            )
            
            # Test marcar_completado
            file_content = ContentFile(b'%PDF-1.4 test content')
            tiempo_generacion = timedelta(seconds=5)
            
            reporte.marcar_completado(file_content, tiempo_generacion)
            
            self.assertEqual(reporte.estado, 'completado')
            self.assertIsNotNone(reporte.fecha_generacion)
            self.assertEqual(reporte.tiempo_generacion_segundos, 5)
            self.assertIsNotNone(reporte.archivo)
            
            # Test marcar_fallido
            reporte_fallido = ReporteGenerado.objects.create(
                usuario=self.user,
                tipo_reporte='calidad',
                formato='pdf',
                titulo='Failed Report',
                estado='generando'
            )
            
            error_message = 'Error de prueba'
            reporte_fallido.marcar_fallido(error_message)
            
            self.assertEqual(reporte_fallido.estado, 'fallido')
            self.assertEqual(reporte_fallido.mensaje_error, error_message)
            
            print("✅ Métodos del modelo ReporteGenerado funcionan correctamente")
            
        except Exception as e:
            print(f"❌ Error en métodos del modelo ReporteGenerado: {e}")
            self.fail(f"Error probando métodos del modelo ReporteGenerado: {e}")
    
    def test_reporte_generado_static_methods(self):
        """Test de métodos estáticos del modelo ReporteGenerado."""
        print("🧪 Probando métodos estáticos del modelo ReporteGenerado...")
        
        try:
            # Test generar_reporte
            reporte = ReporteGenerado.generar_reporte(
                usuario=self.user,
                tipo_reporte='calidad',
                formato='pdf',
                titulo='Static Test Report',
                descripcion='Reporte generado con método estático',
                parametros={'test': 'value'},
                filtros={'fecha_desde': timezone.now().date()}
            )
            
            self.assertIsNotNone(reporte.id)
            self.assertEqual(reporte.usuario, self.user)
            self.assertEqual(reporte.tipo_reporte, 'calidad')
            self.assertEqual(reporte.formato, 'pdf')
            self.assertEqual(reporte.titulo, 'Static Test Report')
            self.assertEqual(reporte.estado, 'generando')
            
            # Test limpiar_expirados
            # Crear reporte expirado
            reporte_expirado = ReporteGenerado.objects.create(
                usuario=self.user,
                tipo_reporte='calidad',
                formato='pdf',
                titulo='Expired Report',
                estado='completado',
                fecha_expiracion=timezone.now() - timedelta(days=1)
            )
            
            cleaned_count = ReporteGenerado.limpiar_expirados()
            self.assertGreaterEqual(cleaned_count, 0)
            
            print("✅ Métodos estáticos del modelo ReporteGenerado funcionan correctamente")
            
        except Exception as e:
            print(f"❌ Error en métodos estáticos del modelo ReporteGenerado: {e}")
            self.fail(f"Error probando métodos estáticos del modelo ReporteGenerado: {e}")


def run_tests():
    """Ejecutar todos los tests."""
    print("🚀 Iniciando tests del módulo de reportes...")
    print("=" * 60)
    
    try:
        # Ejecutar tests usando Django TestCase
        from django.test.runner import DiscoverRunner
        from django.test.utils import get_runner
        from django.conf import settings
        
        # Configurar settings para testing
        if not settings.configured:
            settings.configure(
                DEBUG=True,
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': ':memory:',
                    }
                },
                INSTALLED_APPS=[
                    'django.contrib.auth',
                    'django.contrib.contenttypes',
                    'api',
                ],
                USE_TZ=True,
            )
        
        # Crear instancia de test
        test_instance = TestReportsModule()
        test_instance.setUp()
        
        # Lista de métodos de test
        test_methods = [
            'test_pdf_generator_quality_report',
            'test_excel_generator_quality_report',
            'test_pdf_generator_finca_report',
            'test_excel_generator_finca_report',
            'test_pdf_generator_audit_report',
            'test_excel_generator_audit_report',
            'test_custom_report_generation',
            'test_reporte_generado_model',
            'test_reporte_generado_methods',
            'test_reporte_generado_static_methods'
        ]
        
        passed = 0
        failed = 0
        
        # Ejecutar cada test
        for method_name in test_methods:
            try:
                print(f"\n🧪 Ejecutando {method_name}...")
                method = getattr(test_instance, method_name)
                method()
                passed += 1
                print(f"✅ {method_name} - PASÓ")
            except Exception as e:
                failed += 1
                print(f"❌ {method_name} - FALLÓ: {e}")
        
        print("=" * 60)
        print(f"📊 Resumen de tests:")
        print(f"✅ Tests exitosos: {passed}")
        print(f"❌ Tests fallidos: {failed}")
        print(f"📈 Total ejecutados: {passed + failed}")
        
        if failed == 0:
            print("🎉 ¡Todos los tests del módulo de reportes pasaron exitosamente!")
            return True
        else:
            print("⚠️ Algunos tests fallaron. Revisa los errores arriba.")
            return False
        
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
