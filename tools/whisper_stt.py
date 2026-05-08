import whisper
import sounddevice as sd
import numpy as np
import wave
import datetime
import os
import sys

def record_audio(filename, duration=5, fs=44100):
    print(f"Gravando por {duration} segundos...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    print("Gravação concluída.")
    
    # Salvar como WAV
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) # 16-bit
        wf.setframerate(fs)
        # Converter float32 para int16 para o formato WAV padrão
        recording_int16 = (recording * 32767).astype(np.int16)
        wf.writeframes(recording_int16.tobytes())

def transcribe_audio(filename, model_name="base"):
    print(f"Carregando modelo Whisper ({model_name})...")
    model = whisper.load_model(model_name)
    print("Transcrevendo...")
    result = model.transcribe(filename)
    return result['text'].strip()

def main():
    # Garantir que a pasta audio existe
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    # Gerar nome do arquivo com timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(audio_dir, f"recording_{timestamp}.wav")

    try:
        # 1. Grava
        record_audio(filename, duration=5)
        
        # 2. Transcreve
        text = transcribe_audio(filename)
        
        print("\n--- RESULTADO ---")
        print(f"Texto: {text}")
        print(f"Arquivo salvo em: {filename}")
        print("-----------------\n")
        
        # Imprimir apenas o texto para facilitar uso por outros scripts
        print(f"TEXT_RESULT:{text}")

    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
