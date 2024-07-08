from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import Perfil, Paciente, Enfermero, Medico

# Registrar los modelos en el admin
admin.site.register(Permission)
admin.site.register(Perfil)
admin.site.register(Paciente)
admin.site.register(Enfermero)
admin.site.register(Medico)