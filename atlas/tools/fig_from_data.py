"""Static design-space figure (EN / ZH) generated from the atlas data, so the figure matches the website."""
import json, os, runpy, sys, html as H
FIG = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(FIG, "..", "site")
lang = sys.argv[1]; out = sys.argv[2]; NOCAP = 'nocap' in sys.argv
sys_argv = sys.argv; sys.argv = ["build.py", "/tmp/claude-0/_unused.html"]
g = runpy.run_path(os.path.join(FIG, "build.py")); sys.argv = sys_argv
ICON, DEFS, CSS = g["ICON"], g["DEFS"], g["CSS"]

D = json.load(open(os.path.join(SITE, "data.json" if lang == "en" else "data_zh.json")))
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
nb = lambda c: f' <span class="new">{NEW}</span>' if c.get("new") else ""
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

def section(d, cls=""):
    body = ""
    for gname, cs in d["groups"]:
        inner = "".join(item(c) for c in cs)
        if inner: body += (f'<div class="grp">{H.escape(gname)}</div>' if gname else "") + inner
    return f'<div class="sec"><h2><span style="box-shadow: inset 0 -5px 0 {d["color"]}55">{H.escape(d["name"])}</span></h2><div class="box{cls}">{body}</div></div>'

dims = {d["id"]: d for d in D["dims"]}
# code correspondence as a two-column block
code_items = [c for _, cs in dims["code"]["groups"] for c in cs if exs(c["id"])]
code = "".join(f'<div class="crow"><div class="n">{H.escape(c["name"])}</div><div class="d">{H.escape(c["desc"])}</div>{tags(c["id"])}</div>' for c in code_items)
codesec = f'<div class="sec"><h2><span style="box-shadow: inset 0 -5px 0 {dims["code"]["color"]}55">{H.escape(dims["code"]["name"])}</span></h2><div class="box"><div class="bottom">{code}</div></div></div>'
legend = '<div class="legend">' + "".join(f'<div><span class="tag">{H.escape(s["id"])}</span> {H.escape(s["name"])}</div>' for s in D["sources"]) \
         + f'<div><span class="new">{NEW}</span> {"coding found only in the LeetCode set" if lang == "en" else "只在 LeetCode 中出现的编码"}</div>' \
         + f'<div><span class="tag">×n</span> {"number of examples" if lang == "en" else "例子数"}</div></div>'
cap = ("Figure X: A design space for recursion diagrams, listing the possible codings for each of the eight dimensions."
       if lang == "en" else "图 X：递归图示的设计空间，列出八个维度下可能的编码。")
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
"""
if lang == "zh":
    extra += "body{font-family:Inter,'Noto Sans CJK SC',sans-serif}.cap{font-family:'Noto Serif CJK SC','Noto Sans CJK SC',serif}.sub{font-style:normal}"
page = f'''<!doctype html><html lang="{'en' if lang == 'en' else 'zh-CN'}"><head><meta charset="utf-8"><style>{CSS}{extra}</style></head><body>{DEFS}
<div class="cols">
<div class="col">{section(dims["concepts"])}{section(dims["node"])}{section(dims["code"])}</div>
<div class="col">{section(dims["visual"])}{section(dims["flow"])}</div>
<div class="col">{section(dims["annot"])}{section(dims["elision"])}{section(dims["subd"])}</div>
</div>{legend}
{'' if 'nocap' in sys.argv else f'<div class="cap">{cap}</div>'}</body></html>'''
open(out, "w").write(page)
print("wrote", out)
