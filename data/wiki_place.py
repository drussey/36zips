"""Place each rapper via Wikipedia: infobox birth_place/origin + most-mentioned city in article text."""
import json, re, sys, time, urllib.request, urllib.parse, os, collections
UA={"User-Agent":"rap-kilo-index/0.1 (research; contact via github)"}
API="https://en.wikipedia.org/w/api.php?"
def api(**p):
    p.update(format="json"); 
    for i in range(6):
        try:
            r=urllib.request.urlopen(urllib.request.Request(API+urllib.parse.urlencode(p),headers=UA),timeout=30)
            time.sleep(1.2); return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(30*(i+1)); continue
            raise
    raise RuntimeError("429 persisted")
RAW=json.load(open("data/wiki_raw.json")) if os.path.exists("data/wiki_raw.json") else {}
CITIES=[l.strip() for l in open("data/cities.txt") if l.strip()]
CITY_RE={c:re.compile(r"\b"+re.escape(c)+r"\b") for c in CITIES}
def find_title(name):
    for cand in (name, name+" (rapper)"):
        d=api(action="query",prop="extracts",exintro=1,explaintext=1,titles=cand,redirects=1)
        pg=next(iter(d["query"]["pages"].values()))
        intro=pg.get("extract","").lower()
        if "missing" not in pg and any(w in intro for w in ("rapper","hip hop","hip-hop","record producer","musician")): return pg["title"]
    for q in (f'"{name}" rapper', f'{name} rapper', name):
        s=api(action="query",list="search",srsearch=q,srlimit=5)["query"]["search"]
        for h in s:
            snip=re.sub("<[^>]+>","",h["snippet"]).lower()
            if any(w in snip for w in ("rapper","hip hop","hip-hop","record producer","musician","singer")): return h["title"]
        if s: return s[0]["title"]
    return None
def infobox(wikitext):
    out={}
    wikitext=re.sub(r"<!--.*?-->","",wikitext,flags=re.S)
    wikitext=re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>","",wikitext,flags=re.S)
    for key in ("birth_place","origin","birthplace"):
        m=re.search(r"\|\s*"+key+r"\s*=\s*(.+)",wikitext)
        if m:
            v=m.group(1); v=re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>","",v); v=re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]",r"\2",v)
            v=re.sub(r"\{\{[^}]*\}\}","",v); v=re.split(r"<br\s*/?>",v)[0].strip(" .,|")
            if v and "=" not in v and "{" not in v and len(v)<80: out[key]=v
    return out
def place(name):
    t=find_title(name)
    if not t: return dict(name=name,title=None)
    raw=RAW.get(t)
    if not raw:
        d=api(action="query",prop="revisions|extracts",rvprop="content",rvslots="main",explaintext=1,titles=t,redirects=1)
        page=next(iter(d["query"]["pages"].values()))
        raw=dict(wt=page.get("revisions",[{}])[0].get("slots",{}).get("main",{}).get("*",""),text=page.get("extract",""))
        RAW[t]=raw; json.dump(RAW,open("data/wiki_raw.json","w"))
    wt,text=raw["wt"],raw["text"]
    ib=infobox(wt)
    counts={c:len(r.findall(text)) for c,r in CITY_RE.items()}
    counts={c:n for c,n in counts.items() if n}
    top=sorted(counts.items(),key=lambda x:-x[1])[:5]
    return dict(name=name,title=t,birth_place=ib.get("birth_place") or ib.get("birthplace"),origin=ib.get("origin"),
                top_cities=top,is_rapper=("rapper" in text[:600].lower() or "hip hop" in text[:600].lower()))
if __name__=="__main__":
    names=sys.argv[1:] or [l.strip() for l in open("data/rapper_names.txt") if l.strip()]
    cache=json.load(open("data/rapper_places.json")) if os.path.exists("data/rapper_places.json") else {}
    for n in names:
        if n in cache: continue
        try: cache[n]=place(n)
        except Exception as e: cache[n]=dict(name=n,error=str(e))
        print(json.dumps(cache[n],ensure_ascii=False))
        json.dump(cache,open("data/rapper_places.json","w"),indent=1,ensure_ascii=False)
