from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from Perfiles.models import *
from Perfiles.forms import *


def lobby(request):
    return render(request,'staff/lobby.html')

def lista_pacientes(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    pacientes = perfil.medico.pacientes.all()
    return render(request,'staff/lista_pacientes.html',{'pacientes':pacientes})



def paciente_ind(request,access_key):
    perfil = get_object_or_404(Perfil,access_key=access_key)
    informes = perfil.pacientes.informes.all()
    visitas = perfil.pacientes.visita.all()
    return render(request,'staff/paciente_ind.html',{'perfil':perfil,'informes':informes,'visitas':visitas})

def paciente_ind_edit(request,access_key):
    perfil = get_object_or_404(Perfil,access_key=access_key)
    ppk = perfil.pacientes.pk
    paciente = get_object_or_404(Paciente, pk = ppk)
    informes = perfil.pacientes.informes.all()
    visitas = perfil.pacientes.visita.all()
    if request.method == 'POST':
        form1 = PerfilForm(request.POST,instance=perfil)
        form2 = PacienteForm(request.POST, instance=paciente)
        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()
            return redirect('staff/paciente_ind', access_key=access_key)
    else:
        form1 = PerfilForm(instance = perfil)
        form2 = PacienteForm(instance = paciente)
    return render(request,'staff/paciente_ind_edit.html',{'form1':form1,'form2':form2,'paciente':perfil,'informes':informes,'visitas':visitas})

def paciente_perfil(request,access_key):
    perfil = get_object_or_404(Perfil,access_key=access_key)
    if request.method == 'POST':
        form = PerfilForm(request.POST,instance=perfil)
        if form.is_valid():
            form.save()
    return  {'form_paciente':form}

def paciente_paciente(request,access_key):
    perfil = get_object_or_404(Perfil,access_key=access_key)
    ppk = perfil.pacientes.pk
    paciente = get_object_or_404(Paciente, pk = ppk)
    if request.mehod== 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
    return {'form_paciente':form}

# def paciente_informe(request,pk):
#     informe = get_object_or_404(Informe,pk=pk)
#     if request.method=='POST':
#     else:
#         form = InformeForm(instance= informe)
#     return

def paciente_visita(request,pk):
    return  

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