import os
import json
import google.generativeai as genai
from google.api_core import exceptions
from config.settings import GEMINI_API_KEY, get_models_list
from config.logger import agent_logger
from config.prompts import SYSTEM_PROMPT
from tools import ferramentas_do_sistema
from audio.tts import TextToSpeech

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, 'logs', 'history.json')
LAST_MODEL_FILE = os.path.join(BASE_DIR, 'logs', 'last_model.txt')

class AIAgent:
    def __init__(self, tts: TextToSpeech):
        """
        Args:
            tts: Instância compartilhada de TextToSpeech — evita carregar o
                 modelo Pocket-TTS duas vezes na memória.
        """
        self.tts = tts
        self._configure_genai()
        self.models = get_models_list()
        self.active_chat = None
        self.current_model_idx = self._load_last_model_idx()
        self.history = self._load_history()

        # Pré-conecta ao modelo LLM antes do loop de áudio iniciar
        print("[SISTEMA] Iniciando os motores de IA e pré-conectando aos modelos...")
        if not self._start_new_chat(self.current_model_idx):
            print("[ERRO FATAL] Nenhum modelo pôde ser conectado na inicialização.")

    def _configure_genai(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            agent_logger.info("Chave de API do Gemini configurada com sucesso.")
        else:
            agent_logger.warning("AVISO: GEMINI_API_KEY não encontrada no arquivo .env!")

    def _load_history(self):
        """Carrega o histórico do arquivo JSON, se existir."""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    hist = json.load(f)
                agent_logger.info("Histórico anterior carregado do arquivo JSON.")
                return hist
            except Exception as e:
                agent_logger.error(f"Erro ao carregar history.json: {e}")
        return []

    def _load_last_model_idx(self):
        """Carrega o índice do último modelo que funcionou bem."""
        if os.path.exists(LAST_MODEL_FILE):
            try:
                with open(LAST_MODEL_FILE, 'r') as f:
                    model_name = f.read().strip()
                if model_name in self.models:
                    return self.models.index(model_name)
            except:
                pass
        return 0

    def _save_last_model(self, model_name):
        """Salva o nome do modelo atual para priorizá-lo no próximo boot."""
        try:
            with open(LAST_MODEL_FILE, 'w') as f:
                f.write(model_name)
        except:
            pass

    def _start_new_chat(self, start_idx=0):
        # Configurações de geração para maior estabilidade
        generation_config = genai.GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
        )

        # Varre a lista a partir do start_idx, dando a volta (wrap-around) se necessário
        for offset in range(len(self.models)):
            idx = (start_idx + offset) % len(self.models)
            model_name = self.models[idx]
            
            agent_logger.info(f"Tentando estabelecer sessão com o modelo: {model_name}...")
            print(f"\n[SISTEMA] Tentando conectar ao modelo: {model_name}...")
            try:
                model_id = model_name if model_name.startswith("models/") else f"models/{model_name}"
                model = genai.GenerativeModel(
                    model_name=model_id,
                    system_instruction=SYSTEM_PROMPT,
                    tools=ferramentas_do_sistema,
                    generation_config=generation_config
                )
                
                # Dispara um ping de teste silencioso para confirmar se o modelo está 100% online
                print(f"[SISTEMA] Disparando ping de teste ('oi') no modelo {model_name} para validar a API...")
                model.generate_content("Ping de teste de conexão. Responda apenas com a palavra 'OK'.")
                
                # Se passou no teste acima sem dar erro, iniciamos a sala de chat com o histórico
                self.active_chat = model.start_chat(
                    history=self.history,
                    enable_automatic_function_calling=True
                )
                
                self.current_model_idx = idx
                self._save_last_model(model_name)
                
                agent_logger.info(f"Sessão de chat fixada com o modelo: {model_name}")
                print(f"[SISTEMA] Modelo {model_name} passou no teste e foi fixado com sucesso!")
                return True
            except Exception as e:
                agent_logger.error(f"Erro no modelo {model_name}: {e}")
                print(f"[SISTEMA] Erro ao conectar/testar o modelo {model_name}. Pulando para o próximo da lista...")
                continue
        return False

    def generate_response(self, prompt):
        if not self.active_chat and not self._start_new_chat(self.current_model_idx):
            msg = "Erro: Nenhum modelo disponível."
            self.tts.speak(msg)
            return msg

        # Tenta enviar a mensagem varrendo no máximo len(models) vezes para evitar loop infinito
        for _attempt in range(len(self.models)):
            try:
                agent_logger.info(f"Enviando mensagem para o modelo ativo: {self.models[self.current_model_idx]}")
                # O SDK gerencia as tool calls aqui automaticamente
                response = self.active_chat.send_message(prompt)
                
                # Modelos de raciocínio (thinking) retornam os pensamentos na primeira parte e a resposta na última.
                final_text = response.parts[-1].text if response.parts else response.text
                
                # Salva histórico após sucesso
                self._save_history()
                agent_logger.info("Resposta gerada com sucesso e histórico salvo no JSON.")
                
                # Fala apenas a resposta final
                if final_text:
                    self.tts.speak(final_text)
                
                return final_text

            except exceptions.ResourceExhausted:
                agent_logger.warning(f"Limite de cota atingido no modelo {self.models[self.current_model_idx]}.")
                print(f"[SISTEMA] Limite de cota atingido no modelo {self.models[self.current_model_idx]}. Passando para o próximo...")
                self.tts.speak("Meu limite de processamento com este modelo foi atingido. Mudando para o próximo cérebro...")
                next_idx = (self.current_model_idx + 1) % len(self.models)
                if not self._start_new_chat(next_idx):
                    break
            except Exception as e:
                agent_logger.error(f"Erro na geração com {self.models[self.current_model_idx]}: {e}")
                print(f"[SISTEMA] Ocorreu um erro no modelo {self.models[self.current_model_idx]}. Passando para o próximo...")
                next_idx = (self.current_model_idx + 1) % len(self.models)
                if not self._start_new_chat(next_idx):
                    break
        
        msg = "Desculpe, testei todos os modelos da sua lista e nenhum pôde me responder no momento."
        self.tts.speak(msg)
        return msg

    def _save_history(self):
        """Versão simplificada que mantém a estrutura básica para o JSON"""
        if not self.active_chat: return
        
        serializable_history = []
        for content in self.active_chat.history:
            if content.role in ["user", "model"]:
                # Se for o modelo, pega apenas a última parte (ignora pensamentos)
                if content.role == "model" and content.parts:
                    text_parts = [content.parts[-1].text] if hasattr(content.parts[-1], 'text') else []
                else:
                    text_parts = [p.text for p in content.parts if hasattr(p, 'text') and p.text]
                
                if text_parts:
                    serializable_history.append({
                        "role": content.role,
                        "parts": text_parts
                    })
        
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(serializable_history, f, indent=4, ensure_ascii=False)
            self.history = serializable_history
        except Exception as e:
            agent_logger.error(f"Erro ao salvar arquivo history.json: {e}")
