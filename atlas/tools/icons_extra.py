"""Icons for the codings that had none, drawn with the helpers in build.py. Updates data.json in place."""
import json, os, runpy, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv; sys.argv = ["build.py", os.path.join(tempfile.gettempdir(), "_unused.html")]
g = runpy.run_path(os.path.join(HERE, "build.py")); sys.argv = argv
svg, nd, ln, tx, tree = g["svg"], g["nd"], g["ln"], g["tx"], g["tree"]
OR, ORF, BL, BLF, PK, GR, GRF, GY = (g[k] for k in ("OR", "ORF", "BL", "BLF", "PK", "GR", "GRF", "GY"))

def lines(x, y, widths, c, sw=2.2, step=7):
    return "".join(ln(x, y + i * step, x + w, y + i * step, c, sw) for i, w in enumerate(widths))
def centred(widths, c, y=7, step=7):
    return "".join(ln(59 - w / 2, y + i * step, 59 + w / 2, y + i * step, c, 2.2) for i, w in enumerate(widths))
def box(x, y, w, h, c, f="none", dash="", rx=4):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}" stroke="{c}" stroke-width="1.5"{d}/>'

NEW = {
 # decomposition: trusted subcall
 "leap": svg(nd(20, 28) + ln(28, 28, 44, 28, OR) + box(46, 16, 56, 24, PK, "#FBE3F1", "3 2") + tx(74, 32, "trust", PK, 10, w=600)),
 # self-referential data
 "sr_list": svg(box(22, 14, 64, 26, OR) + ln(54, 14, 54, 40, OR) + tx(38, 31, "first", OR, 9) + tx(70, 31, "rest", OR, 9)
                + f'<path d="M70 40 Q70 52 42 52 Q14 52 16 30" fill="none" stroke="{OR}" stroke-width="1.4" marker-end="url(#aO)"/>'),
 "sr_tree": svg(nd(59, 10) + ln(55, 16, 40, 28, OR) + ln(63, 16, 78, 28, OR)
                + "".join(f'<path d="M{x} 30 L{x-12} 50 H{x+12} Z" fill="{ORF}" stroke="{OR}" stroke-width="1.5"/>' + tx(x, 46, "T", OR, 9, w=700) for x in (38, 80))),
 "sr_doll": svg("".join(f'<ellipse cx="59" cy="{30+i*3}" rx="{30-i*8}" ry="{22-i*5.5}" fill="{ORF if i == 3 else "none"}" stroke="{OR}" stroke-width="1.5"/>' for i in range(4))),
 # return & combine
 "combine": svg(nd(36, 46, c=GR, f=GRF) + nd(82, 46, c=GR, f=GRF) + nd(59, 12, c=GR, f=GRF)
                + ln(41, 40, 54, 20, GR, arrow="aG") + ln(77, 40, 64, 20, GR, arrow="aG") + tx(59, 42, "+", GR, 14, w=700)),
 "r_full": svg(tree(c=GR, f=GRF) + "".join(tx(x + 10, y + 3, v, GR, 8, "start", w=700) for (x, y), v in
               [((59, 9), "8"), ((38, 29), "5"), ((80, 29), "3"), ((26, 48), "2"), ((50, 48), "3")])),
 "r_partial": svg(tree(c=GR, f=GRF) + tx(69, 12, "= 8", GR, 9, "start", w=700)),
 # base case
 "base_edge": svg(tx(59, 33, "f(1) → f(0)", OR, 12, mono=True)),
 "base_prune": svg(tree(hi=["d"], hic=PK, hif="#FBE3F1") + tx(50, 52, "×", PK, 12, w=700)),
}

USE = {"leap": "leap", "selfref-list": "sr_list", "selfref-tree": "sr_tree", "selfref-doll": "sr_doll",
       "ret-compose": "combine", "r-full": "r_full", "r-partial": "r_partial", "base-edge": "base_edge", "base-prune": "base_prune"}

if __name__ == "__main__":
    path = os.path.join(HERE, "..", "data.json") if len(sys.argv) < 2 else sys.argv[1]
    D = json.load(open(path))
    D["icons"].update(NEW)
    seen = set()
    for d in D["dims"]:
        for _, cs in d["groups"]:
            for c in cs:
                for x in [c] + c["subs"]:
                    if x["id"] in USE: x["icon"] = USE[x["id"]]; seen.add(x["id"])
    assert seen == set(USE), set(USE) - seen
    json.dump(D, open(path, "w"), ensure_ascii=False)
    print("icons", len(NEW))
