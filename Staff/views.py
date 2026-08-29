from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from Perfiles.models import *
from Perfiles.forms import *
from Pacientes.forms import *
from Staff.forms import *
from Pacientes.models import Visita
from Enfermedades.models import *
from expedientes.models import Expediente
from Hub.decorators import medico_requerido, staff_requerido


# Vista para visitas
@medico_requerido
def visitas(request, access_key):
    perfil = get_object_or_404(Perfil, access_key=access_key)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil)
    visitas = paciente.visita.all()
    return render(request, 'staff/partials/visitas.html', {'visitas': visitas, 'perfil': perfil})

# Vista para expedientes
@medico_requerido
def expedientes(request, access_key):
    perfil = get_object_or_404(Perfil, access_key=access_key)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil)
    expedientes = paciente.expediente.all()
    return render(request, 'staff/partials/expedientes.html', {'expedientes': expedientes, 'perfil': perfil})

# Vista para medicación
@medico_requerido
def medicacion(request, access_key):
    perfil = get_object_or_404(Perfil, access_key=access_key)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil)
    medicacion = paciente.medicacion.all()
    return render(request, 'staff/partials/medicacion.html', {'medicacion': medicacion, 'perfil': perfil})


@login_required
def editar_perfil_medico(request):
    medico = get_object_or_404(Medico, perfil__user=request.user)
    doctor_profile, created = Perfil.objects.get_or_create(medico=medico)
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=doctor_profile)
        if form.is_valid():
            form.save()
            return redirect('perfil_medico')
    else:
        form = PerfilForm(instance=doctor_profile)
    
    # Detectar si la solicitud es de HTMX y devolver un fragmento
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'staff/editar_perfil_fragment.html', {'form': form})
    
    return render(request, 'staff/editar_perfil.html', {'form': form})

@medico_requerido
def prueba(request, access_key):
    perfil = get_object_or_404(Perfil, access_key=access_key)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil)
    visitas = paciente.visita.all()

    contexto = {
        'perfil': range(10),
        'medicacion': range(10),
        'visitas': range(15),
        'expediente': range(10)
    }
    return render(request, 'staff/prueba.html', {'paciente': paciente, 'perfil': perfil, 'visitas': visitas})

@medico_requerido
def detectar_enfermedad(request,pk):
    if request.method == 'GET':
        # perfil = get_object_or_404(Perfil,user=request.user)
        # ppk = perfil.medico.pk
        # medico = get_object_or_404(Medico, pk = ppk)
        exp = get_object_or_404(Expediente,pk=pk)
        # if exp.doctor != medico:
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


@medico_requerido
def lobby(request):
    return render(request,'staff/lobby.html')

@medico_requerido
def lista_pacientes(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    medico, created = Medico.objects.get_or_create(perfil=perfil)
    pacientes = medico.pacientes.all()
    return render(request, 'staff/lista_pacientes.html', {'pacientes': pacientes})

def paciente_ind(request, access_key):
    perfil = get_object_or_404(Perfil, access_key=access_key)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil)
    expedientes = paciente.expediente.all()
    visitas = paciente.visita.all()
    medicacion = paciente.medicacion.all()
    return render(request, 'staff/paciente_ind.html', {'perfil': perfil, 'expedientes': expedientes, 'visitas': visitas, 'medicacion': medicacion})
# se ha de hacer una llamada api a una url para obtener la enfermedad del expediente.


