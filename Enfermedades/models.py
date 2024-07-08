from django.db import models
from Perfiles.models import Paciente,Medico

# Modelo abstracto para Diagnóstico que otros modelos específicos extenderán
class Diagnostico(models.Model):
    paciente = models.ForeignKey(Paciente, related_name='diagnosticos', on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, related_name='diagnosticos', on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.paciente.perfil.nombre} {self.paciente.perfil.apellido} - {self.__class__.__name__}'

# Modelo para el diagnóstico de Cancer de Mama
class CancerMama(models.Model):
    diagnostico = models.ForeignKey(Diagnostico, related_name='cancer_mama', on_delete=models.DO_NOTHING, blank=True, null=True)
    estadio = models.CharField(max_length=50)
    receptor_hormonal = models.BooleanField(default=False)

    def __str__(self):
        return self.diagnostico

# Otros modelos para contexto (sin cambios a menos que se necesiten)
class Diabetes(models.Model):
    diagnostico = models.ForeignKey(Diagnostico, related_name='diabetes', on_delete=models.DO_NOTHING, blank=True, null=True)
    tipo = models.CharField(max_length=50)
    nivel_glucosa = models.FloatField()

class Pneumonia(models.Model):
    diagnostico = models.ForeignKey(Diagnostico, related_name='pneumonia', on_delete=models.DO_NOTHING, blank=True, null=True)
    gravedad = models.CharField(max_length=50)
    tratamiento = models.TextField(blank=True, null=True)

class Lunares(models.Model):
    diagnostico = models.ForeignKey(Diagnostico, related_name='lunares', on_delete=models.DO_NOTHING, blank=True, null=True)
    localizacion = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50)
    tamano = models.FloatField()

class Cardiaco(models.Model):
    diagnostico = models.ForeignKey(Diagnostico, related_name='cardiaco', on_delete=models.DO_NOTHING, blank=True, null=True)
    tipo = models.CharField(max_length=50)
    tratamiento = models.TextField(blank=True, null=True)
    fecha_ultima_revision = models.DateField(default='2000-01-01')
