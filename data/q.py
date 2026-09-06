import json,sys,urllib.request,urllib.parse
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
for q in sys.argv[1:]:
    url="https://genius.com/api/search/lyric?"+urllib.parse.urlencode({"q":q,"per_page":10})
    d=json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30))
    print("=== ",q)
    for s in d["response"]["sections"]:
        for h in s["hits"][:8]:
            r=h["result"]; y=(r.get("release_date_components") or {}).get("year")
            print(y, "|", r["full_title"][:70], "|", " ".join(hl["value"].replace("\n"," / ") for hl in h.get("highlights",[]))[:220])
