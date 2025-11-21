"""
Script para crear un usuario administrador.

Ejecutar: python create_admin_user.py
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin_user():
    """Crea un usuario administrador."""
    username = 'admin_training'
    email = 'admin@cacaoscan.com'
    password = 'admin123'
    
    # Verificar si el usuario ya existe
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f'Usuario {username} actualizado como administrador')
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
        print(f'Usuario administrador creado exitosamente:')
        print(f'  Username: {user.username}')
        print(f'  Email: {user.email}')
        print(f'  Password: {password}')
        print(f'  is_superuser: {user.is_superuser}')
        print(f'  is_staff: {user.is_staff}')

if __name__ == '__main__':
    create_admin_user()

