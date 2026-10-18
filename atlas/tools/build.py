"""Builds a Figure-9-style design-space figure for recursion diagrams (HTML -> PNG/PDF)."""
import sys

OR, ORF = "#C8692F", "#F8D6BF"      # visual encodings
BL, BLF = "#2F64B0", "#CFE0F6"      # annotations
PK = "#D0469B"                      # elision
PU, PUF = "#7E6BD0", "#E2DCFA"      # subdiagrams
GR, GRF = "#23826A", "#CDEDE3"      # flow
GY = "#8A8F98"
INK = "#1E2329"

def svg(body, w=118, h=56):
    return f'<svg viewBox="0 0 {w} {h}" width="{w*1.35:.0f}" height="{h*1.35:.0f}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'

def nd(x, y, s=13, c=OR, f=ORF, sw=1.6):
    return f'<rect x="{x-s/2}" y="{y-s/2}" width="{s}" height="{s}" rx="4" fill="{f}" stroke="{c}" stroke-width="{sw}"/>'

def ln(x1, y1, x2, y2, c=OR, sw=1.4, dash="", arrow=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{arrow})"' if arrow else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{sw}"{d}{m}/>'

def tx(x, y, t, c=OR, s=11, anchor="middle", mono=False, w=500):
    fam = "DejaVu Sans Mono" if mono else "Inter"
    return f'<text x="{x}" y="{y}" fill="{c}" font-size="{s}" font-family="{fam}" font-weight="{w}" text-anchor="{anchor}">{t}</text>'

DEFS = f'''<svg width="0" height="0" style="position:absolute"><defs>
<marker id="aO" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{OR}"/></marker>
<marker id="aG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{GR}"/></marker>
<marker id="aB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{BL}"/></marker>
<marker id="aP" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{PU}"/></marker>
</defs></svg>'''

# a small 5-node tree used by several icons
T = dict(r=(59, 9), a=(38, 29), b=(80, 29), c=(26, 48), d=(50, 48))
def tree(c=OR, f=ORF, edges_c=None, hi=None, hic=BL, hif=BLF, arrow="", up=False):
    ec = edges_c or c
    out = ""
    for p, q in [("r", "a"), ("r", "b"), ("a", "c"), ("a", "d")]:
        (x1, y1), (x2, y2) = T[p], T[q]
        if up:
            x1, y1, x2, y2 = x2, y2, x1, y1
        # shorten toward the target node
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5
        k = 8 / L
        out += ln(x1 + dx * k, y1 + dy * k, x2 - dx * k, y2 - dy * k, ec, arrow=arrow)
    for k, (x, y) in T.items():
        if hi and k in hi:
            out += nd(x, y, c=hic, f=hif, sw=2)
        else:
            out += nd(x, y, c=c, f=f)
    return out

def dots(x, y, c=PK):
    return (f'<rect x="{x-9}" y="{y-4}" width="18" height="8" rx="4" fill="#F7D3EA"/>'
            + "".join(f'<circle cx="{x-5+i*5}" cy="{y}" r="1.4" fill="{c}"/>' for i in range(3)))

ICON = {}
# ---------- visual encodings ----------
ICON["boxbox"] = svg(f'<rect x="20" y="6" width="78" height="44" rx="6" fill="none" stroke="{OR}" stroke-width="1.6"/>'
                     f'<rect x="32" y="14" width="58" height="28" rx="5" fill="none" stroke="{OR}" stroke-width="1.6"/>'
                     f'<rect x="44" y="21" width="38" height="14" rx="4" fill="{ORF}" stroke="{OR}" stroke-width="1.6"/>')
ICON["brackets"] = svg(tx(59, 34, "f(a(b(c)))", OR, 14, mono=True))
ICON["treemap"] = svg(f'<rect x="18" y="6" width="82" height="44" rx="4" fill="none" stroke="{OR}" stroke-width="1.6"/>'
                      + ln(59, 6, 59, 50) + ln(59, 28, 100, 28) + ln(80, 28, 80, 50)
                      + f'<rect x="83" y="31" width="14" height="16" rx="2" fill="{ORF}"/>')
