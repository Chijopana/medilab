"""
Decoradores de autorización.

Regla general del proyecto: **ninguna vista que toque datos clínicos puede
quedarse sin decorador**. Cada uno deja además rastro en la auditoría cuando
deniega el acceso.
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from Hub.audit import AuditLog
from Perfiles.models import Medico, Paciente, Perfil


def _denegar(request, view_func, razon, mensaje):
    AuditLog.acceso_denegado(request.user, view_func.__name__, razon, request=request)
    messages.error(request, mensaje)
    return redirect('hub')


def paciente_requerido(view_func):
    """Solo usuarios del grupo `Pacientes` con un Paciente asociado.

    Deja el paciente en `request.paciente` para que la vista no repita la consulta.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.groups.filter(name='Pacientes').exists():
            return _denegar(request, view_func, 'no pertenece al grupo Pacientes',
                            'Acceso denegado. Esta página es solo para pacientes.')
        try:
            perfil = Perfil.objects.select_related('user').get(user=request.user)
            request.perfil = perfil
            request.paciente = Paciente.objects.get(perfil=perfil)
        except (Perfil.DoesNotExist, Paciente.DoesNotExist):
            return _denegar(request, view_func, 'sin perfil de paciente',
                            'No encontramos tu ficha de paciente. Contacta con administración.')
        return view_func(request, *args, **kwargs)
    return wrapper


def medico_requerido(view_func):
    """Solo usuarios del grupo `Medicos` con un Medico asociado.

    Deja el médico en `request.medico` y su perfil en `request.perfil`.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.groups.filter(name='Medicos').exists():
            return _denegar(request, view_func, 'no pertenece al grupo Medicos',
                            'Acceso denegado. Esta página es solo para personal médico.')
        try:
            perfil = Perfil.objects.select_related('user').get(user=request.user)
            request.perfil = perfil
            request.medico = Medico.objects.get(perfil=perfil)
        except (Perfil.DoesNotExist, Medico.DoesNotExist):
            return _denegar(request, view_func, 'sin perfil de médico',
                            'No encontramos tu ficha de médico. Contacta con administración.')
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_requerido(view_func):
    """Personal administrativo: grupo `Staff` o `is_staff` de Django."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff or request.user.groups.filter(name='Staff').exists():
            return view_func(request, *args, **kwargs)
        return _denegar(request, view_func, 'sin permisos de staff',
                        'Acceso denegado. Requiere permisos de staff.')
    return wrapper
