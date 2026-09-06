"""Pull artist photos and song art for every row, all from Genius.
song -> song_art + primary/featured artist image_url.
Writes site/img/{artists,art}/*.jpg (square, 480px) and data/images_auto.json (per artist|song: chosen + candidates + source urls).
Manual picks in data/images.json override the chosen image in curate.py."""
import json, time, urllib.request, urllib.error, urllib.parse, os, re, subprocess, hashlib
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36 kilo-index/1.0 (contact: daniel@russey.dad)","Accept":"application/json"}
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=json.load(open(f"{ROOT}/data/kilo_prices.json"))
GC=f"{ROOT}/data/genius_images.json"
gcache=json.load(open(GC)) if os.path.exists(GC) else {}
SIZE=480

def get(url,sleep=3):
    while True:
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30); time.sleep(sleep); return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code==429: print("429 backoff 10 min",flush=True); time.sleep(600); continue
            print("http",e.code,url,flush=True); return None
        except Exception as ex: print("err",ex,flush=True); time.sleep(20)

def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")[:60] or "x"
def norm(s): return re.sub(r"[^a-z0-9]","",(s or "").lower())
DEFAULT_AVATAR=re.compile(r"default_avatar|default_cover")

# 1. Genius song -> images (cached)
ids=sorted({str(r["genius_id"]) for r in rows if r.get("genius_id")})
todo=[i for i in ids if i not in gcache]
print(f"genius: {len(ids)} songs, {len(todo)} to fetch",flush=True)
for n,sid in enumerate(todo,1):
    s=(get(f"https://genius.com/api/songs/{sid}") or {}).get("response",{}).get("song") or {}
    art=lambda a: dict(id=a.get("id"),name=a.get("name"),image=a.get("image_url"),header=a.get("header_image_url"))
    gcache[sid]=dict(title=s.get("title"),song_art=s.get("song_art_image_url"),header=s.get("header_image_url"),
                     primary=art(s.get("primary_artist") or {}),featured=[art(a) for a in s.get("featured_artists") or []],
                     primaries=[art(a) for a in s.get("primary_artists") or []])
    json.dump(gcache,open(GC,"w"),indent=1,ensure_ascii=False)
    print(f"  {n}/{len(todo)} {sid} {s.get('artist_names')} - {s.get('title')}",flush=True)

# 3. download + square-crop
def fetch_img(url,dest):
    if os.path.exists(dest): return True
    if not url or DEFAULT_AVATAR.search(url): return False
    tmp=dest+".tmp"
    try:
        req=urllib.request.Request(url,headers={"User-Agent":UA["User-Agent"]})
        with urllib.request.urlopen(req,timeout=60) as r, open(tmp,"wb") as f: f.write(r.read())
        subprocess.run(["convert",tmp+"[0]","-auto-orient","-resize",f"{SIZE}x{SIZE}^","-gravity","center","-extent",f"{SIZE}x{SIZE}","-strip","-quality","84",dest],check=True,capture_output=True)
        os.remove(tmp); time.sleep(0.4); return True
    except Exception as ex:
        print("  img fail",url[:80],ex,flush=True)
        if os.path.exists(tmp): os.remove(tmp)
        return False

for d in ("artists","art"): os.makedirs(f"{ROOT}/site/img/{d}",exist_ok=True)
auto={}
for r in rows:
    g=gcache.get(str(r.get("genius_id"))) or {}
    who=r["performer"] or re.split(r" & |, | \(Ft\.",r["artist"])[0].strip()
    cands=[g.get("primary") or {}]+(g.get("primaries") or [])+(g.get("featured") or [])
    match=next((a for a in cands if a.get("name") and norm(a["name"])==norm(who)),None)
    match=match or next((a for a in cands if a.get("name") and (norm(who) in norm(a["name"]) or norm(a["name"]) in norm(who))),None)
    artist=match or (g.get("primary") or {})
    out=dict(performer=who,artist_photo=None,song_art=None,sources={})
    if artist.get("image"):
        p=f"img/artists/{slug(artist['name'])}-{artist['id']}.jpg"
        if fetch_img(artist["image"],f"{ROOT}/site/{p}"): out["artist_photo"]=p; out["sources"]["artist_photo"]=artist["image"]
    if g.get("song_art"):
        p=f"img/art/{r['genius_id']}.jpg"
        if fetch_img(g["song_art"],f"{ROOT}/site/{p}"): out["song_art"]=p; out["sources"]["song_art"]=g["song_art"]
    out["image"]=out["artist_photo"] or out["song_art"]
    auto[f"{r['artist']}|{r['song']}"]=out
    print(f"{r['id']:>3} {who[:28]:<28} photo={'Y' if out['artist_photo'] else '-'} art={'Y' if out['song_art'] else '-'}",flush=True)
json.dump(auto,open(f"{ROOT}/data/images_auto.json","w"),indent=1,ensure_ascii=False)
n=lambda k: sum(1 for v in auto.values() if v[k])
print(f"done: {len(auto)} rows, artist_photo {n('artist_photo')}, song_art {n('song_art')}, any {n('image')}",flush=True)
