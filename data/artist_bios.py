"""For rows with no home city: pull the Genius song description + primary artist bio/socials -> data/artist_bios.json"""
import json, time, urllib.request, urllib.error, os
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36","Accept":"application/json"}
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=[r for r in json.load(open(f"{ROOT}/data/kilo_prices.json")) if not r["home_city"]]
out=f"{ROOT}/data/artist_bios.json"; cache=json.load(open(out)) if os.path.exists(out) else {}
def get(url):
    while True:
        try: r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30); time.sleep(3); return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code==429: print("429",flush=True); time.sleep(600); continue
            return None
        except Exception: time.sleep(20)
def text(dom):
    if dom is None: return ""
    if isinstance(dom,str): return dom
    if isinstance(dom,list): return "".join(text(x) for x in dom)
    return text(dom.get("children"))
for r in rows:
    k=str(r["id"])
    if k in cache: continue
    s=(get(f"https://genius.com/api/songs/{r['genius_id']}") or {}).get("response",{}).get("song",{})
    pa=s.get("primary_artist") or {}
    a=(get(f"https://genius.com/api/artists/{pa.get('id')}") or {}).get("response",{}).get("artist",{}) if pa.get("id") else {}
    cache[k]=dict(artist=r["artist"],song_desc=text((s.get("description") or {}).get("dom"))[:600],
                  artist_name=a.get("name"),artist_bio=text((a.get("description") or {}).get("dom"))[:800],
                  instagram=a.get("instagram_name"),twitter=a.get("twitter_name"),facebook=a.get("facebook_name"),
                  artist_url=a.get("url"),recording_location=s.get("recording_location"),
                  featured=[f.get("name") for f in s.get("featured_artists") or []],
                  producers=[p.get("name") for p in s.get("producer_artists") or []])
    json.dump(cache,open(out,"w"),indent=1,ensure_ascii=False)
    print(k,r["artist"],"|",cache[k]["artist_bio"][:120].replace("\n"," "),"|",cache[k]["instagram"],flush=True)
print("done",flush=True)
