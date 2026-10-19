/* Dependency-free responsive area chart (works offline). */
const AreaChart = (() => {
  const NS = 'http://www.w3.org/2000/svg';
  let uid = 0;
  const el = (tag, attrs = {}) => {
    const e = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
    return e;
  };

  function label(d, spanHours) {
    const hh = `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
    return spanHours > 36 ? `${I18N.days[(d.getDay() + 6) % 7]} ${pad2(d.getHours())}h` : hh;
  }

  function draw(host, pts, opts = {}) {
    host.innerHTML = '';
    if (!pts.length) {
      host.innerHTML = '<div class="chart-empty">–</div>';
      return;
    }
    const decimals = opts.decimals ?? 0;
    const W = host.clientWidth || 640;
    const H = host.clientHeight || 300;
    const m = { l: 46, r: 14, t: 14, b: 30 };
    const data = pts.map((p) => ({ t: new Date(p.ts), v: p.v }));
    const vals = data.map((d) => d.v);
    const vmin = Math.min(...vals), vmax = Math.max(...vals);
    const pad = Math.max((vmax - vmin) * 0.15, decimals ? 0.2 : 3);
    let lo = vmin - pad, hi = vmax + pad;
    const q = decimals ? 10 : 1;
    lo = Math.floor(lo * q) / q;
    hi = Math.ceil(hi * q) / q;
    if (hi <= lo) hi = lo + 1;

    const t0 = data[0].t.getTime(), t1 = data[data.length - 1].t.getTime();
    const spanHours = (t1 - t0) / 3.6e6;
    const x = (t) => m.l + ((t - t0) / (t1 - t0 || 1)) * (W - m.l - m.r);
    const y = (v) => m.t + (1 - (v - lo) / (hi - lo)) * (H - m.t - m.b);

    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img' });
    const gid = `grad${++uid}`;
    const defs = el('defs');
    const grad = el('linearGradient', { id: gid, x1: 0, y1: 0, x2: 0, y2: 1 });
    grad.append(el('stop', { offset: '0%', 'stop-color': '#16a34a', 'stop-opacity': '.20' }), el('stop', { offset: '100%', 'stop-color': '#16a34a', 'stop-opacity': '0' }));
    defs.append(grad);
    svg.append(defs);

    for (let i = 0; i < 4; i++) {
      const v = lo + ((hi - lo) * i) / 3;
      const yy = y(v);
      svg.append(el('line', { class: 'grid-line', x1: m.l, x2: W - m.r, y1: yy, y2: yy }));
      const tx = el('text', { class: 'axis-text', x: m.l - 8, y: yy + 4, 'text-anchor': 'end' });
      tx.textContent = v.toFixed(decimals);
      svg.append(tx);
    }
    const n = Math.max(3, Math.min(11, Math.floor(W / 90)));
    for (let i = 0; i < n; i++) {
      const t = t0 + ((t1 - t0) * i) / (n - 1);
      const tx = el('text', { class: 'axis-text', x: x(t), y: H - 8, 'text-anchor': i === 0 ? 'start' : i === n - 1 ? 'end' : 'middle' });
      tx.textContent = label(new Date(t), spanHours);
      svg.append(tx);
    }

    const line = data.map((d, i) => `${i ? 'L' : 'M'}${x(d.t).toFixed(1)},${y(d.v).toFixed(1)}`).join('');
    const base = H - m.b;
    svg.append(el('path', { d: `${line}L${x(data[data.length - 1].t).toFixed(1)},${base}L${x(data[0].t).toFixed(1)},${base}Z`, fill: `url(#${gid})` }));
    svg.append(el('path', { class: 'line', d: line }));

    const dot = el('circle', { class: 'dot', r: 5, cx: -10, cy: -10 });
    svg.append(dot);
    host.append(svg);

    const tip = document.createElement('div');
    tip.className = 'chart-tip';
    tip.hidden = true;
    host.append(tip);
    svg.addEventListener('mousemove', (e) => {
      const rect = svg.getBoundingClientRect();
      const px = ((e.clientX - rect.left) / rect.width) * W;
      let best = data[0];
      for (const d of data) if (Math.abs(x(d.t) - px) < Math.abs(x(best.t) - px)) best = d;
      dot.setAttribute('cx', x(best.t));
      dot.setAttribute('cy', y(best.v));
      tip.hidden = false;
      tip.style.left = `${(x(best.t) / W) * rect.width}px`;
      tip.style.top = `${(y(best.v) / H) * rect.height}px`;
      tip.textContent = `${best.v.toFixed(decimals)} ${opts.unit || ''} · ${label(best.t, 0)}`;
    });
    svg.addEventListener('mouseleave', () => {
      tip.hidden = true;
      dot.setAttribute('cx', -10);
    });
  }

  return { draw };
})();
