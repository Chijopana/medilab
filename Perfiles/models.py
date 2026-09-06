import uuid

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models

validador_dni = RegexValidator(
    r'^[0-9]{7,8}[A-Za-z]?$',
    'Introduce un DNI válido: 7 u 8 dígitos y, opcionalmente, la letra.',
)
validador_telefono = RegexValidator(
    r'^\+?[0-9\s]{7,15}$',
    'Introduce un teléfono válido (7-15 dígitos, opcionalmente con prefijo +).',
)


class Perfil(models.Model):
    """Datos personales comunes a pacientes y médicos."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    # Identificador público: se usa en las URLs para no exponer el id incremental.
    access_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    apellido = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField()
    dni = models.CharField(max_length=9, validators=[validador_dni])
    telefono = models.CharField(max_length=12, blank=True, null=True,
                                validators=[validador_telefono])
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    numero_seguro_social = models.CharField(max_length=20, unique=True, blank=True, null=True)

    class Meta:
        ordering = ['apellido', 'nombre']
        verbose_name_plural = 'perfiles'

    def __str__(self):
        return self.nombre_completo or self.user.username

    @property
    def nombre_completo(self):
        return ' '.join(filter(None, [self.nombre, self.apellido]))


class Paciente(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='paciente')
    contacto_emergencia = models.CharField(max_length=255, blank=True, null=True)
    telefono_emergencia = models.CharField(max_length=12, blank=True, null=True,
                                           validators=[validador_telefono])
    medicos = models.ManyToManyField('Medico', related_name='pacientes', blank=True)

    class Meta:
        ordering = ['perfil__apellido', 'perfil__nombre']

    def __str__(self):
        return str(self.perfil)


class Medico(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='medico')
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    numero_colegiado = models.CharField(max_length=20, blank=True, null=True, unique=True)

    class Meta:
        ordering = ['perfil__apellido', 'perfil__nombre']
        verbose_name_plural = 'médicos'

    def __str__(self):
        return str(self.perfil)

    def atiende(self, paciente):
        """¿Este médico tiene relación asistencial con el paciente?

        Es la comprobación que impide que un médico consulte la historia clínica
        de un paciente que no es suyo.
        """
        if paciente is None:
            return False
        return (
            paciente.medicos.filter(pk=self.pk).exists()
            or paciente.visita.filter(medico=self).exists()
            or paciente.expediente.filter(doctor=self).exists()
        )
