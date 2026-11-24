#!/usr/bin/env python3
"""Builds the static site for Raviva Nsiama into dist/.
All content lives in content/ (edited via the CMS at /admin)."""
import html, json, os, glob, shutil

E = html.escape
NAME = "Raviva Nsiama"
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

def load(p): return json.load(open(p, encoding="utf-8"))
def norm(p):
    p = (p or "").strip()
    return p[1:] if p.startswith("/") else p

def T(x): return tuple(x)
FILMS = []
for p in sorted(glob.glob("content/films/*.json")):
    d = load(p)
    if d.get("hidden"): continue
    f = dict(slug=d["slug"], title=d["title"], year=str(d["year"]), kind=d["kind"], meta=d.get("meta") or [],
             hero=norm(d["hero"]), cover=norm(d["cover"]), orient=d.get("orient","land"),
             stills=[norm(x) for x in d.get("stills") or []], feature=norm(d.get("feature")) or None,
             split=int(d.get("feature_after") or 0), cols=int(d.get("columns") or 3),
             mood=(norm(d["mood"]["image"]), d["mood"]["text"]) if d.get("mood") and d["mood"].get("image") else None,
             bts=(d["bts"]["title"], [norm(x) for x in d["bts"]["images"]]) if d.get("bts") and d["bts"].get("images") else None,
             lead=d.get("lead",""), text=d.get("text") or [],
             credits=[(c["role"], c["name"]) for c in d.get("credits") or []],
             voices=[(v["name"], v["role"], v["quotes"]) for v in d.get("voices") or []],
             screenings=d.get("screenings") or [], awards=d.get("awards") or [],
             laurels=[(norm(l["image"]), l.get("alt","Festival laurel")) for l in d.get("laurels") or []],
             watch=(d["watch"]["label"], d["watch"].get("url") or None) if d.get("watch") and d["watch"].get("label") else None,
             video=norm(d.get("video")), video_poster=norm(d.get("video_poster")), order=d.get("order", 99))
    FILMS.append(f)
FILMS.sort(key=lambda f: f["order"])

def blk(b):
    t = b["type"]
    if t == "textimg": return ("textimg", norm(b["image"]), b.get("title",""), b.get("text",""), b.get("side","r"))
    if t == "kit": return ("kit", norm(b["image"]), b.get("caption",""))
    if t == "palette": return ("palette", [(c["hex"], c["label"]) for c in b.get("colors") or []])
    if t == "full": return ("full", norm(b["image"]))
    if t == "images": return (b.get("layout","pair"), [norm(x) for x in b.get("images") or []])
    if t == "strip": return ("strip", b.get("title",""), [norm(x) for x in b.get("images") or []])
    if t == "text": return ("text", b.get("title",""), b.get("text",""))
    if t == "feed": return ("feed", norm(b["image"]), b.get("url",""), b.get("handle",""))
    if t == "video": return ("video", norm(b["video"]), norm(b.get("poster")))
    if t == "portraits": return ("portraits", [(norm(i["image"]), i["name"], i.get("url","")) for i in b.get("items") or []])
    if t == "links": return ("links", b.get("title",""), [(i["label"], i["url"]) for i in b.get("items") or []])
    return ("none",)
VISUAL = []
for p in sorted(glob.glob("content/visual/*.json")):
    d = load(p)
    if d.get("hidden"): continue
    VISUAL.append(dict(slug=d["slug"], title=d["title"], year=str(d["year"]), sort=str(d.get("sort_year") or d["year"]),
        kind=d["kind"], cover=norm(d["cover"]), role=d.get("role",""), lead=d.get("lead",""),
        blocks=[blk(b) for b in d.get("blocks") or []], order=d.get("order", 99)))
VISUAL.sort(key=lambda v: v["order"])

LISTS = load("content/lists.json")
AWARDS = [(a["label"], a["title"], a["details"], a["when"], "hi" if a.get("highlight") else "") for a in LISTS.get("awards") or []]
EXHIB = [(e["when"], e["title"], e["details"], e.get("url") or None) for e in LISTS.get("exhibitions") or []]
EARLIER = [(e["title"], e["details"]) for e in LISTS.get("earlier") or []]
PRESS = [(e["when"], e["title"], e["details"], e.get("url") or None) for e in LISTS.get("press") or []]
PAGES = load("content/pages.json")

