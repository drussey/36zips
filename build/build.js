// Build-time step: project US states + city coordinates once, emit site/data.js (no runtime deps).
const fs = require('fs');
const path = require('path');
const { geoAlbers, geoPath } = require('d3-geo');
const { feature, mesh } = require('topojson-client');

const ROOT = path.resolve(__dirname, '..');
const W = 975, H = 610;

const topo = JSON.parse(fs.readFileSync(path.join(__dirname, 'states-10m.json')));
const site = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/site_data.json')));
const geocode = JSON.parse(fs.readFileSync(path.join(__dirname, 'geocode.json')));
const unodcRaw = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/unodc_us_wholesale.json')));

// Lower 48 only; AK(02) HI(15) PR(72) and territories go to the "global box".
const SKIP = new Set(['02', '15', '72', '60', '66', '69', '78']);
const states = feature(topo, topo.objects.states);
states.features = states.features.filter(f => !SKIP.has(f.id));

const proj = geoAlbers().fitExtent([[10, 10], [W - 10, H - 10]], states);
const pathGen = geoPath(proj);

const statePaths = states.features.map(f => ({ id: f.id, name: f.properties.name, d: pathGen(f) }));
const borders = pathGen(mesh(topo, topo.objects.states, (a, b) => a !== b && !SKIP.has(a.id) && !SKIP.has(b.id)));
const outline = pathGen(mesh(topo, topo.objects.states, (a, b) => a === b && !SKIP.has(a.id)));

// Rough FX so the colour scale is comparable across currencies (Sept 2026 ballpark).
const FX = { USD: 1, GBP: 1.3, CAD: 0.73 };

const entries = [];
const missing = new Set();
for (const r of site.entries) {
  const key = r.home_city;
  const g = key ? geocode[key] : null;
  if (key && !g) missing.add(key);
  let region = 'unknown', group = 'UNDISCLOSED', x = null, y = null, lat = null, lon = null;
  if (g) {
    [lat, lon] = g;
    // Canada sits inside the Albers frame, so it goes on the map itself; everywhere else abroad goes to the inset.
    if (g[2] && g[2] !== 'CANADA') { region = 'global'; group = g[2]; }
    else { region = 'us'; group = g[2] || 'US'; [x, y] = proj([lon, lat]); }
  }
  entries.push({
    id: r.id, on_map: !(r.flags || []).includes('companion'), sus: ['outlier', 'hyperbole', 'profit_not_price'].some(f => (r.flags || []).includes(f)), image: r.image || null, song_art: r.song_art || null, year: r.year, date: r.date, date_precision: r.date_precision, date_source: r.date_source, date_display: r.date_display, date_note: r.date_note, album: r.album, artist: r.artist, performer: r.performer, song: r.song, quote: r.quote,
    price_k: r.price_k, usd_k: Math.round(r.price_k * (FX[r.currency] || 1) * 10) / 10,
    currency: r.currency, kind: r.kind, confidence: r.confidence, flags: r.flags, note: r.note,
    city: key ? key.replace(/ \(title\)$/, '') : null, city_source: r.home_city_source, city_basis: r.inferred_basis, city_url: r.inferred_url, city_confidence: r.inferred_confidence, lyric_location: r.lyric_location, region, group, lat, lon, x, y,
    genius_url: r.genius_url, annotation_url: r.annotation_url,
    annotation_text: r.annotation_text, annotation_votes: r.annotation_votes,
  });
}
if (missing.size) { console.error('UNGEOCODED:', [...missing]); process.exit(1); }

// Spread co-located US dots in a sunflower spiral so a 39-deep Atlanta reads as a cluster, not one dot.
const byXY = new Map();
for (const e of entries.filter(e => e.region === 'us' && e.on_map)) {
  const k = `${e.x.toFixed(1)},${e.y.toFixed(1)}`;
  if (!byXY.has(k)) byXY.set(k, []);
  byXY.get(k).push(e);
}
const GOLDEN = Math.PI * (3 - Math.sqrt(5));
for (const group of byXY.values()) {
  group.sort((a, b) => a.year - b.year);
  const cx = group[0].x, cy = group[0].y;
  const step = 5.2;
  group.forEach((e, i) => {
    if (group.length === 1) return;
    const r = step * Math.sqrt(i + 0.6);
    const t = i * GOLDEN;
    e.x = +(cx + r * Math.cos(t)).toFixed(2);
    e.y = +(cy + r * Math.sin(t)).toFixed(2);
  });
  group.forEach(e => { e.x = +e.x.toFixed(2); e.y = +e.y.toFixed(2); });
}

// UNODC's US wholesale average, thousands of dollars per kilo, plotted mid-year like any year-only entry.
const unodc = {
  label: unodcRaw.title,
  source: unodcRaw.source,
  source_url: unodcRaw.annex_url,
  points: Object.entries(unodcRaw.prices_usd_per_kg)
    .map(([y, v]) => ({ year: +y, k: +(v / 1000).toFixed(2) }))
    .sort((a, b) => a.year - b.year),
};

const out = {
  size: [W, H],
  states: statePaths, borders, outline,
  entries,
  unodc,
  yearly: site.yearly,
  meta: { ...site.meta, fx: FX, built: new Date().toISOString().slice(0, 10) },
};
fs.mkdirSync(path.join(ROOT, 'site'), { recursive: true });
fs.writeFileSync(path.join(ROOT, 'site/data.js'), 'window.KILO = ' + JSON.stringify(out) + ';\n');
const c = entries.reduce((a, e) => (a[e.region] = (a[e.region] || 0) + 1, a), {});
console.log('entries', entries.length, c, 'unodc', unodc.points.length, 'states', statePaths.length, '->', 'site/data.js', (fs.statSync(path.join(ROOT, 'site/data.js')).size / 1024).toFixed(0) + 'KB');
