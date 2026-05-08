import logging
import os
from datetime import datetime

# Define a pasta raiz do projeto e cria a pasta logs se não existir
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Nome do arquivo de log, ex: logs/agent_connection.log
log_filename = os.path.join(LOG_DIR, "agent_connection.log")

# Configuração base do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        #logging.StreamHandler() # Continua imprimindo no console
    ]
)

# Criamos uma instância dedicada para o agente
agent_logger = logging.getLogger("AIAgent")
