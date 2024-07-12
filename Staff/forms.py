from django import forms
from Perfiles.models import *
from .models import *
from Enfermedades.models import *


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nombre','apellido','dni','email','telefono','direccion','fecha_nacimiento','numero_seguro_social']

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['contacto_emergencia','telefono_emergencia']

class MedicacionForm(forms.ModelForm):
    class Meta:
        model = Medicacion
        fields = ['medico','medicina','fecha_inicio','fecha_final']
class CancerForm(forms.ModelForm):
    class Meta:
        models = CancerMama 
        fields = ['estadio','receptor_hormonal']
class DiabetesForm(forms.ModelForm):
    class Meta:
        models = Diabetes
        fields = ['tipo','nivel_glucosa']
class PneumoniaForm(forms.ModelForm):
    class Meta:
        models = Pneumonia 
        fields = ['gravedad','tratamiento']
class LunaresForm(forms.ModelForm):
    class Meta:
        models = Lunares
        fields = ['localizacion','tipo','tamano']
class CardiacoForm(forms.ModelForm):
    class Meta:
        models = Cardiaco
        fields = ['tipo','tratamiento','fecha_ultima_revision']