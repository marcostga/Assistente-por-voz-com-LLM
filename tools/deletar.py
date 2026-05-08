import os
import shutil

def deletar(caminho: str) -> str:
    """Deleta um arquivo ou uma pasta no sistema.
    Args:
        caminho: O caminho absoluto ou relativo do arquivo ou pasta a ser deletado.
    """
    try:
        if not os.path.exists(caminho):
            return f"Erro: O caminho '{caminho}' não existe."
            
        if os.path.isfile(caminho):
            os.remove(caminho)
            return f"Arquivo '{caminho}' deletado com sucesso."
        elif os.path.isdir(caminho):
            shutil.rmtree(caminho)
            return f"Pasta '{caminho}' e todo o seu conteúdo foram deletados com sucesso."
    except Exception as e:
        return f"Erro ao deletar '{caminho}': {e}"
