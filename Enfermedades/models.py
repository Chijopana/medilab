"""
Datos clínicos específicos de cada patología, colgados de un expediente.

Cada modelo guarda las variables que necesita el correspondiente modelo de IA
o el protocolo de la especialidad.
"""
from django.db import models

from expedientes.models import Expediente


class CancerMama(models.Model):
    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='cancer_mama_images/', blank=True)

    class Meta:
        verbose_name = 'cáncer de mama'
        verbose_name_plural = 'cánceres de mama'

    def __str__(self):
        return f'Cáncer de mama - Expediente {self.expediente_id}'


class Diabetes(models.Model):
    class Genero(models.TextChoices):
        MUJER = 'Mujer', 'Mujer'
        HOMBRE = 'Hombre', 'Hombre'
        OTRO = 'Otro', 'Otro'

    class Fumador(models.TextChoices):
        NUNCA = 'never', 'Nunca'
        ACTUAL = 'current', 'Fumador actual'
        EXFUMADOR = 'former', 'Exfumador'
        SIN_DATO = 'No Info', 'Sin información'

    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    genero = models.CharField(max_length=10, choices=Genero.choices)
    edad = models.DecimalField(max_digits=5, decimal_places=2)
    hipertension = models.BooleanField(default=False)
    ataques_cardiacos = models.BooleanField('cardiopatía previa', default=False)
    historial_fumador = models.CharField(max_length=10, choices=Fumador.choices)
    bmi = models.DecimalField('IMC', max_digits=5, decimal_places=2)
    nivel_hba1c = models.DecimalField('nivel HbA1c', max_digits=4, decimal_places=2)
    glucosa_sangre = models.IntegerField('glucosa en sangre')
    diabetes = models.BooleanField('diagnóstico positivo', default=False)

    class Meta:
        verbose_name_plural = 'diabetes'

    def __str__(self):
        return f'Diabetes - Expediente {self.expediente_id}'


class Pneumonia(models.Model):
    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='pneumonia_images/', blank=True, null=True)

    class Meta:
        verbose_name = 'neumonía'
        verbose_name_plural = 'neumonías'

    def __str__(self):
        return f'Neumonía - Expediente {self.expediente_id}'


class Lunares(models.Model):
    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='lunares_images/', blank=True, null=True)

    class Meta:
        verbose_name = 'lunar'
        verbose_name_plural = 'lunares'

    def __str__(self):
        return f'Lunares - Expediente {self.expediente_id}'


class Cardiaco(models.Model):
    expediente = models.OneToOneField(Expediente, on_delete=models.CASCADE)
    estado_salud = models.IntegerField()
    revision_medica = models.IntegerField()
    ejercicio = models.IntegerField()
    enfermedad_cardiaca = models.IntegerField()
    cancer_piel = models.IntegerField()
    otros_cancer = models.IntegerField()
    depresion = models.IntegerField('depresión')
    diabetes = models.IntegerField()
    artritis = models.IntegerField()
    genero = models.IntegerField('género')
    categoria_edad = models.IntegerField('categoría de edad')
    altura = models.DecimalField('altura (cm)', max_digits=5, decimal_places=2)
    peso = models.DecimalField('peso (kg)', max_digits=5, decimal_places=2)
    bmi = models.DecimalField('IMC', max_digits=5, decimal_places=2, blank=True, null=True)
    historial_fumador = models.CharField(max_length=3)
    consumo_alcohol = models.DecimalField(max_digits=5, decimal_places=2)
    consumo_frutas = models.DecimalField(max_digits=5, decimal_places=2)
    consumo_vegetales = models.DecimalField(max_digits=5, decimal_places=2)
    consumo_papas_fritas = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = 'caso cardíaco'
        verbose_name_plural = 'casos cardíacos'

    def calcular_bmi(self):
        """IMC = peso (kg) / altura (m)^2."""
        if self.peso and self.altura:
            altura_metros = self.altura / 100
            return round(self.peso / (altura_metros ** 2), 2)
        return None

    def save(self, *args, **kwargs):
        self.bmi = self.calcular_bmi()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Caso cardíaco - Expediente {self.expediente_id}'
