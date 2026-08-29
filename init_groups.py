#!/usr/bin/env python
"""
Script para inicializar grupos de usuarios y datos básicos de la aplicación.
Ejecutar desde la shell de Django:
    python manage.py shell < init_groups.py
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Crear grupos
print("Creando grupos de usuarios...")

# Grupo Pacientes
pacientes_group, created = Group.objects.get_or_create(name='Pacientes')
if created:
    print("✓ Grupo 'Pacientes' creado")
else:
    print("✓ Grupo 'Pacientes' ya existe")

# Grupo Médicos
medicos_group, created = Group.objects.get_or_create(name='Medicos')
if created:
    print("✓ Grupo 'Medicos' creado")
else:
    print("✓ Grupo 'Medicos' ya existe")

# Grupo Staff
staff_group, created = Group.objects.get_or_create(name='Staff')
if created:
    print("✓ Grupo 'Staff' creado")
else:
    print("✓ Grupo 'Staff' ya existe")

print("\n✓ Inicialización completada.")
print("\nAhora puedes asignar usuarios a estos grupos en el admin:")
print("  - http://localhost:8000/admin/auth/group/")
