from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required

def pagina_principal(request):
    return render(request,'pacientes/pagina_principal.html')

def historial_medico(request):
    return render(request,'pacientes/historial_medico.html')

def visitas(request):
    return render(request,'pacientes/visitas.html')

def del_visita(request):
    return render(request,'pacientes/del_visitas.html')

def nueva_visita(request):
    return render(request,'pacientes/nueva_visita.html')

def consultas(request):
    return render(request,'pacientes/consultas.html')

def perfil(request):
    return render(request,'pacientes/perfil.html')