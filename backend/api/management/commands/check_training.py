"""
Comando Django para verificar el estado de entrenamientos en ejecución.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

try:
    from api.models import TrainingJob
except ImportError:
    TrainingJob = None


class Command(BaseCommand):
    help = 'Verifica el estado de entrenamientos en ejecución'

    def handle(self, *args, **options):
        if TrainingJob is None:
            self.stdout.write(
                self.style.ERROR('TrainingJob no está disponible')
            )
            return

        # Buscar jobs en ejecución
        running_jobs = TrainingJob.objects.filter(status='running').order_by('-created_at')
        pending_jobs = TrainingJob.objects.filter(status='pending').order_by('-created_at')

        self.stdout.write("=" * 60)
        self.stdout.write("ESTADO DE ENTRENAMIENTOS")
        self.stdout.write("=" * 60)

        if running_jobs.exists():
            self.stdout.write(f"\n🚀 Jobs EN EJECUCIÓN: {running_jobs.count()}")
            for job in running_jobs:
                duration = (timezone.now() - job.created_at).total_seconds() if job.created_at else 0
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                
                self.stdout.write(f"\nJob ID: {job.job_id}")
                self.stdout.write(f"  Tipo: {job.get_job_type_display()}")
                self.stdout.write(f"  Progreso: {job.progress_percentage:.1f}%")
                self.stdout.write(f"  Duración: {hours}h {minutes}m")
                self.stdout.write(f"  Iniciado: {job.created_at}")
                self.stdout.write(f"\n  Para cancelar:")
                self.stdout.write(f"   python manage.py cancel_training {job.job_id}")
        else:
            self.stdout.write("\n✅ No hay jobs en ejecución")

        if pending_jobs.exists():
            self.stdout.write(f"\n⏳ Jobs PENDIENTES: {pending_jobs.count()}")
            for job in pending_jobs:
                self.stdout.write(f"\nJob ID: {job.job_id}")
                self.stdout.write(f"  Tipo: {job.get_job_type_display()}")
                self.stdout.write(f"  Creado: {job.created_at}")
        else:
            self.stdout.write("\n✅ No hay jobs pendientes")

        # Resumen
        completed_jobs = TrainingJob.objects.filter(status='completed').count()
        failed_jobs = TrainingJob.objects.filter(status='failed').count()
        cancelled_jobs = TrainingJob.objects.filter(status='cancelled').count()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("RESUMEN")
        self.stdout.write("=" * 60)
        self.stdout.write(f"  En ejecución: {running_jobs.count()}")
        self.stdout.write(f"  Pendientes: {pending_jobs.count()}")
        self.stdout.write(f"  Completados: {completed_jobs}")
        self.stdout.write(f"  Fallidos: {failed_jobs}")
        self.stdout.write(f"  Cancelados: {cancelled_jobs}")

