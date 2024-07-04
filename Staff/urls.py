from django.urls import path
from . import views
urlpatterns = [
    path('',views.lobby,name='staff/lobby'),
    path('lista_pacientes/',views.lobby,name='staff/lista_pacientes'),
    path('lista_pacientes/cosas',views.lobby,name='staff/paciente_ind'),
    path('lista_enfermedades/',views.lobby,name='staff/lista_enfermedades'),
    path('inbox/',views.lobby,name='staff/inbox'),
]