def paciente_ind_edit(request, access_key):
    perfil = get_object_or_404(Perfil, access_key=access_key)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil)
    expedientes = paciente.expediente.all()
    visitas = paciente.visita.all().order_by('-hora_fecha')
    medicacion = paciente.medicacion.all()
    if request.method == 'POST':
        form1 = PerfilForm(request.POST, instance=perfil)
        form2 = PacienteForm(request.POST, instance=paciente)
        visita_lista = {visita.pk: VisitaForm(request.POST, instance=visita) for visita in visitas}
        medicacion_lista = {medic.pk: MedicacionForm(request.POST, instance=medic) for medic in medicacion}
        if form1.is_valid() and form2.is_valid() and all(form.is_valid() for form in visita_lista.values()) and all(form.is_valid() for form in medicacion_lista.values()):
            form1.save()
            form2.save()
            for form in visita_lista.values():
                form.save()
            for form in medicacion_lista.values():
                form.save()
            return redirect(reverse('staff/paciente_ind', kwargs={'access_key': access_key}))
        else:
            messages.error(request, "Error al actualizar los datos. Por favor, revisa los formularios.")
    else:
        form1 = PerfilForm(instance=perfil)
        form2 = PacienteForm(instance=paciente)
        visita_lista = {visita.pk: VisitaForm(instance=visita) for visita in visitas}
        medicacion_lista = {medic.pk: MedicacionForm(instance=medic) for medic in medicacion}
    return render(request, 'staff/paciente_ind_edit.html', {'form_perfil': form1, 'form_paciente': form2, 'paciente': perfil, 'expediente': expedientes, 'visitas': visita_lista, 'medicacion': medicacion_lista})




def paciente_nueva_medicacion(request, access_key):
    perfil_med = get_object_or_404(Perfil, user=request.user)
    medico, created = Medico.objects.get_or_create(perfil=perfil_med)
    perfil_pac = get_object_or_404(Perfil, access_key=access_key)
    paciente, created = Paciente.objects.get_or_create(perfil=perfil_pac)
    if request.method == 'POST':
        form = MedicacionFormCreacion(request.POST)
        if form.is_valid():
            med = form.save(commit=False)
            med.paciente = paciente
            med.medico = medico
            med.save()
            return redirect(reverse('staff/paciente_ind', kwargs={'access_key': access_key}))
    else:
        form = MedicacionFormCreacion()
    return render(request, 'staff/nueva_med.html', {'form': form})

def lista_consultas(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    medico, created = Medico.objects.get_or_create(perfil=perfil)
    visitas = medico.visita.all()
    return render(request, 'staff/lista_consultas.html', {'visitas': visitas})

def consulta(request,pk):
    visita = get_object_or_404(Visita,pk=pk)
    if request.method == 'POST':
        form = VisitaForm(request.POST,instance=visita)
        if form.is_valid():
            form.save()
            return redirect('staff/lobby')
    else:
        form = VisitaForm(instance=visita)
    return render(request,'staff/consulta_ind.html',{'form':form,'visita':visita})


def nueva_consulta(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    medico, created = Medico.objects.get_or_create(perfil=perfil)
    if request.method == 'POST':
        form = VisitaFormMedico(request.POST)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.medico = medico
            visita.save()
            return redirect('staff/lista_consultas')
    else:
        form = VisitaFormMedico()
    return render(request, 'staff/nueva_consulta.html', {'form': form})

def del_consulta(request,pk):
    consulta = get_object_or_404(Visita,pk=pk)
    if request.method == 'POST':
        consulta.delete()
    return redirect('staff/lista_consultas')

def perfil(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST,instance=perfil)
        if form.is_valid():
            form.save()
    else:
        form = PerfilForm(instance=perfil)
    return render(request,'staff/perfil.html',{'form':form,'perfil':perfil})



def inbox(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    medico, created = Medico.objects.get_or_create(perfil=perfil)
    temporal = medico.temporal_expediente.all()
    return render(request, 'staff/inbox.html', {'temporal': temporal})

def formulario(request,pk):
    return render(request,'staff/formulario.html')

def resultado(request,pk):
    return render(request,'staff/resultado.html')

# En el paso medio entre formulario y resultado, hacer que se guarde el expediente, se borre el temporal y que 
# solo se pueda acceder al resultado si eres el medico. En caso contrario, e404 personalizado.