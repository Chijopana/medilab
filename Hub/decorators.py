"""
Decoradores personalizados para autorización y validación de acceso.
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from Perfiles.models import Perfil, Paciente, Medico


def paciente_requerido(view_func):
    """
    Decorador que verifica si el usuario es un paciente.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            perfil = Perfil.objects.get(user=request.user)
            if request.user.groups.filter(name='Pacientes').exists():
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Acceso denegado. Esta página es solo para pacientes.')
                return redirect('hub')
        except Perfil.DoesNotExist:
            messages.error(request, 'Perfil no encontrado.')
            return redirect('hub')
    return wrapper


def medico_requerido(view_func):
    """
    Decorador que verifica si el usuario es un médico.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            perfil = Perfil.objects.get(user=request.user)
            medico = Medico.objects.get(perfil=perfil)
            if request.user.groups.filter(name='Medicos').exists():
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Acceso denegado. Esta página es solo para médicos.')
                return redirect('hub')
        except (Perfil.DoesNotExist, Medico.DoesNotExist):
            messages.error(request, 'Perfil de médico no encontrado.')
            return redirect('hub')
    return wrapper


def staff_requerido(view_func):
    """
    Decorador que verifica si el usuario es part del staff.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.groups.filter(name='Staff').exists() or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Acceso denegado. Requiere permisos de staff.')
            return redirect('hub')
    return wrapper


def paciente_es_propietario(view_func):
    """
    Decorador que verifica si el paciente es el propietario de la cuenta.
    Se usa en vistas que pueden acceder a datos de otros pacientes.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            perfil = Perfil.objects.get(user=request.user)
            paciente = Paciente.objects.get(perfil=perfil)
            request.paciente = paciente
            return view_func(request, *args, **kwargs)
        except (Perfil.DoesNotExist, Paciente.DoesNotExist):
            messages.error(request, 'Acceso denegado.')
            return redirect('hub')
    return wrapper
