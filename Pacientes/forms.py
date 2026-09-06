from django import forms
from django.utils import timezone

from Perfiles.models import Medico

from .models import Visita


class _FechaHoraInput(forms.DateTimeInput):
    """Selector nativo de fecha y hora del navegador."""
    input_type = 'datetime-local'

    def format_value(self, value):
        # El input datetime-local exige exactamente este formato.
        if value is None:
            return ''
        if hasattr(value, 'strftime'):
            return timezone.localtime(value).strftime('%Y-%m-%dT%H:%M') \
                if timezone.is_aware(value) else value.strftime('%Y-%m-%dT%H:%M')
        return value


class _VisitaBaseForm(forms.ModelForm):
    """Widgets y validación comunes a los tres formularios de visita."""

    class Meta:
        model = Visita
        fields = []
        widgets = {
            'hora_fecha': _FechaHoraInput(attrs={'class': 'form-control'}),
            'descripcion_problema': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4,
                       'placeholder': 'Describe brevemente el motivo de la consulta'}),
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'medico' in self.fields:
            self.fields['medico'].queryset = Medico.objects.select_related('perfil')
            self.fields['medico'].empty_label = 'Selecciona un profesional'

    def clean_hora_fecha(self):
        hora_fecha = self.cleaned_data.get('hora_fecha')
        # Solo se valida al crear: una visita ya pasada puede seguir editándose.
        if hora_fecha and self.instance.pk is None and hora_fecha < timezone.now():
            raise forms.ValidationError('La fecha de la visita no puede estar en el pasado.')
        return hora_fecha


class VisitaForm(_VisitaBaseForm):
    """Edición completa (uso interno / staff)."""

    class Meta(_VisitaBaseForm.Meta):
        fields = ['paciente', 'medico', 'hora_fecha', 'descripcion_problema', 'estado']


class VisitaFormPaciente(_VisitaBaseForm):
    """El paciente elige médico, fecha y motivo; él mismo se asigna en la vista."""

    class Meta(_VisitaBaseForm.Meta):
        fields = ['medico', 'hora_fecha', 'descripcion_problema']


class VisitaFormMedico(_VisitaBaseForm):
    """El médico elige paciente, fecha y motivo; él mismo se asigna en la vista."""

    class Meta(_VisitaBaseForm.Meta):
        fields = ['paciente', 'hora_fecha', 'descripcion_problema', 'estado']
