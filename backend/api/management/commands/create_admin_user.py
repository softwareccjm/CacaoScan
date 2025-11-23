"""
Comando Django para crear un usuario administrador.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Crea un usuario administrador predeterminado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin_training',
            help='Nombre de usuario del administrador'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@cacaoscan.com',
            help='Email del administrador'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Contraseña del administrador'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Usuario {username} actualizado como administrador')
            )
        else:
            # Crear nuevo usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='Training',
                is_superuser=True,
                is_staff=True,
                is_active=True
            )
            self.stdout.write(
                self.style.SUCCESS('Usuario administrador creado exitosamente:')
            )
            self.stdout.write(f'  Username: {user.username}')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Password: {password}')
            self.stdout.write(f'  is_superuser: {user.is_superuser}')
            self.stdout.write(f'  is_staff: {user.is_staff}')

