"""
Rutas raíz del proyecto Medilab.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Hub.urls')),
    path('Staff/', include('Staff.urls')),
    path('Pacientes/', include('Pacientes.urls')),
    path('expedientes/', include('expedientes.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('Error_404/', include('E404.urls')),
]

# Páginas de error personalizadas (solo se usan con DEBUG=False).
handler404 = 'E404.views.error_404'
handler500 = 'E404.views.error_500'
handler403 = 'E404.views.error_403'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Medilab · Administración'
admin.site.site_title = 'Medilab'
admin.site.index_title = 'Gestión del sistema'
