from django.contrib.auth.models import Group

def user_groups(request):
    if request.user.is_authenticated:
        user_groups = request.user.groups.values_list('name', flat=True)
        return {
            'is_paciente': 'Pacientes' in user_groups,
            'is_medico': 'Medicos' in user_groups,
        }
    return {
        'is_paciente': False,
        'is_medico': False,
    }