ICON["calltree"] = svg(tree() + tx(59, 12.5, "f", OR, 8.5, w=700))
ICON["statetree"] = svg(tree() + tx(59, 12.5, "5", OR, 8.5, w=700) + tx(38, 32.5, "4", OR, 8.5, w=700) + tx(80, 32.5, "3", OR, 8.5, w=700))
ICON["choicetree"] = svg(tree() + tx(42, 18, "+", OR, 11, w=700) + tx(77, 18, "−", OR, 11, w=700))
ICON["chain"] = svg(nd(24, 28) + ln(32, 28, 46, 28, arrow="aO") + nd(55, 28) + ln(63, 28, 77, 28, arrow="aO") + nd(86, 28)
                    + tx(104, 32, "∅", OR, 12))
ICON["stack"] = svg("".join(f'<rect x="38" y="{8+i*11}" width="42" height="9" rx="3" fill="{ORF if i==0 else "none"}" stroke="{OR}" stroke-width="1.5"/>' for i in range(4)))
ICON["subst"] = svg("".join(ln(24, 7 + i * 7, 24 + w, 7 + i * 7, OR, 2.2) for i, w in enumerate([20, 38, 58, 72, 52, 30, 12])))
ICON["indent"] = svg("".join(ln(20 + i * 12, 9 + i * 9, 62 + i * 12, 9 + i * 9, OR, 2.2) for i in range(5)))
ICON["table"] = svg("".join(f'<rect x="{30+c*20}" y="{10+r*14}" width="16" height="11" rx="3" fill="none" stroke="{OR}" stroke-width="1.5"/>' for r in range(3) for c in range(3))
                    + tx(22, 19, "1", OR, 9) + tx(22, 33, "2", OR, 9) + tx(22, 47, "3", OR, 9))
ICON["doll"] = svg("".join(f'<ellipse cx="{30+i*22}" cy="{30+i*3}" rx="{12-i*2.4}" ry="{18-i*3.4}" fill="{ORF if i==0 else "none"}" stroke="{OR}" stroke-width="1.5"/>' for i in range(4)))

# ---------- flow ----------
def ftree(arrow="aG", up=False, c=GR, f=GRF):
    return tree(c=c, f=f, arrow=arrow, up=up)
ICON["static"] = svg(tree(c=GR, f=GRF))
ICON["down"] = svg(ftree())
ICON["up"] = svg(ftree(up=True))
ICON["round"] = svg(ftree() + f'<path d="M86 24 Q100 12 70 8" fill="none" stroke="{GR}" stroke-width="1.4" stroke-dasharray="3 2" marker-end="url(#aG)"/>'
                    + f'<path d="M20 44 Q14 30 30 26" fill="none" stroke="{GR}" stroke-width="1.4" stroke-dasharray="3 2" marker-end="url(#aG)"/>')
ICON["rewrite"] = svg(tx(14, 16, "f(3)", GR, 10, "start", True) + tx(14, 30, "⇒ 3·f(2)", GR, 10, "start", True) + tx(14, 44, "⇒ 3·2·f(1)", GR, 10, "start", True) + tx(14, 56, "⇒ 6", GR, 10, "start", True), h=60)

# ---------- annotations ----------
ICON["base"] = svg(tree(hi=["c", "d", "b"]) + tx(26, 51, "Δ", BL, 8, w=700) + tx(50, 51, "Δ", BL, 8, w=700) + tx(80, 32, "Δ", BL, 8, w=700))
ICON["retval"] = svg(nd(36, 12) + nd(36, 46) + ln(36, 20, 36, 38) + f'<path d="M48 42 Q60 29 48 16" fill="none" stroke="{BL}" stroke-width="1.6" marker-end="url(#aB)"/>'
                     + tx(76, 33, "= 8", BL, 12, w=700))
ICON["prune"] = svg(tree(hi=["d"]) + tx(50, 52, "×", BL, 12, w=700) + tx(98, 22, "×", BL, 11, w=700) + tx(104, 22, "fail", BL, 9, "start"), w=130)
ICON["role"] = svg(nd(24, 28, c=OR, f=ORF) + nd(44, 28, c=GR, f=GRF, sw=2) + nd(64, 28, c=OR, f=ORF) + nd(84, 28, c=BL, f=BLF, sw=2)
                   + tx(44, 50, "pivot", GR, 9) + tx(84, 50, "done", BL, 9))
