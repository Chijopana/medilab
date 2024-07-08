from django import forms
from .models import Visita

class VisitaFormPaciente(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ['medico','descripcion_problema']

class VisitaFormMedico(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ['paciente','hora_fecha','descripcion_problema']
