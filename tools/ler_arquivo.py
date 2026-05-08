def ler_arquivo(caminho: str) -> str:
    """
    Lê o conteúdo de um arquivo de texto existente no computador e retorna o texto.
    """
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erro ao ler arquivo: {e}"
