from django.db import models

from Perfiles.models import Medico, Paciente


class Visita(models.Model):
    """Cita entre un paciente y un médico."""

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        REALIZADA = 'realizada', 'Realizada'
        CANCELADA = 'cancelada', 'Cancelada'

    paciente = models.ForeignKey(Paciente, related_name='visita', on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, related_name='visita', on_delete=models.PROTECT)
    hora_fecha = models.DateTimeField('fecha y hora', blank=True, null=True)
    descripcion_problema = models.TextField('motivo de la consulta')
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)

    class Meta:
        ordering = ['-hora_fecha']
        verbose_name_plural = 'visitas'

    def __str__(self):
        return f'Visita de {self.paciente} con {self.medico} el {self.hora_fecha}'
