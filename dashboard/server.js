const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// ─── Paths ────────────────────────────────────────────────────────────────────
const ROOT = path.resolve(__dirname, '..');
const STT_FILE     = path.join(ROOT, 'audio', 'stt.py');
const TTS_FILE     = path.join(ROOT, 'audio', 'tts.py');
const LLM_FILE     = path.join(ROOT, 'agent', 'llm.py');
const PROMPTS_FILE = path.join(ROOT, 'config', 'prompts.py');
const MODELOS_FILE = path.join(ROOT, 'MODELOS', 'MODELOS.json');
const ENV_FILE     = path.join(ROOT, '.env');
const LOG_FILE     = path.join(ROOT, 'logs', 'agent_connection.log');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ─── Helpers ──────────────────────────────────────────────────────────────────

function readFile(p) {
  try { return fs.readFileSync(p, 'utf-8'); } catch { return ''; }
}

function writeFile(p, content) {
  fs.writeFileSync(p, content, 'utf-8');
}

/** Reads a numeric constant: CONST_NAME = 1.23 */
function readNum(src, name) {
  const m = src.match(new RegExp(`${name}\\s*=\\s*([\\d._]+)`));
  return m ? parseFloat(m[1].replace(/_/g, '')) : null;
}

/** Reads a string constant: CONST_NAME = "value" */
function readStr(src, name) {
  const m = src.match(new RegExp(`${name}\\s*=\\s*["']([^"']+)["']`));
  return m ? m[1] : null;
}

/** Replaces a numeric constant in source text */
function setNum(src, name, value) {
  return src.replace(new RegExp(`(${name}\\s*=\\s*)[\\d._]+`), `$1${value}`);
}

/** Replaces a string constant in source text */
function setStr(src, name, value) {
  return src.replace(new RegExp(`(${name}\\s*=\\s*)["'][^"']*["']`), `$1"${value}"`);
}

/** Reads the SYSTEM_PROMPT multiline string from prompts.py */
function readSystemPrompt(src) {
  const m = src.match(/SYSTEM_PROMPT\s*=\s*"""([\s\S]*?)"""/);
  return m ? m[1].trim() : '';
}

/** Writes back the SYSTEM_PROMPT */
function setSystemPrompt(src, value) {
  return src.replace(
    /SYSTEM_PROMPT\s*=\s*"""[\s\S]*?"""/,
    `SYSTEM_PROMPT = """\n${value}"""`
  );
}

/** Reads .env key */
function readEnvKey(src, key) {
  const m = src.match(new RegExp(`^${key}=(.*)$`, 'm'));
  return m ? m[1].trim() : '';
}

/** Sets .env key */
function setEnvKey(src, key, value) {
  if (new RegExp(`^${key}=`, 'm').test(src)) {
    return src.replace(new RegExp(`^(${key}=).*$`, 'm'), `$1${value}`);
  }
  return src.trimEnd() + `\n${key}=${value}\n`;
}

/** Reads generation_config fields from llm.py */
function readGenConfig(src) {
  return {
    temperature:      readNum(src, 'temperature'),
    top_p:            readNum(src, 'top_p'),
    top_k:            readNum(src, 'top_k'),
    max_output_tokens: readNum(src, 'max_output_tokens'),
  };
}

// ─── GET /api/config ──────────────────────────────────────────────────────────

