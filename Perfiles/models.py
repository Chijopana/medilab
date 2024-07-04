from django.db import models
from django.contrib.auth.models import User
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
    # numero_seguro_social = models.CharField(max_length=20, unique=True)

    def _str_(self):
        return self.user.username

class Paciente(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='Paciente')
    contacto_emergencia = models.CharField(max_length=255)
    telefono_emergencia = models.CharField(max_length=12)

class Enfermero(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='Enfermero')
    pacientes = models.ManyToManyField(Paciente, related_name='Enfermero')
class Medico(models.Model):
    # especialidad = models.ForeignKey(especialidades, on_delete=models.CASCADE,related_name='Medico')
    pacientes = models.ManyToManyField(Paciente, related_name='Medico')
    enfermeros = models.ManyToManyField(Enfermero, related_name='Medico')
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='Medico')


