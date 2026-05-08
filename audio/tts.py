import os
import urllib.request
import numpy as np
import sounddevice as sd
import re
from piper.voice import PiperVoice

MODEL_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx"
CONFIG_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx.json"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'audio', 'models')
MODEL_PATH = os.path.join(MODELS_DIR, 'pt_BR-faber-medium.onnx')
CONFIG_PATH = os.path.join(MODELS_DIR, 'pt_BR-faber-medium.onnx.json')

class TextToSpeech:
    def __init__(self):
        self._ensure_model_exists()
        self.voice = PiperVoice.load(MODEL_PATH)
        
    def _ensure_model_exists(self):
        if not os.path.exists(MODELS_DIR):
            os.makedirs(MODELS_DIR)
            
        if not os.path.exists(MODEL_PATH):
            print("\n[SISTEMA] Baixando modelo de voz neural de alta qualidade (Piper TTS - pt-BR). Isso ocorre apenas uma vez...")
            print("[SISTEMA] Aguarde, o download tem cerca de 60MB...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            urllib.request.urlretrieve(CONFIG_URL, CONFIG_PATH)
            print("[SISTEMA] Voz neural baixada com sucesso!\n")

    def speak(self, text):
        print(f"Agente: {text}")
        
        # Limpeza de caracteres de formatação (Markdown) para não confundir o robô
        # Remove asteriscos, hashtags, barras e crases.
        clean_text = re.sub(r'[*#/`~]', '', text)
        
        # Inicia o stream de áudio com a taxa de amostragem requerida pelo modelo
        stream = sd.OutputStream(
            samplerate=self.voice.config.sample_rate,
            channels=1,
            dtype='int16'
        )
        stream.start()
        
        # Sintetiza o texto limpo para áudio em tempo real e toca no alto-falante
        try:
            for audio_chunk in self.voice.synthesize(clean_text):
                # audio_chunk.audio_int16_array já é o array numpy no formato correto
                stream.write(audio_chunk.audio_int16_array)
        except Exception as e:
            print(f"[ERRO TTS] Falha ao reproduzir áudio: {e}")
        finally:
            stream.stop()
            stream.close()