def img(name, alt="", cls="", eager=False):
    name = norm(name)
    src = name if "." in name else f"img/{name}.jpg"
    return f'<img src="{src}" alt="{E(alt)}"{" class="+chr(34)+cls+chr(34) if cls else ""} loading="lazy" decoding="async">'

def ext(text, url):
    return f'<a href="{url}" target="_blank" rel="noopener">{E(text)} <span class="ar">↗</span></a>' if url else E(text)

def awards():
    cards = "".join(f'<div class="aw {c}"><span class="when">{w}</span><b>{E(s)}</b><h4>{E(t)}</h4><p>{E(d)}</p></div>' for s,t,d,w,c in AWARDS)
    return f'<section class="tbl"><h3>Awards &amp; Recognition</h3><div class="awg">{cards}</div></section>'

def earlier():
    li = "".join(f'<li><b>{E(a)}</b><span>{E(c)}</span></li>' for a,c in EARLIER)
    return f'<div class="earlier"><h4>Earlier exhibitions &amp; screenings</h4><ul>{li}</ul></div>'

def table(title, data):
    rows = "".join(f'<tr><td>{a}</td><td>{ext(b,u)}</td><td>{E(c)}</td></tr>' for a,b,c,u in data)
    return f'<section class="tbl"><h3>{title}</h3><table class="stack"><thead><tr><th>When</th><th>Event / Publication</th><th>Details</th></tr></thead><tbody>{rows}</tbody></table></section>'

def stills(f):
    o = f["orient"]; cols = f.get("cols", 3)
    T = lambda n: f'<figure>{img(n, f["title"]+" – still")}</figure>'
    s = f["stills"]; k = f.get("split", 0)
    parts = [T(x) for x in s[:k]] if f.get("feature") else []
    if f.get("feature"):
        parts.append(f'<figure class="feat">{img(f["feature"], f["title"]+" – still")}</figure>')
        parts += [T(x) for x in s[k:]]
    else:
        parts = [T(x) for x in s]
    return f'<div class="band sband"><div class="wrap"><div class="sec-h"><h2>Stills</h2></div><div class="sgrid {o}" style="--c:{cols}">{"".join(parts)}</div></div></div>'

def mood(f):
    if not f.get("mood"): return ""
    pic, paras = f["mood"]
    return (f'<div class="band moodband"><div class="wrap mood"><figure class="nb">{img(pic, f["title"]+" – notebook moodboard")}</figure>'
            f'<div class="mood-t"><h4>Moodboard &amp; concept</h4>{"".join(f"<p>{E(p)}</p>" for p in paras)}</div></div></div>')

def voices(f):
    if not f.get("voices"): return ""
    cols = "".join(f'<div class="vc"><h4>{E(n)} · {E(r)}</h4>{"".join(f"<blockquote>“{E(q)}”</blockquote>" for q in qs)}</div>' for n,r,qs in f["voices"])
    return f'<div class="band voiceband"><div class="wrap"><div class="sec-h"><h2>Voices from the magazine</h2></div><p class="vintro">For the publication, Raviva interviewed the two performers about their bodies, the gaze and the spaces they claim. A few of their answers:</p><div class="voices">{cols}</div></div></div>'

def bts(f):
    if not f.get("bts"): return ""
    title, ims = f["bts"]
    figs = "".join(f'<figure>{img(x, f["title"]+" – "+title)}</figure>' for x in ims)
    return f'<div class="band btsband"><div class="wrap"><div class="sec-h"><h2>{E(title)}</h2></div><div class="bts">{figs}</div></div></div>'

def video(f):
    if not f.get("video"): return ""
    if os.path.exists(f["video"]):
        return f'<div class="band vidband"><div class="wrap"><figure class="pubvid"><video src="{f["video"]}" poster="{f["video_poster"]}" controls playsinline preload="metadata" muted loop></video><figcaption>Leafing through the publication</figcaption></figure></div></div>'
    return '<div class="band vidband"><div class="wrap"><figure class="pubvid ph"><div>Publication video<br><small>Leafing through the magazine · video follows</small></div></figure></div></div>'

