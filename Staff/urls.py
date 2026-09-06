from django.urls import path

from . import views

urlpatterns = [
    path('', views.lobby, name='staff/lobby'),

    # Pacientes
    path('lista_pacientes/', views.lista_pacientes, name='staff/lista_pacientes'),
    path('lista_pacientes/<uuid:access_key>/', views.paciente_ind,
         name='staff/paciente_ind'),
    path('lista_pacientes/<uuid:access_key>/edit/', views.paciente_ind_edit,
         name='staff/paciente_ind_edit'),
    path('paciente/<uuid:access_key>/visitas/', views.visitas, name='staff/visitas'),
    path('paciente/<uuid:access_key>/expedientes/', views.expedientes,
         name='staff/expedientes'),
    path('paciente/<uuid:access_key>/medicacion/', views.medicacion,
         name='staff/medicacion'),
    path('paciente/<uuid:access_key>/medicacion/nueva/', views.nueva_medicacion,
         name='staff/nueva_medicacion'),

    # Visitas
    path('lista_consultas/', views.lista_consultas, name='staff/lista_consultas'),
    path('lista_consultas/nueva/', views.nueva_consulta, name='staff/nueva_consulta'),
    path('lista_consultas/<int:pk>/mod/', views.consulta, name='staff/mod_visita'),
    path('lista_consultas/<int:pk>/del/', views.del_consulta, name='staff/del_consulta'),

    # Expedientes y perfil
    path('consulta_expediente/<int:pk>/', views.detectar_enfermedad,
         name='staff/detectar_enfermedad'),
    path('inbox/', views.inbox, name='staff/inbox'),
    path('perfil/', views.perfil, name='staff/perfil'),
]
