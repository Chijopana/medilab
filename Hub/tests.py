"""Tests de registro, autenticación y cierre de sesión."""
from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from Perfiles.models import Medico, Paciente, Perfil


def crear_paciente(username='paciente1', dni='12345678A', email=None):
    grupo, _ = Group.objects.get_or_create(name='Pacientes')
    user = User.objects.create_user(username=username, password='Test1234!')
    user.groups.add(grupo)
    perfil = Perfil.objects.create(
        user=user, nombre='Juan', apellido='Pérez',
        email=email or f'{username}@example.com', dni=dni,
    )
    return user, Paciente.objects.create(perfil=perfil)


def crear_medico(username='medico1', dni='87654321B'):
    grupo, _ = Group.objects.get_or_create(name='Medicos')
    user = User.objects.create_user(username=username, password='Test1234!')
    user.groups.add(grupo)
    perfil = Perfil.objects.create(
        user=user, nombre='Carlos', apellido='García',
        email=f'{username}@example.com', dni=dni,
    )
    return user, Medico.objects.create(perfil=perfil)


class RegistroTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('crear_usuario')
        self.datos = {
            'username': 'nuevopaciente',
            'password': 'ContrasenaSegura9',
            'password_confirm': 'ContrasenaSegura9',
            'nombre': 'Ana',
            'apellido': 'López',
            'email': 'ana@example.com',
            'dni': '11223344C',
        }

    def test_pagina_carga(self):
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'Hub/crear_usuario.html')

    def test_registro_crea_usuario_perfil_paciente_y_grupo(self):
        respuesta = self.client.post(self.url, self.datos)
        self.assertRedirects(respuesta, reverse('log_in'))

        user = User.objects.get(username='nuevopaciente')
        self.assertTrue(user.groups.filter(name='Pacientes').exists())
        self.assertTrue(Paciente.objects.filter(perfil__user=user).exists())
        # La contraseña debe quedar cifrada, nunca en claro.
        self.assertNotEqual(user.password, 'ContrasenaSegura9')
        self.assertTrue(user.check_password('ContrasenaSegura9'))

    def test_contrasenas_distintas_no_registran(self):
        datos = self.datos | {'password_confirm': 'OtraDistinta9'}
        respuesta = self.client.post(self.url, datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(User.objects.filter(username='nuevopaciente').exists())

    def test_contrasena_debil_se_rechaza(self):
        datos = self.datos | {'password': '12345678', 'password_confirm': '12345678'}
        self.client.post(self.url, datos)
        self.assertFalse(User.objects.filter(username='nuevopaciente').exists())

    def test_dni_duplicado_se_rechaza(self):
        crear_paciente(username='otro', dni='11223344C')
        self.client.post(self.url, self.datos)
        self.assertFalse(User.objects.filter(username='nuevopaciente').exists())

    def test_fallo_no_deja_usuario_huerfano(self):
        """Si el perfil no valida, el User tampoco debe quedar creado."""
        datos = self.datos | {'dni': ''}
        self.client.post(self.url, datos)
        self.assertFalse(User.objects.filter(username='nuevopaciente').exists())


class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        crear_paciente()
        crear_medico()
        self.url = reverse('log_in')

    def test_pagina_carga(self):
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'Hub/log_in.html')

    def test_paciente_va_a_su_area(self):
        respuesta = self.client.post(self.url, {'username': 'paciente1',
                                                'password': 'Test1234!'})
        self.assertRedirects(respuesta, reverse('pacientes/pagina_principal'))

    def test_medico_va_al_panel(self):
        respuesta = self.client.post(self.url, {'username': 'medico1',
                                                'password': 'Test1234!'})
        self.assertRedirects(respuesta, reverse('staff/lobby'))

    def test_credenciales_invalidas(self):
        respuesta = self.client.post(self.url, {'username': 'paciente1',
                                                'password': 'incorrecta'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.wsgi_request.user.is_authenticated)

    def test_next_externo_se_ignora(self):
        """Un ?next apuntando fuera del sitio no debe usarse (open redirect)."""
        respuesta = self.client.post(self.url, {
            'username': 'paciente1', 'password': 'Test1234!',
            'next': 'https://sitio-malicioso.example/',
        })
        self.assertRedirects(respuesta, reverse('pacientes/pagina_principal'))


class LogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        crear_paciente()

    def test_logout_por_post(self):
        self.client.login(username='paciente1', password='Test1234!')
        respuesta = self.client.post(reverse('log_out'))
        self.assertRedirects(respuesta, reverse('hub'))
        self.assertFalse(respuesta.wsgi_request.user.is_authenticated)

    def test_logout_por_get_no_permitido(self):
        """Un GET no debe cerrar sesión: permitiría desloguear desde un enlace ajeno."""
        self.client.login(username='paciente1', password='Test1234!')
        respuesta = self.client.get(reverse('log_out'))
        self.assertEqual(respuesta.status_code, 405)
