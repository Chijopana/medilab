from django.contrib import admin

from .models import Medico, Paciente, Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni', 'email', 'telefono', 'user')
    search_fields = ('nombre', 'apellido', 'dni', 'email', 'user__username')
    list_filter = ('user__groups',)
    readonly_fields = ('access_key',)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'contacto_emergencia', 'telefono_emergencia')
    search_fields = ('perfil__nombre', 'perfil__apellido', 'perfil__dni')
    filter_horizontal = ('medicos',)
    autocomplete_fields = ('perfil',)


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'especialidad', 'numero_colegiado')
    search_fields = ('perfil__nombre', 'perfil__apellido', 'numero_colegiado')
    list_filter = ('especialidad',)
    autocomplete_fields = ('perfil',)
