"""
Expedientes clínicos: consulta, descarga en PDF y diagnóstico asistido por IA.

Ninguna vista de este módulo es pública: la historia clínica solo la ve el
propio paciente, un médico con relación asistencial o el personal de staff
(ver `Hub.accesos`).
"""
import logging
from io import BytesIO

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from expedientes import carga_modelos
from Hub.accesos import medico_de, paciente_de, puede_ver_expediente
from Hub.audit import AuditLog

from .models import Expediente

logger = logging.getLogger(__name__)

# Catálogo de modelos de IA disponibles. La clave es lo que llega del formulario:
# se valida siempre contra este diccionario antes de usarla.
#
# `tamano` y `escalado` NO son decorativos: tienen que coincidir con lo que el
# modelo espera. Si el tamaño no cuadra, Keras vuelve a trazar el grafo en cada
# petición y la predicción se queda colgada durante minutos; si el escalado no
# cuadra, el resultado sale, pero no significa nada.
#   escalado '0-1'   -> se divide entre 255 aquí
#   escalado 'crudo' -> se pasan los píxeles 0-255 tal cual (el modelo lleva
#                       una capa Rescaling propia y volver a escalar lo rompería)
MODELOS_IA = {
    'Pneumonia': {
        'fichero': 'pneumonia.h5',
        'nombre_visible': 'Neumonía (radiografía de tórax)',
        'etiqueta_negativa': 'Sin signos de neumonía',
        'etiqueta_positiva': 'Posible neumonía detectada',
        'tamano': (224, 224),
        'escalado': '0-1',
    },
    'Lunares': {
        'fichero': 'lunares.keras',
        'nombre_visible': 'Lunares (melanoma)',
        'etiqueta_negativa': 'No parece melanoma',
        'etiqueta_positiva': 'Posible melanoma detectado',
        'tamano': (224, 224),
        'escalado': '0-1',
    },
    'Tuberculosis': {
        # Se sirve desde el .keras convertido; el .h5 original es la fuente.
        # Ver expedientes/carga_modelos.py: Keras 3 no puede deserializar el .h5.
        'fichero': 'tuberculosis.keras',
        'fichero_origen': 'tuberculosis.h5',
        'nombre_visible': 'Tuberculosis (radiografía de tórax)',
        'etiqueta_negativa': 'Sin signos de tuberculosis',
        'etiqueta_positiva': 'Posible tuberculosis detectada',
        # InceptionV3 a 300x300, con Rescaling(1/255) dentro del propio modelo.
        'tamano': (300, 300),
        'escalado': 'crudo',
    },
    'TumorCerebral': {
        'fichero': 'tumor_cerebral.h5',
        'nombre_visible': 'Tumor cerebral (resonancia magnética)',
        'etiqueta_negativa': 'Sin signos de tumor',
        'etiqueta_positiva': 'Posible tumor cerebral detectado',
        'tamano': (240, 240),
        'escalado': '0-1',
    },
}

TIPOS_IMAGEN_ACEPTADOS = {'image/jpeg', 'image/png', 'image/webp', 'image/bmp'}


def _preprocesar_imagen(imagen_file, tamano, escalado):
    import numpy as np
    from PIL import Image

    img = Image.open(imagen_file).convert('RGB').resize(tamano)
    arr = np.array(img).astype('float32')
    if escalado == '0-1':
        arr = arr / 255.0
    return np.expand_dims(arr, axis=0)


def _validar_imagen(imagen):
    """Devuelve un mensaje de error, o None si la imagen es aceptable."""
    if imagen.size > settings.MAX_UPLOAD_SIZE:
        limite = settings.MAX_UPLOAD_SIZE // (1024 * 1024)
        return f'La imagen supera el límite de {limite} MB.'
    if imagen.content_type not in TIPOS_IMAGEN_ACEPTADOS:
        return 'Formato no admitido. Sube una imagen JPG, PNG, WEBP o BMP.'
    try:
        from PIL import Image
        Image.open(imagen).verify()   # comprueba que sea realmente una imagen
        imagen.seek(0)
    except Exception:
        return 'El fichero no es una imagen válida o está dañado.'
    return None


# ---------------------------------------------------------------------------
# Diagnóstico por IA
# ---------------------------------------------------------------------------
@login_required
def diagnostico_ia(request):
    resultado = None
    # Solo se acepta una especialidad del catálogo; cualquier otra cosa se ignora.
    especialidad = request.POST.get('especialidad') or request.GET.get('especialidad')
    if especialidad not in MODELOS_IA:
        especialidad = 'Pneumonia'

    if request.method == 'POST':
        imagen = request.FILES.get('imagen')
        if imagen is None:
            messages.error(request, 'Selecciona una imagen para analizar.')
        elif (error := _validar_imagen(imagen)):
            messages.error(request, error)
        elif not carga_modelos.disponible(MODELOS_IA[especialidad]):
            messages.error(
                request,
                'El modelo de este análisis todavía no está instalado en el servidor. '
                'Consulta el README para descargarlo.',
            )
        else:
            info = MODELOS_IA[especialidad]
            try:
                modelo = carga_modelos.cargar(especialidad, info)
                entrada = _preprocesar_imagen(imagen, info['tamano'], info['escalado'])
                salida = modelo.predict(entrada, verbose=0)[0]
                prediccion = float(salida[0])
                es_positivo = prediccion >= 0.5
                confianza = prediccion if es_positivo else (1 - prediccion)
                resultado = {
                    'diagnostico': info['etiqueta_positiva'] if es_positivo
                                   else info['etiqueta_negativa'],
                    'confianza': round(confianza * 100, 1),
                    'positivo': es_positivo,
                    'analisis': info['nombre_visible'],
                }
                AuditLog.registrar(
                    request.user, 'DIAGNOSTICO_IA',
                    f"Análisis: {especialidad} - Resultado: {resultado['diagnostico']}",
                    request=request,
                )
            except Exception:
                logger.exception('Fallo al ejecutar el modelo %s', especialidad)
                messages.error(
                    request,
                    'No hemos podido analizar la imagen. Inténtalo de nuevo en unos minutos.',
                )

    contexto = {
        'especialidad': especialidad,
        'especialidades': MODELOS_IA,
        'resultado': resultado,
    }
    return render(request, 'expedientes/diagnostico_ia.html', contexto)


