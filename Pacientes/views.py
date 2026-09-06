"""
Panel del paciente.

`@paciente_requerido` deja el paciente autenticado en `request.paciente`; todas
las consultas parten de ahí, de forma que un paciente nunca puede alcanzar los
datos de otro aunque manipule los identificadores de la URL.
"""
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from Enfermedades.models import Cardiaco, CancerMama, Diabetes, Lunares, Pneumonia
from expedientes.models import Expediente
from Hub.audit import AuditLog
from Hub.decorators import paciente_requerido
from Pacientes.forms import VisitaFormPaciente
from Pacientes.models import Visita
from Perfiles.forms import PacienteForm, PerfilForm

MODELOS_ENFERMEDAD = {
    'CancerMama': CancerMama,
    'Diabetes': Diabetes,
    'Pneumonia': Pneumonia,
    'Lunares': Lunares,
    'Cardiaco': Cardiaco,
}


@paciente_requerido
def pagina_principal(request):
    ahora = timezone.now()
    proxima = (request.paciente.visita
               .filter(hora_fecha__gte=ahora)
               .select_related('medico__perfil')
               .order_by('hora_fecha')
               .first())
    contexto = {
        'proxima_visita': proxima,
        'total_visitas': request.paciente.visita.count(),
        'total_expedientes': request.paciente.expediente.count(),
        'medicacion_activa': sum(1 for m in request.paciente.medicacion.all() if m.activa),
    }
    contexto['seccion'] = 'inicio'
    return render(request, 'pacientes/pagina_principal.html', contexto)


@paciente_requerido
def historial_medico(request):
    expedientes = (request.paciente.expediente
                   .select_related('doctor__perfil')
                   .order_by('-fecha_hora'))
    pagina = Paginator(expedientes, 10).get_page(request.GET.get('page'))
    return render(request, 'pacientes/historial_medico.html',
                  {'pagina': pagina, 'seccion': 'historial'})


@paciente_requerido
def visitas(request):
    visitas_qs = request.paciente.visita.select_related('medico__perfil')
    pagina = Paginator(visitas_qs, 10).get_page(request.GET.get('page'))
    return render(request, 'pacientes/visitas.html',
                  {'pagina': pagina, 'seccion': 'visitas'})


@paciente_requerido
def nueva_visita(request):
    if request.method == 'POST':
        form = VisitaFormPaciente(request.POST)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.paciente = request.paciente
            visita.save()
            AuditLog.registrar(request.user, 'CREAR_VISITA', objeto_id=visita.pk,
                               request=request)
            messages.success(request, 'Visita solicitada correctamente.')
            return redirect('pacientes/visitas')
    else:
        form = VisitaFormPaciente()
    return render(request, 'pacientes/nueva_visita.html',
                  {'form': form, 'seccion': 'visitas'})


@paciente_requerido
def mod_visita(request, pk):
    # Filtrar por paciente es lo que impide editar la visita de otra persona.
    visita = get_object_or_404(Visita, pk=pk, paciente=request.paciente)
    if request.method == 'POST':
        form = VisitaFormPaciente(request.POST, instance=visita)
        if form.is_valid():
            form.save()
            AuditLog.registrar(request.user, 'MODIFICAR_VISITA', objeto_id=visita.pk,
                               request=request)
            messages.success(request, 'Visita actualizada.')
            return redirect('pacientes/visitas')
    else:
        form = VisitaFormPaciente(instance=visita)
    return render(request, 'pacientes/modificar_visita.html',
                  {'form': form, 'visita': visita, 'seccion': 'visitas'})


@paciente_requerido
@require_POST
def del_visita(request, pk):
    visita = get_object_or_404(Visita, pk=pk, paciente=request.paciente)
    AuditLog.registrar(request.user, 'ELIMINAR_VISITA', objeto_id=visita.pk, request=request)
    visita.delete()
    messages.success(request, 'Visita cancelada.')
    return redirect('pacientes/visitas')


@paciente_requerido
def perfil(request):
    if request.method == 'POST':
        form_perfil = PerfilForm(request.POST, instance=request.perfil)
        form_paciente = PacienteForm(request.POST, instance=request.paciente)
        if form_perfil.is_valid() and form_paciente.is_valid():
            form_perfil.save()
            form_paciente.save()
            messages.success(request, 'Datos guardados.')
            return redirect('pacientes/perfil')
        messages.error(request, 'Revisa los campos marcados en rojo.')
    else:
        form_perfil = PerfilForm(instance=request.perfil)
        form_paciente = PacienteForm(instance=request.paciente)
    return render(request, 'pacientes/perfil.html', {
        'form_perfil': form_perfil,
        'form_paciente': form_paciente,
        'perfil': request.perfil,
        'seccion': 'perfil',
    })


@paciente_requerido
def medicacion(request):
    tratamientos = request.paciente.medicacion.select_related('medico__perfil')
    return render(request, 'pacientes/medicacion.html',
                  {'medicacion': tratamientos, 'seccion': 'medicacion'})


@paciente_requerido
def detectar_enfermedad(request, pk):
    """Datos clínicos de un expediente propio, en JSON."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    expediente = get_object_or_404(Expediente, pk=pk)
    if expediente.paciente_id != request.paciente.pk:
        AuditLog.acceso_denegado(request.user, 'detectar_enfermedad',
                                 f'expediente {pk}', request=request)
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    modelo = MODELOS_ENFERMEDAD.get(expediente.especialidad)
    if modelo is None:
        return JsonResponse({'error': 'Especialidad no válida'}, status=400)

    return JsonResponse({'resultado': list(modelo.objects.filter(
        expediente=expediente).values())})
