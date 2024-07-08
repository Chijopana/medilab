from django.urls import path
from . import views
urlpatterns = [
    path('',views.pagina_principal,name='pacientes/pagina_principal'),
    path('analisis/',views.analisis,name='pacientes/analisis'),
    path('vacunas/',views.vacunas,name='pacientes/vacunas'),
    path('diagnosticos/',views.diagnosticos,name='pacientes/diagnosticos'),
    path('visitas/',views.visitas,name='pacientes/visitas'),
    path('visitas/<int:pk>/mod',views.mod_visitas,name='pacientes/mod_visitas'),
    path('visitas/<int:pk>/del',views.del_visitas,name='pacientes/del_visitas'),
    path('visitas/nueva_visita/',views.agendar_visita,name='pacientes/agendar_visita'),
    path('medicacion/',views.medicacion,name='pacientes/medicacion'),
    path('consultas/',views.consultas,name='pacientes/consultas'),
    path('perfil/',views.perfil,name='pacientes/perfil'),
    path('perfil/mod',views.mod_perfil,name='pacientes/mod_perfil'),
]