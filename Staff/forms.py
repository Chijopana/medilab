from django import forms

from .models import Medicacion


class MedicacionForm(forms.ModelForm):
    """Alta/edición de un tratamiento. Paciente y médico los fija la vista."""

    class Meta:
        model = Medicacion
        fields = ['medicina', 'dosis', 'instrucciones', 'fecha_inicio', 'fecha_final']
        widgets = {
            'medicina': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej. Ibuprofeno 600 mg'}),
            'dosis': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej. 1 comprimido cada 8 h'}),
            'instrucciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_inicio': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'fecha_final': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }

    def clean(self):
        datos = super().clean()
        inicio, final = datos.get('fecha_inicio'), datos.get('fecha_final')
        if inicio and final and final < inicio:
            self.add_error('fecha_final',
                           'La fecha de fin no puede ser anterior a la de inicio.')
        return datos
