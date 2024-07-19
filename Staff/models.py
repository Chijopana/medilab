from django.db import models
from Perfiles.models import *


class Medicacion(models.Model):
    paciente = models.ForeignKey(Paciente, related_name = 'medicacion', on_delete=models.DO_NOTHING)
    medico = models.ForeignKey(Medico,related_name='medicacion', on_delete=models.DO_NOTHING)
    medicina = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()

    def __str__(self):
        return self.medicina
    