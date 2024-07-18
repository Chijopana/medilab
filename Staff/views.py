from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from Perfiles.models import *
from Perfiles.forms import *
from Pacientes.forms import *
from Pacientes.models import *


def lobby(request):
    return render(request,'staff/lobby.html')

def lista_pacientes(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    pacientes = perfil.medico.pacientes.all()
    return render(request,'staff/lista_pacientes.html',{'pacientes':pacientes})

def paciente_ind(request,access_key):
    perfil = get_object_or_404(Perfil,access_key=access_key)
    expedientes = perfil.pacientes.expediente.all()
    visitas = perfil.pacientes.visita.all()
    return render(request,'staff/paciente_ind.html',{'perfil':perfil,'expedientes':expedientes,'visitas':visitas})

def paciente_ind_edit(request,access_key):
    perfil = get_object_or_404(Perfil,access_key=access_key)
    ppk = perfil.pacientes.pk
    paciente = get_object_or_404(Paciente, pk = ppk)
    expedientes = perfil.pacientes.expediente.all()
    visitas = perfil.pacientes.visita.all()
    form1 = PerfilForm(instance = perfil)
    form2 = PacienteForm(instance = paciente)
    return render(request,'staff/paciente_ind_edit.html',{'form_perfil':form1,'form_paciente':form2,'paciente':perfil,'expedientes':expedientes,'visitas':visitas})

def paciente_perfil(request,access_key):
    perfil = get_object_or_404(Perfil,access_key=access_key)
    if request.method == 'POST':
        form = PerfilForm(request.POST,instance=perfil)
        if form.is_valid():
            form.save()
            return {'form_perfil':form}

def paciente_paciente(request,access_key):
    perfil = get_object_or_404(Perfil,access_key=access_key)
    ppk = perfil.pacientes.pk
    paciente = get_object_or_404(Paciente, pk = ppk)
    if request.method== 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return {'form_paciente':form}

def paciente_visita(request,pk):
    visita = get_object_or_404(Visita,pk=pk)
    if request.method == 'POST':
        form = VisitaForm(request.POST,instance=visita)
        if form.is_valid():
            form.save()
            return  {'form_visita':form}
    else:
        form = VisitaForm(instance=visita)
    return  {'form_visita':form}


def lista_consultas(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    ppk = perfil.medico.pk
    medico=get_object_or_404(Medico,pk=ppk)
    visitas = medico.visita.all()
    return render(request,'staff/lista_consultas.html',{'visitas':visitas})

def consulta_ind(request,pk):
    visita = get_object_or_404(Visita,pk=pk)
    if request.method == 'POST':
        form = VisitaForm(request.POST,instance=visita)
        if form.is_valid():
            form.save()
            return {'form':form}
    else:
        form = VisitaForm(instance=visita)
    return {'form':form}

def nueva_consulta(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    ppk = perfil.medico.pk
    medico = get_object_or_404(Medico,pk=ppk)
    if request.method=='POST':
        form = VisitaFormMedico(request.POST)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.medico = medico
            visita.save()
            return redirect('staff/lista_consultas')
    else:
        form = VisitaFormMedico()
    return render(request,'staff/nueva_consulta.html',{'form':form})

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
            return {'form':form}
    else:
        form = PerfilForm(instance=perfil)
    return render(request,'staff/perfil.html',{'form':form,'perfil':perfil})

def inbox(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    temporal = perfil.medico.temporal_expediente.all()
    return render(request,'staff/inbox.html',{'temporal':temporal})

def formulario(request,pk):
    return render(request,'staff/formulario.html')

def resultado(request,pk):
    return render(request,'staff/resultado.html')

# En el paso medio entre formulario y resultado, hacer que se guarde el expediente, se borre el temporal y que 
# solo se pueda acceder al resultado si eres el medico. En caso contrario, e404 personalizado.