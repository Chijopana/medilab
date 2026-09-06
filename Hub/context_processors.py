"""Variables disponibles en todas las plantillas."""


def user_groups(request):
    """Expone el rol del usuario para poder ramificar el menú en las plantillas."""
    if not request.user.is_authenticated:
        return {'is_paciente': False, 'is_medico': False}

    grupos = set(request.user.groups.values_list('name', flat=True))
    return {
        'is_paciente': 'Pacientes' in grupos,
        'is_medico': 'Medicos' in grupos,
    }