app.get('/api/config', (req, res) => {
  const sttSrc     = readFile(STT_FILE);
  const ttsSrc     = readFile(TTS_FILE);
  const llmSrc     = readFile(LLM_FILE);
  const promptsSrc = readFile(PROMPTS_FILE);
  const envSrc     = readFile(ENV_FILE);

  let models = [];
  try { models = JSON.parse(readFile(MODELOS_FILE)); } catch {}

  res.json({
    stt: {
      model_name:       readStr(sttSrc, 'model_name') || 'base',
      silence_thresh:   readNum(sttSrc, 'SILENCE_THRESH'),
      speech_pad_pre:   readNum(sttSrc, 'SPEECH_PAD_PRE'),
      speech_pad_post:  readNum(sttSrc, 'SPEECH_PAD_POST'),
      max_duration:     readNum(sttSrc, 'MAX_DURATION'),
      chunk_duration:   readNum(sttSrc, 'CHUNK_DURATION'),
    },
    tts: {
      language_model: readStr(ttsSrc, 'LANGUAGE_MODEL'),
      voice_name:     readStr(ttsSrc, 'VOICE_NAME'),
    },
    llm: {
      api_key:           readEnvKey(envSrc, 'GEMINI_API_KEY'),
      models_list:       models,
      ...readGenConfig(llmSrc),
    },
    agent: {
      system_prompt: readSystemPrompt(promptsSrc),
    },
  });
});

// ─── POST /api/config ─────────────────────────────────────────────────────────

app.post('/api/config', (req, res) => {
  try {
    const { stt, tts, llm, agent } = req.body;

    // --- STT ---
    if (stt) {
      let src = readFile(STT_FILE);
      if (stt.silence_thresh  != null) src = setNum(src, 'SILENCE_THRESH',  stt.silence_thresh);
      if (stt.speech_pad_pre  != null) src = setNum(src, 'SPEECH_PAD_PRE',  stt.speech_pad_pre);
      if (stt.speech_pad_post != null) src = setNum(src, 'SPEECH_PAD_POST', stt.speech_pad_post);
      if (stt.max_duration    != null) src = setNum(src, 'MAX_DURATION',     stt.max_duration);
      if (stt.chunk_duration  != null) src = setNum(src, 'CHUNK_DURATION',   stt.chunk_duration);
      writeFile(STT_FILE, src);
    }

    // --- TTS ---
    if (tts) {
      let src = readFile(TTS_FILE);
      if (tts.language_model) src = setStr(src, 'LANGUAGE_MODEL', tts.language_model);
      if (tts.voice_name)     src = setStr(src, 'VOICE_NAME',     tts.voice_name);
      writeFile(TTS_FILE, src);
    }

    // --- LLM generation config ---
    if (llm) {
      let src = readFile(LLM_FILE);
      if (llm.temperature         != null) src = setNum(src, 'temperature',         llm.temperature);
      if (llm.top_p               != null) src = setNum(src, 'top_p',               llm.top_p);
      if (llm.top_k               != null) src = setNum(src, 'top_k',               llm.top_k);
      if (llm.max_output_tokens   != null) src = setNum(src, 'max_output_tokens',    llm.max_output_tokens);
      writeFile(LLM_FILE, src);

      // Models list
      if (Array.isArray(llm.models_list)) {
        writeFile(MODELOS_FILE, JSON.stringify(llm.models_list, null, '\t'));
      }

      // API key
      if (llm.api_key != null) {
        let env = readFile(ENV_FILE);
        env = setEnvKey(env, 'GEMINI_API_KEY', llm.api_key);
        writeFile(ENV_FILE, env);
      }
    }

    // --- Agent prompt ---
    if (agent && agent.system_prompt != null) {
      let src = readFile(PROMPTS_FILE);
      src = setSystemPrompt(src, agent.system_prompt);
      writeFile(PROMPTS_FILE, src);
    }

    res.json({ ok: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok: false, error: err.message });
  }
});

// ─── GET /api/logs ────────────────────────────────────────────────────────────

app.get('/api/logs', (req, res) => {
  try {
    const content = readFile(LOG_FILE);
    // Return last 200 lines
    const lines = content.split('\n').filter(Boolean);
    res.json({ lines: lines.slice(-200).reverse() });
  } catch {
    res.json({ lines: [] });
  }
});

// ─── Start ────────────────────────────────────────────────────────────────────

app.listen(PORT, () => {
  console.log(`\n🚀 GHOST Dashboard rodando em http://localhost:${PORT}\n`);
});
