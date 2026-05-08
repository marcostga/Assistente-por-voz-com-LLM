"""
audio/stt.py — Speech-to-Text via OpenAI Whisper (local, offline)

Pipeline:
    Microfone (sounddevice @ 16kHz)
        → VAD por energia com pre-roll buffer
        → Array float32 normalizado
        → Whisper (transcrição direta via numpy — sem FFmpeg, sem disco)

Por que sem FFmpeg?
    - Gravamos diretamente em 16kHz (taxa nativa do Whisper), sem re-sampling.
    - Passamos np.ndarray ao invés de caminho de arquivo, evitando I/O em disco.
    - Menor latência, zero dependências externas de sistema.

Por que com pre-roll buffer?
    - Capturamos ~300ms de áudio ANTES da fala ser detectada.
    - Evita o Whisper "perder" a primeira sílaba (ex: "Oi" virar "i").
"""

import collections
from typing import Optional
import numpy as np
import sounddevice as sd
import scipy.signal as signal
import whisper


# ─── Configurações de gravação ────────────────────────────────────────────────
SAMPLE_RATE      = 16_000   # Hz — taxa nativa do Whisper (sem re-sampling)
CHANNELS         = 1
DTYPE            = "float32"

# ─── Parâmetros de VAD (Voice Activity Detection) ─────────────────────────────
CHUNK_DURATION   = 0.05     # s  — tamanho de cada bloco analisado (50ms)
SILENCE_THRESH   = 0.012    # RMS mínimo para considerar "voz"
SPEECH_PAD_PRE   = 0.35     # s  — pre-roll: captura X segundos ANTES da fala
SPEECH_PAD_POST  = 1.2      # s  — espera X segundos de silêncio pós-fala para encerrar
MAX_DURATION     = 30       # s  — duração máxima absoluta de uma gravação

CHUNK_SIZE       = int(SAMPLE_RATE * CHUNK_DURATION)
PRE_ROLL_CHUNKS  = int(SPEECH_PAD_PRE / CHUNK_DURATION)
SILENCE_CHUNKS   = int(SPEECH_PAD_POST / CHUNK_DURATION)
MAX_CHUNKS       = int(MAX_DURATION / CHUNK_DURATION)


class SpeechToText:
    """Motor de STT local usando OpenAI Whisper."""

    def __init__(self, model_name: str = "base"):
        """
        Args:
            model_name: Tamanho do modelo Whisper.
                'tiny'   — muito rápido, menos preciso (~39MB)
                'base'   — bom equilíbrio para pt-BR (~145MB)  ← padrão
                'small'  — mais preciso, mais lento (~466MB)
                'medium' — alta qualidade, requer GPU recomendada (~1.5GB)
        """
        print(f"[STT] Carregando modelo Whisper '{model_name}'...")
        self.model = whisper.load_model(model_name)
        self._check_device_sample_rate()
        print(f"[STT] Pronto. Modelo '{model_name}' carregado.")

    # ─── Setup ────────────────────────────────────────────────────────────────

    def _check_device_sample_rate(self):
        """
        Verifica se o dispositivo de entrada suporta 16kHz nativamente.
        Se não suportar, grava em outra taxa e usa scipy para re-samplear.
        """
        try:
            sd.check_input_settings(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE)
            self._native_rate = SAMPLE_RATE
        except sd.PortAudioError:
            # Dispositivo não suporta 16kHz — usa a taxa padrão e re-samplea depois
            info = sd.query_devices(kind="input")
            self._native_rate = int(info["default_samplerate"])
            print(
                f"[STT] Microfone não suporta 16kHz nativamente. "
                f"Gravando em {self._native_rate}Hz e re-sampleando via scipy."
            )

    # ─── Gravação com VAD ─────────────────────────────────────────────────────

    def _record(self) -> np.ndarray:
        """
        Grava o áudio usando detecção de voz por energia (VAD).

        Fases:
            1. AGUARDANDO — monitora silêncio, mantém pre-roll buffer circular
            2. GRAVANDO   — captura tudo até silêncio prolongado ou MAX_DURATION
        """
        native_chunk = int(self._native_rate * CHUNK_DURATION)
        pre_roll     = collections.deque(maxlen=PRE_ROLL_CHUNKS)
        recorded     = []
        silent_count = 0
        speaking     = False

        print("🎙️  Ouvindo... (fale normalmente, silêncio encerra)")

        with sd.InputStream(
            samplerate=self._native_rate,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=native_chunk
        ) as stream:
            for _ in range(MAX_CHUNKS):
                chunk, _ = stream.read(native_chunk)
                rms = float(np.sqrt(np.mean(chunk ** 2)))

                if not speaking:
                    pre_roll.append(chunk.copy())
                    if rms > SILENCE_THRESH:
                        speaking = True
                        print("🔴 Gravando...")
                        # Injeta o pre-roll para não perder o início da fala
                        recorded.extend(list(pre_roll))
                        recorded.append(chunk.copy())
                else:
                    recorded.append(chunk.copy())
                    if rms <= SILENCE_THRESH:
                        silent_count += 1
                        if silent_count >= SILENCE_CHUNKS:
                            print("⏹️  Silêncio detectado. Processando...")
                            break
                    else:
                        silent_count = 0

        if not recorded:
            return np.array([], dtype=DTYPE)

        audio = np.concatenate(recorded, axis=0).flatten()

        # Re-samplear para 16kHz se o microfone usou taxa diferente
        if self._native_rate != SAMPLE_RATE:
            num_samples = int(len(audio) * SAMPLE_RATE / self._native_rate)
            audio = signal.resample(audio, num_samples).astype(DTYPE)

        return audio

    # ─── Transcrição ──────────────────────────────────────────────────────────

    def _transcribe(self, audio: np.ndarray, language: str) -> Optional[str]:
        """
        Envia o array numpy diretamente ao Whisper (sem FFmpeg, sem arquivo).

        O Whisper espera: float32, mono, 16kHz, valores em [-1.0, 1.0].
        """
        # Normalização de pico — garante range [-1, 1] sem distorção
        peak = np.max(np.abs(audio))
        if peak > 0:
            audio = audio / peak

        # Clamp de segurança
        audio = np.clip(audio, -1.0, 1.0)

        result = self.model.transcribe(
            audio,
            language=language,
            fp16=False,      # CPU-safe (fp16 só funciona em GPU CUDA)
            verbose=False,
            condition_on_previous_text=False,  # Evita alucinações em frases curtas
            no_speech_threshold=0.6,           # Descarta se Whisper achar que não há fala
        )

        text = result.get("text", "").strip()

        # Filtra respostas que o Whisper inventa em silêncio
        if not text or text in (".", "...", "Obrigado.", "Obrigada."):
            return None

        return text

    # ─── Interface pública ────────────────────────────────────────────────────

    def listen(self, language: str = "pt") -> Optional[str]:
        """
        Escuta o microfone e retorna o texto transcrito.

        Args:
            language: Código ISO 639-1. 'pt' para português (pt-BR incluso).

        Returns:
            Texto transcrito, ou None se nenhuma fala válida foi detectada.
        """
        audio = self._record()

        if audio.size == 0:
            print("[STT] Nenhum áudio capturado.")
            return None

        try:
            text = self._transcribe(audio, language)
            if text:
                print(f"👤 Você disse: {text}")
            else:
                print("[STT] Nenhuma fala reconhecida.")
            return text
        except Exception as e:
            print(f"[ERRO STT] Falha na transcrição: {e}")
            return None
