"""Static design-space figure (EN / ZH) generated from the atlas data, so the figure matches the website."""
import json, os, runpy, sys, tempfile, html as H
FIG = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(FIG, "..")
lang = sys.argv[1]; out = sys.argv[2]; NOCAP = 'nocap' in sys.argv
sys_argv = sys.argv; sys.argv = ["build.py", os.path.join(tempfile.gettempdir(), "_unused.html")]
g = runpy.run_path(os.path.join(FIG, "build.py")); sys.argv = sys_argv
ICON, DEFS, CSS = g["ICON"], g["DEFS"], g["CSS"]

D = json.load(open(os.path.join(SITE, "data.json" if lang == "en" else "data_zh.json")))
ICON = {**ICON, **D["icons"]}
dims = {d["id"]: d for d in D["dims"]}  # icons added after build.py (icons_extra.py) live in the data
EX = D["examples"]
KIDS = {c["id"]: [s["id"] for s in c["subs"]] for d in D["dims"] for _, cs in d["groups"] for c in cs}
def exs(i):
    ids = {i, *KIDS.get(i, [])}
    return [e for e in EX if ids & set(e["codes"])]
order = [s["id"] for s in D["sources"]]
def tags(i):
    cnt = {}
    for e in exs(i): cnt[e["src"]] = cnt.get(e["src"], 0) + 1
    t = "".join(f'<span class="tag">{H.escape(s)}{" ×" + str(cnt[s]) if cnt[s] > 1 else ""}</span>' for s in order if s in cnt)
    return f' <span class="tags">{t}</span>' if t else ""
NEW = "new" if lang == "en" else "新增"
nb = lambda c: ""  # the “new” badge was dropped
ic = lambda k: f'<div class="ic">{ICON[k]}</div>' if k and k in ICON else ""

def item(c):
    if not exs(c["id"]): return ""
    subs = [s for s in c["subs"] if exs(s["id"])]
    d = f'<div class="d">{H.escape(c["desc"])}</div>' if c.get("desc") else ""
    left = f'<div class="main"><div class="n">{H.escape(c["name"])}{nb(c)}{"" if subs else tags(c["id"])}</div>{d}</div>'
    if not subs:
        return f'<div class="row">{left}{ic(c.get("icon"))}</div>'
    cells = "".join(f'<div class="sub"><div><span>{H.escape(s["name"])}{nb(s)}</span>{tags(s["id"])}</div>{ic(s.get("icon"))}</div>' for s in subs)
    return f'<div class="row split">{left}<div class="subs">{cells}</div></div>'

def table(parts):
    """One design-space table: concept | dimension | coding, one coding per row.
    parts: (dim id, None for all groups, or [(group index, first item, end item)]);
    a dim or group continued from the other half is marked as such."""
    H3 = ("Concept", "Dimension", "Coding") if lang == "en" else ("概念", "维度", "编码")
    CONT = " (cont.)" if lang == "en" else "（续）"
    body = ""
    for key, sel in parts:
        d = dims[key]
        sel = sel or [(j, 0, None) for j in range(len(d["groups"]))]
        cont = sel[0][:2] != (0, 0)
        q = "" if cont else f'<span class="q">{H.escape(d["q"])}</span>'
        gs = []
        for j, a, b in sel:
            g, cs = d["groups"][j]
            cs = [c for c in cs if exs(c["id"])][a:b]
            if cs: gs.append(((g or "") + (CONT if a else ""), cs))
        n = sum(len(cs) for _, cs in gs)
        if not n: continue
        rows, first = "", True
        for g, cs in gs:
            for k, c in enumerate(cs):
                rows += "<tr>" + (f'<th class="cc" rowspan="{n}"><span class="t" style="box-shadow: inset 0 -5px 0 {d["color"]}55">{H.escape(d["name"])}{CONT if cont else ""}</span>{q}</th>' if first else "") \
                    + (f'<th class="dc" rowspan="{len(cs)}">{H.escape(g)}</th>' if k == 0 else "") + f'<td class="kc">{item(c)}</td></tr>'
                first = False
        body += f"<tbody>{rows}</tbody>"
    return f'<table class="dt"><thead><tr>{"".join(f"<th>{h}</th>" for h in H3)}</tr></thead>{body}</table>'

