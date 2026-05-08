import os

def listar_diretorio(caminho: str = ".") -> str:
    """
    Lista todos os arquivos e pastas dentro de um diretório específico. 
    Se não for fornecido caminho, lista a pasta atual.
    """
    try:
        itens = os.listdir(caminho)
        return f"Conteúdo do diretório '{caminho}':\n" + "\n".join(itens)
    except Exception as e:
        return f"Erro ao listar diretório: {e}"
