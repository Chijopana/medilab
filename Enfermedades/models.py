from django.db import models
from Perfiles.models import Paciente,Medico
from expedientes.models import Expediente


class CancerMama(models.Model):
    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='cancer_mama_images/', blank=True) 

    def __str__(self):
        return f'Cancer de Mama - Expediente {self.expediente}'
    
class Diabetes(models.Model):
    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    genero = models.CharField(max_length=6)  
    edad = models.DecimalField(max_digits=5, decimal_places=2)
    hipertension = models.IntegerField()  
    ataques_cardiacos = models.IntegerField()  
    historial_fumador = models.CharField(max_length=7)  
    bmi = models.DecimalField(max_digits=5, decimal_places=2)
    nivel_hba1c = models.DecimalField(max_digits=4, decimal_places=2)
    glucosa_sangre = models.IntegerField()
    diabetes = models.IntegerField()  


    def __str__(self):
        return f'Diabetes - Expediente {self.expediente}'

class Pneumonia(models.Model):
    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='pneumonia_images/', blank=True, null=True)
   
    def __str__(self):
        return f'Pneumonia - Expediente {self.expediente}'

class Lunares(models.Model):
    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='lunares_images/', blank=True, null=True)
    
    def __str__(self):
        return f'Lunares - Expediente {self.expediente}'

class Cardiaco(models.Model):
    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    estado_salud = models.IntegerField()  
    revision_medica = models.IntegerField()
    ejercicio = models.IntegerField()
    enfermedad_cardiaca = models.IntegerField()  
    cancer_piel = models.IntegerField()  
    otros_cancer = models.IntegerField()  
    depresion = models.IntegerField()  
    diabetes = models.IntegerField()  
    artritis = models.IntegerField()  
    genero = models.IntegerField()  
    categoria_edad = models.IntegerField()  
    altura = models.DecimalField(max_digits=5, decimal_places=2)  
    peso = models.DecimalField(max_digits=5, decimal_places=2)  
    bmi = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=False)  
    historial_fumador = models.CharField(max_length=3)  
    consumo_alcohol = models.DecimalField(max_digits=5, decimal_places=2) 
    consumo_frutas = models.DecimalField(max_digits=5, decimal_places=2)  
    consumo_vegetales = models.DecimalField(max_digits=5, decimal_places=2)  
    consumo_papas_fritas = models.DecimalField(max_digits=5, decimal_places=2)  

    def calcular_bmi(self):
        if self.peso and self.altura:
            altura_metros = self.altura / 100  
            self.bmi = self.peso / (altura_metros ** 2)
        else:
            self.bmi = None

    def save(self, *args, **kwargs):
        self.calcular_bmi()
        super(Cardiaco, self).save(*args, **kwargs)

    def __str__(self):
        return f'Problema Cardiaco - Expediente {self.expediente}'
    