ICON["cursor"] = svg("".join(f'<rect x="{18+i*18}" y="10" width="14" height="14" rx="3" fill="{BLF if i in (1,2,3) else "none"}" stroke="{BL if i in (1,2,3) else GY}" stroke-width="1.5"/>' for i in range(5))
                     + ln(43, 46, 43, 29, BL, 1.5, arrow="aB") + ln(79, 46, 79, 29, BL, 1.5, arrow="aB") + tx(43, 55, "i", BL, 9) + tx(79, 55, "j", BL, 9), h=58)
ICON["choicelab"] = svg(tree() + tx(40, 17, "take", BL, 8.5, "end", w=600) + tx(78, 17, "skip", BL, 8.5, "start", w=600))
ICON["dup"] = svg(f'<ellipse cx="30" cy="34" rx="20" ry="18" fill="none" stroke="{BL}" stroke-width="1.5" stroke-dasharray="3 2"/>'
                  + nd(30, 26) + nd(22, 44, 10) + nd(38, 44, 10) + ln(28, 32, 23, 39) + ln(32, 32, 37, 39)
                  + f'<ellipse cx="88" cy="34" rx="20" ry="18" fill="none" stroke="{BL}" stroke-width="1.5" stroke-dasharray="3 2"/>'
                  + nd(88, 26) + nd(80, 44, 10) + nd(96, 44, 10) + ln(86, 32, 81, 39) + ln(90, 32, 95, 39) + tx(59, 38, "=", BL, 14, w=700))
ICON["path"] = svg(tree() + f'<path d="M50 6 Q30 16 18 44 Q22 58 34 50 Q38 40 46 52 Q58 58 52 38 Q62 30 72 34 Q90 44 90 30 Q86 14 66 6" fill="none" stroke="{BL}" stroke-width="1.4" stroke-dasharray="2 2"/>')

# ---------- node content ----------
ICON["n_data"] = svg(tx(59, 33, "[1, 4, 3]", OR, 13, mono=True))
ICON["n_call"] = svg(tx(59, 33, "fib 3", OR, 13, mono=True))
ICON["n_state"] = svg(tx(59, 33, "(i, k)", OR, 13, mono=True))
ICON["n_partial"] = svg(tx(59, 33, "(* 6 (f 5))", OR, 12, mono=True))
ICON["n_sym"] = svg(tx(59, 33, "f(n/b)", OR, 14, w=500).replace('font-family="Inter"', 'font-family="DejaVu Serif" font-style="italic"'))

# ---------- elision ----------
ICON["full"] = svg(tree(c=GY, f="#EEEFF1"))
ICON["unpat"] = svg(nd(20, 28, c=GY, f="none") + nd(40, 28, c=GY, f="none") + dots(62, 28) + nd(86, 28, c=GY, f="none"))
ICON["pattern"] = svg(nd(20, 28, c=GY, f="#D5D8DD") + nd(38, 28, c=GY, f="none") + nd(56, 28, c=GY, f="#D5D8DD") + nd(74, 28, c=GY, f="none") + dots(96, 28))
ICON["blackbox"] = svg(tree(c=GY, f="#EEEFF1").replace("", "") + f'<rect x="19.5" y="41.5" width="13" height="13" rx="2" fill="{INK}"/><rect x="43.5" y="41.5" width="13" height="13" rx="2" fill="{INK}"/>')
ICON["deferred"] = svg(f'<rect x="16" y="10" width="86" height="36" rx="6" fill="none" stroke="{GY}" stroke-width="1.5"/>'
                       + tx(59, 33, "f(rest…)", GY, 12, mono=True) + dots(96, 46))

# ---------- subdiagrams ----------
ICON["multirep"] = svg(tx(18, 16, "(cons 1", PU, 9, "start", True) + tx(24, 28, "(cons 2", PU, 9, "start", True) + tx(30, 40, "'()))", PU, 9, "start", True)
                       + f'<rect x="78" y="10" width="30" height="36" rx="4" fill="none" stroke="{PU}" stroke-width="1.5"/><rect x="85" y="20" width="16" height="18" rx="3" fill="{PUF}" stroke="{PU}" stroke-width="1.5"/>')
def mini(x, y, c=PU, f=PUF, which=None):
    pts = [(x, y), (x - 12, y + 18), (x + 12, y + 18)]
    o = ln(x - 3, y + 5, x - 9, y + 13, c) + ln(x + 3, y + 5, x + 9, y + 13, c)
    for i, (a, b) in enumerate(pts):
        o += f'<circle cx="{a}" cy="{b}" r="5" fill="{f if which == i else "white"}" stroke="{c}" stroke-width="1.5"/>'
    return o
