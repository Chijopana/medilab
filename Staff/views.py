from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from Perfiles.models import *
from Pacientes.models import Visita
from .models import *
from .filters import PerfilFilter,VisitaFilter
from .forms import *
from Pacientes.forms import *


# Create your views here.
# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def lobby(request):
    return render(request,'staff/lobby.html')

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def lista_pacientes(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    if request.user.has_perm('auth._Todo'):
        perfiles = None
    else:
        if request.user.has_perm('auth._Es_Medico'):   
            pacientes = perfil.medico.pacientes.all()
            key = [luz.perfil.pk for luz in pacientes]
        elif request.user.has_perm('auth._Es_Enfermero'):
            pacientes = perfil.enfermero.pacientes.all()
            key = [luz.perfil.pk for luz in pacientes]
        else:
            key = [-10]
        perfiles = Perfil.objects.filter(pk__in=key)
    filtro_pacientes = PerfilFilter(request.GET, queryset=perfiles)
    paginator = Paginator(filtro_pacientes.qs, 10) # 10 empleados por página
    page_number = request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    return render(request,'staff/lista_pacientes.html',{'filter':filtro_pacientes, 'page_obj':page_obj})

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def paciente_ind(request,access_key):
    indiv = get_object_or_404(Perfil,access_key=access_key)
    return render(request,'staff/paciente_ind.html',{'paciente':indiv})

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def paciente_ind_edit(request,access_key):
    ind_perfil = get_object_or_404(Perfil,access_key=access_key)
    ppk = ind_perfil.pacientes.pk
    ind_pac = get_object_or_404(Paciente, pk = ppk)
    if request.method == 'POST':
        form1 = PerfilForm(request.POST,instance=ind_perfil)
        form2 = PacienteForm(request.POST, instance=ind_pac)
        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()
            return redirect('staff/paciente_ind', access_key=access_key)
    else:
        form1 = PerfilForm(instance = ind_perfil)
        form2 = PacienteForm(instance = ind_pac)
    return render(request,'staff/paciente_ind_edit.html',{'form1':form1,'form2':form2,'paciente':ind_perfil})

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def paciente_ind_mod_medicacion(request, access_key, pk):
    medicacion = get_object_or_404(Medicacion, pk=pk)
    if request.method == 'POST':
        form = MedicacionForm(request.POST,instance=medicacion)
        if form.is_valid():
            form.save()
            return redirect('staff/paciente_ind', access_key=access_key)
    else:
        form = MedicacionForm(instance= medicacion)
    return render(request,'staff/paciente_ind_mod_medicacion.html',{'form':form,'medicacion':medicacion})

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def paciente_ind_nueva_medicacion(request, access_key):
    pacient = get_object_or_404(Perfil,access_key=access_key)
    if request.method == 'POST':
        form = MedicacionForm(request.POST)
        if form.is_valid():
            medic = form.save(commit=False)
            medic.perfil = pacient
            medic.save()
            return redirect('staff/paciente_ind', access_key=access_key)
    else:
        form = MedicacionForm()
    return render(request, 'staff/paciente_ind_nueva_medicacion.html',{'form':form})

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def paciente_ind_del_medicacion(request, access_key, pk):
    medicacion = get_object_or_404(Medicacion,pk=pk)
    if request.method == 'POST':
        medicacion.delete()
        return redirect('staff/paciente_ind', access_key=access_key)
    return render(request,'staff/del_med.html')

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def lista_consultas(request):
    perfil  = get_object_or_404(Perfil, user = request.user)
    visitax = perfil.medico.visita.all()
    filtro_visitas = VisitaFilter(request.GET, queryset=visitax)
    paginator = Paginator(filtro_visitas.qs, 15) # 15 empleados por página
    page_number = request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    return render(request,'staff/lista_consultas.html',{'page_obj':page_obj,'filter':filtro_visitas})

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def mod_consultas(request,pk):
    consulta = get_object_or_404(Visita,pk=pk)
    if request.method=='POST':
        form = VisitaFormMedico(request.POST,instance=consulta)
        if form.is_valid():
            form.save()
            return redirect('staff/lista_consultas')
    else:
        form = VisitaFormMedico(instance=consulta)
    return render(request,'staff/mod_consultas.html',{'form':form})

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def del_consultas(request,pk):
    consulta = get_object_or_404(Visita,pk=pk)
    if request.method == 'POST':
        consulta.delete()
        return redirect('staff/lista_consultas')
    return render(request,'staff/del_consultas.html')

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def nueva_consultas(request):
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
    return render(request,'staff/nueva_consultas.html',{'form':form})

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def sf_perfil(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    return render(request,'staff/sf_perfil.html',{'perfil':perfil})

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def sf_mod_perfil(request,access_key):
    ind_perfil = get_object_or_404(Perfil,access_key=access_key)
    if request.method == 'POST':
        form = PerfilForm(request.POST,instance=ind_perfil)
        if form.is_valid():
            form.save()
            return redirect('staff/perfil')
    else:
        form = PerfilForm(instance = ind_perfil)
    return render(request,'staff/sf_mod_perfil.html',{'form':form,'staff':ind_perfil})

# def lista_enfermedades(request):
#     return render(request,'staff/lista_enfermedades.html')

# @login_required
# @permission_required(['auth._Es_Medico','auth._Es_Enfermero'], login_url='error_404')
def inbox(request):
    perfil = get_object_or_404(Perfil, user = request.user)
    medic = get_object_or_404(Medico,perfil=perfil)
    resultados  = medic.resultados_pruebas.all()
    return render(request,'staff/inbox.html',{'resultados':resultados})