(() => {
  const hrBox = $('#chartHr');
  const tempBox = $('#chartTemp');
  let hours = 24;
  let series = { hr: [], temp: [] };

  function stat(valueEl, subEl, value, state, range, unit) {
    valueEl.textContent = value ?? '–';
    subEl.textContent = `${state === 'high' || state === 'low' ? I18N[state] : I18N.normal} · ${I18N.normal_range}: ${range[0]}–${range[1]} ${unit}`;
    subEl.className = 'stat-sub ' + (state === 'high' || state === 'low' ? 'bad' : 'ok');
  }

  function draw() {
    AreaChart.draw(hrBox, series.hr, { decimals: 0, unit: 'BPM' });
    AreaChart.draw(tempBox, series.temp, { decimals: 1, unit: '°C' });
  }

  async function load() {
    try {
      const [latest, hr, temp] = await Promise.all([
        api('/api/vitals/latest'),
        api(`/api/vitals/history?metric=heart_rate&hours=${hours}`),
        api(`/api/vitals/history?metric=temperature&hours=${hours}`),
      ]);
      stat($('#hrValue'), $('#hrSub'), latest.heart_rate, latest.hr_status, APP.hrRange, 'BPM');
      stat($('#tempValue'), $('#tempSub'), latest.temperature, latest.temp_status, APP.tempRange, '°C');
      $('#simBanner').hidden = !latest.simulated;
      series = { hr: hr.points, temp: temp.points };
      draw();
    } catch (e) { toast(e.message, true); }
  }

  $$('#rangeToggle button').forEach((b) => b.addEventListener('click', () => {
    $$('#rangeToggle button').forEach((x) => x.classList.toggle('active', x === b));
    hours = +b.dataset.hours;
    load();
  }));
  new ResizeObserver(draw).observe(hrBox);
  load();
  setInterval(load, 30000);
})();