def film_view(f, i):
    nxt = FILMS[(i+1) % len(FILMS)]
    cred = "".join(f"<li><i>{E(a)}</i> {E(b)}</li>" for a,b in f["credits"])
    scr = "".join(f"<li>{E(s)}</li>" for s in f["screenings"])
    aw = "".join(f"<li>{E(s)}</li>" for s in f["awards"])
    watch = ""
    if f["watch"]:
        label, url = f["watch"]
        watch = f'<a class="btn" href="{url}" rel="noopener" target="_blank">{label} ↗</a>' if url else f'<a class="btn" href="#contact">{label}</a>'
    laur = "".join(f'<img src="{l}" alt="{E(a)}">' for l,a in f["laurels"])
    body = "".join(f"<p>{E(t)}</p>" for t in f["text"])
    about = "project" if ("Photo" in f["kind"]) else "film"
    return f'''
<section class="view" id="v-{f["slug"]}" data-title="{E(f["title"])}">
  <div class="phero">{img(f["hero"], f["title"]+" – still")}<div class="phero-t"><p class="kick">{E(f["kind"])}</p><h1>{E(f["title"])}</h1><p class="meta">{f["year"]} · {" · ".join(E(m) for m in f["meta"])}</p></div></div>
  <div class="band"><div class="wrap pintro"><h4>About the {about}</h4><div><p class="lead">{E(f["lead"])}</p>{body}{watch}</div></div></div>
  {video(f)}
  {stills(f)}
  {voices(f)}
  {mood(f)}
  {bts(f)}
  <div class="facts band"><div class="wrap fgrid2">
    <div><h4>Team</h4><ul class="cred">{cred}</ul></div>
    <div>{("<h4>Screenings</h4><ul>"+scr+"</ul>") if scr else ""}{("<h4>Recognition</h4><ul>"+aw+"</ul>") if aw else ""}</div>
  </div></div>
  {f'<div class="laurels">{laur}</div>' if laur else ""}
  <a class="next band" href="#{nxt["slug"]}"><span>Next project</span><b>{E(nxt["title"])}</b>{img(nxt["cover"], "")}</a>
</section>'''

def block(v, bl):
    t = bl[0]; T = v["title"]
    if t == "none": return ""
    fig = lambda n, cls="": f'<figure class="{cls}">{img(n, T)}</figure>'
    if t == "textimg":
        _, n, h, txt, side = bl
        return f'<div class="band"><div class="cs cs-ti {side}"><div class="cs-t"><h4>{E(h)}</h4><p>{E(txt)}</p></div>{fig(n)}</div></div>'
    if t == "kit":
        return f'<div class="band csk"><div class="cs"><figure class="kit">{img(bl[1], T+" – brand kit")}<figcaption>{E(bl[2])}</figcaption></figure></div></div>'
    if t == "palette":
        sw = "".join(f'<div><span style="background:{h}"></span><b>{E(l)}</b><i>{h}</i></div>' for h,l in bl[1])
        return f'<div class="band"><div class="cs"><h4>Colour palette</h4><div class="pal">{sw}</div></div></div>'
    if t == "full":
        return f'<div class="band"><div class="cs">{fig(bl[1],"cs-full")}</div></div>'
    if t in ("pair","trio","quad"):
        return f'<div class="band"><div class="cs cs-{t}">{"".join(fig(n) for n in bl[1])}</div></div>'
    if t == "strip":
        return f'<div class="band"><div class="cs"><h4>{E(bl[1])}</h4><div class="cs-strip">{"".join(fig(n) for n in bl[2])}</div></div></div>'
    if t == "text":
        return f'<div class="band"><div class="cs cs-text"><h4>{E(bl[1])}</h4><p>{E(bl[2])}</p></div></div>'
    if t == "feed":
        _, n, url, handle = bl
        return f'<div class="band csk"><div class="cs cs-feed"><figure>{img(n, T+" – Instagram feed")}</figure><div><h4>Instagram</h4><p>A selection of the feed: posts, carousels and reels.</p><a class="btn" href="{url}" target="_blank" rel="noopener">{handle} ↗</a></div></div></div>'
    if t == "video":
        return f'<div class="band"><div class="cs cs-vid"><video src="{bl[1]}" controls playsinline preload="metadata" poster="{bl[2]}"></video><p class="meta">Artist reel for Instagram, 9:16</p></div></div>'
    if t == "portraits":
        ps = "".join(f'<a href="{u}" target="_blank" rel="noopener"><figure>{img(n, "Portrait of "+nm)}</figure><span>{E(nm)} ↗</span></a>' for n,nm,u in bl[1])
        return f'<div class="band"><div class="cs"><h4>Meet the Artist · portraits</h4><div class="cs-ports">{ps}</div></div></div>'
    if t == "links":
        li = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{E(l)} <span class="ar">↗</span></a></li>' for l,u in bl[2])
        return f'<div class="band"><div class="cs cs-links"><h4>{E(bl[1])}</h4><ul>{li}</ul></div></div>'
    return ""

