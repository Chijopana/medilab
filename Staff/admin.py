from django.contrib import admin

from .models import Medicacion


@admin.register(Medicacion)
class MedicacionAdmin(admin.ModelAdmin):
    list_display = ('medicina', 'paciente', 'medico', 'fecha_inicio', 'fecha_final', 'activa')
    list_filter = ('fecha_inicio', 'fecha_final')
    search_fields = ('medicina', 'paciente__perfil__nombre', 'paciente__perfil__apellido')
    autocomplete_fields = ('paciente', 'medico')

    @admin.display(boolean=True, description='En curso')
    def activa(self, obj):
        return obj.activa
