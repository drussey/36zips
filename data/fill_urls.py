import json,time,urllib.request,urllib.parse,re
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
import os
rows=json.load(open("data/kilo_prices.json"))
found=json.load(open("data/url_fixups.json")) if os.path.exists("data/url_fixups.json") else {}
for e in rows:
    if e["genius_url"]: continue
    q=f'{e["artist"].split(" &")[0]} {e["song"]}'
    d=json.load(urllib.request.urlopen(urllib.request.Request("https://genius.com/api/search/song?"+urllib.parse.urlencode({"q":q}),headers=UA),timeout=30))
    time.sleep(4)
    for s in d["response"]["sections"]:
        for h in s["hits"]:
            r=h["result"]
            if re.sub(r"\W","",e["song"].lower())[:10] in re.sub(r"\W","",r["title"].lower()):
                found[f'{e["artist"]}|{e["song"]}']=(r["url"],r["id"],(r.get("release_date_components") or {}).get("year")); break
        if f'{e["artist"]}|{e["song"]}' in found: break
    print(e["artist"],"-",e["song"],"->",found.get(f'{e["artist"]}|{e["song"]}'))
json.dump(found,open("data/url_fixups.json","w"),indent=1)
