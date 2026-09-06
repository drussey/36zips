import json, sys, time, urllib.request, urllib.parse, re
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
def search(q, pages=2):
    out=[]
    for p in range(1,pages+1):
        url="https://genius.com/api/search/lyric?"+urllib.parse.urlencode({"q":q,"per_page":20,"page":p})
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30)
            d=json.load(r)
        except Exception as e:
            print("ERR",q,e,file=sys.stderr); break
        hits=[h for s in d["response"]["sections"] for h in s["hits"]]
        if not hits: break
        for h in hits:
            res=h["result"]; rd=res.get("release_date_components") or {}
            out.append({"q":q,"title":res["full_title"],"artist":res["artist_names"],
                        "year":rd.get("year"),"url":res["url"],"id":res["id"],
                        "snips":[hl["value"] for hl in h.get("highlights",[])]})
        time.sleep(4)
    return out
qfile=sys.argv[1] if len(sys.argv)>1 else "data/queries.txt"; outfile=sys.argv[2] if len(sys.argv)>2 else "data/raw_hits.json"
queries=[l.strip() for l in open(qfile) if l.strip()]
allhits=[]
for q in queries:
    allhits+=search(q)
json.dump(allhits,open(outfile,"w"),indent=1)
print(len(allhits),"hits")
