from .criar_arquivo import criar_arquivo
from .criar_pasta import criar_pasta
from .ler_arquivo import ler_arquivo
from .listar_diretorio import listar_diretorio
from .deletar import deletar
from .mover import mover
from .adicionar_texto import adicionar_texto
from .obter_hora import obter_hora
from .executar_comando import executar_comando

# Exporta a lista de ferramentas que o Gemini vai usar
ferramentas_do_sistema = [
    criar_arquivo, 
    criar_pasta, 
    ler_arquivo, 
    listar_diretorio,
    deletar,
    mover,
    adicionar_texto,
    obter_hora,
    executar_comando
]
