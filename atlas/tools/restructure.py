"""Migrate data.json from the Figure-9-style dimensions to the concept-first structure.

Each recursion concept, with the ways it is drawn under it.
Code correspondence sits outside the concepts.
Run once: python3 restructure.py (it refuses to run on already migrated data).
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "data.json") if len(sys.argv) < 2 else sys.argv[1]
D = json.load(open(PATH))
if D["dims"][0]["id"] == "selfref":
    sys.exit("already migrated")

OLD = {}
for d in D["dims"]:
    for _, cs in d["groups"]:
        for c in cs:
            OLD[c["id"]] = c
            for s in c["subs"]: OLD[s["id"]] = s

def C(id, name=None, desc=None, icon=None, subs=()):
    o = OLD.get(id, {})
    return dict(id=id, name=name or o["name"], desc=o.get("desc", "") if desc is None else desc,
                icon=icon if icon is not None else o.get("icon"), subs=[C(s) if isinstance(s, str) else s for s in subs], new=False)
def S(id, name=None, icon=None):
    o = OLD.get(id, {})
    return dict(id=id, name=name or o["name"], icon=icon if icon is not None else o.get("icon"), new=False)

DIMS = [
 dict(id="selfref", name="Self-referential data", q="Which data refers to itself, and what sits inside one node?", col=0, color="#C8692F", groups=[
   ("Data", [C("selfref-list", desc="A list whose rest is again a list."), C("selfref-tree", desc="A tree whose children are trees."), C("selfref-doll", desc="A pictorial object holding a smaller copy.")]),
   ("Node content", [C("n-data"), C("n-call"), C("n-state"), C("n-partial")])]),
 dict(id="base", name="Base case", q="Is the stopping point shown, and how?", col=0, color="#D0469B", groups=[("Marking", [
     C("a-base", "Marked", "Labelled or highlighted as the base case.", "base"),
     C("base-edge", "Reached, not marked", "The last call is drawn but not singled out."),
     C("base-prune", "Dead-end leaf", "A failed branch ends the recursion.")])]),
 dict(id="decomp", name="Decomposition", q="How are the smaller instances laid out, and how many calls are drawn?", col=1, color="#2F64B0", groups=[
   ("Structure", [C("nested", subs=["v-boxbox", "v-brackets", "v-treemap"]),
                  C("tree", subs=["v-calltree", "v-statetree", "v-choicetree", "v-resulttree"]),
                  C("chain", subs=["v-boxptr", "v-rewire"]),
                  C("v-stack"), C("v-table"), C("v-subst"), C("v-indent"), C("v-partition"), C("v-mapping"), C("v-metaphor")]),
   ("Choices", [C("a-choice"), C("a-prune")]),
   ("Elision (calls)", [C("e-full"), C("e-pat"), C("e-unpat"), C("e-black"),
                        C("deferred", subs=["e-trace", "e-done"]),
                        C("leap", "Trusted subcall", "The subcall’s result is used without drawing inside it (leap of faith).")])]),
 dict(id="retcomb", name="Return & combine", q="How do results come back, and how many returns are drawn?", col=2, color="#23826A", groups=[
   ("Flow", [C("f-up"), C("f-round"), C("f-rewrite")]),
   ("Marks", [C("a-ret"), C("ret-compose", "Combine step", "How sub-results merge is drawn."), C("a-path"), C("a-callstep")]),
   ("Elision (returns)", [
     C("r-full", "All returns drawn", "Every call’s result is shown coming back."),
     C("r-partial", "Some returns drawn", "Only some results, e.g. the final one."),
     C("r-none", "Returns not drawn", "Calls only; for a recursive process the way back is missing.", "down")])]),
 dict(id="code", name="Code Correspondence", q="How does it tie back to the code?", col=3, color="#3E8E3E", groups=[("Link", [
     C("c-is"),
     C("c-link", "Linked to the code", "Placed next to it, arrowed into it, or sharing its names.", subs=["c-side", "c-arrows", "c-ids"]),
     C("c-text", "Linked through math or prose", "An equation or a written explanation, not the code.", subs=["c-rec", "c-prose"])])]),
]

RENAME = {"f-down": "r-none", "state-stack": "v-stack"}
DROP = {"n-sym", "s-time", "s-scen", "s-rep", "a-role", "a-cursor", "overlap", "a-dup", "cost-level", "cost-total", "decomp-struct", "decomp-gen", "f-static", "ret-value", "choice-branch", "choice-prune", "choice-back", "state-acc"}

RET_NONE = {19, 29, 37, 38}   # recursive process, way back not drawn
RET_PARTIAL = {20}            # only the final return 12

for i, e in enumerate(D["examples"]):
    old = e["codes"]
    new = []
    add = lambda c: c not in new and new.append(c)
    for c in old:
        if c in DROP or (c in RENAME and RENAME[c] == "r-none"): continue
        if c == "base-edge" and "a-base" in old: continue
        add(RENAME.get(c, c))
    if i in RET_NONE: add("r-none")
    elif i in RET_PARTIAL: add("r-partial")
    elif {"f-up", "f-round", "f-rewrite", "ret-value"} & set(old): add("r-full")
    e["codes"] = new

D["dims"] = DIMS
known = {c["id"] for d in DIMS for _, cs in d["groups"] for c in cs} | {s["id"] for d in DIMS for _, cs in d["groups"] for c in cs for s in c["subs"]}
missing = {c for e in D["examples"] for c in e["codes"]} - known
assert not missing, missing
json.dump(D, open(PATH, "w"), ensure_ascii=False)
print("migrated", len(D["examples"]))
