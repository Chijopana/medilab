from django.urls import path
from . import views
urlpatterns = [
    path('expedientes/',views.expedientes,name='expedientes'),
    path('<int:expediente_id>/', views.ver_expediente, name='ver_expediente'),
   path('expedientes/<int:expediente_id>/pdf/', views.descargar_expediente_pdf, name='descargar_expediente_pdf'),
   path('expedientes_IA_2/',views.expediente_IA_2,name='expediente_IA_2'),
    path('expedientes_chatbot_1/',views.expediente_chatbot_1,name='expediente_chatbot_1'),
]