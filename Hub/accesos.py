"""
Reglas de acceso a datos clínicos.

Se centralizan aquí para que la respuesta a "¿puede esta persona ver esto?"
sea la misma en todas las vistas y no haya que repetirla (ni olvidarla).
"""
from Perfiles.models import Medico, Paciente


def paciente_de(user):
    """Devuelve el Paciente asociado al usuario, o None."""
    return Paciente.objects.filter(perfil__user=user).first()


def medico_de(user):
    """Devuelve el Medico asociado al usuario, o None."""
    return Medico.objects.filter(perfil__user=user).first()


def puede_acceder_a_paciente(user, paciente):
    """El propio paciente, un médico que le atiende, o el staff."""
    if not user.is_authenticated or paciente is None:
        return False
    if user.is_staff or user.is_superuser:
        return True
    if paciente.perfil.user_id == user.id:
        return True
    medico = medico_de(user)
    return medico is not None and medico.atiende(paciente)


def puede_ver_expediente(user, expediente):
    """Además del acceso al paciente, el médico autor siempre puede verlo."""
    if not user.is_authenticated or expediente is None:
        return False
    if user.is_staff or user.is_superuser:
        return True
    if expediente.paciente.perfil.user_id == user.id:
        return True
    medico = medico_de(user)
    if medico is None:
        return False
    return expediente.doctor_id == medico.pk or medico.atiende(expediente.paciente)
