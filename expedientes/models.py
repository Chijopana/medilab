from django.db import models

from Perfiles.models import Medico, Paciente


class EspecialidadChoices(models.TextChoices):
    """Áreas clínicas cubiertas por el sistema (y por los modelos de IA)."""

    CANCER_MAMA = 'CancerMama', 'Cáncer de mama'
    DIABETES = 'Diabetes', 'Diabetes'
    PNEUMONIA = 'Pneumonia', 'Neumonía'
    LUNARES = 'Lunares', 'Lunares / melanoma'
    CARDIACO = 'Cardiaco', 'Cardiología'
    TUBERCULOSIS = 'Tuberculosis', 'Tuberculosis'
    TUMOR_CEREBRAL = 'TumorCerebral', 'Tumor cerebral'


# Nombre del departamento que se muestra en el expediente y en el PDF.
DEPARTAMENTOS = {
    EspecialidadChoices.CANCER_MAMA: 'Oncología',
    EspecialidadChoices.DIABETES: 'Endocrinología',
    EspecialidadChoices.PNEUMONIA: 'Neumología',
    EspecialidadChoices.LUNARES: 'Dermatología',
    EspecialidadChoices.CARDIACO: 'Cardiología',
    EspecialidadChoices.TUBERCULOSIS: 'Neumología',
    EspecialidadChoices.TUMOR_CEREBRAL: 'Neurología',
}


class Expediente(models.Model):
    """Entrada de la historia clínica de un paciente."""

    fecha_hora = models.DateTimeField('fecha y hora', blank=True, null=True)
    paciente = models.ForeignKey(Paciente, related_name='expediente', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Medico, related_name='expediente', on_delete=models.PROTECT)
    antecedentes = models.TextField()
    diagnostico = models.TextField(blank=True)
    tratamiento = models.TextField(blank=True)
    especialidad = models.CharField(
        max_length=50,
        choices=EspecialidadChoices.choices,
        blank=True, null=True,
    )

    class Meta:
        ordering = ['-fecha_hora']
        verbose_name_plural = 'expedientes'

    def __str__(self):
        return f'Expediente de {self.paciente} con {self.doctor} el {self.fecha_hora}'

    @property
    def departamento(self):
        return DEPARTAMENTOS.get(self.especialidad, 'Medicina general')


class TemporalExpediente(models.Model):
    """Expediente en borrador, a la espera de que el médico lo revise y firme."""

    fecha_hora = models.DateTimeField('fecha y hora', blank=True, null=True)
    paciente = models.ForeignKey(Paciente, related_name='temporal_expediente',
                                 on_delete=models.CASCADE)
    doctor = models.ForeignKey(Medico, related_name='temporal_expediente',
                               on_delete=models.CASCADE)
    antecedentes = models.TextField()
    especialidad = models.CharField(
        max_length=50,
        choices=EspecialidadChoices.choices,
        blank=True, null=True,
    )

    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = 'expediente temporal'
        verbose_name_plural = 'expedientes temporales'

    def __str__(self):
        return f'Borrador de {self.paciente} ({self.get_especialidad_display()})'
