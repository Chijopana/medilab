from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required

def lobby(request):
    return render(request,'staff/lobby.html')

def lista_pacientes(request):
    return render(request,'staff/lista_pacientes.html')

def paciente_ind(request):
    return render(request,'staff/paciente_ind.html')

def paciente_ind_edit(request):
    return render(request,'staff/paciente_ind_edit.html')

def paciente_ind_del(request):
    return render(request,'staff/lista_pacientes.html')

def lista_consultas(request):
    return render(request,'staff/lista_consultas.html')

def nueva_consulta(request):
    return render(request,'staff/nueva_consulta.html')

def del_consulta(request):
    return render(request,'staff/lista_consultas.html')

def inbox(request):
    return render(request,'staff/inbox.html')

def perfil(request):
    return render(request,'staff/perfil.html')