from django.contrib import admin

from .models import Visita


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'hora_fecha', 'estado')
    list_filter = ('estado', 'hora_fecha')
    search_fields = ('paciente__perfil__nombre', 'paciente__perfil__apellido',
                     'descripcion_problema')
    date_hierarchy = 'hora_fecha'
    autocomplete_fields = ('paciente', 'medico')
