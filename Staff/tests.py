"""Tests del panel médico: rol y relación asistencial."""
from django.test import Client, TestCase
from django.urls import reverse

from Hub.tests import crear_medico, crear_paciente


class AccesoPanelMedicoTest(TestCase):
    def setUp(self):
        self.client = Client()
        crear_medico()
        crear_paciente()

    def test_sin_login_redirige(self):
        respuesta = self.client.get(reverse('staff/lobby'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('log_in'), respuesta.url)

    def test_medico_accede(self):
        self.client.login(username='medico1', password='Test1234!')
        respuesta = self.client.get(reverse('staff/lobby'))
        self.assertEqual(respuesta.status_code, 200)

    def test_paciente_no_accede_al_panel_medico(self):
        self.client.login(username='paciente1', password='Test1234!')
        respuesta = self.client.get(reverse('staff/lobby'))
        self.assertRedirects(respuesta, reverse('hub'))

    def test_paciente_no_lista_pacientes(self):
        self.client.login(username='paciente1', password='Test1234!')
        respuesta = self.client.get(reverse('staff/lista_pacientes'))
        self.assertRedirects(respuesta, reverse('hub'))


class RelacionAsistencialTest(TestCase):
    """Conocer el access_key de un paciente no basta para ver su ficha."""

    def setUp(self):
        self.client = Client()
        _, self.medico = crear_medico('medico1', '11111111A')
        _, self.otro_medico = crear_medico('medico2', '22222222B')
        _, self.paciente = crear_paciente('paciente1', '33333333C')
        self.paciente.medicos.add(self.medico)
        self.access_key = self.paciente.perfil.access_key

    def _urls_del_paciente(self):
        return [
            reverse('staff/paciente_ind', args=[self.access_key]),
            reverse('staff/paciente_ind_edit', args=[self.access_key]),
            reverse('staff/visitas', args=[self.access_key]),
            reverse('staff/expedientes', args=[self.access_key]),
            reverse('staff/medicacion', args=[self.access_key]),
        ]

    def test_su_medico_ve_la_ficha(self):
        self.client.login(username='medico1', password='Test1234!')
        for url in self._urls_del_paciente():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_otro_medico_no_ve_la_ficha(self):
        self.client.login(username='medico2', password='Test1234!')
        for url in self._urls_del_paciente():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_otro_medico_no_puede_editar(self):
        self.client.login(username='medico2', password='Test1234!')
        respuesta = self.client.post(
            reverse('staff/paciente_ind_edit', args=[self.access_key]),
            {'nombre': 'Hackeado', 'apellido': 'X', 'dni': '99999999Z',
             'email': 'x@example.com'},
        )
        self.assertEqual(respuesta.status_code, 404)
        self.paciente.perfil.refresh_from_db()
        self.assertNotEqual(self.paciente.perfil.nombre, 'Hackeado')

    def test_otro_medico_no_puede_prescribir(self):
        self.client.login(username='medico2', password='Test1234!')
        respuesta = self.client.post(
            reverse('staff/nueva_medicacion', args=[self.access_key]),
            {'medicina': 'X', 'fecha_inicio': '2026-01-01', 'fecha_final': '2026-02-01'},
        )
        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(self.paciente.medicacion.count(), 0)
