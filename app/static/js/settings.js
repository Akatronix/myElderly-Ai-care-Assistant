(() => {
  const form = $('#settingsForm');
  const large = $('#largeText');
  try { large.checked = localStorage.getItem('largeText') === '1'; } catch (e) { /* ignore */ }

  large.addEventListener('change', () => {
    document.documentElement.classList.toggle('large-text', large.checked);
    try { localStorage.setItem('largeText', large.checked ? '1' : '0'); } catch (e) { /* ignore */ }
  });

  async function load() {
    try {
      const s = await api('/api/settings');
      form.elder_name.value = s.elder_name;
      form.family_phone.value = s.family_phone;
      const row = (ok, text) => `<li><span class="${ok ? 'dot-ok' : 'dot-bad'}"></span>${esc(text)}</li>`;
      $('#statusList').innerHTML =
        row(s.voice_ready, 'Speech (YarnGPT)') +
        row(s.assistant_ready, 'Assistant (Groq)') +
        row(!s.simulate_sensors, s.simulate_sensors ? 'Sensors: test data' : 'Sensors: live') +
        row(false, `${I18N.nav_alert} SMS / ${I18N.call_family}: ${I18N.coming_soon}`);
    } catch (e) { toast(e.message, true); }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await api('/api/settings', { method: 'POST', json: { elder_name: form.elder_name.value, family_phone: form.family_phone.value } });
      toast(I18N.saved);
      setTimeout(() => location.reload(), 600); // refresh the name in the header
    } catch (err) { toast(err.message, true); }
  });

  load();
})();
