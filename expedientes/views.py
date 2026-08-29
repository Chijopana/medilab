import os
import numpy as np
from PIL import Image
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from .models import Expediente
from tensorflow.keras.applications.inception_v3 import preprocess_input as preprocess_inceptionv3
 
MODELOS_IA = {
    'Pneumonia': {
        'tipo': 'binario',
        'path': os.path.join(settings.BASE_DIR, 'expedientes', 'modelos_ia', 'pneumonia.h5'),
        'nombre_visible': 'Neumonía (radiografía de tórax)',
        'etiqueta_negativa': 'Sin signos de neumonía',
        'etiqueta_positiva': 'Posible neumonía detectada',
    },
    'Lunares': {
        'tipo': 'binario',
        'path': os.path.join(settings.BASE_DIR, 'expedientes', 'modelos_ia', 'lunares.keras'),
        'nombre_visible': 'Lunares (melanoma)',
        'etiqueta_negativa': 'No parece melanoma',
        'etiqueta_positiva': 'Posible melanoma detectado',
    },
    'Tuberculosis': {
        'tipo': 'binario',
        'path': os.path.join(settings.BASE_DIR, 'expedientes', 'modelos_ia', 'tuberculosis.h5'),
        'nombre_visible': 'Tuberculosis (radiografía de tórax)',
        'etiqueta_negativa': 'Sin signos de tuberculosis',
        'etiqueta_positiva': 'Posible tuberculosis detectada',
        'normalizador': 'inceptionv3',
    },
    'TumorCerebral': {
    'tipo': 'binario',
    'path': os.path.join(settings.BASE_DIR, 'expedientes', 'modelos_ia', 'tumor_cerebral.h5'),
    'nombre_visible': 'Tumor cerebral (resonancia magnética)',
    'etiqueta_negativa': 'Sin signos de tumor',
    'etiqueta_positiva': 'Posible tumor cerebral detectado',
    'tamano': (240, 240),
},
}
 
_modelos_cache = {}
 
def _cargar_modelo(especialidad):
    if especialidad not in _modelos_cache:
        import tensorflow as tf
        _modelos_cache[especialidad] = tf.keras.models.load_model(MODELOS_IA[especialidad]['path'])
    return _modelos_cache[especialidad]
 
def _preprocesar_imagen(imagen_file, tamano=(224, 224), normalizador=None):
    img = Image.open(imagen_file).convert('RGB').resize(tamano)
    arr = np.array(img).astype('float32')
    if normalizador == 'inceptionv3':
        arr = preprocess_inceptionv3(arr)
    else:
        arr = arr / 255.0
    return np.expand_dims(arr, axis=0)
 
 
def expediente_IA_2(request):
    resultado = None
    especialidad = request.POST.get('especialidad', 'Pneumonia')
 
    if request.method == 'POST' and request.FILES.get('imagen'):
        imagen = request.FILES['imagen']
        info = MODELOS_IA[especialidad]
        modelo = _cargar_modelo(especialidad)
        entrada = _preprocesar_imagen(imagen, info.get('tamano', (224, 224)), info.get('normalizador'))
        salida = modelo.predict(entrada)[0]
        print("ESPECIALIDAD:", especialidad, "SALIDA CRUDA:", salida)
 
        if info['tipo'] == 'binario':
            prediccion = float(salida[0])
            es_positivo = prediccion >= 0.5
            confianza = prediccion if es_positivo else (1 - prediccion)
            resultado = {
                'diagnostico': info['etiqueta_positiva'] if es_positivo else info['etiqueta_negativa'],
                'confianza': round(confianza * 100, 1),
                'positivo': es_positivo,
            }
        else:  # multiclase
            indice = int(np.argmax(salida))
            clase = info['clases'][indice]
            confianza = float(salida[indice])
            resultado = {
                'diagnostico': clase,
                'confianza': round(confianza * 100, 1),
                'positivo': clase != info['clase_normal'],
            }
 
    contexto = {
        'especialidad': especialidad,
        'especialidades': MODELOS_IA,
        'resultado': resultado,
    }
    return render(request, 'expedientes/expediente_IA_2.html', contexto)
 
 
def ver_expediente(request, expediente_id):
    expediente = get_object_or_404(Expediente, id=expediente_id)
    return render(request, 'expedientes/expedientes.html', {'expediente': expediente})
 
def generate_pdf(expediente):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
 
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1 * inch, height - 1 * inch, "Medilab")
 
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, height - 1.5 * inch, f"Nombre: {expediente.paciente.perfil.nombre}")
    p.drawString(1 * inch, height - 1.75 * inch, f"Apellido: {expediente.paciente.perfil.apellido}")
    p.drawString(1 * inch, height - 2 * inch, f"Email: {expediente.paciente.perfil.email}")
    p.drawString(1 * inch, height - 2.25 * inch, f"DNI: {expediente.paciente.perfil.dni}")
    p.drawString(1 * inch, height - 2.5 * inch, f"Tel.: {expediente.paciente.perfil.telefono}")
    p.drawString(1 * inch, height - 2.75 * inch, f"N.S.S.: {expediente.paciente.perfil.numero_seguro_social}")
 
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, height - 3.25 * inch, "Información del Expediente")
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, height - 3.5 * inch, f"Fecha expediente: {expediente.fecha_hora}")
    p.drawString(1 * inch, height - 3.75 * inch, f"Doctor/a: {expediente.doctor.perfil.nombre} {expediente.doctor.perfil.apellido}")
 
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, height - 4.25 * inch, "Información Adicional")
    p.setFont("Helvetica", 12)
    if expediente.especialidad == "CancerMama":
        p.drawString(1 * inch, height - 4.5 * inch, "Especialidad: Oncología")
    elif expediente.especialidad == "Diabetes":
        p.drawString(1 * inch, height - 4.5 * inch, "Especialidad: Endocrinología")
    elif expediente.especialidad == "Pneumonia":
        p.drawString(1 * inch, height - 4.5 * inch, "Especialidad: Neumología")
    elif expediente.especialidad == "Lunares":
        p.drawString(1 * inch, height - 4.5 * inch, "Especialidad: Dermatología")
    elif expediente.especialidad == "Cardiaco":
        p.drawString(1 * inch, height - 4.5 * inch, "Especialidad: Cardiología")
 
    p.drawString(1 * inch, height - 4.75 * inch, f"Antecedentes: {expediente.antecedentes}")
 
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, height - 5.25 * inch, "Contacto")
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, height - 5.5 * inch, "teléfono: 639 482 715")
    p.drawString(1 * inch, height - 5.75 * inch, "email: info@example.com")
    p.drawString(1 * inch, height - 6 * inch, "pagina web: http://127.0.0.1:8000/")
 
    p.showPage()
    p.save()
 
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
 
def descargar_expediente_pdf(request, expediente_id):
    expediente = get_object_or_404(Expediente, id=expediente_id)
    pdf = generate_pdf(expediente)
 
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="expediente_{expediente_id}.pdf"'
    response.write(pdf)
    return response
 
def expedientes(request):
    contexto={
        'perfil':'profile',
        'medicacion': 'medicacion',
        'expedientes':'expediente'
    }
    return render(request,'expedientes/expedientes.html',contexto)
 
def expediente_chatbot_1(request):
    contexto={
        'perfil':'profile',
        'medicacion': 'medicacion',
        'expedientes':'expediente'
    }
    return render(request,'expedientes/expediente_chatbot_1.html',contexto)
 