from django.db import models
from django.contrib.auth.models import User, Group
import uuid

# Create your models here.
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    access_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    email = models.EmailField()
    telefono = models.CharField(max_length=12)
    direccion = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()
    numero_seguro_social = models.CharField(max_length=20, unique=True, default='')

    def __str__(self):
        return self.user.username

class Paciente(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='pacientes')
    contacto_emergencia = models.CharField(max_length=255, blank=True, null=True)
    telefono_emergencia = models.CharField(max_length=12, blank=True, null=True)
    medicos = models.ManyToManyField('Medico', related_name='pacientes',blank=True, null=True)
    
    def __str__(self):
        return self.perfil.user.username


class Enfermero(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='enfermero')
    pacientes = models.ManyToManyField(Paciente, related_name='enfermero', blank=True, null=True)

    def __str__(self):
        return self.perfil.user.username

class Medico(models.Model):
    enfermeros = models.ManyToManyField(Enfermero, related_name='medico', blank=True, null=True)
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='medico')

    def __str__(self):
        return self.perfil.user.username


