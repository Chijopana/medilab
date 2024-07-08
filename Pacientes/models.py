from django.db import models
from Perfiles.models import Paciente, Medico

class Visita(models.Model):
    paciente = models.ForeignKey(Paciente, related_name='visita',on_delete=models.DO_NOTHING)
    medico = models.ForeignKey(Medico, related_name='visita',on_delete=models.DO_NOTHING)
    hora_fecha = models.DateTimeField(blank=True, null=True)
    descripcion_problema = models.TextField()

    def __str__(self):
        return f'Visita de {self.paciente.perfil.nombre} {self.paciente.perfil.apellido} con {self.medico.perfil.nombre} {self.medico.perfil.apellido} el {self.hora_fecha}'
