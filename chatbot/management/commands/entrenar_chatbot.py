"""
Reentrena el modelo de intenciones del chatbot a partir de `chatbot/modelo/intents.json`.

    python manage.py entrenar_chatbot

Genera tres ficheros en `chatbot/modelo/`:
    chat_model.keras      la red entrenada
    tokenizer.pickle      el vocabulario
    label_encoder.pickle  la correspondencia índice <-> etiqueta

El modelo que venía con el proyecto estaba entrenado en historia del arte (de otro
proyecto), así que respondía sobre el Renacimiento a quien preguntaba por sus citas.
"""
import json
import os
import pickle
import unicodedata

from django.core.management.base import BaseCommand, CommandError

MODELO_DIR = os.path.join('chatbot', 'modelo')
MAX_LEN = 20              # debe coincidir con chatbot/views.py
VOCAB_SIZE = 2000
DIM_EMBEDDING = 32


def normalizar(texto):
    """Minúsculas y sin tildes, para que 'cómo' y 'como' sean la misma palabra."""
    texto = texto.lower().strip()
    sin_tildes = unicodedata.normalize('NFD', texto)
    return ''.join(c for c in sin_tildes if unicodedata.category(c) != 'Mn')


class Command(BaseCommand):
    help = 'Reentrena el modelo de intenciones del chatbot desde intents.json.'

    def add_arguments(self, parser):
        parser.add_argument('--epochs', type=int, default=350,
                            help='Número de épocas de entrenamiento (por defecto 350).')

    def handle(self, *args, **opciones):
        # Import perezoso: no queremos cargar TensorFlow en cada comando de manage.py
        import numpy as np
        from sklearn.preprocessing import LabelEncoder
        from tensorflow import keras

        ruta_intents = os.path.join(MODELO_DIR, 'intents.json')
        if not os.path.exists(ruta_intents):
            raise CommandError(f'No encuentro {ruta_intents}')

        with open(ruta_intents, encoding='utf-8') as f:
            datos = json.load(f)

        frases, etiquetas = [], []
        for intent in datos['intents']:
            for patron in intent['patterns']:
                frases.append(normalizar(patron))
                etiquetas.append(intent['tag'])

        num_clases = len(set(etiquetas))
        self.stdout.write(f'Intenciones: {num_clases}')
        self.stdout.write(f'Frases de entrenamiento: {len(frases)}')

        codificador = LabelEncoder()
        y = codificador.fit_transform(etiquetas)

        tokenizer = keras.preprocessing.text.Tokenizer(
            num_words=VOCAB_SIZE, oov_token='<OOV>')
        tokenizer.fit_on_texts(frases)
        secuencias = tokenizer.texts_to_sequences(frases)
        X = keras.preprocessing.sequence.pad_sequences(
            secuencias, truncating='post', maxlen=MAX_LEN)

        modelo = keras.Sequential([
            keras.layers.Input(shape=(MAX_LEN,)),
            keras.layers.Embedding(VOCAB_SIZE, DIM_EMBEDDING),
            keras.layers.GlobalAveragePooling1D(),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(num_clases, activation='softmax'),
        ])
        modelo.compile(loss='sparse_categorical_crossentropy',
                       optimizer='adam', metrics=['accuracy'])

        self.stdout.write('\nEntrenando...')
        historial = modelo.fit(np.array(X), np.array(y),
                               epochs=opciones['epochs'], verbose=0)
        precision = historial.history['accuracy'][-1]
        self.stdout.write(f'Precisión sobre el conjunto de entrenamiento: {precision:.1%}')

        os.makedirs(MODELO_DIR, exist_ok=True)
        modelo.save(os.path.join(MODELO_DIR, 'chat_model.keras'))
        with open(os.path.join(MODELO_DIR, 'tokenizer.pickle'), 'wb') as f:
            pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)
        with open(os.path.join(MODELO_DIR, 'label_encoder.pickle'), 'wb') as f:
            pickle.dump(codificador, f, protocol=pickle.HIGHEST_PROTOCOL)

        self.stdout.write(self.style.SUCCESS(
            f'\nModelo guardado en {MODELO_DIR}/'))
        if precision < 0.9:
            self.stdout.write(self.style.WARNING(
                'La precisión es baja. Añade más variantes en los "patterns" '
                'de intents.json o sube --epochs.'))
