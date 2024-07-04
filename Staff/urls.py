from django.urls import path
from . import views
urlpatterns = [
    path('',views.lobby,name='staff/lobby'),
    path('lista_pacientes/',views.lista_pacientes,name='staff/lista_pacientes'),
    path('lista_pacientes/cosas',views.paciente_ind,name='staff/paciente_ind'),
    path('lista_enfermedades/',views.lista_enfermedades,name='staff/lista_enfermedades'),
    path('inbox/',views.inbox,name='staff/inbox'),
]