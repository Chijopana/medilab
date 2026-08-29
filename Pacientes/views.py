from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from Perfiles.models import *
from Perfiles.forms import *
from Pacientes.forms import *
from Pacientes.models import Visita
from Enfermedades.models import *
from expedientes.models import Expediente
from Hub.decorators import paciente_requerido, paciente_es_propietario


@paciente_requerido
def detectar_enfermedad(request,pk):
    if request.method == 'GET':
        perfil = get_object_or_404(Perfil, user=request.user)
        paciente = get_object_or_404(Paciente, perfil=perfil)
        exp = get_object_or_404(Expediente, pk=pk)
        
        # Validar que el expediente pertenece al paciente
        if exp.paciente != paciente:
            return JsonResponse({'error': 'Acceso denegado'}, status=403)
        
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


@paciente_requerido
def pagina_principal(request):
    return render(request,'pacientes/pagina_principal.html')

@paciente_requerido
def historial_medico(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil)
    expedientes = paciente.expediente.all()
    return render(request, 'pacientes/historial_medico.html', {'expedientes': expedientes})

@paciente_requerido
def visitas(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil)
    visitas = paciente.visita.all()
    return render(request, 'pacientes/visitas.html', {'visitas': visitas})

@paciente_requerido
def mod_visita(request,pk):
    visita = get_object_or_404(Visita,pk=pk)
    if request.method=='POST':
        form = VisitaForm(request.POST, instance=visita)
        if form.is_valid():
            form.save()
            return redirect('pacientes/pagina_principal')
    else:
        form = VisitaForm(instance=visita)
    return render(request,'pacientes/modificar_visita.html',{'form':form,'visita':visita})

@paciente_requerido
def del_visita(request,pk):
    visita = get_object_or_404(Visita,pk=pk)
    if request.method=='POST':
        visita.delete()
    return redirect('pacientes/pagina_principal')
    
@paciente_requerido
def nueva_visita(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil)
    if request.method == 'POST':
        form = VisitaFormPaciente(request.POST)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.paciente = paciente
            visita.save()
            return redirect('pacientes/pagina_principal')
    else:
        form = VisitaFormPaciente()
    return render(request, 'pacientes/nueva_visita.html', {'form': form})

@paciente_requerido
def perfil(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil)
    if request.method == 'POST':
        form1 = PerfilForm(request.POST, instance=perfil)
        form2 = PacienteForm(request.POST, instance=paciente)
        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()
            return redirect('pacientes/pagina_principal')
    else:
        form1 = PerfilForm(instance=perfil)
        form2 = PacienteForm(instance=paciente)
    return render(request, 'pacientes/perfil.html', {'perfil': perfil, 'paciente': paciente, 'form1': form1, 'form2': form2})

@paciente_requerido
def medicacion(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil)
    medicacion = paciente.medicacion.all()
    return render(request, 'pacientes/medicacion.html', {'medicacion': medicacion})

@paciente_requerido
def consultas(request):

    return render(request,'pacientes/consultas.html')

