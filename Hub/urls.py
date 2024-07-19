from django.urls import path
from . import views
urlpatterns = [
    path('',views.hub,name='hub'),
    path('log_in/',views.log_in,name='log_in'),
    path('crear_usuario/',views.crear_usuario,name='crear_usuario'),
    path('log_out/',views.log_out,name='log_out'),
]
