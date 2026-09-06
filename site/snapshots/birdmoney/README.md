# Rap Kilo Index

The price of a kilo of cocaine over the years, sourced only from rap lyrics.

## Data

| File | What |
|---|---|
| `data/kilo_prices.json` / `.csv` | Hand-curated entries: one lyric = one row |
| `data/site_data.json` | Same entries plus per-year aggregates, ready for the front end |
| `data/raw_hits*.json` | Raw Genius lyric-search hits (not curated) |
| `data/candidates*.tsv` | Auto-filtered snippets that mention a kilo term and a number |
| `data/queries*.txt` | Search phrases used |
| `data/unodc_us_wholesale.json` | UNODC's average US wholesale price of a kilo, 1990–2021, for the benchmark line on the chart. Not lyric data |

### Row schema

| Field | Meaning |
|---|---|
| `year` | Release year (Genius) |
| `date`, `date_precision`, `date_display` | Best date for the bar: a date the lyric itself fixes (`date_source`=`lyric`, reason in `date_note`), else the song's Genius release date, else the album's. Precision is `day`, `month`, or `year` |
| `image`, `image_source`, `song_art` | Card photo. `data/images.json` (hand picks, keyed `artist|song`) wins; else `data/images_auto.json` from `data/fetch_images.py`, which uses the performer's Genius photo, else the song art. Files live in `site/img/{artists,art}/`, square 480px |
| `album`, `song_release`, `album_release` | From the Genius song page (`data/release_dates.json`, fetched by `data/release_dates.py`) |
| `artist` | Credited artist |
| `performer` | Who actually raps the line, when known |
| `song`, `quote` | Song title and the line, lightly trimmed |
| `price_k` | Price in thousands of `currency` per kilo |
| `kind` | `sell` (rapper's asking price), `buy` (what they pay), `quoted` (stated as market price), `profit` (not a price) |
| `currency` | USD, GBP, CAD |
| `city` | Rapper's home market, when known |
| `confidence` | `high` / `medium` / `low` that the number is really a per-kilo cocaine price |
| `flags` | `implied_unit` (kilo not named in the line), `retrospective` (line refers to an earlier era), `outlier`, `hyperbole`, `homage`, `meta`, `derived`, `posthumous`, `profit_not_price`, `wordplay` |
| `source` | `lyric_search` (found by phrase search) or `annotation` (found because a Genius annotation decoded the line) |
| `lyric_location` | A place the lyric itself names ("11-5 in Dade County"), kept separate from where the rapper is from |
| `wiki_title`, `wiki_birth_place`, `wiki_origin`, `wiki_top_city` | From the performer's Wikipedia article: infobox birth place and origin, plus the city mentioned most often in the article text |
| `home_city`, `home_city_source` | Resolved market: `lyric_location`, else hand-entered `city`, else `wiki_origin`, else `wiki_top_city`, else `wiki_birth_place`, else `inferred_city`. Source says which rule fired |
| `inferred_city`, `inferred_basis`, `inferred_url`, `inferred_confidence` | From `data/inferred_places.json`: hand-checked placements for artists with no Wikipedia page (Genius bios, SoundCloud/Bandcamp, local press). Keyed by `artist|song` |
| `genius_url` | Song page |
| `annotation_url` | `https://genius.com/<referent id>`: opens the song page scrolled to the quoted line with its annotation open. Null when nobody has annotated that line. `annotation_text` and `annotation_votes` carry the fan explanation |

Aggregates in `site_data.json` exclude `profit`, anything flagged `outlier`, and non-USD rows.

## Site

`site/` is the static front end: **36 Zips — the price of a kilo according to rap**. Open `site/index.html` in a browser, or serve the folder as-is. No runtime dependencies; the map, projected dot positions and all entries live in `site/data.js`.

Styled after Gucci Mane's *Bird Money* cover (`birdmoney.jpeg`): acid lime and violet as the twin accents, fat black outlines, bevelled gradient wordmarks, gold kept only for the price. The masthead wordmark is inline SVG rather than HTML text — `paint-order: stroke fill` is the only reliable way to keep a heavy outline *behind* the fill. The previous gold-and-felt theme is frozen in `site/snapshots/pre-birdmoney/`; see the `RESTORE.md` in there to put it back.

- US map with one dot per lyric on the rapper's home market, coloured green → gold → red by price (USD-equivalent, $10K–$45K+). Co-located dots spiral out from the city.
- Worldwide inset (bottom-left of the map) holds the UK, Canada, Ireland, France, and any entries with no known city. Alaska and Hawaii have no entries.
- Chart below the map: release date across, dollars per kilo up, one dot per lyric, same colours. Prices above $50K sit on the top line.
- Behind that chart, a dashed chrome line: UNODC's average US wholesale price of a kilo, from `data/unodc_us_wholesale.json` (World Drug Report statistical annex 8.3, sheet `Cocaine_US`, row "Average, in US$"). Nominal, like the lyrics, so the two sit on the same footing. Keyed on the chart, sourced in the note under it.
- Hover any dot to highlight its twin on the other chart and show the card (price, date, artist, song, quote, city, Genius annotation, links). Click to pin the card so the links are clickable; Esc or click away releases. A pinned card sets `#e<id>` in the URL, so every bar has a shareable link.

Rebuild `site/data.js` after changing the data:

```
cd build && npm install && node build.js      # needs data/site_data.json; fails loudly on any city missing from build/geocode.json
```

## Pipeline

```
python3 data/genius_sweep.py data/queries.txt data/raw_hits.json   # 1. sweep Genius lyric search by price phrases
ROSTER=data/artists.txt python3 data/annot_crawl.py                 # 2. crawl Genius annotations for a roster of artists
python3 data/wiki_place.py                                          # 3. place each rapper via Wikipedia -> rapper_places.json
python3 data/annot_links.py                                         # 3b. match each quote to its Genius referent -> annotation_links.json
python3 data/curate.py                                              # 4. hand-curated list + joins -> kilo_prices.json/csv
python3 data/release_dates.py                                       # 4b. song + album release dates from Genius -> release_dates.json
python3 data/fetch_images.py                                        # 4c. Genius artist photos + song art -> site/img/, images_auto.json
python3 data/build.py                                               # 5. precise dates + yearly aggregates -> site_data.json
node build/build.js                                                 # 6. project map + dots -> site/data.js (the static site reads only this)
```

Step 2 exists because phrase search misses lines where the kilo is implied ("I count 18-5 every time they swing my door"). The crawler keeps any annotation that mentions a kilo term and a dollar figure (`annot_hits.jsonl`); those were triaged by hand into `curate.py`. Artist names are resolved by exact match on Genius's artist search; ambiguous short names (AZ, B.G., TRU) needed that.

Step 3 uses the Wikipedia API. Only accepted when the article title shares a word with the rapper's name; `WIKI_BAD` in `curate.py` lists same-name collisions that slipped through. Most-mentioned city picks up tour stops for touring acts (Westside Gunn's is Paris), so infobox origin ranks above it.

Genius's public endpoints rate-limit hard (HTTP 429) after a few hundred fast requests, and the block lasts about an hour. Both scripts sleep between calls and back off on 429. Wikipedia rate-limits too.

## Caveats

- Numbers like "36" often mean ounces in a kilo, not dollars. Those were dropped.
- "Bricks" of weed, molly, or fentanyl were dropped when the context made that clear.
- A rapper's number is a boast, a memory, or a bar, not a survey. Treat medians, not single points.
- The UNODC line is one self-reported national average a year, not a distribution: UNODC's own country table puts the 2018 US range at $4,000–$45,000 a kilo. It is unadjusted for purity, and jumps like the 2011 spike to $40,800 may be reporting artefacts rather than the market moving. It is a backdrop for the bars, not a truth they should be scored against. The series stops at 2021; UNODC has published no US wholesale figure since.
