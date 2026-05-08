# 👻 GHOST (General Heuristic & Operational System Transmitter)

**Um Agente de IA Autônomo Modular com Interação de Voz em Tempo Real e Sistema Auto-curável de LLMs.**

O **GHOST** é um agente de inteligência artificial desenhado para operar localmente, combinando processamento de linguagem natural avançado (Google Gemini), reconhecimento de fala (STT) e síntese de voz neural de alta fidelidade (Piper TTS). Sua arquitetura se destaca pela resiliência: o sistema gerencia limites de cota de API e erros de rede realizando o *fallback* automático entre múltiplos modelos LLM de forma transparente e mantendo o contexto da conversa.

## ✨ Funcionalidades Principais

* 🎙️ **Reconhecimento de Voz Contínuo (STT):** Ouve e entende o usuário de forma ininterrupta utilizando `SpeechRecognition`.

* 🗣️ **Síntese de Voz Neural (TTS):** Respostas incrivelmente naturais renderizadas localmente com `piper-tts` (Otimizado para streaming de áudio e limpo de artefatos markdown).

* 🧠 **Integração LLM (Google Gemini):** Raciocínio avançado capaz de invocar ferramentas do sistema automaticamente (*Function Calling*).

* 🛡️ **Resiliência e Fallback de Modelos:** Em caso de `ResourceExhausted` (fim da cota da API) ou falhas de conexão, o GHOST notifica o usuário via áudio e transita automaticamente para o próximo modelo disponível na lista de fallback, preservando todo o histórico.

* 💾 **Memória Persistente:** O histórico completo da conversa e o índice do último modelo estável são salvos em formato JSON (`history.json`), garantindo que o agente retome de onde parou entre as execuções.

* 🛠️ **Ferramentas do Sistema (Tools):** O agente possui capacidade autônoma para:

  * Gerenciar arquivos (Criar, Ler, Modificar, Deletar e Mover).

  * Executar comandos no terminal.

  * Realizar pesquisas na web (`search_engine`).

  * Realizar requisições HTTP (`http_client`).

  * Monitorar recursos físicos do PC (`system_monitor`).

  * Consultar informações temporais.

## 🏗️ Arquitetura do Sistema

O projeto é modularizado para facilitar a manutenção e a expansão. O fluxo principal ocorre da seguinte maneira:

1. **Input (STT):** O microfone captura o áudio do usuário e converte em texto.

2. **Processamento (AIAgent):** O texto é enviado ao modelo ativo do Gemini. Se o modelo falhar (erro ou limite de cota), o módulo iterativamente tenta o próximo modelo da lista até obter sucesso.

3. **Execução de Ferramentas:** Se a IA decidir que precisa criar um arquivo ou ler o estado do sistema, ela invoca as ferramentas da pasta `/tools`.

4. **Output (TTS):** A resposta gerada pela IA sofre uma filtragem para remoção de formatações visuais e pensamentos ("thinking tokens"), sendo convertida em fala pelo Piper TTS.

## 📂 Estrutura de Diretórios
```

GHOST/

│

├── agent/                  # Coração lógico e comunicação com a API LLM (AIAgent)

│   └── llm.py              # Classe principal que gerencia o modelo, histórico e fallback

├── audio/                  # Módulos de Áudio STT (Speech-to-Text) e TTS (Text-to-Speech)

├── config/                 # Configurações globais, prompts de sistema (SYSTEM_PROMPT) e logging

├── logs/                   # Arquivos gerados em runtime (history.json, last_model.txt, logs de sistema)

├── tools/                  # Ferramentas autônomas consumíveis pela IA (Function Calling)

│   ├── criar_arquivo.py

│   ├── executar_comando.py

│   ├── system_monitor.py

│   └── ...                 

├── MODELOS/                # Pasta de armazenamento para arquivos offline de modelos TTS/etc.

├── .env                    # Arquivo de variáveis de ambiente (Chave da API)

├── main.py                 # Ponto de entrada do sistema

└── requirements.txt        # Dependências do projeto

```

## 🚀 Como Instalar e Rodar

### 1. Pré-requisitos

- **Python 3.10+**
- Microfone e saídas de áudio configuradas e ativas no PC.
- Uma chave de API do Google Gemini.

### 2. Instalação

Clone o repositório e navegue até a pasta do projeto:

bash

git clone https://github.com/marcostga/Assistente-por-voz-com-LLM.git

cd ghost-ai

Instale as dependências via `pip`:

bash

pip install -r requirements.txt

### 3. Configuração

Crie um arquivo `.env` na raiz do projeto (ou edite o existente) e adicione sua chave de API do Gemini:

env

GEMINI_API_KEY=sua_chave_de_api_aqui

_(Opcional)_ Verifique e certifique-se de baixar os arquivos de modelo de voz (ex: arquivo de voz do Faber) necessários pelo `piper-tts` e colocá-los na estrutura exigida na pasta do seu sistema.

### 4. Inicialização

Inicie o sistema rodando o arquivo principal:

bash

python main.py

O GHOST testará silenciosamente a conexão com os modelos de IA disponíveis, fixará o modelo mais estável e se apresentará em áudio aguardando seus comandos.

## 🛠️ Tecnologias Utilizadas

- **[Google Generative AI](https://ai.google.dev/)** - Cérebro Lógico e Function Calling.
- **[Piper TTS](https://github.com/rhasspy/piper)** - Sintetização Neural Local Rápida.
- **[SpeechRecognition](https://pypi.org/project/SpeechRecognition/)** - Reconhecimento de Áudio.
- **[PyAudio / sounddevice](https://pypi.org/project/PyAudio/)** - Manipulação de fluxos de entrada e saída.

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---

Você pode copiar esse código Markdown e colar no seu arquivo `README.md` no repositório do GitHub. Se quiser alterar o tom ou adicionar alguma ferramenta específica que eu não detalhei nas `tools/`, basta me falar!
