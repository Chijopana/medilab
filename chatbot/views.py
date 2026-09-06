"""
Chatbot de intenciones de Medilab.

El modelo de Keras se carga de forma perezosa (la primera vez que alguien
escribe) y se cachea en memoria: importar TensorFlow al arrancar hacía que
cualquier comando de `manage.py` tardase decenas de segundos.

Para reentrenarlo tras editar `modelo/intents.json`:
    python manage.py entrenar_chatbot
"""
import json
import logging
import os
import pickle
import random
import unicodedata

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

MODELO_DIR = os.path.join(os.path.dirname(__file__), 'modelo')
MAX_LEN = 20                      # debe coincidir con el comando de entrenamiento
LONGITUD_MAXIMA_MENSAJE = 500

# Por debajo de esta confianza preferimos admitir que no lo hemos entendido
# antes que soltar una respuesta al azar.
UMBRAL_CONFIANZA = 0.45

RESPUESTAS_SIN_ENTENDER = [
    'No estoy seguro de haber entendido. Puedo ayudarte con citas, historial, '
    'medicación, expedientes en PDF o el diagnóstico por IA. ¿Cuál de esos?',
    'Eso no lo sé. Prueba a preguntarme cómo pedir cita, ver tu historial o '
    'usar el diagnóstico con IA.',
]

# Se rellena en la primera petición: (modelo, tokenizer, label_encoder, intents, keras)
_recursos = None


def normalizar(texto):
    """Minúsculas y sin tildes: igual que en el entrenamiento."""
    texto = texto.lower().strip()
    sin_tildes = unicodedata.normalize('NFD', texto)
    return ''.join(c for c in sin_tildes if unicodedata.category(c) != 'Mn')


def _cargar_recursos():
    """Carga modelo, tokenizer, codificador e intenciones una sola vez."""
    global _recursos
    if _recursos is None:
        from tensorflow import keras  # import pesado: solo cuando hace falta

        modelo = keras.models.load_model(os.path.join(MODELO_DIR, 'chat_model.keras'))
        with open(os.path.join(MODELO_DIR, 'tokenizer.pickle'), 'rb') as f:
            tokenizer = pickle.load(f)
        with open(os.path.join(MODELO_DIR, 'label_encoder.pickle'), 'rb') as f:
            label_encoder = pickle.load(f)
        with open(os.path.join(MODELO_DIR, 'intents.json'), encoding='utf-8') as f:
            intents = json.load(f)
        _recursos = (modelo, tokenizer, label_encoder, intents, keras)
    return _recursos


def home(request):
    return render(request, 'chatbot/chatbot.html')


@require_POST
def get_response(request):
    mensaje = (request.POST.get('message') or '').strip()
    if not mensaje:
        return JsonResponse({'response': '¿En qué puedo ayudarte?'})
    if len(mensaje) > LONGITUD_MAXIMA_MENSAJE:
        return JsonResponse(
            {'response': 'El mensaje es demasiado largo. Resúmelo, por favor.'},
            status=400,
        )

    try:
        import numpy as np

        modelo, tokenizer, label_encoder, intents, keras = _cargar_recursos()

        secuencia = keras.preprocessing.sequence.pad_sequences(
            tokenizer.texts_to_sequences([normalizar(mensaje)]),
            truncating='post', maxlen=MAX_LEN,
        )
        prediccion = modelo.predict(secuencia, verbose=0)[0]
        indice = int(np.argmax(prediccion))
        confianza = float(prediccion[indice])

        if confianza < UMBRAL_CONFIANZA:
            return JsonResponse({'response': random.choice(RESPUESTAS_SIN_ENTENDER)})

        etiqueta = label_encoder.inverse_transform([indice])[0]
        for intent in intents['intents']:
            if intent['tag'] == etiqueta and intent.get('responses'):
                return JsonResponse({'response': random.choice(intent['responses'])})

        return JsonResponse({'response': random.choice(RESPUESTAS_SIN_ENTENDER)})

    except FileNotFoundError:
        logger.error('Faltan los ficheros del modelo del chatbot en %s. '
                     'Ejecuta: python manage.py entrenar_chatbot', MODELO_DIR)
        return JsonResponse(
            {'response': 'El asistente no está disponible ahora mismo.'}, status=503
        )
    except Exception:
        logger.exception('Error al generar la respuesta del chatbot')
        return JsonResponse(
            {'response': 'Ha ocurrido un error procesando tu mensaje. Inténtalo de nuevo.'},
            status=500,
        )
