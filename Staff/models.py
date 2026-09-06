from django.db import models

from Perfiles.models import Medico, Paciente


class Medicacion(models.Model):
    """Tratamiento prescrito por un médico a un paciente."""

    paciente = models.ForeignKey(Paciente, related_name='medicacion', on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, related_name='medicacion', on_delete=models.PROTECT)
    medicina = models.CharField('medicamento', max_length=255)
    dosis = models.CharField(max_length=120, blank=True)
    instrucciones = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'medicación'
        verbose_name_plural = 'medicaciones'

    def __str__(self):
        return f'{self.medicina} ({self.paciente})'

    @property
    def activa(self):
        from django.utils import timezone
        return self.fecha_inicio <= timezone.localdate() <= self.fecha_final
