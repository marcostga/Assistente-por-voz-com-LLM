"""
audio/tts.py — Text-to-Speech via Pocket-TTS (Kyutai, local, offline, CPU)

Modelo:  'portuguese_24l' — variante 24 camadas, maior qualidade para pt-BR
Voz:     'rafael' — voz masculina nativa em português (pré-incluída no pacote)
Pipeline:
    Texto limpo
        → TTSModel.generate_audio()   (inferência local, ~200ms first-chunk)
        → Tensor PyTorch 1D (PCM float32)
        → NumPy array → sounddevice (reprodução direta, sem arquivo em disco)

Voice state caching:
    - Na primeira execução, gera e salva o state em .safetensors (~rápido)
    - Nas execuções seguintes, carrega o cache do disco (muito mais rápido)

Referência: https://github.com/kyutai-labs/pocket-tts
"""

import os
import re
import numpy as np
import sounddevice as sd
from pocket_tts import TTSModel, export_model_state

# ─── Configurações ────────────────────────────────────────────────────────────

# Modelo de linguagem: 'portuguese' (12 camadas, mais rápido)
#                      'portuguese_24l' (24 camadas, melhor qualidade) ← recomendado
LANGUAGE_MODEL = "portuguese_24l"

# Voz pt-BR disponível: 'rafael' (única voz pt nativa no catálogo)
VOICE_NAME = "rafael"

BASE_DIR    = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR  = os.path.join(BASE_DIR, "audio", "models")
VOICE_CACHE = os.path.join(MODELS_DIR, f"voice_{VOICE_NAME}.safetensors")


class TextToSpeech:
    """Motor de TTS local usando Pocket-TTS (Kyutai)."""

    def __init__(self):
        os.makedirs(MODELS_DIR, exist_ok=True)
        self._load_model()

    # ─── Inicialização ────────────────────────────────────────────────────────

    def _load_model(self):
        """
        Carrega o modelo TTS e o voice state, com cache em safetensors para
        inicializações rápidas após a primeira execução.
        """
        print(f"[TTS] Carregando modelo Pocket-TTS '{LANGUAGE_MODEL}'...")
        print("[TTS] (Primeira execução faz download automático do modelo ~100MB)")

        # load_model() baixa o modelo automaticamente do HuggingFace se necessário
        self.model = TTSModel.load_model(LANGUAGE_MODEL)
        self.sample_rate = self.model.sample_rate

        # Carrega ou cria o cache de voice state
        if os.path.exists(VOICE_CACHE):
            # Cache encontrado — carregamento rápido (apenas lê kvcache do disco)
            print(f"[TTS] Carregando voice state do cache: {os.path.basename(VOICE_CACHE)}")
            self.voice_state = self.model.get_state_for_audio_prompt(VOICE_CACHE)
        else:
            # Primeira vez — processa o áudio de referência da voz e salva cache
            print(f"[TTS] Configurando voz '{VOICE_NAME}' pela primeira vez...")
            self.voice_state = self.model.get_state_for_audio_prompt(VOICE_NAME)
            print(f"[TTS] Salvando cache de voz em: {VOICE_CACHE}")
            export_model_state(self.voice_state, VOICE_CACHE)
            print("[TTS] Cache salvo. Próximas inicializações serão mais rápidas.")

        print(f"[TTS] Pronto. Voz '{VOICE_NAME}' @ {self.sample_rate}Hz.")

    # ─── Utilitários ──────────────────────────────────────────────────────────

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Remove formatação Markdown para não confundir o modelo TTS.
        Preserva pontuação e acentuação naturais do português.
        """
        # Remove símbolos de formatação: *, #, `, ~, \, __
        clean = re.sub(r'[*#`~\\]|_{2,}', '', text)
        # Colapsa espaços extras
        clean = re.sub(r' {2,}', ' ', clean).strip()
        return clean

    # ─── Interface pública ────────────────────────────────────────────────────

    def speak(self, text: str) -> None:
        """
        Sintetiza o texto e reproduz diretamente no alto-falante.

        Args:
            text: Texto a ser falado. Pode conter Markdown — será limpo.
        """
        print(f"🤖 Agente: {text}")

        clean = self._clean_text(text)
        if not clean:
            return

        # Aviso para textos muito longos (>500 chars podem demorar mais de 10s no CPU)
        if len(clean) > 500:
            print(f"[TTS] Aviso: texto longo ({len(clean)} chars). A síntese pode demorar.")

        try:
            # Gera o áudio — retorna Tensor PyTorch 1D com PCM float32
            audio_tensor = self.model.generate_audio(self.voice_state, clean)

            # .cpu() garante compatibilidade tanto em CPU quanto GPU antes do .numpy()
            audio_np = audio_tensor.cpu().numpy().astype(np.float32)

            # Para qualquer reprodução anterior antes de iniciar a nova
            # (evita sobreposição se speak() for chamado enquanto ainda está tocando)
            sd.stop()

            # Reprodução direta via sounddevice (bloqueante — aguarda terminar)
            sd.play(audio_np, samplerate=self.sample_rate)
            sd.wait()

        except Exception as e:
            print(f"[ERRO TTS] Falha ao sintetizar/reproduzir: {e}")
            sd.stop()  # Garante limpeza do stream mesmo em caso de erro

