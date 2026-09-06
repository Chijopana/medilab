from django.urls import path

from . import views

urlpatterns = [
    path('', views.error_404, name='error_404'),
]
