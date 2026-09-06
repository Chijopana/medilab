"""
Landing, registro y autenticación.
"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from Hub.audit import AuditLog
from Perfiles.models import Paciente

from .forms import NuevoPerfilForm, UserForm


def _destino_por_rol(user):
    """A dónde llevar al usuario nada más iniciar sesión."""
    if user.groups.filter(name='Medicos').exists():
        return reverse('staff/lobby')
    if user.groups.filter(name='Pacientes').exists():
        return reverse('pacientes/pagina_principal')
    if user.is_staff:
        return reverse('admin:index')
    return reverse('hub')


def hub(request):
    return render(request, 'Hub/main_hub.html')


def crear_usuario(request):
    if request.user.is_authenticated:
        return redirect(_destino_por_rol(request.user))

    if request.method == 'POST':
        form_user = UserForm(request.POST)
        form_perfil = NuevoPerfilForm(request.POST)

        if form_user.is_valid() and form_perfil.is_valid():
            # Todo o nada: si algo falla no queda un User huérfano sin Perfil.
            with transaction.atomic():
                user = form_user.save()
                perfil = form_perfil.save(commit=False)
                perfil.user = user
                perfil.save()
                Paciente.objects.create(perfil=perfil)
                grupo, _ = Group.objects.get_or_create(name='Pacientes')
                user.groups.add(grupo)

            AuditLog.registrar(user, 'CREAR_USUARIO', f'Alta de paciente {user.username}',
                               request=request)
            messages.success(request, 'Cuenta creada. Ya puedes iniciar sesión.')
            return redirect('log_in')

        messages.error(request, 'No hemos podido crear la cuenta. Revisa los datos.')
    else:
        form_user = UserForm()
        form_perfil = NuevoPerfilForm()

    return render(request, 'Hub/crear_usuario.html',
                  {'form_user': form_user, 'form_perfil': form_perfil})


def log_in(request):
    if request.user.is_authenticated:
        return redirect(_destino_por_rol(request.user))

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            AuditLog.registrar(user, 'LOGIN', request=request)

            # Respetar ?next=..., pero solo si apunta a este mismo sitio.
            destino = request.POST.get('next') or request.GET.get('next')
            if destino and url_has_allowed_host_and_scheme(
                    destino, allowed_hosts={request.get_host()},
                    require_https=request.is_secure()):
                return redirect(destino)
            return redirect(_destino_por_rol(user))

        AuditLog.registrar(None, 'LOGIN_FALLIDO', f'Usuario probado: {username}',
                           request=request)
        messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'Hub/log_in.html', {'next': request.GET.get('next', '')})


@require_POST
def log_out(request):
    if request.user.is_authenticated:
        AuditLog.registrar(request.user, 'LOGOUT', request=request)
    logout(request)
    messages.info(request, 'Has cerrado sesión.')
    return redirect('hub')
