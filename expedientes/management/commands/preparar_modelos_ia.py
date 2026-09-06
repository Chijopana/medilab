"""
Comprueba los modelos de IA y deja listos los que necesitan conversión.

    python manage.py preparar_modelos_ia

Conviene ejecutarlo tras descargar los modelos: si no, la conversión de
tuberculosis la acaba pagando el primer usuario que use esa pantalla.
"""
import time

from django.core.management.base import BaseCommand

from expedientes import carga_modelos
from expedientes.views import MODELOS_IA


class Command(BaseCommand):
    help = 'Verifica los modelos de IA y convierte los que lo necesiten.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--probar', action='store_true',
            help='Además, lanza una predicción de prueba sobre cada modelo.',
        )

    def handle(self, *args, **opciones):
        faltan = []

        for clave, info in MODELOS_IA.items():
            self.stdout.write(f"\n{info['nombre_visible']}")

            if not carga_modelos.disponible(info):
                self.stdout.write(self.style.WARNING(
                    f"  falta {info['fichero']} en expedientes/modelos_ia/"))
                faltan.append(clave)
                continue

            t0 = time.time()
            try:
                modelo = carga_modelos.cargar(clave, info)
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'  error al cargar: {type(e).__name__}: {e}'))
                faltan.append(clave)
                continue

            self.stdout.write(self.style.SUCCESS(
                f'  cargado en {time.time() - t0:.1f}s '
                f'(entrada {info["tamano"][0]}x{info["tamano"][1]}, '
                f'escalado {info["escalado"]})'))

            if opciones['probar']:
                import numpy as np

                alto, ancho = info['tamano']
                imagen = np.random.rand(1, alto, ancho, 3).astype('float32')
                if info['escalado'] == 'crudo':
                    imagen *= 255
                t0 = time.time()
                salida = modelo.predict(imagen, verbose=0)
                self.stdout.write(
                    f'  predicción de prueba en {time.time() - t0:.1f}s '
                    f'-> {float(salida[0][0]):.4f}')

        self.stdout.write('')
        if faltan:
            self.stdout.write(self.style.WARNING(
                f'Faltan {len(faltan)} modelo(s): {", ".join(faltan)}. '
                'Mira la sección 4 del README para descargarlos.'))
        else:
            self.stdout.write(self.style.SUCCESS('Todos los modelos están listos.'))
