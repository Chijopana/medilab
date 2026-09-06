"""
Panel del personal médico.

Todas las vistas exigen el rol de médico y, cuando actúan sobre un paciente
concreto, comprueban además que exista relación asistencial (`Medico.atiende`).
Sin esa segunda comprobación, conocer el `access_key` de un paciente bastaría
para leer su historia clínica.
"""
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from Enfermedades.models import Cardiaco, CancerMama, Diabetes, Lunares, Pneumonia
from expedientes.models import Expediente
from Hub.audit import AuditLog
from Hub.decorators import medico_requerido
from Pacientes.forms import VisitaForm, VisitaFormMedico
from Pacientes.models import Visita
from Perfiles.forms import PacienteForm, PerfilForm
from Perfiles.models import Paciente, Perfil
from Staff.forms import MedicacionForm

# Modelos de datos clínicos consultables desde la API de detección.
MODELOS_ENFERMEDAD = {
    'CancerMama': CancerMama,
    'Diabetes': Diabetes,
    'Pneumonia': Pneumonia,
    'Lunares': Lunares,
    'Cardiaco': Cardiaco,
}


def _paciente_del_medico(request, access_key):
    """Obtiene el paciente por access_key comprobando la relación asistencial.

    Devuelve 404 (no 403) si el médico no le atiende: así no se confirma
    siquiera que ese access_key exista.
    """
    perfil = get_object_or_404(Perfil, access_key=access_key)
    paciente = Paciente.objects.filter(perfil=perfil).first()
    if paciente is None or not request.medico.atiende(paciente):
        AuditLog.acceso_denegado(request.user, 'panel médico',
                                 f'paciente {access_key}', request=request)
        raise Http404
    return paciente


# ---------------------------------------------------------------------------
# Panel principal
# ---------------------------------------------------------------------------
@medico_requerido
def lobby(request):
    medico = request.medico
    ahora = timezone.now()
    proximas = (Visita.objects
                .filter(medico=medico, hora_fecha__gte=ahora)
                .select_related('paciente__perfil')
                .order_by('hora_fecha')[:5])
    contexto = {
        'total_pacientes': medico.pacientes.count(),
        'visitas_pendientes': Visita.objects.filter(
            medico=medico, hora_fecha__gte=ahora,
            estado=Visita.Estado.PENDIENTE).count(),
        'total_expedientes': Expediente.objects.filter(doctor=medico).count(),
        'proximas_visitas': proximas,
        'seccion': 'inicio',
    }
    return render(request, 'staff/lobby.html', contexto)


# ---------------------------------------------------------------------------
# Pacientes
# ---------------------------------------------------------------------------
@medico_requerido
def lista_pacientes(request):
    busqueda = request.GET.get('q', '').strip()
    pacientes = (request.medico.pacientes
                 .select_related('perfil')
                 .order_by('perfil__apellido', 'perfil__nombre'))
    if busqueda:
        pacientes = pacientes.filter(
            Q(perfil__nombre__icontains=busqueda)
            | Q(perfil__apellido__icontains=busqueda)
            | Q(perfil__dni__icontains=busqueda)
        )
    pagina = Paginator(pacientes, 15).get_page(request.GET.get('page'))
    return render(request, 'staff/lista_pacientes.html',
                  {'pagina': pagina, 'busqueda': busqueda, 'seccion': 'pacientes'})


@medico_requerido
def paciente_ind(request, access_key):
    paciente = _paciente_del_medico(request, access_key)
    return render(request, 'staff/paciente_ind.html', {
        'perfil': paciente.perfil,
        'paciente': paciente,
        'expedientes': paciente.expediente.select_related('doctor__perfil')[:5],
        'visitas': paciente.visita.select_related('medico__perfil')[:5],
        'medicacion': paciente.medicacion.select_related('medico__perfil')[:5],
        'seccion': 'pacientes',
    })


@medico_requerido
def paciente_ind_edit(request, access_key):
    paciente = _paciente_del_medico(request, access_key)
    perfil = paciente.perfil

    if request.method == 'POST':
        form_perfil = PerfilForm(request.POST, instance=perfil)
        form_paciente = PacienteForm(request.POST, instance=paciente)
        if form_perfil.is_valid() and form_paciente.is_valid():
            form_perfil.save()
            form_paciente.save()
            AuditLog.registrar(request.user, 'MODIFICAR_PACIENTE',
                               f'Paciente {perfil.nombre_completo}',
                               objeto_id=paciente.pk, request=request)
            messages.success(request, 'Datos del paciente actualizados.')
            return redirect(reverse('staff/paciente_ind', kwargs={'access_key': access_key}))
        messages.error(request, 'Revisa los campos marcados en rojo.')
    else:
        form_perfil = PerfilForm(instance=perfil)
        form_paciente = PacienteForm(instance=paciente)

    return render(request, 'staff/paciente_ind_edit.html', {
        'form_perfil': form_perfil,
        'form_paciente': form_paciente,
        'perfil': perfil,
        'seccion': 'pacientes',
    })


@medico_requerido
def visitas(request, access_key):
    paciente = _paciente_del_medico(request, access_key)
    return render(request, 'staff/partials/visitas.html', {
        'visitas': paciente.visita.select_related('medico__perfil', 'paciente__perfil'),
        'perfil': paciente.perfil,
        'seccion': 'pacientes',
    })


