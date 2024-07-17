from django.urls import path
from . import views
urlpatterns = [
    path('',views.lobby,name='staff/lobby'),

    path('lista_pacientes/',views.lista_pacientes,name='staff/lista_pacientes'),
    path('lista_pacientes/<uuid:access_key>',views.paciente_ind,name='staff/paciente_ind'),
    path('lista_pacientes/<uuid:access_key>/edit',views.paciente_ind_edit,name='staff/paciente_ind_edit'),
    path('lista_pacientes/<uuid:access_key>/del',views.paciente_ind_del,name='staff/paciente_ind_del'),

    path('lista_consultas/',views.lista_consultas,name='staff/lista_consultas'),
    path('lista_consultas/nueva_consulta',views.nueva_consulta,name='staff/nueva_consulta'),
    path('lista_consultas/<int:pk>/del',views.del_consulta,name='staff/del_consulta'),

    path('inbox/',views.inbox,name='staff/inbox'),

    path('perfil',views.perfil,name='staff/perfil'),


]