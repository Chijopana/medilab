from django.urls import path
from . import views
urlpatterns = [
    path('',views.login,name='login'),
    path('crear_usuario',views.crear_usuario,name='crear_usuario'),
    path('crear_staff',views.crear_staff,name='crear_staff'),
    path('Hub/',views.hub,name='hub'),
    path('logout/',views.logout,name='logout'),
]
