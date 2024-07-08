from django.db import models
from Perfiles.models import Perfil,Medico

class ResultadoPruebas(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE,related_name='resultados_pruebas') #el del paciente
    tipo_prueba = models.CharField(max_length=255)
    resultado = models.TextField()
    medicos = models.ManyToManyField(Medico, related_name='resulados_pruebas')

    def __str__(self):
        return f'Resultado de {self.tipo_prueba} para {self.perfil.nombre} {self.perfil.apellido} realizado el {self.fecha_realizacion}'

class Medicacion(models.Model):
    perfil = models.ForeignKey(Perfil, related_name = 'medicacion', on_delete=models.DO_NOTHING)
    medico = models.ForeignKey(Medico,related_name='medicacion', on_delete=models.DO_NOTHING)
    medicina = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()

    def __str__(self):
        return self.medicina
    