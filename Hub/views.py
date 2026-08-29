from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserForm, NuevoPerfilForm
from Perfiles.forms import *
from Perfiles.models import Paciente
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required

# Create your views here.

def hub(request):
    return render(request, 'Hub/main_hub.html')

def crear_usuario(request):
    grupo = get_object_or_404(Group, name='Pacientes')
    if request.method == 'POST':
        form1 = UserForm(request.POST)
        form2 = NuevoPerfilForm(request.POST)

        if form1.is_valid() and form2.is_valid():
            user = form1.save()
            perfil = form2.save(commit=False)
            perfil.user = user
            perfil.save()
            # Crear automáticamente el objeto Paciente asociado
            paciente, created = Paciente.objects.get_or_create(perfil=perfil)
            user.groups.add(grupo)
            messages.success(request, 'Usuario creado exitosamente. Por favor inicia sesión.')
            return redirect('log_in')
        else:
            messages.error(request,'Error. Por favor, intentelo de nuevo')
    else:
        form1 = UserForm()
        form2 = NuevoPerfilForm()

    return render(request,'Hub/crear_usuario.html',{'form1':form1,'form2':form2,})

def log_in(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Verificar si es médico por grupo o por modelo
            if user.groups.filter(name='Medicos').exists() or hasattr(user, 'perfil') and hasattr(user.perfil, 'medico'):
                return redirect('staff/lobby')
            else:
                return redirect('pacientes/pagina_principal')
        else:
            messages.error(request, 'Usuario inválido o contraseña errónea')

    return render(request,'Hub/log_in.html')

def log_out(request):
    logout(request)
    return redirect('log_in')