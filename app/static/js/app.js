/* myElderly — shared helpers, alarm engine, status bar. Loaded on every page. */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const pad2 = (n) => String(n).padStart(2, '0');
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmt = (str, vars = {}) => String(str).replace(/\{(\w+)\}/g, (m, k) => (vars[k] ?? m));

async function api(path, opts = {}) {
  const init = { method: opts.method || 'GET', headers: {} };
  if (opts.json !== undefined) {
    init.headers['Content-Type'] = 'application/json';
    init.body = JSON.stringify(opts.json);
  }
  if (opts.body) init.body = opts.body;
  const res = await fetch(path, init);
  let data = {};
  try { data = await res.json(); } catch (e) { /* non-JSON */ }
  if (!res.ok) {
    const err = new Error(data.error || data.message || `${res.status} ${res.statusText}`);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

function toast(message, bad = false) {
  const box = $('#toasts');
  const el = document.createElement('div');
  el.className = 'toast' + (bad ? ' bad' : '');
  el.textContent = message;
  box.appendChild(el);
  setTimeout(() => el.remove(), 4500);
}

const fmtDateTime = (iso) =>
  new Date(iso).toLocaleString([], { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false });

/* ---------- shared renderers ---------- */
function renderSchedule(listEl, schedule, onChange) {
  if (!schedule.length) {
    listEl.innerHTML = `<li class="empty">${esc(I18N.no_medicine_today)}</li>`;
    return;
  }
  const label = { due: I18N.due_now, upcoming: I18N.upcoming, missed: I18N.missed };
  listEl.innerHTML = schedule.map((s) => `
    <li class="med-row ${s.status}">
      <span class="med-time">${esc(s.slot)}</span>
      <span class="med-info"><b>${esc(s.name)}</b><span>${esc(s.dose)}</span></span>
      ${s.status === 'taken'
        ? `<span class="badge taken">${esc(fmt(I18N.taken_at, { time: s.taken_at }))}</span>`
        : `<span class="badge ${s.status}">${esc(label[s.status])}</span>
           <button class="btn small primary" data-take="${s.medicine_id}" data-slot="${esc(s.slot)}" type="button">${esc(I18N.mark_taken)}</button>`}
    </li>`).join('');
  $$('[data-take]', listEl).forEach((btn) => btn.addEventListener('click', async () => {
    btn.disabled = true;
    try {
      await api('/api/medicines/take', { method: 'POST', json: { medicine_id: +btn.dataset.take, slot: btn.dataset.slot } });
      document.dispatchEvent(new Event('data-changed'));
      if (onChange) onChange();
    } catch (e) { toast(e.message, true); btn.disabled = false; }
  }));
}

function renderAlerts(listEl, alerts, onChange) {
  if (!alerts.length) {
    listEl.innerHTML = `<li class="empty">${esc(I18N.no_alerts)}</li>`;
    return;
  }
  listEl.innerHTML = alerts.map((a) => `
    <li class="alert-row ${a.acknowledged ? 'ack' : ''}">
      <span class="badge ${esc(a.level)}">!</span>
      <span class="msg">${esc(a.message)}<br><span class="when">${esc(fmtDateTime(a.ts))}</span></span>
      ${a.acknowledged ? '' : `<button class="btn small" data-ack="${a.id}" type="button">${esc(I18N.acknowledge)}</button>`}
    </li>`).join('');
  $$('[data-ack]', listEl).forEach((btn) => btn.addEventListener('click', async () => {
    await api(`/api/alerts/${btn.dataset.ack}/ack`, { method: 'POST' });
    if (onChange) onChange();
  }));
}

/* ---------- clock, internet, chrome ---------- */
function tickClock() {
  const d = new Date();
  const c = $('#clock');
  if (c) c.textContent = `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
}
setInterval(tickClock, 5000);
tickClock();

async function checkInternet() {
  let online = false;
  try { online = (await api('/api/internet')).online && navigator.onLine; } catch (e) { online = false; }
  const pill = $('#netPill');
  if (!pill) return;
  pill.dataset.online = online ? '1' : '0';
  $('#netText').textContent = online ? I18N.online : I18N.offline;
}
checkInternet();
setInterval(checkInternet, 20000);
window.addEventListener('online', checkInternet);
window.addEventListener('offline', checkInternet);

$('#collapseBtn')?.addEventListener('click', () => $('#app').classList.toggle('collapsed'));
$('#fullscreenBtn')?.addEventListener('click', () => {
  if (document.fullscreenElement) document.exitFullscreen();
  else document.documentElement.requestFullscreen?.();
});

/* ---------- phone (coming soon) & SOS ---------- */
$$('#callBtn').forEach((b) => b.addEventListener('click', async () => {
  try { await api('/api/phone/call', { method: 'POST' }); } catch (e) { /* 501 expected */ }
  toast(I18N.phone_not_impl);
}));

const sosModal = $('#sosModal');
$('#sosBtn')?.addEventListener('click', () => { sosModal.hidden = false; });
$('#sosNo')?.addEventListener('click', () => { sosModal.hidden = true; });
$('#sosYes')?.addEventListener('click', async () => {
  sosModal.hidden = true;
  try {
    await api('/api/emergency', { method: 'POST' });
    toast(I18N.emergency_sent);
    setTimeout(() => toast(I18N.phone_not_impl), 600);
    document.dispatchEvent(new Event('data-changed'));
  } catch (e) { toast(e.message, true); }
});

/* ---------- alarm sound ---------- */
const Sound = {
  ctx: null, timer: null, auto: null,
  unlock() {
    try {
      if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      if (this.ctx.state === 'suspended') this.ctx.resume();
    } catch (e) { /* no audio */ }
  },
  beep(freq = 880, dur = 0.18, when = 0) {
    if (!this.ctx) return;
    const t = this.ctx.currentTime + when;
    const o = this.ctx.createOscillator();
    const g = this.ctx.createGain();
    o.type = 'sine';
    o.frequency.value = freq;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.45, t + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g).connect(this.ctx.destination);
    o.start(t);
    o.stop(t + dur + 0.05);
  },
  start() {
    this.stop();
    const pattern = () => { this.beep(880, 0.18, 0); this.beep(880, 0.18, 0.28); this.beep(1175, 0.3, 0.56); };
    pattern();
    this.timer = setInterval(pattern, 1500);
    this.auto = setTimeout(() => this.stop(), 120000);
  },
  stop() { clearInterval(this.timer); clearTimeout(this.auto); },
  test() { this.unlock(); this.beep(880, 0.2, 0); this.beep(1175, 0.3, 0.3); },
};
['click', 'keydown', 'touchstart'].forEach((ev) => document.addEventListener(ev, () => Sound.unlock(), { once: true }));

/* ---------- alarm + medicine reminder engine (runs on every page) ---------- */
const Reminders = {
  alarms: [], meds: [], fired: new Set(), current: null,
  async refresh() {
    try {
      const [a, m] = await Promise.all([api('/api/alarms'), api('/api/medicines/today')]);
      this.alarms = a.alarms;
      this.meds = m.schedule;
    } catch (e) { /* server briefly unreachable */ }
  },
  tick() {
    if (this.current) return;
    const d = new Date();
    const hhmm = `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
    const dow = (d.getDay() + 6) % 7; // Monday = 0
    const stamp = `${d.toDateString()} ${hhmm}`;
    for (const a of this.alarms) {
      const key = `a${a.id} ${stamp}`;
      if (a.enabled && a.time === hhmm && (!a.days.length || a.days.includes(dow)) && !this.fired.has(key)) {
        this.fired.add(key);
        return this.ring({ title: a.label || I18N.alarm_ringing, text: hhmm, kind: 'alarm' });
      }
    }
    for (const s of this.meds) {
      const key = `m${s.medicine_id} ${s.slot} ${stamp}`;
      if (s.status !== 'taken' && s.slot === hhmm && !this.fired.has(key)) {
        this.fired.add(key);
        return this.ring({ title: I18N.medicine_time, text: `${s.name} ${s.dose}`.trim(), kind: 'med', med: s });
      }
    }
  },
  ring(info) {
    this.current = info;
    $('#ringTitle').textContent = info.title;
    $('#ringText').textContent = info.text;
    $('#ringDismiss').textContent = info.kind === 'med' ? I18N.mark_taken : I18N.dismiss;
    $('#ringSnooze').textContent = I18N.snooze;
    $('#ringModal').hidden = false;
    Sound.start();
  },
  close() {
    Sound.stop();
    $('#ringModal').hidden = true;
    this.current = null;
  },
};
$('#ringDismiss')?.addEventListener('click', async () => {
  const info = Reminders.current;
  Reminders.close();
  if (info && info.kind === 'med') {
    try {
      await api('/api/medicines/take', { method: 'POST', json: { medicine_id: info.med.medicine_id, slot: info.med.slot } });
      document.dispatchEvent(new Event('data-changed'));
    } catch (e) { toast(e.message, true); }
  }
});
$('#ringSnooze')?.addEventListener('click', () => {
  const info = Reminders.current;
  Reminders.close();
  if (info) setTimeout(() => Reminders.ring(info), 5 * 60 * 1000);
});
Reminders.refresh();
setInterval(() => Reminders.refresh(), 60000);
setInterval(() => Reminders.tick(), 4000);
document.addEventListener('data-changed', () => Reminders.refresh());