ICON["multiscen"] = svg(tx(14, 30, "a", PU, 11) + mini(38, 14, which=1) + tx(70, 30, "b", PU, 11) + mini(94, 14, which=2))
ICON["overtime"] = svg(mini(28, 14, which=0) + ln(48, 26, 66, 26, PU, 1.5, arrow="aP") + mini(88, 14, which=1))

# ---------- layout ----------
def section(title, color, body):
    return f'<div class="sec"><h2><span style="box-shadow: inset 0 -5px 0 {color}55">{title}</span></h2><div class="box">{body}</div></div>'

def tags(src):
    if not src:
        return ""
    out = "".join(f'<span class="tag{" ours" if s == "Ours" else ""}{" unsure" if s.endswith("?") else ""}{" lc" if s.startswith("LC×") else ""}{" lccn" if s == "LC-cn" else ""}">{s}</span>' for s in src.split(","))
    return f'<div class="tags">{out}</div>'

def row(name, desc, icon=None, subs=None, src=""):
    ic = f'<div class="ic">{ICON[icon]}</div>' if icon else ""
    d = f'<div class="d">{desc}</div>' if desc else ""
    left = f'<div class="main"><div class="n">{name}</div>{d}{tags(src)}</div>'
    if subs:
        s = "".join(f'<div class="sub"><div><span>{sn}</span>{tags(ss)}</div>{"<div class=ic>"+ICON[si]+"</div>" if si else ""}</div>' for sn, si, ss in subs)
        return f'<div class="row split">{left}<div class="subs">{s}</div></div>'
    return f'<div class="row">{left}{ic}</div>'

def crow(name, subs, src=""):
    s = "".join(f'<div class="csub"><span>{x}</span>{tags(xs)}</div>' for x, xs in subs)
    return f'<div class="row split"><div class="main"><div class="n">{name}</div></div><div class="subs">{s}</div></div>' if subs else f'<div class="row"><div class="main"><div class="n">{name}</div>{tags(src)}</div></div>'

# --- new icons for codings found in the LeetCode vote>=5 set ---
ICON["rewire"] = svg(nd(22, 38) + nd(59, 38) + nd(96, 38) + ln(30, 38, 50, 38, OR, 1.2, "2 2")
                     + f'<path d="M24 29 Q59 0 92 29" fill="none" stroke="{OR}" stroke-width="1.5" marker-end="url(#aO)"/>'
                     + f'<path d="M53 46 Q40 56 28 46" fill="none" stroke="{OR}" stroke-width="1.5" marker-end="url(#aO)"/>')
ICON["resulttree"] = svg(f'<circle cx="59" cy="10" r="7" fill="{ORF}" stroke="{OR}" stroke-width="1.5"/>' + tx(59, 13.5, "×", OR, 10, w=700)
                         + ln(53, 15, 41, 25) + ln(65, 15, 77, 25)
                         + f'<circle cx="38" cy="30" r="7" fill="{ORF}" stroke="{OR}" stroke-width="1.5"/>' + tx(38, 33.5, "−", OR, 10, w=700)
                         + tx(80, 34, "5", OR, 11, w=700) + ln(33, 35, 26, 44) + ln(43, 35, 50, 44) + tx(24, 53, "2", OR, 11, w=700) + tx(52, 53, "3", OR, 11, w=700))
ICON["partition"] = svg(f'<rect x="8" y="20" width="22" height="18" rx="4" fill="none" stroke="{OR}" stroke-dasharray="3 2" stroke-width="1.3"/>'
                        + nd(19, 29, 11) + nd(42, 29, 13, c=BL, f=BLF, sw=2)
                        + f'<rect x="54" y="20" width="58" height="18" rx="4" fill="none" stroke="{OR}" stroke-dasharray="3 2" stroke-width="1.3"/>'
                        + nd(65, 29, 11) + nd(83, 29, 11) + nd(101, 29, 11) + tx(19, 52, "left", OR, 9) + tx(83, 52, "right", OR, 9))
