import os
import shutil

def mover(origem: str, destino: str) -> str:
    """Move ou renomeia um arquivo ou pasta.
    Args:
        origem: Caminho atual do arquivo ou pasta.
        destino: Novo caminho ou novo nome para o arquivo/pasta.
    """
    try:
        if not os.path.exists(origem):
            return f"Erro: A origem '{origem}' não existe."
            
        shutil.move(origem, destino)
        return f"'{origem}' movido/renomeado para '{destino}' com sucesso."
    except Exception as e:
        return f"Erro ao mover/renomear: {e}"
