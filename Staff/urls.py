from django.urls import path
from . import views
urlpatterns = [
    path('',views.lobby,name='staff/lobby'),

    path('lista_pacientes/',views.lista_pacientes,name='staff/lista_pacientes'),
    path('lista_pacientes/<uuid:access_key>',views.paciente_ind,name='staff/paciente_ind'),
    path('lista_pacientes/<uuid:access_key>/edit',views.paciente_ind_edit,name='staff/paciente_ind_edit'),
    path('lista_pacientes/<uuid:access_key>/form_perfil',views.paciente_perfil,name='staff/paciente_perfil'),
    path('lista_pacientes/<uuid:access_key>/form_paciente',views.paciente_paciente,name='staff/paciente_paciente'),
    path('lista_pacientes/<int:pk>/form_visita',views.paciente_visita,name='staff/paciente_visita'),
    path('lista_pacientes/<int:pk>/form_medicacion',views.paciente_medicacion,name='staff/paciente_medicacion'),

    path('lista_consultas/',views.lista_consultas,name='staff/lista_consultas'),
    path('lista_consultas/<int:pk>/',views.consulta_ind,name='staff/constulta_ind'),
    path('lista_consultas/nueva_consulta',views.nueva_consulta,name='staff/nueva_consulta'),
    path('lista_consultas/<int:pk>/del',views.del_consulta,name='staff/del_consulta'),

    path('inbox/',views.inbox,name='staff/inbox'),
    path('inbox/<int:pk>/formulario',views.formulario,name='staff/formulario'),
    path('inbox/<int:pk>/resultado',views.resultado,name='staff/resultado'),
    path('perfil',views.perfil,name='staff/perfil'),

]

    # path('lista_pacientes/<int:pk>/form_informe',views.paciente_informe,name='staff/paciente_informe'),
