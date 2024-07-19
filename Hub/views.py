from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserForm
from Perfiles.forms import *
from django.contrib.auth.models import Group, User
# Create your views here.

def hub(request):
    return render(request,'Hub/main_hub.html')

def crear_usuario(request):
    grupo = get_object_or_404(Group, name='Pacientes')
    if request.method == 'POST':
        form1 = UserForm(request.POST)
        form2 = PerfilForm(request.POST)
        form3 = PacienteForm(request.POST)

        if form1.is_valid() and form2.is_valid() and form3.is_valid():
            usery = form1.save()
            luz =form2.save(commit=False)
            luz.user=usery
            luz.save()
            luz.user.groups.add(grupo)
            pacientex = form3.save(commit=False)
            pacientex.perfil = luz
            pacientex.save()
            return redirect('log_in')
        else:
            messages.error(request,'Error. Por favor, intentelo de nuevo')
    else:
        form1 = UserForm()
        form2 = PerfilForm()
        form3 = PacienteForm()
    return render(request,'Hub/crear_usuario.html',{'form1':form1,'form2':form2,'form3':form3})

def log_in(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            if request.user.has_perm('auth._Es_Medico') or request.user.has_perm('auth._Es_Enfermero'):
                return redirect('staff/lobby')
            else:
                return redirect('pacientes/pagina_principal')
        else:
            # return redirect('error_404')
            messages.error(request,'Usuario invalido o contraseña erronea')

    return render(request,'Hub/log_in.html')

def log_out(request):
    logout(request)
    return redirect('log_in')