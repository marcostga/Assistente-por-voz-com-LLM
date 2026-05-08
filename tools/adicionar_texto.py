import os

def adicionar_texto(caminho_arquivo: str, texto: str) -> str:
    """Adiciona texto ao final de um arquivo existente sem apagar o conteúdo anterior.
    Args:
        caminho_arquivo: Caminho do arquivo de texto.
        texto: Texto a ser adicionado no final do arquivo.
    """
    try:
        with open(caminho_arquivo, 'a', encoding='utf-8') as f:
            f.write(texto + '\n')
        return f"Texto adicionado com sucesso ao arquivo '{caminho_arquivo}'."
    except Exception as e:
        return f"Erro ao adicionar texto no arquivo '{caminho_arquivo}': {e}"
