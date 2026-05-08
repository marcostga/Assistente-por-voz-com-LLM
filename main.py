import os
import sys

# Suprimir logs verbosos de gRPC/protobuf antes de qualquer import do SDK
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"

from audio.stt import SpeechToText
from audio.tts import TextToSpeech
from agent.llm import AIAgent


def main():
    print("=" * 50)
    print("  Iniciando o sistema GHOST...")
    print("=" * 50)

    stt = SpeechToText(model_name="base")   # Whisper 'base' — bom custo-benefício para pt-BR
    tts = TextToSpeech()
    agent = AIAgent(tts=tts)  # Compartilha a mesma instância — carrega o modelo só uma vez

    tts.speak("Olá! Sistema GHOST iniciado. Como posso ajudar?")

    try:
        while True:
            # 1. Escuta o usuário com detecção de silêncio automática
            user_input = stt.listen(language="pt")

            if not user_input:
                continue

            # 2. Verifica comandos de encerramento
            if user_input.lower().strip() in ["sair", "encerrar", "fechar", "desligar", "exit", "quit"]:
                tts.speak("Desligando o sistema. Até logo!")
                break

            # 3. Processa com a IA
            print("\n[SISTEMA] Processando com a IA...")
            agent.generate_response(user_input)

    except KeyboardInterrupt:
        print("\n[SISTEMA] Interrompido pelo usuário (Ctrl+C). Encerrando...")
        tts.speak("Encerrando. Até logo!")
    except Exception as e:
        print(f"[ERRO FATAL] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
