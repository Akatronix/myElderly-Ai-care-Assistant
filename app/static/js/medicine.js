(() => {
  async function load() {
    try {
      const [today, all] = await Promise.all([api('/api/medicines/today'), api('/api/medicines')]);
      const pct = today.adherence_7d;
      $('#adherenceText').textContent = `${I18N.medicine_level}: ${pct == null ? '–' : pct + '%'}  ·  ${today.taken}/${today.total}`;
      renderSchedule($('#medList'), today.schedule, load);
      renderAll(all.medicines);
    } catch (e) { toast(e.message, true); }
  }

  function renderAll(meds) {
    const list = $('#allMeds');
    if (!meds.length) {
      list.innerHTML = `<li class="empty">${esc(I18N.no_medicines)}</li>`;
      return;
    }
    list.innerHTML = meds.map((m) => `
      <li class="row-item">
        <span class="grow"><b>${esc(m.name)}</b><span>${esc([m.dose, m.times.join(', '), m.notes].filter(Boolean).join(' · '))}</span></span>
        <button class="btn small" data-del="${m.id}" type="button" title="${esc(I18N.delete)}">${'🗑'}</button>
      </li>`).join('');
    $$('[data-del]', list).forEach((btn) => btn.addEventListener('click', async () => {
      if (!confirm(`${I18N.delete}?`)) return;
      await api(`/api/medicines/${btn.dataset.del}`, { method: 'DELETE' });
      document.dispatchEvent(new Event('data-changed'));
      load();
    }));
  }

  $('#medForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const f = e.target;
    try {
      await api('/api/medicines', {
        method: 'POST',
        json: { name: f.name.value, dose: f.dose.value, times: f.times.value, notes: f.notes.value },
      });
      f.reset();
      toast(I18N.saved);
      document.dispatchEvent(new Event('data-changed'));
      load();
    } catch (err) { toast(err.message, true); }
  });

  load();
})();
