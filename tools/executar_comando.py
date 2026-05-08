import subprocess

def executar_comando(comando: str) -> str:
    """Executa um comando no terminal (CMD/Powershell) e retorna a saída. Use com responsabilidade.
    Args:
        comando: A string do comando a ser executado.
    """
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        saida = resultado.stdout if resultado.stdout else resultado.stderr
        if not saida:
            return "Comando executado com sucesso, mas não retornou nenhuma saída visual."
        return f"Saída do comando:\n{saida}"
    except Exception as e:
        return f"Erro crítico ao executar o comando '{comando}': {e}"