def vis_view(v, i):
    nxt = VISUAL[(i+1) % len(VISUAL)]
    body = "".join(block(v, bl) for bl in v["blocks"])
    return f"""
<section class="view" id="v-{v["slug"]}" data-title="{E(v["title"])}">
  <div class="vhero"><div class="vh-img">{img(v["cover"], v["title"], eager=True)}</div><div class="vh-t"><a href="#visual-works" class="back">← Visual Works</a><p class="meta">{v["year"]} · {E(v["kind"])}</p><h1>{E(v["title"])}</h1><p class="vlead">{E(v["lead"])}</p><p class="vrole"><i>Role</i>{E(v["role"])}</p></div></div>
  {body}
  <a class="next band" href="#{nxt["slug"]}"><span>Next project</span><b>{E(nxt["title"])}</b>{img(nxt["cover"], "")}</a>
</section>"""

def card(slug, title, year, kind, cover):
    return f'<a class="card" href="#{slug}"><div class="ph">{img(cover, title)}</div><p><b>{E(title)}</b><span>{year} · {E(kind)}</span></p></a>'

film_cards = "".join(card(f["slug"], f["title"], f["year"], f["kind"].split(" · ")[0], f["cover"]) for f in FILMS)
vis_cards = "".join(f'<a class="vw" href="#{v["slug"]}"><figure>{img(v["cover"], v["title"])}</figure><b>{E(v["title"])}</b><span>{E(v["kind"])} · {v["year"]}</span></a>' for v in VISUAL)
def cov(x): c = norm(x["cover"]); return c if "." in c else f"img/{c}.jpg"
index_rows = "".join(f'<a class="irow" href="#{x["slug"]}" data-img="{cov(x)}"><span>{x["year"]}</span><b>{E(x["title"])}</b><i>{E(x["kind"])}</i></a>' for x in sorted(FILMS+VISUAL, key=lambda x: x.get("sort", x["year"]), reverse=True))
routes = ["home","work","visual-works","about","contact","impressum","datenschutz"] + [f["slug"] for f in FILMS] + [v["slug"] for v in VISUAL]
P = lambda ps: "\n      ".join(f"<p>{E(p)}</p>" for p in ps)
H, A = PAGES["home"], PAGES["about"]
tpl = open("template.html", encoding="utf-8").read()
out = (tpl.replace("{{FILM_CARDS}}", film_cards)
          .replace("{{VIS_CARDS}}", vis_cards)
          .replace("{{INDEX_ROWS}}", index_rows)
          .replace("{{FILM_VIEWS}}", "".join(film_view(f,i) for i,f in enumerate(FILMS)))
          .replace("{{VIS_VIEWS}}", "".join(vis_view(v,i) for i,v in enumerate(VISUAL)))
          .replace("{{TABLES}}", awards()+table("Exhibitions &amp; Screenings", EXHIB).replace("</section>", earlier()+"</section>")+table("Press &amp; Features", PRESS))
          .replace("{{HOME_HEADING}}", E(H["heading"])).replace("{{HOME_TEXT}}", P(H["text"]))
          .replace("{{ABOUT_TEXT}}", P(A["text"])).replace("{{ABOUT_NOTE}}", E(A["note"]))
          .replace("{{ABOUT_FACTS}}", "".join(f'<div><h4>{E(k["label"])}</h4><b>{E(k["value"])}</b></div>' for k in A["facts"]))
          .replace("{{ROUTES}}", json.dumps(routes))
          .replace("{{FILMISH}}", json.dumps(["work"]+[f["slug"] for f in FILMS]))
          .replace("{{VISISH}}", json.dumps(["visual-works"]+[v["slug"] for v in VISUAL])))

# output
shutil.rmtree("dist", ignore_errors=True); os.makedirs("dist")
open("dist/index.html","w",encoding="utf-8").write(out)
for d in ("img","media","fonts","admin"):
    if os.path.isdir(d): shutil.copytree(d, f"dist/{d}")
for fn in ("_headers","_redirects","robots.txt","favicon.ico"):
    if os.path.exists(fn): shutil.copy(fn, f"dist/{fn}")
print("ok", len(out), "chars ·", len(FILMS), "films ·", len(VISUAL), "visual works")