# ---------------------------------------------------------------------------
# Consulta de expedientes
# ---------------------------------------------------------------------------
@login_required
def mis_expedientes(request):
    """Lista los expedientes visibles para quien consulta.

    Un paciente ve los suyos; un médico, los de los pacientes que atiende.
    """
    paciente = paciente_de(request.user)
    if paciente is not None:
        expedientes = Expediente.objects.filter(paciente=paciente)
        titulo = 'Mis expedientes'
    else:
        medico = medico_de(request.user)
        if medico is None:
            expedientes = Expediente.objects.none()
        else:
            # Los que ha firmado él y los de los pacientes que tiene asignados.
            expedientes = Expediente.objects.filter(
                Q(doctor=medico) | Q(paciente__medicos=medico)).distinct()
        titulo = 'Expedientes de mis pacientes'

    expedientes = expedientes.select_related('paciente__perfil', 'doctor__perfil')
    pagina = Paginator(expedientes, 10).get_page(request.GET.get('page'))
    return render(request, 'expedientes/lista_expedientes.html',
                  {'pagina': pagina, 'titulo': titulo})


@login_required
def ver_expediente(request, expediente_id):
    expediente = get_object_or_404(
        Expediente.objects.select_related('paciente__perfil', 'doctor__perfil'),
        id=expediente_id,
    )
    if not puede_ver_expediente(request.user, expediente):
        AuditLog.acceso_denegado(request.user, 'ver_expediente',
                                 f'expediente {expediente_id}', request=request)
        raise Http404

    AuditLog.registrar(request.user, 'VER_EXPEDIENTE', objeto_id=expediente.id,
                       request=request)
    return render(request, 'expedientes/expediente_detalle.html',
                  {'expediente': expediente})


@login_required
def descargar_expediente_pdf(request, expediente_id):
    expediente = get_object_or_404(
        Expediente.objects.select_related('paciente__perfil', 'doctor__perfil'),
        id=expediente_id,
    )
    if not puede_ver_expediente(request.user, expediente):
        AuditLog.acceso_denegado(request.user, 'descargar_expediente_pdf',
                                 f'expediente {expediente_id}', request=request)
        raise Http404

    AuditLog.registrar(request.user, 'DESCARGAR_EXPEDIENTE', objeto_id=expediente.id,
                       request=request)

    respuesta = HttpResponse(generar_pdf(expediente), content_type='application/pdf')
    respuesta['Content-Disposition'] = (
        f'attachment; filename="expediente_{expediente_id}.pdf"'
    )
    return respuesta


def generar_pdf(expediente):
    """Genera el PDF del expediente con ReportLab."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    ancho, alto = letter
    perfil = expediente.paciente.perfil
    medico = expediente.doctor.perfil

    y = alto - 1 * inch

    def linea(texto, salto=0.25, fuente='Helvetica', tamano=12):
        nonlocal y
        p.setFont(fuente, tamano)
        p.drawString(1 * inch, y, texto)
        y -= salto * inch

    linea('Medilab', salto=0.45, fuente='Helvetica-Bold', tamano=16)

    linea('Datos del paciente', salto=0.3, fuente='Helvetica-Bold', tamano=13)
    linea(f'Nombre: {perfil.nombre_completo or "-"}')
    linea(f'DNI: {perfil.dni}')
    linea(f'Email: {perfil.email}')
    linea(f'Teléfono: {perfil.telefono or "-"}')
    linea(f'N.S.S.: {perfil.numero_seguro_social or "-"}', salto=0.45)

    linea('Información del expediente', salto=0.3, fuente='Helvetica-Bold', tamano=13)
    linea(f'Fecha: {expediente.fecha_hora:%d/%m/%Y %H:%M}' if expediente.fecha_hora
          else 'Fecha: -')
    linea(f'Profesional: {medico.nombre_completo or "-"}')
    linea(f'Especialidad: {expediente.departamento}', salto=0.45)

    linea('Contenido clínico', salto=0.3, fuente='Helvetica-Bold', tamano=13)
    for etiqueta, valor in (('Antecedentes', expediente.antecedentes),
                            ('Diagnóstico', expediente.diagnostico),
                            ('Tratamiento', expediente.tratamiento)):
        if not valor:
            continue
        linea(f'{etiqueta}:', salto=0.22, fuente='Helvetica-Bold', tamano=11)
        # Troceado sencillo para que el texto largo no se salga de la página.
        for trozo in _trocear(valor, 90):
            linea(trozo, salto=0.2, tamano=10)
        y -= 0.1 * inch

    y = min(y, 1.4 * inch)
    linea('Contacto: 639 482 715 · info@example.com', salto=0.2,
          fuente='Helvetica-Oblique', tamano=9)

    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def _trocear(texto, ancho):
    """Parte un texto en líneas de como mucho `ancho` caracteres, sin cortar palabras."""
    lineas, actual = [], ''
    for palabra in texto.split():
        if len(actual) + len(palabra) + 1 > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = f'{actual} {palabra}'.strip()
    if actual:
        lineas.append(actual)
    return lineas
