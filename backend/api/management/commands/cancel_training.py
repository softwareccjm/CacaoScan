"""
Comando Django para cancelar un entrenamiento en ejecución.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

try:
    from api.models import TrainingJob
except ImportError:
    TrainingJob = None


class Command(BaseCommand):
    help = 'Cancela un trabajo de entrenamiento en ejecución'

    def add_arguments(self, parser):
        parser.add_argument(
            'job_id',
            type=str,
            nargs='?',
            help='ID del trabajo a cancelar (opcional, lista trabajos si no se especifica)'
        )

    def handle(self, *args, **options):
        if TrainingJob is None:
            self.stdout.write(
                self.style.ERROR('TrainingJob no está disponible')
            )
            return

        job_id = options.get('job_id')
        
        if not job_id:
            # Listar jobs corriendo si no se especifica job_id
            running_jobs = TrainingJob.objects.filter(status='running').order_by('-created_at')
            
            if running_jobs.exists():
                self.stdout.write("=" * 60)
                self.stdout.write("JOBS EN EJECUCIÓN:")
                self.stdout.write("=" * 60)
                for job in running_jobs:
                    self.stdout.write(f"\nJob ID: {job.job_id}")
                    self.stdout.write(f"Tipo: {job.get_job_type_display()}")
                    self.stdout.write(f"Progreso: {job.progress_percentage:.1f}%")
                    self.stdout.write(f"Iniciado: {job.created_at}")
                    self.stdout.write(f"\nPara cancelar:")
                    self.stdout.write(f"  python manage.py cancel_training {job.job_id}")
            else:
                self.stdout.write(self.style.WARNING("No hay trabajos en ejecución"))
            return
        
        # Cancelar trabajo específico
        try:
            job = TrainingJob.objects.get(job_id=job_id)
            
            if job.status not in ['pending', 'running']:
                self.stdout.write(
                    self.style.WARNING(
                        f"El trabajo {job_id} no está en estado 'pending' o 'running' "
                        f"(estado actual: {job.status})"
                    )
                )
                return
            
            job.status = 'cancelled'
            job.completed_at = timezone.now()
            job.save()
            
            self.stdout.write(
                self.style.SUCCESS(f"Trabajo {job_id} cancelado exitosamente")
            )
            
        except TrainingJob.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Trabajo {job_id} no encontrado")
            )