ICON["mapping"] = svg("".join(nd(16 + i * 18, 14, 11) for i in range(6)) + "".join(nd(34 + i * 18, 46, 11) for i in range(4))
                      + "".join(ln(34 + i * 18, 40, 52 + i * 18, 21, OR, 1.2, arrow="aO") for i in range(4))
                      + tx(112, 17, "n", OR, 9, "start") + tx(112, 49, "n−1", OR, 9, "start"), w=130)
ICON["donebox"] = svg(nd(16, 28) + ln(24, 28, 38, 28, GY, 1.4) + f'<rect x="40" y="16" width="70" height="24" rx="5" fill="#E9EAEC" stroke="{GY}" stroke-width="1.5"/>'
                      + tx(75, 32, "done", GY, 11, w=600))
ICON["callstep"] = svg(nd(18, 16, 11) + ln(24, 16, 34, 16) + nd(40, 16, 11) + f'<rect x="58" y="9" width="44" height="14" rx="3" fill="{BLF}" stroke="{BL}"/>' + tx(80, 19.5, "call 1", BL, 9, w=600)
                       + nd(18, 42, 11) + ln(24, 42, 34, 42) + nd(40, 42, 11) + f'<rect x="58" y="35" width="44" height="14" rx="3" fill="{BLF}" stroke="{BL}"/>' + tx(80, 45.5, "call 2", BL, 9, w=600))

