from django import forms
from Perfiles.models import *
from .models import *


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['email','telefono','direccion']

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['contacto_emergencia','telefono_emergencia']

class MedicacionForm(forms.ModelForm):
    class Meta:
        model = Medicacion
        fields = ['medico','medicina','fecha_inicio','fecha_final']
