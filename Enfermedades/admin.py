from django.contrib import admin

from .models import Cardiaco, CancerMama, Diabetes, Lunares, Pneumonia


@admin.register(CancerMama, Pneumonia, Lunares)
class PruebaImagenAdmin(admin.ModelAdmin):
    list_display = ('expediente',)
    autocomplete_fields = ('expediente',)


@admin.register(Diabetes)
class DiabetesAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'edad', 'genero', 'bmi', 'glucosa_sangre', 'diabetes')
    list_filter = ('diabetes', 'genero', 'historial_fumador')
    autocomplete_fields = ('expediente',)


@admin.register(Cardiaco)
class CardiacoAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'categoria_edad', 'peso', 'altura', 'bmi',
                    'enfermedad_cardiaca')
    list_filter = ('enfermedad_cardiaca', 'diabetes', 'artritis')
    readonly_fields = ('bmi',)
    autocomplete_fields = ('expediente',)
