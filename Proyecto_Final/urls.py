"""
URL configuration for Proyecto_Final project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path ('',include('Hub.urls')),
    path ('Staff/',include('Staff.urls')),
    path ('Pacientes/',include('Pacientes.urls')),
    path ('Error_404/',include('E404.urls')),
    path ('chatbot/',include('chatbot.urls')),
    path ('expedientes/',include('expedientes.urls')),
    # Estas dos últimas no tendrían que ser accesibles, pero si se le añade alguna vista, la ruta está creada.
    # path ('Perfiles/',include('Perfiles.urls')),
    # path ('Enfermedades/',include('Enfermedades.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
