from django.urls import path

from . import views

urlpatterns = [
    path('', views.mis_expedientes, name='expedientes'),
    path('diagnostico-ia/', views.diagnostico_ia, name='diagnostico_ia'),
    path('<int:expediente_id>/', views.ver_expediente, name='ver_expediente'),
    path('<int:expediente_id>/pdf/', views.descargar_expediente_pdf,
         name='descargar_expediente_pdf'),
]
