# chatbot_app/views.py
from django.shortcuts import render
from django.http import JsonResponse
import json
import numpy as np
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder
import pickle
import pyttsx3
import os

# Load model, tokenizer, and label encoder
model = keras.models.load_model(os.path.join(os.path.dirname(__file__), 'modelo/chat_model.keras'))
with open(os.path.join(os.path.dirname(__file__), 'modelo/tokenizer.pickle'), 'rb') as handle:
    tokenizer = pickle.load(handle)
with open(os.path.join(os.path.dirname(__file__), 'modelo/label_encoder.pickle'), 'rb') as enc:
    lbl_encoder = pickle.load(enc)
with open(os.path.join(os.path.dirname(__file__), "modelo/intents.json"), encoding='utf-8') as file:
    data = json.load(file)

# Parameters
max_len = 20

def home(request):
    return render(request, 'chatbot/chatbot.html')

def get_response(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        
        result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([message]), truncating='post', maxlen=max_len))
        tag = lbl_encoder.inverse_transform([np.argmax(result)])
        response = ""

        for i in data['intents']:
            if i['tag'] == tag:
                response = np.random.choice(i['responses'])
                texto_a_voz(response)

        return JsonResponse({"response": response})

def texto_a_voz(texto):
    engine = pyttsx3.init()
    
    # Puedes configurar propiedades como el volumen y la velocidad
    engine.setProperty('rate', 150)  # Velocidad de habla
    engine.setProperty('volume', 1)  # Volumen (0.0 a 1.0)

    # Convierte el texto a voz
    engine.say(texto)
    
    # Reproduce la voz
    engine.runAndWait()
