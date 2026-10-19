(() => {
  const selected = new Set();
  const chips = $('#dayChips');

  I18N.days.forEach((name, i) => {
    const c = document.createElement('button');
    c.type = 'button';
    c.className = 'chip';
    c.textContent = name;
    c.addEventListener('click', () => {
      selected.has(i) ? selected.delete(i) : selected.add(i);
      c.classList.toggle('active', selected.has(i));
    });
    chips.append(c);
  });

  async function load() {
    try {
      const { alarms } = await api('/api/alarms');
      const list = $('#alarmList');
      if (!alarms.length) {
        list.innerHTML = `<li class="empty">${esc(I18N.no_alarms)}</li>`;
        return;
      }
      list.innerHTML = alarms.map((a) => `
        <li class="row-item">
          <span class="big-time">${esc(a.time)}</span>
          <span class="grow"><b>${esc(a.label || I18N.alarm_ringing)}</b>
            <span>${a.days.length ? a.days.map((d) => esc(I18N.days[d])).join(', ') : esc(I18N.every_day)}</span></span>
          <label class="switch"><input type="checkbox" data-toggle="${a.id}" ${a.enabled ? 'checked' : ''}><span></span></label>
          <button class="btn small" data-del="${a.id}" type="button" title="${esc(I18N.delete)}">🗑</button>
        </li>`).join('');
      $$('[data-toggle]', list).forEach((cb) => cb.addEventListener('change', async () => {
        await api(`/api/alarms/${cb.dataset.toggle}`, { method: 'PATCH', json: { enabled: cb.checked } });
        Reminders.refresh();
      }));
      $$('[data-del]', list).forEach((btn) => btn.addEventListener('click', async () => {
        await api(`/api/alarms/${btn.dataset.del}`, { method: 'DELETE' });
        Reminders.refresh();
        load();
      }));
    } catch (e) { toast(e.message, true); }
  }

  $('#alarmForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const f = e.target;
    try {
      await api('/api/alarms', { method: 'POST', json: { time: f.time.value, label: f.label.value, days: [...selected] } });
      f.label.value = '';
      selected.clear();
      $$('.chip', chips).forEach((c) => c.classList.remove('active'));
      toast(I18N.saved);
      Reminders.refresh();
      load();
    } catch (err) { toast(err.message, true); }
  });

  $('#testSoundBtn').addEventListener('click', () => Sound.test());
  document.addEventListener('data-changed', load);
  load();
})();
