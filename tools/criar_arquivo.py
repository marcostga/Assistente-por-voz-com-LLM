import os

def criar_arquivo(caminho: str, conteudo: str) -> str:
    """
    Cria um novo arquivo no computador com o conteúdo especificado. 
    Use caminhos absolutos ou relativos à raiz do projeto.
    Útil para escrever códigos, criar configurações ou salvar notas.
    """
    try:
        # Garante que as pastas pai existam
        os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        return f"Sucesso: Arquivo '{caminho}' criado."
    except Exception as e:
        return f"Erro ao criar arquivo: {e}"
