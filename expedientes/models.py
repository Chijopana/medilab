from django.db import models
from Perfiles.models import *
from Enfermedades.models import *

class Expediente(models.Model):
    class EspecialidadChoices(models.TextChoices):
        CANCER_MAMA = 'CancerMama', 'Cáncer de Mama'
        DIABETES = 'Diabetes', 'Diabetes'
        PNEUMONIA = 'Pneumonia', 'Neumonía'
        LUNARES = 'Lunares', 'Lunares'
        CARDIACO = 'Cardiaco', 'Cardiaco'
    
    fecha_hora = models.DateTimeField(blank=True, null=True)
    paciente = models.ForeignKey(Paciente, related_name='expediente', on_delete=models.DO_NOTHING)
    doctor = models.ForeignKey(Medico,related_name='expediente', on_delete=models.DO_NOTHING)
    antecedentes = models.TextField()
    especialidad = models.CharField(
        max_length=50,
        choices=EspecialidadChoices.choices,
        blank=True,null=True
    )
    def __str__(self):
        return f"Expediente de {self.paciente} con {self.doctor} el {self.fecha_hora}"

class temporal_expediente(models.Model):
    class EspecialidadChoices(models.TextChoices):
        CANCER_MAMA = 'CancerMama', 'CancerMama'
        DIABETES = 'Diabetes', 'Diabetes'
        PNEUMONIA = 'Pneumonia', 'Neumonía'
        LUNARES = 'Lunares', 'Lunares'
        CARDIACO = 'Cardiaco', 'Cardiaco'

    fecha_hora = models.DateTimeField(blank=True, null=True)
    paciente = models.ForeignKey(Paciente, related_name='temporal_expediente', on_delete=models.DO_NOTHING)
    doctor = models.ForeignKey(Medico,related_name='temporal_expediente', on_delete=models.DO_NOTHING)
    antecedentes = models.TextField()
    especialidad = models.CharField(
        max_length=50,
        choices=EspecialidadChoices.choices,
        blank=True,null=True
    )
# La variable 'especialidad' no se toca. Se pondrá automaticamente.