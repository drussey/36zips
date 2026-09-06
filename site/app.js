(function () {
  'use strict';
  const D = window.KILO;
  const [W, H] = D.size;
  const R = 4.6;
  const NS = 'http://www.w3.org/2000/svg';
  // touch = no hover: tap picks, the card is a bottom sheet you step through
  const TOUCH = matchMedia('(pointer: coarse)').matches;
  const NARROW = () => matchMedia('(max-width: 700px)').matches;
  const TAP_R = 18; // css px around a fingertip that counts as "on" a dot

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

  // every dot, per chart, so a tap can be matched by distance instead of by hit-testing a 4px circle
  const REG = new Map();
  function dot(parent, e, x, y, r, inset) {
    r = r || R;
    const g = el('g', { class: 'dot', 'data-id': e.id, transform: `translate(${x},${y})` }, parent);
    el('circle', { class: 'hit', r: r + 2 }, g);
    el('circle', { class: 'ring', r }, g);
    el('circle', { class: 'core', r, fill: color(e.usd_k) }, g);
    el('circle', { class: 'spec', r, fill: 'url(#spec)' }, g);
    const svg = parent.ownerSVGElement;
    if (!REG.has(svg)) REG.set(svg, []);
    REG.get(svg).push({ id: e.id, x, y, r, el: g, inset: !!inset });
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
  // `companion` rows (one line priced two eras) share their partner's map dot: chart only.
  const us = D.entries.filter(e => e.region === 'us' && e.on_map).sort((a, b) => a.usd_k - b.usd_k);
  for (const e of us) dot(dotsG, e, e.x, e.y);

  // ---------- worldwide inset: abroad + undisclosed (+ AK/HI, empty) ----------
  const GROUP_ORDER = ['UK', 'CANADA', 'IRELAND', 'FRANCE', 'UNDISCLOSED'];
  const GROUP_NAMES = { UK: 'UNITED KINGDOM', CANADA: 'CANADA', IRELAND: 'IRELAND', FRANCE: 'FRANCE', UNDISCLOSED: 'UNDISCLOSED' };
  const groups = {};
  for (const e of D.entries) if (e.region !== 'us' && e.on_map) (groups[e.group] = groups[e.group] || []).push(e);
  const gbox = el('g', { class: 'gbox' }, map);
  (function globalBox() {
    const bx = -6, bw = 310;
    const labelW = 118, rowH = 22, step = R * 2 + 3;
    const perRow = Math.floor((bw - 12 - labelW - 8) / step);

    // lay the rows out first so the box hugs its contents and can sit in the corner
    const rows = [];
    let ch = 40;
    for (const k of GROUP_ORDER) {
      const list = (groups[k] || []).sort((a, b) => a.year - b.year);
      if (!list.length) continue;
      rows.push({ k, list, dy: ch });
      ch += rowH + Math.floor((list.length - 1) / perRow) * step;
    }
    const bh = ch - rowH + 16;
    const by = H - bh + 6;

    const g = gbox;
    el('rect', { class: 'gbox-rect', x: bx, y: by, width: bw, height: bh }, g);
    el('rect', { class: 'gbox-rect-in', x: bx + 3, y: by + 3, width: bw - 6, height: bh - 6 }, g);
    el('text', { class: 'gbox-title', x: bx + 12, y: by + 20, text: 'WORLDWIDE' }, g);

    for (const r of rows) {
      const y = by + r.dy;
      el('text', { class: 'gbox-label', x: bx + 12, y: y + 3.5, text: `${GROUP_NAMES[r.k]} (${r.list.length})` }, g);
      const x = bx + 12 + labelW;
      r.list.forEach((e, i) => {
        dot(g, e, x + (i % perRow) * step, y + Math.floor(i / perRow) * step, null, true);
      });
    }
  })();
  // on a phone the inset is too small to read or tap: the same groups become chips under the map
  (function worldChips() {
    const wrap = $('#worldChips');
    for (const k of GROUP_ORDER) {
      const list = groups[k];
      if (!list || !list.length) continue;
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'wchip';
      b.innerHTML = `${esc(GROUP_NAMES[k])}<b>${list.length}</b>`;
      b.addEventListener('click', ev => {
        ev.stopPropagation();
        openChooser(byDateIds(list), GROUP_NAMES[k], tl);
      });
      wrap.appendChild(b);
    }
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

  // ---------- the card ----------
  const card = $('#card');
  const byId = {};
  for (const e of D.entries) byId[e.id] = e;
  const dotsFor = id => document.querySelectorAll(`.dot[data-id="${id}"]`);
  const byDateIds = list => list.slice().sort((a, b) => frac(a) - frac(b) || a.id - b.id).map(e => e.id);
  const ALL = byDateIds(D.entries);
  const cityIds = e => byDateIds(D.entries.filter(x => x.on_map && x.city && x.city === e.city));

  // what prev/next steps through: everything by date, one city, or whatever was under the finger
  let seq = ALL, seqTitle = '';
  let hotIds = [], pinnedId = null, chooserOpen = false, pinSvg = null;
  const isOpen = () => pinnedId !== null || chooserOpen;
  const anchorFor = id => (pinSvg && pinSvg.querySelector(`.dot[data-id="${id}"]`)) || dotsFor(id)[0];

  function navBar(e) {
    const n = seq.length, i = seq.indexOf(e.id);
    if (n < 2 || i < 0) return '';
    return `<div class="card-bar">
      <button type="button" class="nav prev" aria-label="Previous">◂</button>
      <button type="button" class="nav where" title="Show the list">${i + 1} / ${n}${seqTitle ? ` · ${esc(seqTitle)}` : ''}</button>
      <button type="button" class="nav next" aria-label="Next">▸</button>
    </div>`;
  }

  function render(e) {
    const perf = e.performer && e.performer !== e.artist ? `<span class="perf">${esc(e.performer)}</span>` : '';
    const fx = e.currency !== 'USD' ? `<span class="fx">≈ $${e.usd_k}K USD</span>` : '';
    const where = e.city ? esc(e.city) : 'UNDISCLOSED';
    const inferred = e.city_source === 'inferred';
    const placed = inferred ? `<p class="note placed">Placed by inference: ${esc(e.city_basis || '')}${e.city_url ? ` <a href="${esc(e.city_url)}" target="_blank" rel="noopener">source ▸</a>` : ''}</p>` : '';
    const annotBody = /^https?:\/\/\S+$/.test((e.annotation_text || '').trim())
      ? `<a href="${esc(e.annotation_text.trim())}" target="_blank" rel="noopener">Video ▸</a>`
      : esc(e.annotation_text);
    const annot = e.annotation_text
      ? `<p class="annot"><b>GENIUS</b> ${annotBody}</p>` : '';
    const links = [`<a href="${esc(e.genius_url)}" target="_blank" rel="noopener">LYRICS ▸</a>`];
    if (e.annotation_url) links.push(`<a href="${esc(e.annotation_url)}" target="_blank" rel="noopener">ANNOTATION ▸</a>`);
    const photo = e.image ? `<img class="card-photo" src="${esc(e.image)}" alt="${esc(e.performer || e.artist)}">` : '';
    card.classList.toggle('has-photo', !!e.image);
    card.classList.remove('is-list');
    card.innerHTML = `
      <button type="button" class="card-close" aria-label="Close">×</button>
      ${navBar(e)}
      <div class="card-body">
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
      <div class="card-links">${links.join('')}</div>
      </div>`;
    card.scrollTop = 0;
    const body = $('.card-body', card); if (body) body.scrollTop = 0;
  }

  // several dots under one finger: a list to pick from, in date order
  function renderChooser(ids, title) {
    card.classList.remove('has-photo');
    card.classList.add('is-list');
    const manyCities = new Set(ids.map(id => byId[id].city || '')).size > 1;
    const rows = ids.map(id => {
      const e = byId[id];
      const perf = e.performer && e.performer !== e.artist ? ` <span class="perf">${esc(e.performer)}</span>` : '';
      const city = manyCities && e.city ? ` · <span class="rc">${esc(e.city.replace(/,.*$/, ''))}</span>` : '';
      return `<li><button type="button" class="row" data-id="${e.id}">
        <span class="sw" style="background:${color(e.usd_k)}"></span>
        <span class="rp">${fmtK(e.price_k, e.currency)}</span>
        <span class="rw">${esc(e.artist)}${perf}</span>
        <span class="ry">${esc(e.year)}${city}</span>
        <span class="rq">${esc(e.quote)}</span>
      </button></li>`;
    }).join('');
    card.innerHTML = `
      <button type="button" class="card-close" aria-label="Close">×</button>
      <div class="card-bar"><span class="where">${ids.length} lyrics${title ? ` · ${esc(title)}` : ''}</span></div>
      <div class="card-body"><ul class="chooser">${rows}</ul></div>`;
    $('.card-body', card).scrollTop = 0;
  }

  function place(anchor) {
    if (!anchor) return;
    const r = anchor.getBoundingClientRect();
    const vw = window.innerWidth, vh = window.innerHeight;
    if (NARROW()) return; // bottom sheet via CSS
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

  function highlight(ids) {
    for (const id of hotIds) dotsFor(id).forEach(d => d.classList.remove('hot'));
    hotIds = ids;
    const svgs = document.querySelectorAll('svg');
    if (!ids.length) { svgs.forEach(s => s.classList.remove('has-hot')); return; }
    for (const id of ids) dotsFor(id).forEach(d => d.classList.add('hot'));
    svgs.forEach(s => s.classList.add('has-hot'));
  }
  function setHot(id, anchor) {
    if (id === null) { highlight([]); card.hidden = true; return; }
    highlight([id]);
    render(byId[id]);
    card.hidden = false;
    place(anchor);
  }
  function setSeq(ids, title) { seq = ids; seqTitle = title || ''; }
  function pin(id, anchor, ids, title) {
    if (ids) setSeq(ids, title);
    else if (!seq.includes(id)) setSeq(ALL, '');
    if (pinnedId !== null) dotsFor(pinnedId).forEach(d => d.classList.remove('pinned'));
    pinnedId = id; chooserOpen = false;
    setHot(id, anchor);
    dotsFor(id).forEach(d => d.classList.add('pinned'));
    card.classList.add('pinned');
    history.replaceState(null, '', '#e' + id);
  }
  function unpin() {
    if (pinnedId !== null) dotsFor(pinnedId).forEach(d => d.classList.remove('pinned'));
    pinnedId = null; chooserOpen = false;
    card.classList.remove('pinned', 'is-list');
    setHot(null);
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  }
  function openChooser(ids, title, svg) {
    if (pinnedId !== null) dotsFor(pinnedId).forEach(d => d.classList.remove('pinned'));
    pinnedId = null; chooserOpen = true;
    if (svg) pinSvg = svg;
    setSeq(ids, title);
    highlight(ids);
    renderChooser(ids, title);
    card.hidden = false;
    card.classList.add('pinned');
    place(anchorFor(ids[0]));
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  }
  function step(dir) {
    if (pinnedId === null || seq.length < 2) return;
    const i = seq.indexOf(pinnedId);
    const id = seq[(i + dir + seq.length) % seq.length];
    pin(id, anchorFor(id));
  }

  // ---------- tap picking: everything within a fingertip of the tap, matched in chart units ----------
  function pickAt(svg, cx, cy) {
    const list = REG.get(svg) || [];
    const rect = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal;
    if (!rect.width || !vb.width) return [];
    // xMidYMid meet: uniform scale, centred in the box
    const s = Math.min(rect.width / vb.width, rect.height / vb.height);
    const ox = rect.left + (rect.width - vb.width * s) / 2, oy = rect.top + (rect.height - vb.height * s) / 2;
    const px = vb.x + (cx - ox) / s, py = vb.y + (cy - oy) / s;
    const insetHidden = getComputedStyle(gbox).display === 'none';
    const hits = [];
    for (const d of list) {
      if (d.inset && insetHidden) continue;
      const dist = Math.hypot(d.x - px, d.y - py) * s;
      if (dist <= TAP_R + d.r * s) hits.push({ id: d.id, dist });
    }
    return hits;
  }
  function titleFor(ids, svg) {
    const es = ids.map(id => byId[id]);
    const count = {};
    for (const e of es) { const c = e.city || 'Undisclosed'; count[c] = (count[c] || 0) + 1; }
    const cities = Object.keys(count).sort((a, b) => count[b] - count[a]);
    if (cities.length === 1) return cities[0];
    if (svg === map) return `Around ${cities[0]}`;
    const ys = es.map(e => +e.date.slice(0, 4));
    const a = Math.min(...ys), b = Math.max(...ys);
    return a === b ? String(a) : `${a}–${b}`;
  }
  function tapOne(id, svg) {
    if (pinnedId === id) { unpin(); return; }
    pinSvg = svg;
    const e = byId[id];
    let ids = ALL, title = '';
    if (svg === map) {
      if (e.region !== 'us') { ids = byDateIds(groups[e.group] || [e]); title = GROUP_NAMES[e.group] || ''; }
      else { const c = cityIds(e); if (c.length > 1) { ids = c; title = e.city; } }
    }
    pin(id, anchorFor(id), ids, title);
  }

  if (TOUCH) {
    for (const svg of [map, tl]) {
      svg.addEventListener('click', ev => {
        const hits = pickAt(svg, ev.clientX, ev.clientY);
        if (!hits.length) return; // falls through to the document: tap away closes
        ev.stopPropagation();
        if (hits.length === 1) { tapOne(hits[0].id, svg); return; }
        const ids = byDateIds(hits.map(h => byId[h.id]));
        openChooser(ids, titleFor(ids, svg), svg);
      });
    }
    // swipe the sheet sideways to step
    let tx = 0, ty = 0, tOn = false;
    card.addEventListener('touchstart', ev => { const t = ev.touches[0]; tx = t.clientX; ty = t.clientY; tOn = true; }, { passive: true });
    card.addEventListener('touchend', ev => {
      if (!tOn) return; tOn = false;
      const t = ev.changedTouches[0]; const dx = t.clientX - tx, dy = t.clientY - ty;
      if (Math.abs(dx) > 48 && Math.abs(dx) > Math.abs(dy) * 1.5) step(dx < 0 ? 1 : -1);
    }, { passive: true });
  } else {
    document.querySelectorAll('svg .dots, svg .gbox').forEach(container => {
      container.addEventListener('mouseover', ev => {
        const d = ev.target.closest('.dot'); if (!d || isOpen()) return;
        setHot(+d.dataset.id, d);
      });
      container.addEventListener('mouseout', ev => {
        const d = ev.target.closest('.dot'); if (!d || isOpen()) return;
        if (ev.relatedTarget && d.contains(ev.relatedTarget)) return;
        setHot(null);
      });
      container.addEventListener('click', ev => {
        const d = ev.target.closest('.dot'); if (!d) return;
        ev.stopPropagation();
        const id = +d.dataset.id;
        pinSvg = d.ownerSVGElement;
        if (pinnedId === id) unpin(); else pin(id, d, ALL, '');
      });
    });
  }

  card.addEventListener('click', ev => {
    ev.stopPropagation();
    const b = ev.target.closest('button'); if (!b) return;
    if (b.classList.contains('card-close')) unpin();
    else if (b.classList.contains('prev')) step(-1);
    else if (b.classList.contains('next')) step(1);
    else if (b.classList.contains('where')) openChooser(seq, seqTitle);
    else if (b.classList.contains('row')) { const id = +b.dataset.id; pin(id, anchorFor(id)); }
  });
  document.addEventListener('click', () => { if (isOpen()) unpin(); });
  document.addEventListener('keydown', ev => {
    if (ev.key === 'Escape' && isOpen()) unpin();
    else if (ev.key === 'ArrowRight' && pinnedId !== null) { ev.preventDefault(); step(1); }
    else if (ev.key === 'ArrowLeft' && pinnedId !== null) { ev.preventDefault(); step(-1); }
  });
  window.addEventListener('resize', () => { if (pinnedId !== null) place(anchorFor(pinnedId)); });

  const hint = TOUCH ? 'Tap a dot. Tap a cluster to pick from it.' : 'Hover a dot. Click to pin it.';
  document.querySelectorAll('.tap-hint').forEach(p => { p.textContent = hint; });

  // deep link: #e42
  const m = location.hash.match(/^#e(\d+)$/);
  if (m && byId[+m[1]]) {
    const id = +m[1];
    // phones lead with the timeline, so land on that dot; otherwise the map dot, or the timeline for chart-only rows
    const d = (NARROW() ? tl : map).querySelector(`.dot[data-id="${id}"]`) || dotsFor(id)[0];
    if (d) {
      if (NARROW()) {
        // the sheet takes the bottom of the screen, so park the dot in the top third
        const r = d.getBoundingClientRect();
        window.scrollTo({ top: window.scrollY + r.top - window.innerHeight * 0.3, behavior: 'instant' });
      } else d.scrollIntoView({ block: 'center', behavior: 'instant' });
      pinSvg = d.ownerSVGElement;
      pin(id, d, ALL, '');
    }
  }
})();
