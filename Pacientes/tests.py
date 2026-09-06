"""Tests de acceso y aislamiento de datos en el área del paciente."""
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from Hub.tests import crear_medico, crear_paciente
from Pacientes.models import Visita


class AccesoAreaPacienteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user, self.paciente = crear_paciente()

    def test_sin_login_redirige_al_login(self):
        respuesta = self.client.get(reverse('pacientes/pagina_principal'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('log_in'), respuesta.url)

    def test_paciente_accede_a_su_area(self):
        self.client.login(username='paciente1', password='Test1234!')
        respuesta = self.client.get(reverse('pacientes/pagina_principal'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'pacientes/pagina_principal.html')

    def test_usuario_sin_rol_no_accede(self):
        User.objects.create_user(username='suelto', password='Test1234!')
        self.client.login(username='suelto', password='Test1234!')
        respuesta = self.client.get(reverse('pacientes/pagina_principal'))
        self.assertRedirects(respuesta, reverse('hub'))

    def test_medico_no_entra_en_el_area_de_paciente(self):
        crear_medico()
        self.client.login(username='medico1', password='Test1234!')
        respuesta = self.client.get(reverse('pacientes/pagina_principal'))
        self.assertRedirects(respuesta, reverse('hub'))


class AislamientoEntrePacientesTest(TestCase):
    """Un paciente no puede tocar las visitas de otro."""

    def setUp(self):
        self.client = Client()
        _, self.paciente1 = crear_paciente('paciente1', '11111111A')
        _, self.paciente2 = crear_paciente('paciente2', '22222222B')
        _, self.medico = crear_medico()
        self.visita_ajena = Visita.objects.create(
            paciente=self.paciente2, medico=self.medico,
            hora_fecha=timezone.now() + timezone.timedelta(days=3),
            descripcion_problema='Consulta privada del paciente 2',
        )
        self.client.login(username='paciente1', password='Test1234!')

    def test_no_ve_la_visita_ajena_en_su_listado(self):
        respuesta = self.client.get(reverse('pacientes/visitas'))
        self.assertNotContains(respuesta, 'Consulta privada del paciente 2')

    def test_no_puede_abrir_la_visita_ajena(self):
        respuesta = self.client.get(
            reverse('pacientes/mod_visita', args=[self.visita_ajena.pk]))
        self.assertEqual(respuesta.status_code, 404)

    def test_no_puede_borrar_la_visita_ajena(self):
        respuesta = self.client.post(
            reverse('pacientes/del_visita', args=[self.visita_ajena.pk]))
        self.assertEqual(respuesta.status_code, 404)
        self.assertTrue(Visita.objects.filter(pk=self.visita_ajena.pk).exists())

    def test_borrar_requiere_post(self):
        propia = Visita.objects.create(
            paciente=self.paciente1, medico=self.medico,
            hora_fecha=timezone.now() + timezone.timedelta(days=1),
            descripcion_problema='Mi consulta',
        )
        respuesta = self.client.get(reverse('pacientes/del_visita', args=[propia.pk]))
        self.assertEqual(respuesta.status_code, 405)
        self.assertTrue(Visita.objects.filter(pk=propia.pk).exists())
