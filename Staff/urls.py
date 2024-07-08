from django.urls import path
from . import views
urlpatterns = [
    path('',views.lobby,name='staff/lobby'),
    path('lista_pacientes/',views.lista_pacientes,name='staff/lista_pacientes'),
    path('lista_pacientes/<uuid:access_key>',views.paciente_ind,name='staff/paciente_ind'),
    path('lista_pacientes/<uuid:access_key>/edit',views.paciente_ind_edit,name='staff/paciente_ind_edit'),
    path('lista_pacientes/<uuid:access_key>/<int:pk>/mod_medicacion',views.paciente_ind_mod_medicacion,name='staff/paciente_ind_mod_medicacion'),
    path('lista_pacientes/<uuid:access_key>/nueva_medicacion',views.paciente_ind_nueva_medicacion,name='staff/paciente_ind_nueva_medicacion'),
    path('lista_pacientes/<uuid:access_key>/<int:pk>/del_medicacion',views.paciente_ind_del_medicacion,name='staff/paciente_ind_del_medicacion'),
    path('lista_consultas/',views.lista_consultas,name='staff/lista_consultas'),
    path('lista_consultas/<int:pk>/',views.mod_consultas,name='staff/mod_consultas'),
    path('lista_consultas/<int:pk>/del',views.del_consultas,name='staff/del_consultas'),
    path('nueva_consultas/',views.nueva_consultas,name='staff/nueva_consultas'),
    # path('lista_enfermedades/',views.lista_enfermedades,name='staff/lista_enfermedades'),
    path('inbox/',views.inbox,name='staff/inbox'),
    path('perfil',views.sf_perfil,name='staff/perfil'),
    path('perfil/<uuid:access_key>',views.sf_mod_perfil,name='staff/mod_perfil'),
]