/* app.js — GHOST Dashboard Logic */

// ── State ────────────────────────────────────────────────────────────────────
let config = {};
let modelsList = [];
let dragSrc = null;

// ── Tab Navigation ────────────────────────────────────────────────────────────
const TAB_META = {
  stt:   { title: 'Speech-to-Text',   desc: 'Configurações do módulo de reconhecimento de voz (Whisper local)' },
  tts:   { title: 'Text-to-Speech',   desc: 'Configurações do módulo de síntese de voz (Pocket-TTS / Kyutai)' },
  llm:   { title: 'Modelo de IA',     desc: 'Chave de API, modelos Gemini e parâmetros de geração' },
  agent: { title: 'Agente',           desc: 'System prompt e personalidade do GHOST' },
  logs:  { title: 'Logs',             desc: 'Histórico de conexões e eventos do agente' },
};

document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => switchTab(btn.dataset.tab));
});

function switchTab(name) {
  document.querySelectorAll('.nav-item').forEach(b => b.classList.toggle('active', b.dataset.tab === name));
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.id === `tab-${name}`));
  document.getElementById('tab-title').textContent = TAB_META[name].title;
  document.getElementById('tab-desc').textContent  = TAB_META[name].desc;
  if (name === 'logs') loadLogs();
}

// ── Radio Cards ───────────────────────────────────────────────────────────────
function setupRadioGroup(groupId, onChange) {
  const group = document.getElementById(groupId);
  if (!group) return;
  group.querySelectorAll('.radio-card').forEach(card => {
    card.addEventListener('click', () => {
      group.querySelectorAll('.radio-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      card.querySelector('input[type="radio"]').checked = true;
      if (onChange) onChange(card.dataset.value);
    });
  });
}

function setRadio(groupId, value) {
  const group = document.getElementById(groupId);
  if (!group) return;
  group.querySelectorAll('.radio-card').forEach(card => {
    const match = card.dataset.value === value;
    card.classList.toggle('selected', match);
    if (match) card.querySelector('input[type="radio"]').checked = true;
  });
}

function getRadio(groupId) {
  const group = document.getElementById(groupId);
  if (!group) return null;
  const sel = group.querySelector('.radio-card.selected');
  return sel ? sel.dataset.value : null;
}

// ── Slider helpers ────────────────────────────────────────────────────────────
function updateVal(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function setSlider(id, value, suffix = '') {
  const el = document.getElementById(id);
  if (!el) return;
  el.value = value;
  // find the associated val-display
  const label = el.closest('.field')?.querySelector('.val-display');
  if (label) label.textContent = suffix ? value + suffix : value;
}

// ── Load Config ───────────────────────────────────────────────────────────────
async function loadConfig() {
  try {
    const res = await fetch('/api/config');
    config = await res.json();
    populate(config);
    setStatus(true);
  } catch (e) {
    setStatus(false);
    showToast('Erro ao carregar configurações: ' + e.message, 'err');
  }
}

function populate(cfg) {
  const stt = cfg.stt || {};
  const tts = cfg.tts || {};
  const llm = cfg.llm || {};
  const agent = cfg.agent || {};

  // STT
  setRadio('stt-model-group', stt.model_name || 'base');
  setSlider('stt-silence-thresh', stt.silence_thresh ?? 0.012, '');
  updateVal('val-silence-thresh', stt.silence_thresh ?? 0.012);
  setSlider('stt-pad-pre',  stt.speech_pad_pre  ?? 0.35, 's');
  setSlider('stt-pad-post', stt.speech_pad_post ?? 1.2,  's');
  setSlider('stt-max-dur',  stt.max_duration    ?? 30,   's');

  // TTS
  setRadio('tts-model-group', tts.language_model || 'portuguese_24l');
  setRadio('tts-voice-group', tts.voice_name || 'rafael');
  document.getElementById('tts-cache-info').innerHTML =
    `<span class="mono">audio/models/voice_${tts.voice_name || 'rafael'}.safetensors</span>`;

  // LLM
  const apiInput = document.getElementById('llm-api-key');
  if (apiInput) apiInput.value = llm.api_key || '';
  setSlider('llm-temperature', llm.temperature ?? 0.7, '');
  updateVal('val-temperature', llm.temperature ?? 0.7);
  setSlider('llm-top-p', llm.top_p ?? 0.95, '');
  updateVal('val-top-p', llm.top_p ?? 0.95);
  setSlider('llm-top-k', llm.top_k ?? 40, '');
  updateVal('val-top-k', llm.top_k ?? 40);
  setSlider('llm-max-tokens', llm.max_output_tokens ?? 2048, '');
  updateVal('val-max-tokens', llm.max_output_tokens ?? 2048);
  modelsList = [...(llm.models_list || [])];
  renderModelsList();

  // Agent
  const promptEl = document.getElementById('agent-prompt');
  if (promptEl) promptEl.value = agent.system_prompt || '';
}

// ── Models List ───────────────────────────────────────────────────────────────
function renderModelsList() {
  const container = document.getElementById('models-list');
  container.innerHTML = '';
  modelsList.forEach((m, i) => {
    const item = document.createElement('div');
    item.className = 'model-item';
    item.draggable = true;
    item.dataset.index = i;
    item.innerHTML = `
      <span class="drag-handle">⠿</span>
      <span class="model-rank">#${i + 1}</span>
      <span class="model-name">${m}</span>
      <button class="model-delete" onclick="removeModel(${i})" title="Remover">✕</button>
    `;

    // Drag & drop reorder
    item.addEventListener('dragstart', e => {
      dragSrc = i;
      e.dataTransfer.effectAllowed = 'move';
      item.style.opacity = '0.5';
    });
    item.addEventListener('dragend',  () => item.style.opacity = '1');
    item.addEventListener('dragover', e => { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; });
    item.addEventListener('drop', e => {
      e.preventDefault();
      if (dragSrc === null || dragSrc === i) return;
      const moved = modelsList.splice(dragSrc, 1)[0];
      modelsList.splice(i, 0, moved);
      dragSrc = null;
      renderModelsList();
    });

    container.appendChild(item);
  });
}

function addModel() {
  const input = document.getElementById('new-model-input');
  const val = input.value.trim();
  if (!val) return;
  if (!modelsList.includes(val)) {
    modelsList.push(val);
    renderModelsList();
  }
  input.value = '';
}

function removeModel(idx) {
  modelsList.splice(idx, 1);
  renderModelsList();
}

// ── Save Config ───────────────────────────────────────────────────────────────
async function saveConfig() {
  const btn = document.getElementById('save-btn');
  btn.textContent = '⏳ Salvando...';
  btn.disabled = true;

  const payload = {
    stt: {
      silence_thresh:   parseFloat(document.getElementById('stt-silence-thresh').value),
      speech_pad_pre:   parseFloat(document.getElementById('stt-pad-pre').value),
      speech_pad_post:  parseFloat(document.getElementById('stt-pad-post').value),
      max_duration:     parseFloat(document.getElementById('stt-max-dur').value),
    },
    tts: {
      language_model: getRadio('tts-model-group'),
      voice_name:     (() => {
        const custom = document.getElementById('tts-custom-voice').value.trim();
        return custom || getRadio('tts-voice-group');
      })(),
    },
    llm: {
      api_key:           document.getElementById('llm-api-key').value.trim(),
      temperature:       parseFloat(document.getElementById('llm-temperature').value),
      top_p:             parseFloat(document.getElementById('llm-top-p').value),
      top_k:             parseInt(document.getElementById('llm-top-k').value),
      max_output_tokens: parseInt(document.getElementById('llm-max-tokens').value),
      models_list:       modelsList,
    },
    agent: {
      system_prompt: document.getElementById('agent-prompt').value,
    },
  };

  try {
    const res = await fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.ok) {
      showToast('✅ Configurações salvas com sucesso!', 'ok');
    } else {
      showToast('❌ Erro: ' + data.error, 'err');
    }
  } catch (e) {
    showToast('❌ Falha na comunicação: ' + e.message, 'err');
  } finally {
    btn.textContent = '💾 Salvar Alterações';
    btn.disabled = false;
  }
}

// ── Logs ──────────────────────────────────────────────────────────────────────
async function loadLogs() {
  const viewer = document.getElementById('log-viewer');
  try {
    const res = await fetch('/api/logs');
    const data = await res.json();
    if (!data.lines || data.lines.length === 0) {
      viewer.innerHTML = '<div class="log-empty">Nenhum log encontrado.</div>';
      return;
    }
    viewer.innerHTML = data.lines.map(line => {
      let cls = 'log-line';
      if (line.includes(' - INFO - '))    cls += ' INFO';
      if (line.includes(' - WARNING - ')) cls += ' WARNING';
      if (line.includes(' - ERROR - '))   cls += ' ERROR';
      return `<div class="${cls}">${escapeHtml(line)}</div>`;
    }).join('');
  } catch {
    viewer.innerHTML = '<div class="log-empty">Erro ao carregar logs.</div>';
  }
}

function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── UI Helpers ────────────────────────────────────────────────────────────────
function showToast(msg, type = 'ok') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast show ${type}`;
  setTimeout(() => t.classList.remove('show'), 3500);
}

function setStatus(ok) {
  const dot  = document.getElementById('status-dot');
  const text = document.getElementById('status-text');
  dot.className = 'status-dot ' + (ok ? 'ok' : 'err');
  text.textContent = ok ? 'Conectado' : 'Sem conexão';
}

function toggleApiKey() {
  const inp = document.getElementById('llm-api-key');
  inp.type = inp.type === 'password' ? 'text' : 'password';
}

// ── Init ──────────────────────────────────────────────────────────────────────
setupRadioGroup('stt-model-group');
setupRadioGroup('tts-model-group');
setupRadioGroup('tts-voice-group', val => {
  document.getElementById('tts-cache-info').innerHTML =
    `<span class="mono">audio/models/voice_${val}.safetensors</span>`;
});

loadConfig();
