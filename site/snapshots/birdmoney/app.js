(function () {
  'use strict';
  const D = window.KILO;
  const [W, H] = D.size;
  const R = 4.6;
  const NS = 'http://www.w3.org/2000/svg';

  // ---------- helpers ----------
  const $ = (s, p) => (p || document).querySelector(s);
  function el(tag, attrs, parent) {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) {
      if (k === 'text') n.textContent = attrs[k];
      else n.setAttribute(k, attrs[k]);
    }
    if (parent) parent.appendChild(n);
    return n;
  }
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const fmtK = (k, cur) => {
    const sym = cur === 'GBP' ? '£' : cur === 'CAD' ? 'CA$' : '$';
    const n = Math.round(k * 1000);
    return sym + n.toLocaleString('en-US');
  };

  // ---------- colour scale: money green -> gold -> hot -> blood, by USD-equivalent ----------
  const LO = 10, HI = 45;
  const STOPS = [
    [0.00, [38, 196, 96]],   // green
    [0.35, [214, 175, 55]],  // gold
    [0.65, [255, 122, 0]],   // orange
    [1.00, [232, 16, 42]],   // red
  ];
  function color(usdK) {
    let t = (usdK - LO) / (HI - LO);
    t = Math.max(0, Math.min(1, t));
    for (let i = 1; i < STOPS.length; i++) {
      if (t <= STOPS[i][0]) {
        const [t0, a] = STOPS[i - 1], [t1, b] = STOPS[i];
        const u = (t - t0) / (t1 - t0);
        const c = a.map((v, j) => Math.round(v + (b[j] - v) * u));
        return `rgb(${c[0]},${c[1]},${c[2]})`;
      }
    }
    return 'rgb(232,16,42)';
  }
  // legend
  (function legend() {
    const stops = [];
    for (let i = 0; i <= 10; i++) stops.push(color(LO + (HI - LO) * i / 10));
    $('.legend-bar').style.background = `linear-gradient(90deg, ${stops.join(',')})`;
    $('.legend').firstElementChild.textContent = `$${LO}K`;
    $('.legend').lastElementChild.textContent = `$${HI}K+`;
  })();

  // ---------- shared defs ----------
  function defs(svg) {
    const d = el('defs', {}, svg);
    // felt grain, same recipe as the panel backgrounds, clipped to whatever it is applied to
    const grain = el('filter', { id: 'grain', x: '0', y: '0', width: '1', height: '1' }, d);
    el('feTurbulence', { type: 'fractalNoise', baseFrequency: '0.012 0.02', numOctaves: '3', seed: '7', result: 'n' }, grain);
    el('feColorMatrix', { in: 'n', type: 'matrix', values: '0 0 0 0 .55  0 0 0 0 .8  0 0 0 0 .6  0 0 0 .8 0', result: 'cn' }, grain);
    el('feBlend', { in: 'cn', in2: 'SourceGraphic', mode: 'soft-light', result: 'b' }, grain);
    el('feComposite', { in: 'b', in2: 'SourceGraphic', operator: 'in' }, grain);
    const spec = el('radialGradient', { id: 'spec', cx: '35%', cy: '30%', r: '60%' }, d);
    el('stop', { offset: '0', 'stop-color': '#fff', 'stop-opacity': '.85' }, spec);
    el('stop', { offset: '.45', 'stop-color': '#fff', 'stop-opacity': '.12' }, spec);
    el('stop', { offset: '1', 'stop-color': '#000', 'stop-opacity': '.35' }, spec);
    const chrome = el('linearGradient', { id: 'chromeLine', x1: 0, y1: 0, x2: 0, y2: 1 }, d);
    el('stop', { offset: '0', 'stop-color': '#fff' }, chrome);
    el('stop', { offset: '.45', 'stop-color': '#c4cacf' }, chrome);
    el('stop', { offset: '.5', 'stop-color': '#4a5257' }, chrome);
    el('stop', { offset: '.55', 'stop-color': '#e9ecee' }, chrome);
    el('stop', { offset: '1', 'stop-color': '#6a7277' }, chrome);
    const glow = el('filter', { id: 'glow', x: '-100%', y: '-100%', width: '300%', height: '300%' }, d);
    el('feGaussianBlur', { stdDeviation: '1.6', result: 'b' }, glow);
    const m = el('feMerge', {}, glow);
    el('feMergeNode', { in: 'b' }, m); el('feMergeNode', { in: 'SourceGraphic' }, m);
    const lift = el('filter', { id: 'lift', x: '-10%', y: '-10%', width: '130%', height: '130%' }, d);
    el('feDropShadow', { dx: '4', dy: '6', stdDeviation: '3', 'flood-color': '#000', 'flood-opacity': '.85' }, lift);
    return d;
  }

  function dot(parent, e, x, y, r) {
    r = r || R;
    const g = el('g', { class: 'dot', 'data-id': e.id, transform: `translate(${x},${y})` }, parent);
    el('circle', { class: 'hit', r: r + 2 }, g);
    el('circle', { class: 'ring', r }, g);
    el('circle', { class: 'core', r, fill: color(e.usd_k) }, g);
    el('circle', { class: 'spec', r, fill: 'url(#spec)' }, g);
    return g;
  }

  // ---------- the map ----------
  const map = $('#map');
  map.setAttribute('viewBox', `0 0 ${W} ${H}`);
  defs(map);
  const liftG = el('g', { filter: 'url(#lift)' }, map);
  const landG = el('g', { filter: 'url(#grain)' }, liftG);
  for (const s of D.states) el('path', { class: 'state', d: s.d }, landG);
  el('path', { class: 'borders', d: D.borders }, map);
  el('path', { class: 'outline', d: D.outline }, map);
  el('path', { class: 'outline-hi', d: D.outline }, map);

  const dotsG = el('g', { class: 'dots' }, map);
  const us = D.entries.filter(e => e.region === 'us').sort((a, b) => a.usd_k - b.usd_k);
  for (const e of us) dot(dotsG, e, e.x, e.y);

  // ---------- worldwide inset: abroad + undisclosed (+ AK/HI, empty) ----------
  (function globalBox() {
    const bx = 14, by = 452, bw = 310, bh = 150;
    const g = el('g', { class: 'gbox' }, map);
    el('rect', { class: 'gbox-rect', x: bx, y: by, width: bw, height: bh }, g);
    el('rect', { class: 'gbox-rect-in', x: bx + 3, y: by + 3, width: bw - 6, height: bh - 6 }, g);
    el('text', { class: 'gbox-title', x: bx + 12, y: by + 20, text: 'WORLDWIDE' }, g);

    const order = ['UK', 'CANADA', 'IRELAND', 'FRANCE', 'UNDISCLOSED'];
    const names = { UK: 'UNITED KINGDOM', CANADA: 'CANADA', IRELAND: 'IRELAND', FRANCE: 'FRANCE', UNDISCLOSED: 'UNDISCLOSED' };
    const groups = {};
    for (const e of D.entries) if (e.region !== 'us') (groups[e.group] = groups[e.group] || []).push(e);
    let y = by + 40;
    const labelW = 118, rowH = 22;
    for (const k of order) {
      const list = (groups[k] || []).sort((a, b) => a.year - b.year);
      if (!list.length) continue;
      el('text', { class: 'gbox-label', x: bx + 12, y: y + 3.5, text: `${names[k]} (${list.length})` }, g);
      let x = bx + 12 + labelW, row = 0;
      const perRow = Math.floor((bw - 12 - labelW - 8) / (R * 2 + 3));
      list.forEach((e, i) => {
        const col = i % perRow; row = Math.floor(i / perRow);
        dot(g, e, x + col * (R * 2 + 3), y + row * (R * 2 + 3));
      });
      y += rowH + row * (R * 2 + 3);
    }
    el('text', { class: 'gbox-note', x: bx + 12, y: by + bh - 9, text: 'ALASKA · HAWAII — no bars on record' }, g);
  })();

  // ---------- the years: x = release date, y = dollars per kilo ----------
  const TW = 480, TH = 560, ML = 46, MR = 14, MT = 16, MB = 30;
  const tl = $('#timeline');
  tl.setAttribute('viewBox', `0 0 ${TW} ${TH}`);
  defs(tl);
  function frac(e) {
    const y = +e.date.slice(0, 4);
    const m = e.date.length >= 7 ? +e.date.slice(5, 7) : null;
    const d = e.date.length >= 10 ? +e.date.slice(8, 10) : null;
    if (m == null) return y + 0.5;
    const dim = new Date(y, m, 0).getDate();
    return y + (m - 1 + ((d == null ? dim / 2 : d - 0.5) / dim)) / 12;
  }
  const years = D.entries.map(e => +e.date.slice(0, 4));
  const Y0 = Math.min(...years), Y1 = Math.max(...years) + 1;
  const PMAX = 50;
  const xOf = y => ML + (y - Y0) / (Y1 - Y0) * (TW - ML - MR);
  const yOf = k => MT + (1 - Math.min(k, PMAX) / PMAX) * (TH - MT - MB);

  for (let k = 0; k <= PMAX; k += 10) {
    el('line', { class: 'grid', x1: ML, x2: TW - MR, y1: yOf(k), y2: yOf(k) }, tl);
    el('text', { class: 'yr ylab', x: ML - 8, y: yOf(k) + 4, text: k === PMAX ? `$${k}K+` : `$${k}K` }, tl);
  }
  el('line', { class: 'axis-shadow', x1: ML, x2: TW - MR, y1: yOf(0) + 2, y2: yOf(0) + 2 }, tl);
  el('line', { class: 'axis', x1: ML, x2: TW - MR, y1: yOf(0), y2: yOf(0) }, tl);
  for (let y = Y0; y <= Y1; y++) {
    const x = xOf(y);
    const major = y % 4 === 0;
    el('line', { class: 'tick', x1: x, x2: x, y1: yOf(0) + 3, y2: yOf(0) + (major ? 9 : 5) }, tl);
    if (major && y < Y1) el('text', { class: 'yr', x: xOf(y + 0.5), y: yOf(0) + 22, text: `'${String(y).slice(2)}` }, tl);
  }
  // ---------- background: UNODC's US wholesale average, behind the bars ----------
  (function unodcLine() {
    const U = D.unodc;
    if (!U || !U.points || U.points.length < 2) return;
    const pts = U.points.filter(p => p.year >= Y0 && p.year < Y1);
    if (pts.length < 2) return;
    const g = el('g', { class: 'unodc' }, tl);
    // annual figure, so it sits mid-year like any year-only bar
    const d = pts.map((p, i) => `${i ? 'L' : 'M'}${xOf(p.year + 0.5).toFixed(1)},${yOf(p.k).toFixed(1)}`).join('');
    el('path', { class: 'unodc-shadow', d }, g);
    el('path', { class: 'unodc-line', d }, g);
    const last = pts[pts.length - 1];
    el('circle', { class: 'unodc-cap', cx: xOf(last.year + 0.5), cy: yOf(last.k), r: 2.6 }, g);

    // key, parked in the empty corner above the line's 1990s descent
    const kx = 58, ky = 38;
    el('line', { class: 'unodc-swatch', x1: kx, x2: kx + 17, y1: ky - 3.5, y2: ky - 3.5 }, g);
    el('text', { class: 'unodc-key', x: kx + 23, y: ky, text: 'UNODC — U.S. WHOLESALE' }, g);
    const span = U.points[0].year + '–' + U.points[U.points.length - 1].year;
    el('text', { class: 'unodc-key sub', x: kx + 23, y: ky + 11, text: `AVERAGE $ PER KILO, ${span}` }, g);
  })();

  const tDots = el('g', { class: 'dots' }, tl);
  const sortedT = D.entries.slice().sort((a, b) => a.usd_k - b.usd_k);
  for (const e of sortedT) {
    const j = ((e.id * 7919) % 13 - 6) * 0.3; // small fixed jitter so same-day, same-price bars don't stack exactly
    dot(tDots, e, xOf(frac(e)) + j, yOf(e.usd_k), 3.6);
  }
  // ---------- header / footer counts ----------
  const nUS = us.length, nAbroad = D.entries.filter(e => e.region === 'global').length, nUnk = D.entries.length - nUS - nAbroad;
  $("#dek").textContent = `${D.entries.length} lyrics, ${Y0}–${Y1 - 1}.`;

  // ---------- the card ----------
  const card = $('#card');
  const byId = {};
  for (const e of D.entries) byId[e.id] = e;
  const dotsFor = id => document.querySelectorAll(`.dot[data-id="${id}"]`);
  const KIND = { sell: 'ASKING PRICE', buy: 'PAID', quoted: 'MARKET RATE', profit: 'PROFIT, NOT PRICE' };

  function render(e) {
    const perf = e.performer && e.performer !== e.artist ? `<span class="perf">${esc(e.performer)}</span>` : '';
    const fx = e.currency !== 'USD' ? `<span class="fx">≈ $${e.usd_k}K USD</span>` : '';
    const where = e.city ? esc(e.city) : 'UNDISCLOSED';
    const inferred = e.city_source === 'inferred';
    const placed = inferred ? `<p class="note placed">Placed by inference: ${esc(e.city_basis || '')}${e.city_url ? ` <a href="${esc(e.city_url)}" target="_blank" rel="noopener">source ▸</a>` : ''}</p>` : '';
    const annot = e.annotation_text
      ? `<p class="annot"><b>GENIUS</b> ${esc(e.annotation_text)}</p>` : '';
    const links = [`<a href="${esc(e.genius_url)}" target="_blank" rel="noopener">LYRICS ▸</a>`];
    if (e.annotation_url) links.push(`<a href="${esc(e.annotation_url)}" target="_blank" rel="noopener">ANNOTATION ▸</a>`);
    const photo = e.image ? `<img class="card-photo" src="${esc(e.image)}" alt="${esc(e.performer || e.artist)}">` : '';
    card.classList.toggle('has-photo', !!e.image);
    card.innerHTML = `
      <button class="card-close" aria-label="Close">×</button>
      ${photo}
      <div class="card-top">
        <div class="price">${fmtK(e.price_k, e.currency)}<small> / KILO</small>${e.sus ? '<span class="cap" title="cap">🧢</span>' : ''}</div>
        <div class="year-badge">${esc(e.date_display || e.year)}</div>
      </div>
      <div class="who">${esc(e.artist)}${perf}</div>
      <div class="song">“${esc(e.song)}”${e.album ? ` · ${esc(e.album)}` : ''}</div>
      <blockquote class="quote">${esc(e.quote)}</blockquote>
      <div class="meta"><span class="chip${inferred ? ' inferred' : ''}">${where}${inferred ? ' ?' : ''}</span>${fx}</div>
      ${annot}${placed}
      <div class="card-links">${links.join('')}</div>`;
    $('.card-close', card).addEventListener('click', ev => { ev.stopPropagation(); unpin(); });
  }

  function place(anchor) {
    const r = anchor.getBoundingClientRect();
    const vw = window.innerWidth, vh = window.innerHeight;
    if (vw <= 700) return; // bottom sheet via CSS
    // the page may be zoomed (body { zoom }): rects come back in viewport px, but left/top get multiplied by the zoom
    card.style.left = '0px'; card.style.top = '0px';
    const cr = card.getBoundingClientRect();
    const z = parseFloat(getComputedStyle(document.body).zoom) || 1;
    const cw = cr.width, ch = cr.height;
    let x = r.right + 14, y = r.top - 12;
    if (x + cw > vw - 12) x = r.left - cw - 14;
    if (x < 12) x = Math.max(12, Math.min(vw - cw - 12, r.left - cw / 2));
    if (y + ch > vh - 12) y = vh - ch - 12;
    if (y < 12) y = 12;
    card.style.left = (x / z) + 'px';
    card.style.top = (y / z) + 'px';
  }

  let hotId = null, pinnedId = null;
  function setHot(id, anchor) {
    if (hotId !== null) dotsFor(hotId).forEach(d => d.classList.remove('hot'));
    hotId = id;
    if (id === null) { document.querySelectorAll('svg.has-hot').forEach(s => s.classList.remove('has-hot')); card.hidden = true; return; }
    dotsFor(id).forEach(d => d.classList.add('hot'));
    document.querySelectorAll('svg').forEach(s => s.classList.add('has-hot'));
    render(byId[id]);
    card.hidden = false;
    place(anchor);
  }
  function pin(id, anchor) {
    if (pinnedId !== null) dotsFor(pinnedId).forEach(d => d.classList.remove('pinned'));
    pinnedId = id;
    setHot(id, anchor);
    dotsFor(id).forEach(d => d.classList.add('pinned'));
    card.classList.add('pinned');
    history.replaceState(null, '', '#e' + id);
  }
  function unpin() {
    if (pinnedId !== null) dotsFor(pinnedId).forEach(d => d.classList.remove('pinned'));
    pinnedId = null;
    card.classList.remove('pinned');
    setHot(null);
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  }

  document.querySelectorAll('svg .dots, svg .gbox').forEach(container => {
    container.addEventListener('mouseover', ev => {
      const d = ev.target.closest('.dot'); if (!d || pinnedId !== null) return;
      setHot(+d.dataset.id, d);
    });
    container.addEventListener('mouseout', ev => {
      const d = ev.target.closest('.dot'); if (!d || pinnedId !== null) return;
      if (ev.relatedTarget && d.contains(ev.relatedTarget)) return;
      setHot(null);
    });
    container.addEventListener('click', ev => {
      const d = ev.target.closest('.dot'); if (!d) return;
      ev.stopPropagation();
      const id = +d.dataset.id;
      if (pinnedId === id) unpin(); else pin(id, d);
    });
  });
  card.addEventListener('click', ev => ev.stopPropagation());
  document.addEventListener('click', () => { if (pinnedId !== null) unpin(); });
  document.addEventListener('keydown', ev => { if (ev.key === 'Escape' && pinnedId !== null) unpin(); });
  window.addEventListener('resize', () => { if (pinnedId !== null) { const d = dotsFor(pinnedId)[0]; if (d) place(d); } });

  if (matchMedia('(pointer: coarse)').matches) $('.panel-foot').textContent = 'Tap a dot. Swipe the map sideways.';

  // deep link: #e42
  const m = location.hash.match(/^#e(\d+)$/);
  if (m && byId[+m[1]]) {
    const d = dotsFor(+m[1])[0];
    if (d) { d.scrollIntoView({ block: 'center', behavior: 'instant' }); pin(+m[1], d); }
  }
})();
