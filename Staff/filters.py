import django_filters 
from Perfiles.models import Perfil
from Pacientes.models import Visita

class PerfilFilter(django_filters.FilterSet):
    class Meta:
        model = Perfil
        fields = {
            'nombre':['icontains'],
            'apellido':['icontains'],
            'numero_seguro_social':['exact'],
        }
class VisitaFilter(django_filters.FilterSet):
    class Meta:
        model = Visita
        fields = {
            # 'paciente__nombre':['icontains'],
            # 'paciente__apellido':['icontains'],
            'hora_fecha':['gt'],
        }