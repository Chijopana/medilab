"""
Prepara el proyecto para usarlo o demostrarlo.

    python manage.py init_datos            # solo crea los grupos
    python manage.py init_datos --demo     # además, datos de ejemplo

Sustituye al antiguo `init_groups.py`, que había que ejecutar redirigiendo
un fichero a `manage.py shell`.
"""
import random
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from expedientes.models import EspecialidadChoices, Expediente
from Pacientes.models import Visita
from Perfiles.models import Medico, Paciente, Perfil
from Staff.models import Medicacion

GRUPOS = ['Pacientes', 'Medicos', 'Staff']

MEDICOS_DEMO = [
    ('dra.ruiz', 'Elena', 'Ruiz', '10000001A', 'Neumología', 'COL-1001'),
    ('dr.navarro', 'Marc', 'Navarro', '10000002B', 'Dermatología', 'COL-1002'),
]

PACIENTES_DEMO = [
    ('lucia', 'Lucía', 'Fernández', '20000001C'),
    ('omar', 'Omar', 'Benítez', '20000002D'),
    ('irene', 'Irene', 'Castro', '20000003E'),
    ('pau', 'Pau', 'Moliner', '20000004F'),
]

MOTIVOS = [
    'Tos persistente desde hace tres semanas.',
    'Revisión de un lunar que ha cambiado de color.',
    'Dolor torácico al hacer esfuerzo.',
    'Control rutinario de la tensión arterial.',
    'Fatiga y falta de aire al subir escaleras.',
]

TRATAMIENTOS = [
    ('Amoxicilina 500 mg', '1 cápsula cada 8 horas', 'Tomar con comida.'),
    ('Ibuprofeno 600 mg', '1 comprimido cada 12 horas', 'No superar 3 tomas al día.'),
    ('Salbutamol inhalador', '2 inhalaciones si hay ahogo', 'Máximo 4 veces al día.'),
]

CONTRASENA_DEMO = 'Medilab2026!'


class Command(BaseCommand):
    help = 'Crea los grupos de usuarios y, opcionalmente, datos de demostración.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo', action='store_true',
            help='Crea médicos, pacientes, visitas, expedientes y medicación de ejemplo.',
        )

    def handle(self, *args, **opciones):
        self._crear_grupos()
        if opciones['demo']:
            self._crear_demo()
        self.stdout.write(self.style.SUCCESS('\nListo.'))

    # -- Grupos --------------------------------------------------------------
    def _crear_grupos(self):
        self.stdout.write('Grupos de usuarios:')
        for nombre in GRUPOS:
            _, creado = Group.objects.get_or_create(name=nombre)
            estado = 'creado' if creado else 'ya existía'
            self.stdout.write(f'  - {nombre}: {estado}')

    # -- Datos de demostración -----------------------------------------------
    @transaction.atomic
    def _crear_demo(self):
        random.seed(42)   # datos reproducibles entre ejecuciones
        grupo_medicos = Group.objects.get(name='Medicos')
        grupo_pacientes = Group.objects.get(name='Pacientes')

        self.stdout.write('\nDatos de demostración:')

        medicos = []
        for username, nombre, apellido, dni, especialidad, colegiado in MEDICOS_DEMO:
            medico = self._medico(username, nombre, apellido, dni, especialidad,
                                  colegiado, grupo_medicos)
            medicos.append(medico)

        pacientes = []
        for username, nombre, apellido, dni in PACIENTES_DEMO:
            paciente = self._paciente(username, nombre, apellido, dni, grupo_pacientes)
            paciente.medicos.add(random.choice(medicos))
            pacientes.append(paciente)

        ahora = timezone.now()
        for paciente in pacientes:
            medico = paciente.medicos.first()

            Visita.objects.get_or_create(
                paciente=paciente, medico=medico,
                hora_fecha=ahora + timedelta(days=random.randint(2, 20)),
                defaults={'descripcion_problema': random.choice(MOTIVOS),
                          'estado': Visita.Estado.PENDIENTE},
            )
            Visita.objects.get_or_create(
                paciente=paciente, medico=medico,
                hora_fecha=ahora - timedelta(days=random.randint(10, 90)),
                defaults={'descripcion_problema': random.choice(MOTIVOS),
                          'estado': Visita.Estado.REALIZADA},
            )

            Expediente.objects.get_or_create(
                paciente=paciente, doctor=medico,
                fecha_hora=ahora - timedelta(days=random.randint(5, 60)),
                defaults={
                    'antecedentes': random.choice(MOTIVOS),
                    'diagnostico': 'Sin hallazgos relevantes en la exploración inicial.',
                    'tratamiento': 'Reposo relativo y control en dos semanas.',
                    'especialidad': random.choice(list(EspecialidadChoices)),
                },
            )

            medicina, dosis, instrucciones = random.choice(TRATAMIENTOS)
            Medicacion.objects.get_or_create(
                paciente=paciente, medico=medico, medicina=medicina,
                defaults={
                    'dosis': dosis,
                    'instrucciones': instrucciones,
                    'fecha_inicio': timezone.localdate() - timedelta(days=5),
                    'fecha_final': timezone.localdate() + timedelta(days=10),
                },
            )

        self.stdout.write('')
        self.stdout.write(self.style.WARNING(
            f'  Todas las cuentas de demo usan la contraseña: {CONTRASENA_DEMO}'))
        self.stdout.write(
            f'  Médicos:   {", ".join(m[0] for m in MEDICOS_DEMO)}')
        self.stdout.write(
            f'  Pacientes: {", ".join(p[0] for p in PACIENTES_DEMO)}')

    def _usuario(self, username, grupo):
        user, creado = User.objects.get_or_create(username=username)
        if creado:
            user.set_password(CONTRASENA_DEMO)
            user.save()
        user.groups.add(grupo)
        return user, creado

    def _medico(self, username, nombre, apellido, dni, especialidad, colegiado, grupo):
        user, _ = self._usuario(username, grupo)
        perfil, _ = Perfil.objects.get_or_create(
            user=user,
            defaults={'nombre': nombre, 'apellido': apellido, 'dni': dni,
                      'email': f'{username}@medilab.example'},
        )
        medico, creado = Medico.objects.get_or_create(
            perfil=perfil,
            defaults={'especialidad': especialidad, 'numero_colegiado': colegiado},
        )
        self.stdout.write(f'  - médico {username}: {"creado" if creado else "ya existía"}')
        return medico

    def _paciente(self, username, nombre, apellido, dni, grupo):
        user, _ = self._usuario(username, grupo)
        perfil, _ = Perfil.objects.get_or_create(
            user=user,
            defaults={'nombre': nombre, 'apellido': apellido, 'dni': dni,
                      'email': f'{username}@example.com',
                      'telefono': '600000000',
                      'fecha_nacimiento': timezone.localdate() - timedelta(days=365 * 35)},
        )
        paciente, creado = Paciente.objects.get_or_create(
            perfil=perfil,
            defaults={'contacto_emergencia': 'Familiar de contacto',
                      'telefono_emergencia': '600111222'},
        )
        self.stdout.write(f'  - paciente {username}: {"creado" if creado else "ya existía"}')
        return paciente
