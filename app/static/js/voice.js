/* Voice assistant page: record WAV in the browser -> /api/voice -> play the spoken reply. */
(() => {
  const orb = $('#orb');
  const statusEl = $('#voiceStatus');
  const log = $('#chatLog');
  const banner = $('#voiceBanner');
  const SAMPLE_RATE = 16000;
  const SILENCE_MS = 1800;      // auto-stop after this much silence once speech was heard
  const MAX_MS = 30000;
  const SPEECH_RMS = 0.02;
  const QUIET_RMS = 0.012;

  let state = 'idle';
  let stream, ctx, proc, src, chunks, heardSpeech, quietSince, startedAt, audioEl;

  const labels = {
    idle: I18N.tap_to_talk,
    listening: I18N.listening,
    thinking: I18N.thinking,
    speaking: I18N.speaking,
  };

  function setState(s) {
    state = s;
    orb.dataset.state = s;
    statusEl.textContent = s === 'listening' ? `${I18N.listening} · ${I18N.tap_to_stop}` : labels[s];
    if (s !== 'listening') orb.style.setProperty('--level', 0);
  }

  function addBubble(role, text, actions = [], audioUrl = null) {
    const b = document.createElement('div');
    b.className = `bubble ${role}`;
    b.textContent = text;
    if (actions.length) {
      const wrap = document.createElement('div');
      wrap.className = 'acts';
      actions.forEach((a) => {
        const map = {
          set_alarm: fmt(I18N.action_set_alarm, a),
          medicine_taken: fmt(I18N.action_medicine_taken, a),
          emergency: I18N.emergency_sent,
          call_family: I18N.phone_not_impl,
        };
        const chip = document.createElement('span');
        chip.className = 'act';
        chip.textContent = '✓ ' + (map[a.type] || a.type);
        wrap.append(chip);
      });
      b.append(wrap);
    }
    if (audioUrl) {
      const replay = document.createElement('button');
      replay.type = 'button';
      replay.className = 'btn small';
      replay.style.marginTop = '8px';
      replay.textContent = I18N.play_reply;
      replay.addEventListener('click', () => play(audioUrl));
      b.append(replay);
    }
    log.append(b);
    log.scrollTop = log.scrollHeight;
  }

  function showError(message) {
    const b = document.createElement('div');
    b.className = 'bubble error';
    b.textContent = message;
    log.append(b);
    log.scrollTop = log.scrollHeight;
  }

  /* ---------- recording (PCM -> 16 kHz mono WAV) ---------- */
  function downsample(buf, inRate, outRate) {
    if (inRate === outRate) return buf;
    const ratio = inRate / outRate;
    const out = new Float32Array(Math.floor(buf.length / ratio));
    for (let i = 0; i < out.length; i++) {
      const s = Math.floor(i * ratio), e = Math.min(Math.floor((i + 1) * ratio), buf.length);
      let sum = 0;
      for (let j = s; j < e; j++) sum += buf[j];
      out[i] = e > s ? sum / (e - s) : 0;
    }
    return out;
  }

  function encodeWav(samples, rate) {
    const view = new DataView(new ArrayBuffer(44 + samples.length * 2));
    const str = (o, s) => { for (let i = 0; i < s.length; i++) view.setUint8(o + i, s.charCodeAt(i)); };
    str(0, 'RIFF'); view.setUint32(4, 36 + samples.length * 2, true); str(8, 'WAVE'); str(12, 'fmt ');
    view.setUint32(16, 16, true); view.setUint16(20, 1, true); view.setUint16(22, 1, true);
    view.setUint32(24, rate, true); view.setUint32(28, rate * 2, true); view.setUint16(32, 2, true); view.setUint16(34, 16, true);
    str(36, 'data'); view.setUint32(40, samples.length * 2, true);
    for (let i = 0, o = 44; i < samples.length; i++, o += 2) {
      const s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(o, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    }
    return new Blob([view], { type: 'audio/wav' });
  }

  async function start() {
    banner.hidden = true;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true } });
    } catch (e) {
      banner.textContent = I18N.mic_error;
      banner.hidden = false;
      return;
    }
    Sound.unlock();
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    src = ctx.createMediaStreamSource(stream);
    proc = ctx.createScriptProcessor(4096, 1, 1);
    chunks = [];
    heardSpeech = false;
    quietSince = 0;
    startedAt = performance.now();
    proc.onaudioprocess = (e) => {
      const data = new Float32Array(e.inputBuffer.getChannelData(0));
      chunks.push(data);
      let sum = 0;
      for (let i = 0; i < data.length; i++) sum += data[i] * data[i];
      const rms = Math.sqrt(sum / data.length);
      orb.style.setProperty('--level', Math.min(rms * 8, 1).toFixed(2));
      const now = performance.now();
      if (rms > SPEECH_RMS) { heardSpeech = true; quietSince = 0; }
      else if (heardSpeech && rms < QUIET_RMS) {
        quietSince = quietSince || now;
        if (now - quietSince > SILENCE_MS) stop(true);
      }
      if (now - startedAt > MAX_MS) stop(true);
    };
    src.connect(proc);
    proc.connect(ctx.destination); // output stays silent (we never write to outputBuffer)
    setState('listening');
  }

  function teardown() {
    try { proc && (proc.onaudioprocess = null, proc.disconnect()); src && src.disconnect(); } catch (e) { /* ignore */ }
    stream && stream.getTracks().forEach((t) => t.stop());
    const rate = ctx ? ctx.sampleRate : SAMPLE_RATE;
    ctx && ctx.close();
    proc = src = stream = ctx = null;
    return rate;
  }

  function stop(send) {
    if (state !== 'listening') return;
    const rate = teardown();
    if (!send || !heardSpeech) { setState('idle'); if (send) showError(I18N.no_speech); return; }
    let total = 0;
    chunks.forEach((c) => (total += c.length));
    const all = new Float32Array(total);
    let off = 0;
    chunks.forEach((c) => { all.set(c, off); off += c.length; });
    sendAudio(encodeWav(downsample(all, rate, SAMPLE_RATE), SAMPLE_RATE));
  }

  /* ---------- talking to the server ---------- */
  async function sendAudio(blob) {
    setState('thinking');
    const form = new FormData();
    form.append('audio', blob, 'speech.wav');
    form.append('lang', APP.lang);
    try {
      handleReply(await api('/api/voice', { method: 'POST', body: form }));
    } catch (e) {
      showError(e.message || I18N.error_generic);
      setState('idle');
    }
  }

  async function sendText(text) {
    addBubble('user', text);
    setState('thinking');
    try {
      handleReply(await api('/api/chat', { method: 'POST', json: { text, lang: APP.lang } }), true);
    } catch (e) {
      showError(e.message || I18N.error_generic);
      setState('idle');
    }
  }

  function handleReply(d, userAlreadyShown = false) {
    if (d.transcript && !userAlreadyShown) addBubble('user', d.transcript);
    addBubble('bot', d.reply, d.actions || [], d.audio_url);
    if (d.actions && d.actions.length) document.dispatchEvent(new Event('data-changed'));
    if (d.tts_error) { banner.textContent = d.tts_error; banner.hidden = false; }
    if (d.audio_url) play(d.audio_url); else setState('idle');
  }

  function play(url) {
    if (audioEl) audioEl.pause();
    audioEl = new Audio(url);
    audioEl.onended = () => setState('idle');
    audioEl.onerror = () => setState('idle');
    setState('speaking');
    audioEl.play().catch(() => setState('idle')); // autoplay blocked -> use the "Play reply" button
  }

  orb.addEventListener('click', () => {
    if (state === 'idle') start();
    else if (state === 'listening') stop(true);
    else if (state === 'speaking') { audioEl && audioEl.pause(); setState('idle'); }
  });
  document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
      e.preventDefault();
      orb.click();
    }
  });
  $('#textForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const input = $('#textInput');
    const text = input.value.trim();
    if (!text || state === 'thinking') return;
    input.value = '';
    sendText(text);
  });

  setState('idle');

  // Top-bar "Search or ask..." sends its text here as ?ask=...
  const ask = new URLSearchParams(location.search).get('ask');
  if (ask && ask.trim()) {
    history.replaceState(null, '', location.pathname);
    sendText(ask.trim());
  }
})();
