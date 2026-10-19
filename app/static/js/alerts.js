(() => {
  async function load() {
    try {
      const d = await api('/api/alerts');
      $('#alertCount').textContent = d.count_7d;
      renderAlerts($('#alertList'), d.alerts, load);
    } catch (e) { toast(e.message, true); }
  }
  $('#testAlertBtn').addEventListener('click', async () => {
    await api('/api/alerts/test', { method: 'POST' });
    load();
  });
  document.addEventListener('data-changed', load);
  load();
})();
