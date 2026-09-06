"""For every dataset row, find the Genius referent (annotated lyric span) covering the quoted line
and record annotation_url = https://genius.com/<referent id>. Referents cached per song."""
import json, os, re, time, urllib.request
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
CACHE="data/referents_cache.json"; OUT="data/annotation_links.json"
cache=json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def get(url):
    for i in range(20):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30); time.sleep(2.5); return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code==429: print("429 backoff",flush=True); time.sleep(600); continue
            if e.code==404: return None
            time.sleep(30)
    return None
def referents(sid):
    if str(sid) in cache: return cache[str(sid)]
    out=[]; page=1
    while True:
        d=get(f"https://genius.com/api/referents?song_id={sid}&text_format=plain&per_page=50&page={page}")
        if not d: break
        refs=d["response"]["referents"]
        for r in refs:
            out.append(dict(id=r["id"],fragment=r["fragment"],votes=max([a.get("votes_total",0) for a in r.get("annotations",[])] or [0]),
                            body=(r.get("annotations") or [{}])[0].get("body",{}).get("plain","")[:400]))
        if len(refs)<50 or page>=4: break
        page+=1
    cache[str(sid)]=out; json.dump(cache,open(CACHE,"w")); return out
def norm(s):
    s=s.lower().replace("’","'"); s=re.sub(r"\[\.\.\.\]|\(.*?\)","",s)
    s=re.sub(r"(?<=\d)[\.\-, ]+(?=\d)","",s)      # 17.5 / 17-5 / 18 5 -> 175 / 185
    s=re.sub(r"(?<=[a-z])-(?=[a-z])"," ",s)          # twenty-two -> twenty two
    s=re.sub(r"[^a-z0-9' ]"," ",s)
    return re.sub(r"\s+"," ",s).strip()
ONES={"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,"sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19}
TENS={"twenty":20,"thirty":30,"forty":40,"fifty":50,"sixty":60,"seventy":70,"eighty":80,"ninety":90}
def numwords(toks):
    out=[];i=0
    while i<len(toks):
        t=toks[i]
        if t in TENS:
            v=TENS[t]
            if i+1<len(toks) and toks[i+1] in ONES and ONES[toks[i+1]]<10: v+=ONES[toks[i+1]]; i+=1
            out.append(str(v))
        elif t in ONES: out.append(str(ONES[t]))
        else: out.append(t)
        i+=1
    # glue "17 5" style (digit token followed by single digit) -> 175, matching norm() of "17.5"
    g=[]
    for t in out:
        if g and re.fullmatch(r"\d",t) and re.fullmatch(r"\d{2}",g[-1]): g[-1]=g[-1]+t
        else: g.append(t)
    return g
def words(s): return numwords(norm(s).split())
def match(quote, refs):
    q=words(quote); best=(0,None)
    for r in refs:
        f=words(r["fragment"])
        if not f: continue
        fs=" ".join(f)
        # longest run of consecutive quote words found in fragment
        L=0
        for i in range(len(q)):
            for j in range(len(q),i,-1):
                if j-i<=L: break
                if " ".join(q[i:j]) in fs: L=j-i; break
        # numeric token bonus: the price token itself must appear
        nums=[w for w in q if re.search(r"\d",w)]
        numok=all(n in fs for n in nums) if nums else True
        score=L+(2 if numok else -3)
        if score>best[0]: best=(score,r)
    minlen=3 if len(q)<=5 else 4
    return best[1] if best[0]>=minlen+1 else None
rows=json.load(open("data/kilo_prices.json"))
links=json.load(open(OUT)) if os.path.exists(OUT) else {}
for e in rows:
    key=f'{e["artist"]}|{e["song"]}|{e["quote"][:40]}'
    if (key in links and links[key]["annotation_url"]) or not e.get("genius_id"): continue
    refs=referents(e["genius_id"])
    r=match(e["quote"],refs)
    links[key]=dict(annotation_url=f"https://genius.com/{r['id']}" if r else None,
                    fragment=r["fragment"] if r else None, annotation=r["body"] if r else None, votes=r["votes"] if r else None,
                    n_referents=len(refs))
    json.dump(links,open(OUT,"w"),indent=1,ensure_ascii=False)
    print(("OK  " if r else "--  ")+e["artist"]+" - "+e["song"],flush=True)
print("DONE",flush=True)
