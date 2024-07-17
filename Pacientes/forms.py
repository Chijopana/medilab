from django import forms
from .models import *

class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ['paciente','medico','hora_fecha','descripcion_problema']