N = "<span class='new'>new</span>"
concepts = (
    '<div class="grp">Structure</div>'
    + crow("Self-referential data", [("List", "DCIC,HtDP"), ("Tree", "MIT 6.102"), ("Nested doll", "HtDP")])
    + crow("Decomposition", [("Structural", "HtDP,LC×2"), ("Generative", "HtDP,LYAH,LC×4")])
    + crow("Base case", [("Edge condition", "LYAH,LC×3"), ("Pruned leaf", "LC-cn,LC×1")])
    + crow("Leap of faith " + N, [], "LC×5")
    + '<div class="grp">Process</div>'
    + crow("Return &amp; combine", [("Value return", "RV,LC×8"), ("Result composition", "SICP,LC-cn,LC×3")])
    + crow("Choice / search", [("Branching", "LC-cn,LC×4"), ("Pruning", "LC-cn,LC×2"), ("Backtracking", "LC-cn")])
    + crow("Overlapping subproblems", [], "LC-cn,LC×2")
    + crow("Execution state", [("Call stack", "LC-cn,LC×2"), ("Accumulator", "Ours")])
    + crow("Cost", [("Per level", "CLRS"), ("Total", "CLRS,LC×1")])
)
node = (
    row("Concrete data", "Values of the input itself.", "n_data", src="MIT 6.102,HtDP,LC×15")
    + row("Call with arguments", "The call as written, concrete args.", "n_call", src="SICP,RV,LC×4")
    + row("State tuple", "Only the changing parameters.", "n_state", src="LC-cn,LC×3")
    + row("Partial expression", "Half-evaluated term, as in a trace.", "n_partial", src="SICP,HtDP,LC×2")
    + row("Symbolic", "Parametric size, as in a recurrence.", "n_sym", src="CLRS,LC×1")
)
visual = (
    row("Nested containment", "Calls drawn inside their caller.", subs=[("Box-in-box", "boxbox", "HtDP"), ("Brackets", "brackets", "LYAH,LC×2"), ("Treemap", "treemap", "Ours")])
    + row("Tree (node-link)", "Calls linked to their subcalls.", subs=[("Call tree", "calltree", "SICP,VisuAlgo,LC×3"), ("State tree", "statetree", "LC-cn,LC×2"), ("Choice tree", "choicetree", "LC-cn,LC×1"), ("Result tree " + N, "resulttree", "LC×6")])
    + row("Linear chain", "List of nodes and links.", subs=[("Box-and-pointer", "chain", "HtDP,LC×2"), ("Pointer rewiring " + N, "rewire", "LC×9")])
    + row("Stack", "Frames piled up by depth.", "stack", src="LC-cn,LC×2")
    + row("Substitution trace", "Expression rewritten until a value.", "subst", src="SICP,HtDP,LC×1")
    + row("Indentation staircase", "Depth shown by indentation.", "indent", src="DCIC,HtDP,LC×1")
    + row("Table", "Args, intermediates and results.", "table", src="HtDP,LC×1")
    + row("Partition " + N, "Input split into boxed parts.", "partition", src="LC×3")
    + row("Instance mapping " + N, "Size n aligned to size n−1.", "mapping", src="LC×3")
    + row("Metaphor / pictorial", "Dolls, mirrors, spirals.", "doll", src="LYAH,HtDP,LC×1")
)
flow = (
    row("Static", "Structure only, no direction.", "static", src="HtDP,DCIC,LC×5")
    + row("Downward only", "Calls drawn, returns omitted.", "down", src="VisuAlgo,LC-cn,LC×2")
    + row("Upward only", "Results merging toward the root.", "up", src="HtDP?,LC×1")
    + row("Round trip", "Down to the base case, then back up.", "round", src="SICP,RV,LC×7")
    + row("Rewrite in place", "Time runs down the lines.", "rewrite", src="SICP,HtDP")
)
annot = (
    row("Base-case marker", "Marks where recursion stops.", "base", src="LC-cn,LC×4")
    + row("Return value", "Value written on the way back.", "retval", src="RV,LC-cn,LC×6")
    + row("Prune / fail + legend", "Dead branches, keyed in a legend.", "prune", src="LC-cn,LC×3")
    + row("Role colour", "Colour by role (pivot, done).", "role", src="LYAH,LC×3")
    + row("Cursor / pointer", "Indices into the data.", "cursor", src="LC-cn,LC×6")
    + row("Choice label", "The decision named on the edge.", "choicelab", src="LC-cn,LC×3")
    + row("Call-step label " + N, "Each frame or step numbered.", "callstep", src="LC×3")
    + row("Duplicate marker", "Repeated subproblems circled.", "dup", src="LC-cn,LC×1")
    + row("Traversal path", "Evaluation order traced.", "path", src="SICP,LC-cn,LC×1")
)
elis = (
    row("Full expansion", "Small input, every call drawn.", "full", src="SICP,VisuAlgo,LC×2")
    + row("Unpatterned elision", "No inference can be made.", "unpat", src="LC-cn,LC×1")
    + row("Patterned elision", "Rule implied by a few levels.", "pattern", src="CLRS")
    + row("Black-box leaf", "Leaves drawn as opaque blocks.", "blackbox", src="LC-cn")
    + row("Deferred call", "Subcall left unexpanded.", subs=[("Trace term", "deferred", "HtDP"), ("Done box " + N, "donebox", "LC×3")])
)
subd = (
    row("Multiple representations", "Same recursion, two encodings.", "multirep", src="HtDP,LC×3")
    + row("Multiple scenarios", "Cases of one step side by side.", "multiscen", src="LC-cn,LC×6")
    + row("Over time", "Snapshots of one run.", "overtime", src="HtDP,LC-cn,Ours,LC×13")
)
code = "".join(f'<div class="crow"><div class="n">{a}</div><div class="d">{b}</div>{tags(s)}</div>' for a, b, s in [
    ("Diagram is code", "Trace written in the program’s own syntax.", "SICP,HtDP,DCIC"),
    ("Side by side", "Diagram placed next to the code or rule.", "LYAH,SICP,LC×5"),
    ("Arrows into code", "Arrows tie parts of the diagram to code.", "HtDP,LC×1"),
    ("Shared identifiers", "Function and parameter names reused in nodes.", "SICP,RV,LC×3"),
    ("Recurrence only", "Linked to an equation, not to code.", "CLRS,LC×2"),
    ("Prose only", "Linked through a written explanation.", "LC-cn,LC×2"),
])
LEGEND = [("LYAH", "Learn You a Haskell"), ("SICP", "Structure and Interpretation of Computer Programs"), ("HtDP", "How to Design Programs"),
          ("DCIC", "A Data-Centric Introduction to Computing"), ("CLRS", "Introduction to Algorithms"), ("MIT 6.102", "MIT 6.102 course notes"),
          ("VisuAlgo", "visualgo.net"), ("RV", "recursionvisualizer.com"), ("Ours", "our own sketches"),
          ("LC-cn", "LeetCode.cn, hand-picked solutions"), ("LC×n", "LeetCode, vote ≥ 5: n of 32 solutions")]
legend = ('<div class="legend">' + "".join(f'<div><span class="tag{" ours" if a == "Ours" else ""}{" lc" if a.startswith("LC×") else ""}{" lccn" if a == "LC-cn" else ""}">{a}</span> {b}</div>' for a, b in LEGEND)
          + '<div><span class="tag unsure">X?</span> example to confirm</div><div><span class="new">new</span> coding found only in the LeetCode set</div></div>')

