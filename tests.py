"""
Tests para la autenticación y autorización de la aplicación.
Para ejecutar: python manage.py test
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from Perfiles.models import Perfil, Paciente, Medico


class RegistroUsuarioTest(TestCase):
    """Tests para el registro de usuarios."""

    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        # Crear grupo de pacientes
        Group.objects.create(name='Pacientes')
        self.url_registro = reverse('crear_usuario')

    def test_pagina_registro_carga(self):
        """Verifica que la página de registro carga correctamente."""
        response = self.client.get(self.url_registro)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Hub/crear_usuario.html')

    def test_registro_usuario_exitoso(self):
        """Verifica que se puede registrar un usuario correctamente."""
        data = {
            'username': 'testpaciente',
            'password': 'TestPassword123!',
            'password_confirm': 'TestPassword123!',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'email': 'juan@example.com',
            'dni': '12345678'
        }
        response = self.client.post(self.url_registro, data)
        
        # Verifica que redirige a login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('log_in'))
        
        # Verifica que el usuario fue creado
        user = User.objects.get(username='testpaciente')
        self.assertIsNotNone(user)
        
        # Verifica que fue asignado al grupo Pacientes
        self.assertTrue(user.groups.filter(name='Pacientes').exists())

    def test_registro_con_contrasena_no_coincide(self):
        """Verifica que no se permite registrar con contraseñas diferentes."""
        data = {
            'username': 'testpaciente',
            'password': 'TestPassword123!',
            'password_confirm': 'OtraPassword123!',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'email': 'juan@example.com',
            'dni': '12345678'
        }
        response = self.client.post(self.url_registro, data)
        
        # Verifica que el formulario tiene errores
        self.assertFormError(response, 'form1', None, 'Las contraseñas no coinciden.')


class LoginTest(TestCase):
    """Tests para el login de usuarios."""

    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        
        # Crear grupos
        pacientes_group = Group.objects.create(name='Pacientes')
        medicos_group = Group.objects.create(name='Medicos')
        
        # Crear perfil y usuario paciente
        self.user_paciente = User.objects.create_user(
            username='paciente1',
            password='Test123!',
            email='paciente@example.com'
        )
        self.user_paciente.groups.add(pacientes_group)
        
        perfil_paciente = Perfil.objects.create(
            user=self.user_paciente,
            nombre='Juan',
            apellido='Pérez',
            email='paciente@example.com',
            dni='12345678'
        )
        Paciente.objects.create(perfil=perfil_paciente)
        
        # Crear perfil y usuario médico
        self.user_medico = User.objects.create_user(
            username='medico1',
            password='Test123!',
            email='medico@example.com'
        )
        self.user_medico.groups.add(medicos_group)
        
        perfil_medico = Perfil.objects.create(
            user=self.user_medico,
            nombre='Dr. Carlos',
            apellido='García',
            email='medico@example.com',
            dni='87654321'
        )
        Medico.objects.create(perfil=perfil_medico)
        
        self.url_login = reverse('log_in')

    def test_pagina_login_carga(self):
        """Verifica que la página de login carga correctamente."""
        response = self.client.get(self.url_login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Hub/log_in.html')

    def test_login_paciente_exitoso(self):
        """Verifica que un paciente puede iniciar sesión."""
        data = {
            'username': 'paciente1',
            'password': 'Test123!'
        }
        response = self.client.post(self.url_login, data)
        
        # Verifica que redirige correctamente
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('pacientes/pagina_principal'))
        
        # Verifica que el usuario está autenticado
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_medico_exitoso(self):
        """Verifica que un médico puede iniciar sesión."""
        data = {
            'username': 'medico1',
            'password': 'Test123!'
        }
        response = self.client.post(self.url_login, data)
        
        # Verifica que redirige correctamente
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('staff/lobby'))

    def test_login_con_credenciales_invalidas(self):
        """Verifica que no se permite login con credenciales inválidas."""
        data = {
            'username': 'paciente1',
            'password': 'PasswordIncorrecto'
        }
        response = self.client.post(self.url_login, data)
        
        # Verifica que no redirige
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Hub/log_in.html')


class AutorizacionTest(TestCase):
    """Tests para la autorización y acceso a datos."""

    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        
        # Crear grupos
        pacientes_group = Group.objects.create(name='Pacientes')
        
        # Crear dos usuarios pacientes
        self.user_paciente1 = User.objects.create_user(
            username='paciente1',
            password='Test123!',
            email='paciente1@example.com'
        )
        self.user_paciente1.groups.add(pacientes_group)
        
        perfil1 = Perfil.objects.create(
            user=self.user_paciente1,
            nombre='Juan',
            apellido='Pérez',
            email='paciente1@example.com',
            dni='12345678'
        )
        self.paciente1 = Paciente.objects.create(perfil=perfil1)
        
        self.user_paciente2 = User.objects.create_user(
            username='paciente2',
            password='Test123!',
            email='paciente2@example.com'
        )
        self.user_paciente2.groups.add(pacientes_group)
        
        perfil2 = Perfil.objects.create(
            user=self.user_paciente2,
            nombre='María',
            apellido='García',
            email='paciente2@example.com',
            dni='87654321'
        )
        self.paciente2 = Paciente.objects.create(perfil=perfil2)

    def test_paciente_sin_login_redirige(self):
        """Verifica que una página protegida redirige sin login."""
        url = reverse('pacientes/pagina_principal')
        response = self.client.get(url)
        
        # Debe redirigir a login
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('log_in'), response.url)

    def test_paciente_con_login_puede_acceder(self):
        """Verifica que un paciente autenticado puede acceder a su página."""
        self.client.login(username='paciente1', password='Test123!')
        
        url = reverse('pacientes/pagina_principal')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pacientes/pagina_principal.html')

    def test_usuario_no_paciente_no_puede_acceder(self):
        """Verifica que un usuario sin rol de paciente no puede acceder."""
        user_sin_grupo = User.objects.create_user(
            username='usuario_sin_grupo',
            password='Test123!'
        )
        
        self.client.login(username='usuario_sin_grupo', password='Test123!')
        
        url = reverse('pacientes/pagina_principal')
        response = self.client.get(url)
        
        # Debe redirigir a hub (acceso denegado)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('hub'))


class LogoutTest(TestCase):
    """Tests para el logout de usuarios."""

    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        
        # Crear grupo
        pacientes_group = Group.objects.create(name='Pacientes')
        
        # Crear usuario
        self.user = User.objects.create_user(
            username='testuser',
            password='Test123!',
            email='test@example.com'
        )
        self.user.groups.add(pacientes_group)
        
        perfil = Perfil.objects.create(
            user=self.user,
            nombre='Test',
            apellido='User',
            email='test@example.com',
            dni='12345678'
        )
        Paciente.objects.create(perfil=perfil)

    def test_logout_exitoso(self):
        """Verifica que un usuario puede cerrar sesión."""
        # Login primero
        self.client.login(username='testuser', password='Test123!')
        
        # Logout
        url = reverse('log_out')
        response = self.client.get(url)
        
        # Verifica que redirige a login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('log_in'))
