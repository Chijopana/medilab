from django.contrib import admin

from .models import Expediente, TemporalExpediente


@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'doctor', 'especialidad', 'fecha_hora')
    list_filter = ('especialidad', 'fecha_hora')
    search_fields = ('paciente__perfil__nombre', 'paciente__perfil__apellido',
                     'paciente__perfil__dni', 'antecedentes')
    date_hierarchy = 'fecha_hora'
    autocomplete_fields = ('paciente', 'doctor')


@admin.register(TemporalExpediente)
class TemporalExpedienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'doctor', 'especialidad', 'fecha_hora')
    list_filter = ('especialidad',)
    autocomplete_fields = ('paciente', 'doctor')
