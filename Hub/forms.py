from django import forms
from django.contrib.auth.models import User
from Perfiles.models import Perfil,Paciente

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class PerfilGrandeForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nombre','apellido','email','telefono','direccion','fecha_nacimiento','numero_seguro_social']

class PacienteGrandeForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['contacto_emergencia','telefono_emergencia']