from django import forms
from Perfiles.models import *
from Staff.models import *
from Enfermedades.models import *


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nombre','apellido','dni','email','telefono','direccion','fecha_nacimiento','numero_seguro_social']

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['contacto_emergencia','telefono_emergencia']
