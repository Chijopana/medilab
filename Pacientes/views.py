from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from Perfiles.models import *
from Enfermedades.models import *
from Staff.models import *
from Staff.forms import *
from Pacientes.forms import *

# Create your views here.
# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def pagina_principal(request):
    return render(request,'pacientes/pagina_principal.html')

# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def analisis(request):
    # Con qué lo conecto?
    return render(request,'pacientes/analisis.html')

# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def vacunas(request):
    # Con qué lo conecto?
    return render(request,'pacientes/vacunas.html')

# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def diagnosticos(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    diag = perfil.diagnosticos.all()
    return render(request,'pacientes/diagnosticos.html', {'diagnosticos':diag})

# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def visitas(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    visitax = perfil.pacientes.visita.all()

    return render(request,'pacientes/visitas.html',{'visitas':visitax})

# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def agendar_visita(request):
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
    return render(request,'pacientes/agendar_visita.html',{'form':form})

# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def mod_visitas(request,pk):
    visitax = get_object_or_404(Visita,pk=pk)
    if request.method=='POST':
        form = VisitaFormPaciente(request.POST,instance=visitax)
        if form.is_valid():
            form.save()
            return redirect('pacientes/visitas')
    else:
        form = VisitaFormPaciente(instance=visitax)
    return render(request, 'pacientes/mod_visitas.html',{'form':form})

# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def del_visitas(request,pk):
    visitax = get_object_or_404(Visita,pk=pk)
    if request.method=='POST':
        visitax.delete()
        return redirect('pacientes/visitas')
    return render(request,'pacientes/del_visita.html')

# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def perfil(request):
    perfilx = get_object_or_404(Perfil,user=request.user)
    return render(request, 'pacientes/perfil.html',{'perfil':perfilx})

# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def mod_perfil(request):
    ind_perfil = get_object_or_404(Perfil,user=request.user)
    ppk = ind_perfil.pacientes.pk
    ind_pac = get_object_or_404(Paciente, pk = ppk)
    if request.method == 'POST':
        form1 = PerfilForm(request.POST,instance=ind_perfil)
        form2 = PacienteForm(request.POST, instance=ind_pac)
        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()  
            return redirect('pacientes/perfil')
    else:
        form1 = PerfilForm(instance = ind_perfil)
        form2 = PacienteForm(instance = ind_pac)
    return render(request, 'pacientes/mod_perfil.html',{'form1':form1,'form2':form2,'paciente':ind_perfil})

# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def medicacion(request):
    perfil = get_object_or_404(Perfil,user=request.user)
    medicar = perfil.medicacion.all()
    return render(request,'pacientes/medicacion.html',{'medicacion':medicar})

# @login_required
# @permission_required('auth._Es_Paciente', login_url='error_404')
def consultas(request):
    # bot
    return render(request,'pacientes/consultas.html')