"""Páginas de error personalizadas (se enganchan en Proyecto_Final/urls.py)."""
from django.shortcuts import render


def error_404(request, exception=None):
    return render(request, 'error_404.html', status=404)


def error_500(request):
    return render(request, 'error_500.html', status=500)


def error_403(request, exception=None):
    return render(request, 'error_403.html', status=403)
