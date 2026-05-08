import speech_recognition as sr

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self):
        with sr.Microphone() as source:
            #print("Ajustando o ruído ambiente... Aguarde.")
            self.recognizer.adjust_for_ambient_noise(source)
            print("Pode falar!")
            audio = self.recognizer.listen(source)

        try:
            print("Reconhecendo...")
            # Usando Google STT (gratuito e não precisa de chave)
            text = self.recognizer.recognize_google(audio, language="pt-BR")
            print(f"Você disse: {text}")
            return text
        except sr.UnknownValueError:
            print("Não entendi o que você disse.")
            return None
        except sr.RequestError as e:
            print(f"Erro ao solicitar resultados do serviço STT; {e}")
            return None
