import os
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"

from audio.stt import SpeechToText
from audio.tts import TextToSpeech
from agent.llm import AIAgent

def main():
    print("Iniciando o sistema GHOST...")
    stt = SpeechToText()
    tts = TextToSpeech()
    agent = AIAgent()

    tts.speak("Olá! O sistema modular foi iniciado. Como posso ajudar?")

    while True:
        # 1. Ouvir o usuário
        user_input = stt.listen()
        
        if user_input:
            # Feedback opcional de que entendeu
            # tts.speak(f"Entendi: {user_input}") 
            
            if user_input.lower() in ["sair", "encerrar", "fechar", "desligar"]:
                tts.speak("Desligando o sistema. Até logo!")
                break
            
            # 2. Processar a resposta com a IA (com fallback de modelos)
            print("\nProcessando com a IA...")
            response = agent.generate_response(user_input)

if __name__ == "__main__":
    main()
