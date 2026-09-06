"""
Carga de los modelos de IA, con caché en memoria.

El caso especial es tuberculosis. Ese fichero es un `.h5` guardado con Keras 2.9
que contiene una InceptionV3 anidada (311 capas). Keras 3 no consigue
deserializarlo: `load_model()` se queda dentro de la reconstrucción del grafo
indefinidamente (probado: más de 12 minutos sin terminar, con y sin
`compile=False`). Era la causa del "se cuelga al procesar" que arrastraba el
proyecto.

La solución es no deserializar el grafo: reconstruimos la arquitectura con
`keras.applications.InceptionV3` —que es exactamente la que se guardó— y
copiamos los pesos capa por capa desde el HDF5. Con eso el modelo queda listo en
menos de dos segundos. Después se guarda en formato `.keras` moderno para que
las siguientes cargas sean directas.
"""
import logging
import os

from django.conf import settings

logger = logging.getLogger(__name__)

MODELOS_DIR = os.path.join(settings.BASE_DIR, 'expedientes', 'modelos_ia')

_cache = {}


def ruta(fichero):
    return os.path.join(MODELOS_DIR, fichero)


def _reconstruir_tuberculosis(ruta_h5):
    """Rehace la arquitectura y copia los pesos del HDF5 capa por capa."""
    import h5py
    from tensorflow import keras

    base = keras.applications.InceptionV3(
        include_top=False, weights=None, input_shape=(300, 300, 3))

    entrada = keras.Input(shape=(300, 300, 3))
    x = keras.layers.Rescaling(1.0 / 255)(entrada)     # el modelo escala dentro
    x = base(x)
    x = keras.layers.GlobalAveragePooling2D()(x)
    x = keras.layers.Flatten()(x)
    salida = keras.layers.Dense(1, activation='sigmoid', name='dense')(x)
    modelo = keras.Model(entrada, salida)

    def datasets_de(grupo):
        """{nombre_base: array} de todos los datasets bajo un grupo HDF5."""
        encontrados = {}

        def visitar(nombre, obj):
            if isinstance(obj, h5py.Dataset):
                encontrados[nombre.split('/')[-1]] = obj[()]

        grupo.visititems(visitar)
        return encontrados

    with h5py.File(ruta_h5, 'r') as f:
        pesos = f['model_weights']
        grupo_inception = pesos['inception_v3']

        for capa in base.layers:
            if not capa.weights or capa.name not in grupo_inception:
                continue
            disponibles = datasets_de(grupo_inception[capa.name])
            valores = []
            for w in capa.weights:
                clave = f'{w.name}:0'
                if clave in disponibles:
                    valores.append(disponibles[clave])
                else:
                    # Respaldo: emparejar por forma si el nombre no coincide.
                    candidatos = [v for v in disponibles.values()
                                  if v.shape == tuple(w.shape)]
                    if len(candidatos) != 1:
                        valores = None
                        break
                    valores.append(candidatos[0])
            if valores and len(valores) == len(capa.weights):
                capa.set_weights(valores)
            else:
                logger.warning('No he podido asignar los pesos de la capa %s', capa.name)

        finales = datasets_de(pesos['dense'])
        modelo.get_layer('dense').set_weights([finales['kernel:0'], finales['bias:0']])

    return modelo


def _cargar_de_disco(clave, info):
    from tensorflow import keras

    destino = ruta(info['fichero'])
    if os.path.exists(destino):
        return keras.models.load_model(destino)

    origen = info.get('fichero_origen')
    if origen and os.path.exists(ruta(origen)):
        logger.info('Convirtiendo %s a formato .keras (solo la primera vez)...', origen)
        modelo = _reconstruir_tuberculosis(ruta(origen))
        try:
            modelo.save(destino)
            logger.info('Modelo convertido y guardado en %s', destino)
        except OSError:
            logger.warning('No he podido guardar %s; se reconstruirá en cada arranque.',
                           destino)
        return modelo

    raise FileNotFoundError(f'No encuentro el modelo de {clave} en {MODELOS_DIR}')


def cargar(clave, info):
    """Devuelve el modelo de Keras, cargándolo solo la primera vez."""
    if clave not in _cache:
        _cache[clave] = _cargar_de_disco(clave, info)
    return _cache[clave]


def disponible(info):
    """¿Están los ficheros necesarios para este modelo?"""
    if os.path.exists(ruta(info['fichero'])):
        return True
    origen = info.get('fichero_origen')
    return bool(origen) and os.path.exists(ruta(origen))
