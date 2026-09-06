"""Fetch song + album release dates from Genius for every curated row -> data/release_dates.json (cached, resumable)."""
import json, time, urllib.request, urllib.error, os, sys
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36","Accept":"application/json"}
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=json.load(open(f"{ROOT}/data/kilo_prices.json"))
out_path=f"{ROOT}/data/release_dates.json"
cache=json.load(open(out_path)) if os.path.exists(out_path) else {}

def get(url):
    while True:
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30); time.sleep(3); return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code==429: print("429 backoff 10 min",flush=True); time.sleep(600); continue
            if e.code==404: return None
            print("http",e.code,url,flush=True); time.sleep(30)
        except Exception as ex:
            print("err",ex,flush=True); time.sleep(30)

ids=sorted({str(r["genius_id"]) for r in rows if r.get("genius_id")})
todo=[i for i in ids if i not in cache]
print(f"{len(ids)} songs, {len(todo)} to fetch",flush=True)
for n,sid in enumerate(todo,1):
    d=get(f"https://genius.com/api/songs/{sid}")
    s=(d or {}).get("response",{}).get("song") or {}
    a=s.get("album") or {}
    cache[sid]=dict(title=s.get("title"),artist=s.get("artist_names"),
                    song_release=s.get("release_date_components"),song_release_display=s.get("release_date_for_display"),
                    album=a.get("name"),album_release=a.get("release_date_components"),album_release_display=a.get("release_date_for_display"),
                    recording_location=s.get("recording_location"))
    json.dump(cache,open(out_path,"w"),indent=1,ensure_ascii=False)
    print(f"{n}/{len(todo)} {sid} {s.get('artist_names')} - {s.get('title')} :: song {s.get('release_date_for_display')} | album {a.get('name')} {a.get('release_date_for_display')}",flush=True)
print("done",flush=True)
