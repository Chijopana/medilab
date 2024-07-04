from django.urls import path
from . import views
urlpatterns = [
    path('',views.pagina_principal,name='pacientes/pagina_principal'),
    path('analisis/',views.analisis,name='pacientes/analisis'),
    path('vacunas/',views.vacunas,name='pacientes/vacunas'),
    path('diagnosticos/',views.diagnosticos,name='pacientes/diagnosticos'),
    path('visitas/',views.visitas,name='pacientes/visitas'),
    path('visitas/nueva_visita/',views.agendar_visita,name='pacientes/agendar_visita'),
    path('medicacion/',views.medicacion,name='pacientes/medicacion'),
    path('consultas/',views.consultas,name='pacientes/consultas'),
]