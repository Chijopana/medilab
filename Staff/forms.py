from django import forms
from Perfiles.models import *
from .models import *

class MedicacionForm(forms.ModelForm):
    class Meta:
        model = Medicacion
        fields = ['paciente','medico','medicina','fecha_inicio','fecha_final']

class MedicacionFormCreacion(forms.ModelForm):
    class Meta:
        model = Medicacion
        fields = ['medicina','fecha_inicio','fecha_final']