CSS = f'''
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#fff;color:{INK};font-family:Inter,sans-serif;width:1800px;padding:28px 32px 20px}}
.cols{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:34px}}
.col{{display:flex;flex-direction:column;gap:22px}}
.col+.col{{}}
h2{{font-size:25px;font-weight:600;margin-bottom:8px}}
.box{{border:1.5px solid {INK};border-top:4px solid {INK}}}
.row{{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid {INK};padding:9px 14px;min-height:72px;gap:10px}}
.row:last-child{{border-bottom:none}}
.n{{font-weight:700;font-size:17px}}
.d{{font-size:13.5px;color:#3B4048;margin-top:3px;line-height:1.3}}
.row.split{{padding:0;align-items:stretch}}
.row.split>.main{{padding:10px 14px;flex:0 0 205px}}
.subs{{flex:1;display:flex;flex-direction:column;border-left:1px solid {INK}}}
.sub{{display:flex;align-items:center;justify-content:space-between;padding:5px 12px;background:#F4F4F4;border-bottom:1px solid {INK};font-style:italic;font-size:16px;min-height:64px}}
.sub:last-child{{border-bottom:none}}
.csub{{padding:8px 14px;background:#F4F4F4;border-bottom:1px solid {INK};font-style:italic;font-size:16px}}
.csub:last-child{{border-bottom:none}}
.grp{{padding:7px 14px;font-size:13px;letter-spacing:1.5px;text-transform:uppercase;color:#6B717A;border-bottom:1px solid {INK};background:#fff;font-weight:600}}
.ic{{flex:0 0 auto;display:flex}}
.crow{{padding:9px 14px;border-bottom:1px solid {INK}}}
.crow:last-child{{border-bottom:none}}
.bottom{{display:grid;grid-template-columns:1fr 1fr;gap:0}}
.bottom .crow:nth-child(odd){{border-right:1px solid {INK}}}
.bottom .crow:nth-last-child(-n+2){{border-bottom:none}}
.cap{{margin-top:22px;text-align:center;font-family:'DejaVu Serif',serif;font-weight:700;font-size:19px}}
.tags{{display:flex;flex-wrap:wrap;gap:4px;margin-top:5px}}
.sub .tags{{margin-top:4px}}
.csub{{display:flex;align-items:center;justify-content:space-between;gap:8px}}
.csub .tags{{margin-top:0}}
.tag{{font-style:normal;font-size:12px;font-weight:600;line-height:1;padding:3px 7px;border:1px solid #9AA0A8;border-radius:9px;color:#3B4048;background:#fff;white-space:nowrap}}
.tag.lc{{background:#FCE3C4;border-color:#C8692F;color:#7A3A0E}}
.tag.lccn{{background:#FFF4E6;border-color:#C8692F;color:#7A3A0E}}
.new{{font-size:11px;font-weight:700;color:#fff;background:#C8692F;border-radius:4px;padding:1px 5px;vertical-align:middle;font-style:normal}}
.tag.ours{{border-style:dashed;font-style:italic}}
.tag.unsure{{border-style:dotted;color:#8A8F98}}
.legend{{width:1100px;margin:16px auto 0;display:grid;grid-template-columns:repeat(3,1fr);gap:8px 20px;font-size:14px;color:#3B4048}}
.legend div{{display:flex;align-items:center;gap:8px}}
hr{{border:none;border-top:1px solid #C9CCD1;margin:26px 0 20px}}
'''

html = f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{DEFS}
<div class="cols">
<div class="col">{section("Concepts", "#8A8F98", concepts)}{section("Node Content", "#C8692F", node)}</div>
<div class="col">{section("Visual Encodings", "#C8692F", visual)}{section("Flow Direction", "#23826A", flow)}</div>
<div class="col">{section("Annotations", "#2F64B0", annot)}{section("Elision", "#D0469B", elis)}{section("Subdiagrams", "#7E6BD0", subd)}</div>
</div>
<hr>
<div style="width:1100px;margin:0 auto">{section("Code Correspondence", "#3E8E3E", '<div class="bottom">' + code + '</div>')}</div>
{legend}
<div class="cap">Figure X: A design space for recursion diagrams, listing the possible codings for each of the eight dimensions.</div>
</body></html>'''

open(sys.argv[1], "w").write(html)
