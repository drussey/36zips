"""Crawl Genius annotations for a roster of artists; keep annotations that decode a kilo price.
Resumable: progress in data/annot_state.json, hits appended to data/annot_hits.jsonl."""
import json, os, re, sys, time, urllib.request, urllib.parse
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
SLEEP=float(os.environ.get("SLEEP","4")); SONGS_PER_ARTIST=int(os.environ.get("SONGS","60"))
STATE="data/annot_state.json"; OUT="data/annot_hits.jsonl"; LOG=sys.stderr
state=json.load(open(STATE)) if os.path.exists(STATE) else {"done_artists":[],"done_songs":[]}
done_songs=set(state["done_songs"])
def save(): json.dump(state,open(STATE,"w"))
def get(url, tries=50):
    for i in range(tries):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30)
            time.sleep(SLEEP); return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code==429: print("429, backing off 10 min",file=LOG); LOG.flush(); time.sleep(600); continue
            if e.code==404: return None
            print("HTTP",e.code,url,file=LOG); time.sleep(30)
        except Exception as e:
            print("ERR",e,url,file=LOG); time.sleep(30)
    return None
KILO=re.compile(r"\b(kilo|kilos|kilogram|brick|bricks|key|keys|ki|kis|bird|birds|whole thing)\b",re.I)
MONEY=re.compile(r"(\$\s?\d[\d,\.]*\s*(k|thousand|grand)?|\b\d{1,2}[.,]\d\b|\b\d{1,2}\s*(k|thousand|grand|bands|racks)\b|\b(ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty)[ -]?(one|two|three|four|five|six|seven|eight|nine)?\s*(thousand|grand|k\b))",re.I)
def artist_id(name):
    d=get("https://genius.com/api/search/artist?"+urllib.parse.urlencode({"q":name}))
    if not d: return None
    hits=[h["result"] for s in d["response"]["sections"] for h in s["hits"] if h["type"]=="artist"]
    for r in hits:
        if r["name"].lower()==name.lower(): return r["id"], r["name"]
    return (hits[0]["id"],hits[0]["name"]) if hits else None
def songs(aid):
    out=[]; page=1
    while len(out)<SONGS_PER_ARTIST:
        d=get(f"https://genius.com/api/artists/{aid}/songs?per_page=50&page={page}&sort=popularity")
        if not d: break
        ss=d["response"]["songs"]; out+=ss
        if not d["response"].get("next_page"): break
        page+=1
    return out[:SONGS_PER_ARTIST]
def referents(sid):
    d=get(f"https://genius.com/api/referents?song_id={sid}&text_format=plain&per_page=50")
    return d["response"]["referents"] if d else []
for name in [l.strip() for l in open(os.environ.get("ROSTER","data/artists.txt")) if l.strip()]:
    if name in state["done_artists"]: continue
    a=artist_id(name)
    if not a: print("no artist:",name,file=LOG); state["done_artists"].append(name); save(); continue
    aid,aname=a
    for s in songs(aid):
        if s["id"] in done_songs: continue
        y=(s.get("release_date_components") or {}).get("year")
        for r in referents(s["id"]):
            for ann in r.get("annotations",[]):
                body=ann.get("body",{}).get("plain","")
                if KILO.search(body) and MONEY.search(body):
                    rec=dict(artist=s["primary_artist"]["name"],roster=aname,song=s["title"],year=y,song_id=s["id"],
                             url=s["url"],fragment=r.get("fragment"),annotation=body[:1500],votes=ann.get("votes_total"))
                    open(OUT,"a").write(json.dumps(rec,ensure_ascii=False)+"\n")
        done_songs.add(s["id"]); state["done_songs"]=sorted(done_songs); save()
    state["done_artists"].append(name); save()
    print("done",aname,file=LOG); LOG.flush()
print("CRAWL DONE",file=LOG)
