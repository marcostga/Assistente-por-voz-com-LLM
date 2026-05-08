import os

def criar_pasta(caminho: str) -> str:
    """
    Cria uma nova pasta no computador.
    """
    try:
        os.makedirs(caminho, exist_ok=True)
        return f"Sucesso: Pasta '{caminho}' criada."
    except Exception as e:
        return f"Erro ao criar pasta: {e}"
