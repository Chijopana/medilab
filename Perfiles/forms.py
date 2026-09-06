from django import forms

from .models import Paciente, Perfil


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nombre', 'apellido', 'dni', 'email', 'telefono', 'direccion',
                  'fecha_nacimiento', 'numero_seguro_social']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'numero_seguro_social': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_numero_seguro_social(self):
        # El campo es unique pero admite nulos: normalizamos '' a None para que
        # varios perfiles sin NSS no choquen entre sí.
        return self.cleaned_data.get('numero_seguro_social') or None


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['contacto_emergencia', 'telefono_emergencia']
        widgets = {
            'contacto_emergencia': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_emergencia': forms.TextInput(attrs={'class': 'form-control'}),
        }
