"""Build derived data: precise dates + yearly aggregates for the front end."""
import json, statistics as st, collections, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=json.load(open(f"{ROOT}/data/kilo_prices.json"))
rd_path=f"{ROOT}/data/release_dates.json"
rd=json.load(open(rd_path)) if os.path.exists(rd_path) else {}

# Dates the lyric itself fixes, which beat the release date. (artist, song) -> (date, precision, why)
# Keyed by artist+song, not row id, so the table reads without looking ids up.
# A key may also carry price_k as a third element, for a line that prices two eras in one row pair.
LYRIC_DATES={
    ("Rick Ross","War Ready"): ("1993","year","Lyric: 'Seventeen, I was chargin'' — Rick Ross (b. Jan 28, 1976) was 17 in 1993"),
    ("Gorilla Zoe","Money Man",24): ("2006","year","Lyric: 'Last year was 24, this year is 28' — song released 2007, so 24 is the 2006 price"),
}
MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def comps_to_date(c):
    if not c or not c.get("year"): return None
    y,m,d=c.get("year"),c.get("month"),c.get("day")
    if m and d: return (f"{y:04d}-{m:02d}-{d:02d}","day")
    if m: return (f"{y:04d}-{m:02d}","month")
    return (f"{y:04d}","year")

def display(date,prec):
    y=int(date[:4])
    if prec=="day": return f"{MON[int(date[5:7])-1]} {int(date[8:10])}, {y}"
    if prec=="month": return f"{MON[int(date[5:7])-1]} {y}"
    return str(y)

mismatch=[]
for r in rows:
    info=rd.get(str(r.get("genius_id")),{})
    song=comps_to_date(info.get("song_release")); album=comps_to_date(info.get("album_release"))
    rank={"day":3,"month":2,"year":1}
    ld=LYRIC_DATES.get((r["artist"],r["song"],r["price_k"])) or LYRIC_DATES.get((r["artist"],r["song"]))
    if ld:
        date,prec,why=ld; src="lyric"
    elif song and (not album or rank[song[1]]>=rank[album[1]]):
        date,prec=song; src="song_release"; why=None
    elif album:
        date,prec=album; src="album_release"; why=None
    else:
        date,prec,src,why=str(r["year"]),"year","genius_year",None
    r["date"]=date; r["date_precision"]=prec; r["date_source"]=src; r["date_display"]=display(date,prec)
    r["date_note"]=why
    r["album"]=info.get("album"); r["album_release"]=album[0] if album else None
    r["song_release"]=song[0] if song else None
    if src!="lyric" and int(date[:4])!=r["year"]:
        mismatch.append((r["id"],r["artist"],r["song"],r["year"],date))
        r["curated_year"]=r.get("curated_year",r["year"]); r["year"]=int(date[:4])   # keep the row self-consistent with its Genius page

def chartable(r): return r["kind"]!="profit" and "outlier" not in r["flags"] and r["currency"]=="USD"
by=collections.defaultdict(list)
for r in rows:
    if chartable(r): by[int(r["date"][:4])].append(r["price_k"])
years=[]
for y in sorted(by):
    v=by[y]
    years.append(dict(year=y,n=len(v),median=st.median(v),mean=round(st.mean(v),1),min=min(v),max=max(v)))
json.dump(dict(entries=rows,yearly=years,
               meta=dict(source="Genius lyric search, hand-curated",built="2026-09-03",
                         note="price_k is thousands in `currency`. kind=profit and flags containing 'outlier' are excluded from yearly aggregates; only USD aggregated. date = lyric-stated date, else Genius song release date, else album release date.")),
          open(f"{ROOT}/data/site_data.json","w"),indent=1,ensure_ascii=False)
json.dump(rows,open(f"{ROOT}/data/kilo_prices.json","w"),indent=1,ensure_ascii=False)
prec=collections.Counter(r["date_precision"] for r in rows); src=collections.Counter(r["date_source"] for r in rows)
print("precision",dict(prec),"source",dict(src))
if mismatch:
    print("release year != curated year (year updated, old value kept in curated_year):")
    for m in mismatch: print("  ",m)
print(f"{'year':>5} {'n':>3} {'median':>7} {'mean':>6} {'range':>10}")
for y in years: print(f"{y['year']:>5} {y['n']:>3} {y['median']:>7} {y['mean']:>6} {str(y['min'])+'-'+str(y['max']):>10}")
