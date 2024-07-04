from django.urls import path
from . import views
urlpatterns = [
    path('', views.E404, name='error_404'),
]