from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def lobby(request):
    return render(request,'staff/lobby.html')

def lista_pacientes(request,access_key):
    staff = get_object_or_404()
    return render(request,'staff/lista_pacientes.html')

def paciente_ind(request):
    return render(request,'staff/paciente_ind.html')

def lista_enfermedades(request):
    return render(request,'staff/lista_enfermedades.html')

def inbox(request):
    return render(request,'staff/inbox.html')