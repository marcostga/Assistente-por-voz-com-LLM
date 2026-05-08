from datetime import datetime

def obter_hora() -> str:
    """Retorna a data e a hora atual do sistema do usuário."""
    agora = datetime.now()
    return f"Data e hora atual: {agora.strftime('%Y-%m-%d %H:%M:%S')}"