@medico_requerido
def expedientes(request, access_key):
    paciente = _paciente_del_medico(request, access_key)
    return render(request, 'staff/partials/expedientes.html', {
        'expedientes': paciente.expediente.select_related('doctor__perfil'),
        'perfil': paciente.perfil,
        'seccion': 'pacientes',
    })


@medico_requerido
def medicacion(request, access_key):
    paciente = _paciente_del_medico(request, access_key)
    return render(request, 'staff/partials/medicacion.html', {
        'medicacion': paciente.medicacion.select_related('medico__perfil'),
        'perfil': paciente.perfil,
        'seccion': 'pacientes',
    })


@medico_requerido
def nueva_medicacion(request, access_key):
    paciente = _paciente_del_medico(request, access_key)

    if request.method == 'POST':
        form = MedicacionForm(request.POST)
        if form.is_valid():
            med = form.save(commit=False)
            med.paciente = paciente
            med.medico = request.medico
            med.save()
            AuditLog.registrar(request.user, 'CREAR_MEDICACION', med.medicina,
                               objeto_id=med.pk, request=request)
            messages.success(request, f'Tratamiento «{med.medicina}» prescrito.')
            return redirect(reverse('staff/medicacion', kwargs={'access_key': access_key}))
    else:
        form = MedicacionForm()

    return render(request, 'staff/nueva_medicacion.html',
                  {'form': form, 'perfil': paciente.perfil, 'seccion': 'pacientes'})


# ---------------------------------------------------------------------------
# Visitas
# ---------------------------------------------------------------------------
@medico_requerido
def lista_consultas(request):
    visitas_qs = (request.medico.visita
                  .select_related('paciente__perfil')
                  .order_by('-hora_fecha'))
    estado = request.GET.get('estado')
    if estado in Visita.Estado.values:
        visitas_qs = visitas_qs.filter(estado=estado)
    pagina = Paginator(visitas_qs, 15).get_page(request.GET.get('page'))
    return render(request, 'staff/lista_consultas.html',
                  {'pagina': pagina, 'estado': estado,
                   'estados': Visita.Estado.choices, 'seccion': 'visitas'})


@medico_requerido
def consulta(request, pk):
    visita = get_object_or_404(Visita.objects.select_related('paciente__perfil'),
                               pk=pk, medico=request.medico)
    if request.method == 'POST':
        form = VisitaForm(request.POST, instance=visita)
        if form.is_valid():
            form.save()
            AuditLog.registrar(request.user, 'MODIFICAR_VISITA', objeto_id=visita.pk,
                               request=request)
            messages.success(request, 'Visita actualizada.')
            return redirect('staff/lista_consultas')
    else:
        form = VisitaForm(instance=visita)
    return render(request, 'staff/consulta_ind.html',
                  {'form': form, 'visita': visita, 'seccion': 'visitas'})


@medico_requerido
def nueva_consulta(request):
    if request.method == 'POST':
        form = VisitaFormMedico(request.POST)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.medico = request.medico
            visita.save()
            AuditLog.registrar(request.user, 'CREAR_VISITA', objeto_id=visita.pk,
                               request=request)
            messages.success(request, 'Visita creada.')
            return redirect('staff/lista_consultas')
    else:
        form = VisitaFormMedico()
    # Solo se pueden citar pacientes propios.
    form.fields['paciente'].queryset = request.medico.pacientes.select_related('perfil')
    return render(request, 'staff/nueva_consulta.html',
                  {'form': form, 'seccion': 'visitas'})


@medico_requerido
@require_POST
def del_consulta(request, pk):
    visita = get_object_or_404(Visita, pk=pk, medico=request.medico)
    AuditLog.registrar(request.user, 'ELIMINAR_VISITA', objeto_id=visita.pk, request=request)
    visita.delete()
    messages.success(request, 'Visita eliminada.')
    return redirect('staff/lista_consultas')


# ---------------------------------------------------------------------------
# Bandeja de expedientes pendientes de firmar
# ---------------------------------------------------------------------------
@medico_requerido
def inbox(request):
    borradores = (request.medico.temporal_expediente
                  .select_related('paciente__perfil')
                  .order_by('-fecha_hora'))
    return render(request, 'staff/inbox.html',
                  {'borradores': borradores, 'seccion': 'inbox'})


# ---------------------------------------------------------------------------
# Perfil del profesional
# ---------------------------------------------------------------------------
@medico_requerido
def perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('staff/perfil')
        messages.error(request, 'Revisa los campos marcados en rojo.')
    else:
        form = PerfilForm(instance=request.perfil)
    return render(request, 'staff/perfil.html',
                  {'form': form, 'perfil': request.perfil, 'seccion': 'perfil'})


# ---------------------------------------------------------------------------
# API interna
# ---------------------------------------------------------------------------
@medico_requerido
def detectar_enfermedad(request, pk):
    """Devuelve los datos clínicos asociados a un expediente, en JSON."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    expediente = get_object_or_404(Expediente, pk=pk)
    if not request.medico.atiende(expediente.paciente) \
            and expediente.doctor_id != request.medico.pk:
        AuditLog.acceso_denegado(request.user, 'detectar_enfermedad',
                                 f'expediente {pk}', request=request)
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    modelo = MODELOS_ENFERMEDAD.get(expediente.especialidad)
    if modelo is None:
        return JsonResponse({'error': 'Especialidad no válida'}, status=400)

    return JsonResponse({'resultado': list(modelo.objects.filter(
        expediente=expediente).values())})
