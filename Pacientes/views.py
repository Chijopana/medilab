from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from Perfiles.models import *
from Perfiles.forms import *
from Pacientes.forms import *
from Pacientes.models import *

def detectar_enfermedad(request,pk):
    if request.method == 'GET':
        # perfil = get_object_or_404(Perfil,user=request.user)
        # ppk = perfil.pacientes.pk
        # paciente = get_object_or_404(Paciente, pk = ppk)
        exp = get_object_or_404(Expediente,pk=pk)
        # if exp.paciente != paciente:
            # return JsonResponse({'error': 'Acceso denegado'}, status=403)
        enfermedades = {'CancerMama':CancerMama,
                        'Diabetes':Diabetes,
                        'Pneumonia':Pneumonia,
                        'Lunares':Lunares,
                        'Cardiaco':Cardiaco
                        }
        if exp.especialidad in enfermedades:
            modelo = enfermedades[exp.especialidad]
            resultado = modelo.objects.filter(expediente=exp)
            resultado_json = list(resultado.values())
            return JsonResponse({'resultado':resultado_json})
        else:
            return JsonResponse({'error': 'Especialidad no válida'}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def pagina_principal(request):
    return render(request,'pacientes/pagina_principal.html')

def historial_medico(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    expedientes = perfil.pacientes.expediente.all()
    return render(request,'pacientes/historial_medico.html',{'expedientes':expedientes})

def visitas(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    visitas = perfil.pacientes.visita.all()
    return render(request,'pacientes/visitas.html',{'visitas':visitas})

def del_visita(request,pk):
    visita = get_object_or_404(Visita,pk=pk)
    if request.method=='POST':
        visita.delete()
    return redirect('pacientes/visitas')
    
def nueva_visita(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    ppk = perfil.pacientes.pk
    pacientex = get_object_or_404(Paciente,pk=ppk)
    if request.method=='POST':
        form = VisitaFormPaciente(request.POST)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.paciente = pacientex
            visita.save()
            return redirect('pacientes/visitas')
    else:
        form = VisitaFormPaciente()
    return render(request,'pacientes/nueva_visita.html',{'form':form})

def perfil(request):
    perfil = get_object_or_404(Perfil,user = request.user)
    ppk = perfil.pacientes.pk
    paciente = get_object_or_404(Paciente,pk=ppk)
    if request.method == 'POST':
        form1 = PerfilForm(request.POST,instance=perfil)
        form2 = PacienteForm(request.POST, instance=paciente)
        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()  
            return {'form1':form1,'form2':form2}
    else:
        form1 = PerfilForm(instance = perfil)
        form2 = PacienteForm(instance = paciente)
    return render(request,'pacientes/perfil.html',{'perfil':perfil,'paciente':paciente,'form1':form1,'form2':form2})

def medicacion(request):
    perfil = get_object_or_404(Perfil,user = request.user)
    medicacion = perfil.paciente.medicacion.all()
    return render(request,'pacientes/medicacion.html',{'medicacion':medicacion})

def consultas(request):

    return render(request,'pacientes/consultas.html')

