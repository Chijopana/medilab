from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def pagina_principal(request):
    return render(request,'pacientes/pagina_principal.html')

def analisis(request):
    return render(request,'pacientes/analisis.html')

def vacunas(request):
    return render(request,'pacientes/vacunas.html')

def diagnosticos(request):
    return render(request,'pacientes/diagnosticos.html')

def visitas(request):
    return render(request,'pacientes/visitas.html')

def agendar_visita(request):
    return render(request,'pacientes/agendar_visita.html')

def medicacion(request):
    return render(request,'pacientes/medicacion.html')

def consultas(request):
    return render(request,'pacientes/consultas.html')