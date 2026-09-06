from django.urls import path

from . import views

urlpatterns = [
    path('', views.pagina_principal, name='pacientes/pagina_principal'),
    path('perfil/', views.perfil, name='pacientes/perfil'),
    path('historial/', views.historial_medico, name='pacientes/historial_medico'),
    path('medicacion/', views.medicacion, name='pacientes/medicacion'),

    path('visitas/', views.visitas, name='pacientes/visitas'),
    path('visitas/nueva/', views.nueva_visita, name='pacientes/nueva_visita'),
    path('visitas/<int:pk>/mod/', views.mod_visita, name='pacientes/mod_visita'),
    path('visitas/<int:pk>/del/', views.del_visita, name='pacientes/del_visita'),

    path('consulta_expediente/<int:pk>/', views.detectar_enfermedad,
         name='pacientes/detectar_enfermedad'),
]
