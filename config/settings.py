import os
import json
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Caminho para o JSON de modelos
MODELS_PATH = os.path.join(BASE_DIR, 'MODELOS', 'MODELOS.json')

def get_models_list():
    try:
        with open(MODELS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar lista de modelos: {e}")
        return []
