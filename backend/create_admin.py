#!/usr/bin/env python
"""
Script para crear el usuario administrador en CacaoScan
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()

from django.contrib.auth.models import User, Group

# Verificar si ya existe el usuario admin
if User.objects.filter(username='admin').exists():
    print('⚠️ El usuario admin ya existe')
    admin_user = User.objects.get(username='admin')
    print(f'Username: {admin_user.username}')
    print(f'Email: {admin_user.email}')
    print(f'Is Staff: {admin_user.is_staff}')
    print(f'Is Superuser: {admin_user.is_superuser}')
else:
    # Crear usuario admin
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@cacaoscan.com',
        password='Admin123!',
        first_name='Admin',
        last_name='Sistema',
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    print('✅ Usuario admin creado exitosamente!')
    print(f'Username: {admin_user.username}')
    print(f'Email: {admin_user.email}')
    print(f'Password: Admin123!')

# Verificar grupo admin
admin_group, created = Group.objects.get_or_create(name='admin')
if created:
    print('✅ Grupo admin creado')
else:
    print('ℹ️ Grupo admin ya existe')

# Agregar usuario al grupo admin
admin_user.groups.add(admin_group)
print('✅ Usuario agregado al grupo admin')

print('\n📋 Resumen de usuarios admin:')
all_admins = User.objects.filter(is_staff=True)
for user in all_admins:
    print(f'- {user.username} ({user.email}) - Staff: {user.is_staff}, Superuser: {user.is_superuser}')
