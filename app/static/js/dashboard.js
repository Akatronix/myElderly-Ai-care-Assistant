(() => {
  const chart = $('#chart');
  let data = null;
  let metric = 'heart_rate';

  function setStat(valueEl, subEl, value, state, range, unit) {
    valueEl.textContent = value ?? '–';
    const text = `${state === 'normal' || state === 'unknown' ? I18N.normal : I18N[state]} · ${range[0]}–${range[1]} ${unit}`;
    subEl.textContent = text;
    subEl.className = 'stat-sub ' + (state === 'high' || state === 'low' ? 'bad' : 'ok');
  }

  function drawChart() {
    if (!data) return;
    const isHr = metric === 'heart_rate';
    AreaChart.draw(chart, data.history[metric], { decimals: isHr ? 0 : 1, unit: isHr ? 'BPM' : '°C' });
  }

  function render() {
    const v = data.vitals;
    setStat($('#hrValue'), $('#hrSub'), v.heart_rate, v.hr_status, APP.hrRange, 'BPM');
    setStat($('#tempValue'), $('#tempSub'), v.temperature, v.temp_status, APP.tempRange, '°C');
    $('#medValue').textContent = `${data.medicine.taken}/${data.medicine.total}`;
    const pct = data.medicine.adherence_7d;
    $('#medSub').textContent = `${I18N.medicine_level}: ${pct == null ? '–' : pct + '%'}`;
    $('#alertValue').textContent = data.alerts.count_7d;
    renderSchedule($('#medList'), data.medicine.schedule);
    renderAlerts($('#alertList'), data.alerts.recent, load);
    drawChart();
  }

  async function load() {
    try {
      data = await api('/api/dashboard');
      render();
    } catch (e) { toast(e.message, true); }
  }

  $$('#metricToggle button').forEach((b) => b.addEventListener('click', () => {
    $$('#metricToggle button').forEach((x) => x.classList.toggle('active', x === b));
    metric = b.dataset.metric;
    drawChart();
  }));
  new ResizeObserver(drawChart).observe(chart);
  document.addEventListener('data-changed', load);
  load();
  setInterval(load, 30000);
})();
