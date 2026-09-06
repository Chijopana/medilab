"""Tests del chatbot.

Los que tocan el modelo cargan TensorFlow y tardan; los del contrato HTTP
responden antes de llegar a cargarlo, así que son instantáneos.
"""
import json
import os

from django.test import Client, TestCase
from django.urls import reverse

MODELO_DIR = os.path.join(os.path.dirname(__file__), 'modelo')


class IntentsTest(TestCase):
    """El fichero de intenciones es la fuente de verdad del chatbot."""

    @classmethod
    def setUpTestData(cls):
        with open(os.path.join(MODELO_DIR, 'intents.json'), encoding='utf-8') as f:
            cls.datos = json.load(f)

    def test_estructura_valida(self):
        self.assertIn('intents', self.datos)
        for intent in self.datos['intents']:
            with self.subTest(tag=intent.get('tag')):
                self.assertIn('tag', intent)
                self.assertTrue(intent.get('patterns'), 'sin frases de entrenamiento')
                self.assertTrue(intent.get('responses'), 'sin respuestas')

    def test_no_hay_etiquetas_repetidas(self):
        etiquetas = [i['tag'] for i in self.datos['intents']]
        self.assertEqual(len(etiquetas), len(set(etiquetas)),
                         'hay etiquetas duplicadas en intents.json')

    def test_cubre_las_funciones_de_la_aplicacion(self):
        """Regresión: el modelo original estaba entrenado en historia del arte."""
        etiquetas = {i['tag'] for i in self.datos['intents']}
        for esperada in ('pedir_cita', 'cancelar_cita', 'historial', 'medicacion',
                         'diagnostico_ia', 'descargar_pdf', 'privacidad', 'urgencia'):
            self.assertIn(esperada, etiquetas)

    def test_no_da_consejo_clinico(self):
        """Ante síntomas o medicación, el bot deriva; nunca diagnostica."""
        por_tag = {i['tag']: i for i in self.datos['intents']}
        for tag in ('sintomas', 'consejo_medicamento'):
            texto = ' '.join(por_tag[tag]['responses']).lower()
            self.assertTrue(
                'médico' in texto or 'medico' in texto or 'farmac' in texto,
                f'las respuestas de «{tag}» deben derivar a un profesional')

    def test_urgencia_menciona_el_112(self):
        por_tag = {i['tag']: i for i in self.datos['intents']}
        self.assertIn('112', ' '.join(por_tag['urgencia']['responses']))


class ContratoHttpTest(TestCase):
    """Estas rutas responden sin llegar a cargar el modelo."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('get_response')

    def test_get_no_permitido(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_mensaje_vacio(self):
        respuesta = self.client.post(self.url, {'message': '   '})
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('response', respuesta.json())

    def test_mensaje_demasiado_largo(self):
        respuesta = self.client.post(self.url, {'message': 'a' * 600})
        self.assertEqual(respuesta.status_code, 400)

    def test_widget_carga(self):
        self.assertEqual(self.client.get(reverse('chatbot')).status_code, 200)


class RespuestaDelModeloTest(TestCase):
    """Comprueba de punta a punta que el modelo entrenado responde de Medilab."""

    def test_pregunta_por_una_cita(self):
        respuesta = self.client.post(reverse('get_response'),
                                     {'message': 'como pido una cita'})
        self.assertEqual(respuesta.status_code, 200)
        texto = respuesta.json()['response'].lower()
        self.assertIn('visitas', texto)