# one table per column, side by side (self-referential data + base case | decomposition | return & combine)
TABLES = [[(d["id"], None) for d in D["dims"] if d["col"] == k] for k in sorted({d["col"] for d in D["dims"]})]
legend = '<div class="legend">' + "".join(f'<div><span class="tag">{H.escape(s["id"])}</span> {H.escape(s["name"])}</div>' for s in D["sources"]) \
         + f'<div><span class="tag">×n</span> {"number of examples" if lang == "en" else "例子数"}</div></div>'
cap = ("Figure X: A design space for recursion diagrams in three tables. Each recursion concept lists the dimensions along which it is drawn."
       if lang == "en" else "图 X：递归图示的设计空间（三张表）。每个递归概念下列出它的画法维度。")
extra = """
.tags{display:inline-flex;flex-wrap:wrap;gap:3px;margin-left:6px;vertical-align:1px;font-weight:400}
.tag{font-size:10.5px!important;padding:2px 5px!important}
.row{min-height:0!important;padding:6px 12px!important}
.sub{min-height:0!important;padding:4px 10px!important;font-size:14.5px!important}
.row.split{padding:0!important}.row.split>.main{padding:7px 12px!important;flex:0 0 190px!important}
.n{font-size:15.5px!important}.d{font-size:12.5px!important;margin-top:1px!important}
.ic svg{width:88px;height:42px}
.grp{padding:4px 12px!important;font-size:11px!important}
h2{font-size:22px!important;margin-bottom:6px!important}
.col{gap:16px!important}.cols{gap:26px!important}
body{padding:22px 26px 14px!important}
.tag{font-style:normal;font-size:12px;font-weight:600;line-height:1;padding:3px 7px;border:1px solid #9AA0A8;border-radius:9px;color:#3B4048;background:#fff;white-space:nowrap}
.new{font-size:11px;font-weight:700;color:#fff;background:#C8692F;border-radius:4px;padding:1px 5px;vertical-align:middle;font-style:normal}
.legend{width:100%;margin:14px 0 0;grid-template-columns:repeat(5,auto)!important;justify-content:start;font-size:12.5px!important;display:grid;grid-template-columns:repeat(3,1fr);gap:8px 20px;font-size:14px;color:#3B4048}
.legend div{display:flex;align-items:center;gap:8px}
.halves{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.3fr) minmax(0,1fr);gap:20px;align-items:start}
.subs,.sub>div{min-width:0}.sub .tags{flex-wrap:wrap}
.dt{width:100%;border-collapse:collapse;border:1.5px solid #1C2128;border-top:4px solid #1C2128}
.dt thead th{text-align:left;padding:7px 12px;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:#6B717A;font-weight:600;border-bottom:1.5px solid #1C2128}
.dt tbody{border-top:2.5px solid #1C2128}
.dt th.cc,.dt th.dc{vertical-align:top;text-align:left;border-right:1px solid #1C2128;border-top:1px solid #1C2128}
.dt th.cc{width:112px;padding:10px 10px}
.dt th.cc .t{font-size:18px;font-weight:700}
.dt th.cc .q{display:block;margin-top:6px;font-size:12px;font-weight:400;color:#6B717A;line-height:1.35}
.dt th.dc{width:78px;padding:10px 8px;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:#6B717A;font-weight:600}
.dt td.kc{padding:0;border-top:1px solid #1C2128}
.dt td.kc .row{border-bottom:none}
.dt .sub:last-child{border-bottom:none}
.row.split>.main{flex:0 0 140px!important}
"""
if lang == "zh":
    extra += "body{font-family:Inter,'Noto Sans CJK SC',sans-serif}.cap{font-family:'Noto Serif CJK SC','Noto Sans CJK SC',serif}.sub{font-style:normal}"
page = f'''<!doctype html><html lang="{'en' if lang == 'en' else 'zh-CN'}"><head><meta charset="utf-8"><style>{CSS}{extra}</style></head><body>{DEFS}
<div class="halves">{"".join(table(t) for t in TABLES)}</div>{legend}
{'' if 'nocap' in sys.argv else f'<div class="cap">{cap}</div>'}</body></html>'''
open(out, "w").write(page)
print("wrote", out)
