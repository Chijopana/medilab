"""Tests de acceso a la historia clínica.

Este módulo cubre la regresión más importante del proyecto: antes,
`/expedientes/<id>/` y su PDF eran públicos y cualquiera podía leer la
historia clínica de cualquier paciente probando números.
"""
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from Hub.tests import crear_medico, crear_paciente

from .models import EspecialidadChoices, Expediente


class AccesoExpedienteTest(TestCase):
    def setUp(self):
        self.client = Client()
        _, self.medico = crear_medico('medico1', '11111111A')
        _, self.otro_medico = crear_medico('medico2', '22222222B')
        _, self.paciente = crear_paciente('paciente1', '33333333C')
        _, self.otro_paciente = crear_paciente('paciente2', '44444444D')
        self.paciente.medicos.add(self.medico)

        self.expediente = Expediente.objects.create(
            paciente=self.paciente, doctor=self.medico,
            fecha_hora=timezone.now(),
            antecedentes='Dato clínico confidencial del paciente 1',
            especialidad=EspecialidadChoices.PNEUMONIA,
        )
        self.url_ver = reverse('ver_expediente', args=[self.expediente.id])
        self.url_pdf = reverse('descargar_expediente_pdf', args=[self.expediente.id])

    def test_anonimo_no_lee_el_expediente(self):
        for url in (self.url_ver, self.url_pdf):
            with self.subTest(url=url):
                respuesta = self.client.get(url)
                self.assertEqual(respuesta.status_code, 302)
                self.assertIn(reverse('log_in'), respuesta.url)

    def test_el_paciente_lee_su_expediente(self):
        self.client.login(username='paciente1', password='Test1234!')
        respuesta = self.client.get(self.url_ver)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Dato clínico confidencial')

    def test_otro_paciente_no_lee_el_expediente(self):
        self.client.login(username='paciente2', password='Test1234!')
        for url in (self.url_ver, self.url_pdf):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_su_medico_lo_lee(self):
        self.client.login(username='medico1', password='Test1234!')
        self.assertEqual(self.client.get(self.url_ver).status_code, 200)

    def test_otro_medico_no_lo_lee(self):
        self.client.login(username='medico2', password='Test1234!')
        for url in (self.url_ver, self.url_pdf):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_el_pdf_se_genera(self):
        self.client.login(username='paciente1', password='Test1234!')
        respuesta = self.client.get(self.url_pdf)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta['Content-Type'], 'application/pdf')
        self.assertTrue(respuesta.content.startswith(b'%PDF'))

    def test_listado_solo_muestra_lo_propio(self):
        self.client.login(username='paciente2', password='Test1234!')
        respuesta = self.client.get(reverse('expedientes'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, 'Dato clínico confidencial')


class DiagnosticoIATest(TestCase):
    def setUp(self):
        self.client = Client()
        crear_paciente()
        self.url = reverse('diagnostico_ia')

    def test_requiere_login(self):
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('log_in'), respuesta.url)

    def test_usuario_autenticado_ve_el_formulario(self):
        self.client.login(username='paciente1', password='Test1234!')
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)

    def test_especialidad_desconocida_no_rompe(self):
        """Antes, una clave inventada provocaba un KeyError y un 500."""
        self.client.login(username='paciente1', password='Test1234!')
        respuesta = self.client.post(self.url, {'especialidad': 'NoExiste'})
        self.assertEqual(respuesta.status_code, 200)

    def test_fichero_que_no_es_imagen_se_rechaza(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.login(username='paciente1', password='Test1234!')
        falso = SimpleUploadedFile('virus.jpg', b'no soy una imagen',
                                   content_type='image/jpeg')
        respuesta = self.client.post(self.url,
                                     {'especialidad': 'Pneumonia', 'imagen': falso})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'no es una imagen válida')


class ConfiguracionModelosIATest(TestCase):
    """El catálogo MODELOS_IA tiene que describir bien cada modelo.

    Regresión de tuberculosis: le faltaba `tamano`, así que se le enviaban
    imágenes de 224x224 a un modelo de 300x300 y la predicción no terminaba
    nunca; y se le aplicaba una normalización que el modelo ya hace por dentro.
    """

    def test_cada_modelo_esta_descrito_por_completo(self):
        from expedientes.views import MODELOS_IA

        for clave, info in MODELOS_IA.items():
            with self.subTest(modelo=clave):
                for campo in ('fichero', 'nombre_visible', 'etiqueta_positiva',
                              'etiqueta_negativa', 'tamano', 'escalado'):
                    self.assertIn(campo, info, f'falta «{campo}»')
                self.assertEqual(len(info['tamano']), 2)
                self.assertIn(info['escalado'], ('0-1', 'crudo'))

    def test_tuberculosis_usa_300_y_pixeles_crudos(self):
        from expedientes.views import MODELOS_IA

        tb = MODELOS_IA['Tuberculosis']
        self.assertEqual(tb['tamano'], (300, 300))
        # El modelo lleva una capa Rescaling(1/255) dentro: escalar aquí lo rompe.
        self.assertEqual(tb['escalado'], 'crudo')
        self.assertEqual(tb['fichero_origen'], 'tuberculosis.h5')

    def test_el_preprocesado_respeta_tamano_y_escalado(self):
        import io

        import numpy as np
        from PIL import Image

        from expedientes.views import _preprocesar_imagen

        buf = io.BytesIO()
        Image.fromarray(
            (np.ones((80, 60, 3)) * 200).astype('uint8')).save(buf, format='PNG')

        buf.seek(0)
        crudo = _preprocesar_imagen(buf, (300, 300), 'crudo')
        self.assertEqual(crudo.shape, (1, 300, 300, 3))
        self.assertGreater(crudo.max(), 1.5, 'con escalado «crudo» no se divide entre 255')

        buf.seek(0)
        normalizado = _preprocesar_imagen(buf, (224, 224), '0-1')
        self.assertEqual(normalizado.shape, (1, 224, 224, 3))
        self.assertLessEqual(normalizado.max(), 1.0)
