"""Build the atlas data (codings, examples, icons) and the image files for the interactive page."""
import json, os, runpy, sys
from review import REVIEW, IMGFLAG
from PIL import Image

FIG = "/tmp/claude-0/-home-claude/dabde106-a379-5bf6-a07c-c8dcb0e8fa92/scratchpad/fig"
SITE = os.path.dirname(os.path.abspath(__file__))
DOCX = "/home/claude/docx2/x/word/media"
LCDIR = "/mnt/user-data/uploads/recursion_scraper/output/image_review"

sys.argv = ["build.py", "/tmp/claude-0/_unused.html"]
g = runpy.run_path(os.path.join(FIG, "build.py"))
ICON, DEFS = g["ICON"], g["DEFS"]

# ---------------- codings ----------------
def C(id, name, desc="", icon=None, subs=None, new=False):
    return dict(id=id, name=name, desc=desc, icon=icon, subs=subs or [], new=new)
def S(id, name, icon=None, new=False):
    return dict(id=id, name=name, icon=icon, new=new)

DIMS = [
 dict(id="concepts", name="Concepts", q="Which aspect of recursion is shown?", col=0, color="#7A808A", groups=[
   ("Structure", [
     C("selfref", "Self-referential data", "The data type refers to itself.", subs=[S("selfref-list", "List"), S("selfref-tree", "Tree"), S("selfref-doll", "Nested doll")]),
     C("decomp", "Decomposition", "Problem split into smaller instances.", subs=[S("decomp-struct", "Structural"), S("decomp-gen", "Generative")]),
     C("base", "Base case", "Where recursion stops.", subs=[S("base-edge", "Edge condition"), S("base-prune", "Pruned leaf")]),
     C("leap", "Leap of faith", "The recursive result is trusted, not traced.", new=True)]),
   ("Process", [
     C("retcomb", "Return & combine", "Sub-results flow back and merge.", subs=[S("ret-value", "Value return"), S("ret-compose", "Result composition")]),
     C("choice", "Choice / search", "Each call picks among options.", subs=[S("choice-branch", "Branching"), S("choice-prune", "Pruning"), S("choice-back", "Backtracking")]),
     C("overlap", "Overlapping subproblems", "The same subcall recurs."),
     C("state", "Execution state", "What is held while running.", subs=[S("state-stack", "Call stack"), S("state-acc", "Accumulator")]),
     C("cost", "Cost", "Work done per call or level.", subs=[S("cost-level", "Per level"), S("cost-total", "Total")])])]),
 dict(id="node", name="Node Content", q="What sits inside a node?", col=0, color="#C8692F", groups=[(None, [
     C("n-data", "Concrete data", "Values of the input itself.", "n_data"),
     C("n-call", "Call with arguments", "The call as written, concrete args.", "n_call"),
     C("n-state", "State tuple", "Only the changing parameters.", "n_state"),
     C("n-partial", "Partial expression", "Half-evaluated term, as in a trace.", "n_partial"),
     C("n-sym", "Symbolic", "Parametric size, as in a recurrence.", "n_sym")])]),
 dict(id="visual", name="Visual Encodings", q="Which visual structure?", col=1, color="#C8692F", groups=[(None, [
     C("nested", "Nested containment", "Calls drawn inside their caller.", subs=[S("v-boxbox", "Box-in-box", "boxbox"), S("v-brackets", "Brackets", "brackets"), S("v-treemap", "Treemap", "treemap")]),
     C("tree", "Tree (node-link)", "Calls linked to their subcalls.", subs=[S("v-calltree", "Call tree", "calltree"), S("v-statetree", "State tree", "statetree"), S("v-choicetree", "Choice tree", "choicetree"), S("v-resulttree", "Result tree", "resulttree", True)]),
     C("chain", "Linear chain", "List of nodes and links.", subs=[S("v-boxptr", "Box-and-pointer", "chain"), S("v-rewire", "Pointer rewiring", "rewire", True)]),
     C("v-stack", "Stack", "Frames piled up by depth.", "stack"),
     C("v-subst", "Substitution trace", "Expression rewritten until a value.", "subst"),
     C("v-indent", "Indentation staircase", "Depth shown by indentation.", "indent"),
     C("v-table", "Table", "Args, intermediates and results.", "table"),
     C("v-partition", "Partition", "Input split into boxed parts.", "partition", new=True),
     C("v-mapping", "Instance mapping", "Size n aligned to size n−1.", "mapping", new=True),
     C("v-metaphor", "Metaphor / pictorial", "Dolls, mirrors, spirals.", "doll")])]),
 dict(id="flow", name="Flow Direction", q="Which way does information move?", col=1, color="#23826A", groups=[(None, [
     C("f-static", "Static", "Structure only, no direction.", "static"),
     C("f-down", "Downward only", "Calls drawn, returns omitted.", "down"),
     C("f-up", "Upward only", "Results merging toward the root.", "up"),
     C("f-round", "Round trip", "Down to the base case, then back up.", "round"),
     C("f-rewrite", "Rewrite in place", "Time runs down the lines.", "rewrite")])]),
 dict(id="annot", name="Annotations", q="What gets marked on top?", col=2, color="#2F64B0", groups=[(None, [
     C("a-base", "Base-case marker", "Marks where recursion stops.", "base"),
     C("a-ret", "Return value", "Value written on the way back.", "retval"),
     C("a-prune", "Prune / fail + legend", "Dead branches, keyed in a legend.", "prune"),
     C("a-role", "Role colour", "Colour by role (pivot, done).", "role"),
     C("a-cursor", "Cursor / pointer", "Indices into the data.", "cursor"),
     C("a-choice", "Choice label", "The decision named on the edge.", "choicelab"),
     C("a-callstep", "Call-step label", "Each frame or step numbered.", "callstep", new=True),
     C("a-dup", "Duplicate marker", "Repeated subproblems circled.", "dup"),
     C("a-path", "Traversal path", "Evaluation order traced.", "path")])]),
 dict(id="elision", name="Elision", q="How is size handled?", col=2, color="#D0469B", groups=[(None, [
     C("e-full", "Full expansion", "Small input, every call drawn.", "full"),
     C("e-unpat", "Unpatterned elision", "No inference can be made.", "unpat"),
     C("e-pat", "Patterned elision", "Rule implied by a few levels.", "pattern"),
     C("e-black", "Black-box leaf", "Leaves drawn as opaque blocks.", "blackbox"),
     C("deferred", "Deferred call", "Subcall left unexpanded.", subs=[S("e-trace", "Trace term", "deferred"), S("e-done", "Done box", "donebox", True)])])]),
 dict(id="subd", name="Subdiagrams", q="How many panels, and why?", col=2, color="#7E6BD0", groups=[(None, [
     C("s-rep", "Multiple representations", "Same recursion, two encodings.", "multirep"),
     C("s-scen", "Multiple scenarios", "Cases of one step side by side.", "multiscen"),
     C("s-time", "Over time", "Snapshots of one run.", "overtime")])]),
 dict(id="code", name="Code Correspondence", q="How does it tie back to the code?", col=3, color="#3E8E3E", groups=[(None, [
     C("c-is", "Diagram is code", "Trace written in the program’s own syntax."),
     C("c-side", "Side by side", "Diagram placed next to the code or rule."),
     C("c-arrows", "Arrows into code", "Arrows tie parts of the diagram to code."),
     C("c-ids", "Shared identifiers", "Function and parameter names reused in nodes."),
     C("c-rec", "Recurrence only", "Linked to an equation, not to code."),
     C("c-prose", "Prose only", "Linked through a written explanation.")])]),
]

SOURCES = [
 ("LYAH", "Learn You a Haskell", "textbook"), ("SICP", "Structure and Interpretation of Computer Programs", "textbook"),
 ("HtDP", "How to Design Programs", "textbook"), ("DCIC", "A Data-Centric Introduction to Computing", "textbook"),
 ("CLRS", "Introduction to Algorithms", "textbook"), ("MIT 6.102", "MIT 6.102 course notes", "textbook"),
 ("VisuAlgo", "visualgo.net", "tool"), ("RV", "recursionvisualizer.com", "tool"), ("Ours", "Our own sketches", "ours"),
 ("LC-cn", "LeetCode.cn, hand-picked solutions", "leetcode"), ("LC", "LeetCode, vote ≥ 5 (scraped)", "leetcode"),
]

URL = {
 "LYAH": "https://learnyouahaskell.github.io/recursion.html", "SICP": "https://web.mit.edu/6.001/6.037/sicp.pdf",
 "HtDP5": "https://htdp.org/2026-2-25//Book/part_five.html", "HtDP2": "https://htdp.org/2026-2-25//Book/part_two.html",
 "DCIC": "https://dcic-world.org/2025-08-27/recursive-data.html",
 "MIT": "https://web.mit.edu/6.102/www/sp25/classes/11-recursive-data-types/recursion-and-iteration-review.html",
 "VisuAlgo": "https://visualgo.net/en/recursion", "RV": "https://www.recursionvisualizer.com/",
}
CN = "https://leetcode.cn/problems/"
CNS = {
 "climb": CN + "climbing-stairs/solutions/270926/cong-zhi-jue-si-wei-fen-xi-dong-tai-gui-hua-si-lu-/",
 "2163": CN + "ba-shu-zi-fan-yi-cheng-zi-fu-chuan-lcof/solutions/280712/shou-hui-tu-jie-dfsdi-gui-ji-yi-hua-di-gui-dong-ta/",
 "maxpath": CN + "binary-tree-maximum-path-sum/solutions/297276/shou-hui-tu-jie-hen-you-ya-de-yi-dao-dfsti-by-hyj8/",
 "pattern": CN + "pattern-matching-lcci/solutions/298668/hua-liao-ge-hui-su-de-si-lu-tu-bian-jie-qing-kuang/",
 "winner": CN + "predict-the-winner/solutions/396343/shou-hua-tu-jie-san-chong-xie-fa-di-gui-ji-yi-hua-/",
 "comb": CN + "combinations/solutions/405266/shou-hua-tu-jie-jian-zhi-he-hui-su-by-xiao_ben_zhu/",
 "inorder": CN + "binary-tree-inorder-traversal/solutions/412997/shou-hua-tu-jie-yong-zhan-mo-ni-zhong-xu-bian-li-z/",
 "subset": CN + "partition-equal-subset-sum/solutions/442412/shou-hua-tu-jie-fen-ge-deng-he-zi-ji-dfshui-su-si-/",
 "wordbreak": CN + "word-break-ii/solutions/468624/shou-hua-tu-jie-dan-ci-chai-fen-ii-cong-di-gui-dao/",
 "ababbc": CN + "longest-substring-with-at-least-k-repeating-characters/solutions/624025/shou-hua-tu-jie-tong-guo-fen-zhi-suo-xia-cnn1/",
 "frog": CN + "frog-jump/solutions/603278/shou-hua-tu-jie-ji-hao-de-di-gui-ti-man-8kk2z/",
 "pascal": CN + "pascals-triangle-ii/solutions/601320/shou-hua-tu-jie-119yang-hui-san-jiao-ii-d09dc/",
 "lis": CN + "longest-increasing-subsequence/solutions/198897/chao-xiang-xi-tu-jie-di-gui-dong-tai-gui-hua-er-fe/",
}

def D(n): return ("d", n)
def L(n): return ("l", n)

EX = [
 # textbooks, tools, ours
 ("DCIC", "NumList data definition", "Hand-drawn definition; the rest field points back to NumList.", [D(29)], URL["DCIC"], "selfref-list f-static"),
 ("DCIC", "nl-link nesting", "Each nested nl-link indented one step further.", [D(19), D(5)], URL["DCIC"], "v-indent c-is n-data"),
 ("HtDP", "Fig 44 · Building a list", "cons cells drawn as boxes inside boxes, next to their expressions.", [D(76), D(74)], URL["HtDP2"], "v-boxbox f-static s-rep"),
 ("HtDP", "Fig 45 · Drawing a list", "The same list as a chain of first/rest boxes.", [D(44)], URL["HtDP2"], "v-boxptr"),
 ("HtDP", "Russian dolls", "A doll contains a smaller doll; used to introduce RD data.", [D(9), D(45), D(47)], URL["HtDP5"], "selfref-doll v-metaphor"),
 ("HtDP", "Fig 51 · Self-reference arrows", "Arrows tie the self-reference in the data definition to the recursive call in the template.", [D(32)], URL["HtDP5"], "c-arrows selfref-list decomp-struct"),
 ("HtDP", "Fig 55 · Tabulating", "Arguments, intermediate values and results in a table.", [D(53)], URL["HtDP5"], "v-table"),
 ("HtDP", "Figs 48–50 · Computing with lists", "Step-by-step rewriting of contains-flatt?, the recursive call left unexpanded until its turn.", [D(52), D(34), D(80)], URL["HtDP5"], "v-subst f-rewrite e-trace s-time c-is n-partial"),
 ("HtDP", "quick-sort< by hand", "Substitution trace of quicksort; sorted pieces are appended back together.", [D(2)], URL["HtDP5"], "v-subst decomp-gen f-up ret-compose"),
 ("HtDP", "Fig 153 · Structural vs generative", "The generative template next to the structural one.", [D(16)], URL["HtDP5"], "decomp-struct decomp-gen"),
 ("HtDP", "maximum, rewritten", "Each line rewrites the previous one until a value remains.", [D(64)], URL["HtDP5"], "f-rewrite v-subst"),
 ("SICP", "Fig 1.3 · Linear recursive process", "factorial 6 expands into deferred multiplications, then collapses.", [D(7), D(28)], URL["SICP"], "v-subst n-partial f-rewrite ret-compose c-is"),
 ("SICP", "Fig 1.5 · Tree-recursive process", "fib 5 call tree with a dotted line tracing evaluation order.", [D(18), D(20)], URL["SICP"], "v-calltree e-full a-path f-round n-call c-ids c-side"),
 ("LYAH", "maximum'", "Each call bracketed inside its caller: max 2 (maximum' [5,1]).", [D(65), D(61)], URL["LYAH"], "v-brackets decomp-struct base-edge c-side"),
 ("LYAH", "quicksort", "Pivots in green, placed elements in orange, smaller and bigger lists below.", [D(11), D(42)], URL["LYAH"], "a-role decomp-gen c-side"),
 ("LYAH", "Painter painting himself", "Pictorial metaphor for self-reference.", [D(70), D(41)], URL["LYAH"], "v-metaphor"),
 ("CLRS", "Fig 4.7 · Recursion tree", "Symbolic nodes f(n/b), cost per level summed on the right.", [D(54)], None, "cost-level cost-total n-sym e-pat c-rec"),
 ("MIT 6.102", "Tree-like patterns", "Root A with subtrees; leaves have no children.", [D(48)], URL["MIT"], "selfref-tree f-static"),
 ("MIT 6.102", "sum_nested as a tree", "A nested Python list drawn as a tree of lists.", [D(27)], URL["MIT"], "n-data selfref-tree"),
 ("VisuAlgo", "Fibonacci recursion tree", "Every call of a small input drawn top down.", [D(43)], URL["VisuAlgo"], "v-calltree f-down e-full"),
 ("RV", "virfib", "Calls go down in black; returned values come back up in green.", [D(21)], URL["RV"], "ret-value f-round a-ret n-call c-ids"),
 ("Ours", "Accumulator sketch", "result = 7+4+… updated at each call.", [D(12)], None, "state-acc"),
 ("Ours", "Treemap storyboard", "Four frames of f(5) opening as nested boxes.", [D(15)], None, "v-treemap s-time"),
 # LeetCode.cn, hand-picked
 ("LC-cn", "Climbing stairs", "Node = stairs left; the last panel returns 3+5=8 upward.", [D(39)], CNS["climb"], "v-statetree f-round ret-value ret-compose"),
 ("LC-cn", "Translate numbers to strings (2163)", "Pointer, translated/untranslated colours, failure marks with a legend.", [D(82)], CNS["2163"], "a-prune a-cursor choice-branch"),
 ("LC-cn", "Binary tree maximum path sum", "go left / nowhere / right panels; returned values on edges.", [D(83), D(77), D(86)], CNS["maxpath"], "s-scen a-choice a-ret c-prose"),
 ("LC-cn", "Pattern matching", "Two attempts; the second backtracks.", [D(35)], CNS["pattern"], "choice-back"),
 ("LC-cn", "Predict the winner", "Player 1 and player 2 picks per level.", [D(50)], CNS["winner"], "choice-branch"),
 ("LC-cn", "Combinations", "Triangles mark base cases; pruned branches stop early.", [D(22)], CNS["comb"], "a-base base-prune choice-prune"),
 ("LC-cn", "Inorder traversal with a stack", "Tree beside snapshots of the stack.", [D(55), D(4), D(1), D(63)], CNS["inorder"], "state-stack v-stack a-path s-time"),
 ("LC-cn", "Partition equal subset sum", "Calls drawn going down; returns left out.", [D(23)], CNS["subset"], "f-down"),
 ("LC-cn", "Word break II", "Branches trail off with “…”.", [D(8)], CNS["wordbreak"], "e-unpat"),
 ("LC-cn", "Longest substring with ≥ k repeats", "start/end arrows under ababbc.", [D(57)], CNS["ababbc"], "a-cursor"),
 ("LC-cn", "Frog jump", "Repeated subtrees circled.", [D(46)], CNS["frog"], "overlap a-dup a-base"),
 ("LC-cn", "Pascal’s triangle II", "Repeated subtrees circled; base cases ticked.", [D(58)], CNS["pascal"], "overlap a-dup a-base"),
 ("LC-cn", "Longest increasing subsequence", "match/skip on edges, f(i,j) states, black-box leaves.", [D(14), D(67)], CNS["lis"], "v-choicetree a-choice e-black n-state"),
]

LCS = [  # (problem, slug, solution id, votes, images, codings, note)
 ("Regular Expression Matching", "regular-expression-matching", 4815625, 9, [7, 8], "v-statetree a-choice a-prune n-state f-down base-prune choice-branch", "String states with (i, j) labels; dead branches crossed out."),
 ("Merge Two Sorted Lists", "merge-two-sorted-lists", 2705782, 215, [15, 16], "v-stack state-stack a-callstep f-round c-side s-time c-ids ret-value", "Six numbered steps push frames onto a stack, then return 12."),
 ("Swap Nodes in Pairs", "swap-nodes-in-pairs", 1774708, 662, [21], "v-rewire leap s-time c-prose", "Links redrawn; the rest is said to be handled by the recursion."),
 ("Swap Nodes in Pairs", "swap-nodes-in-pairs", 2481145, 23, [22, 23, 24, 25, 26, 27, 28], "v-rewire v-brackets e-done s-time leap", "The rest of the list bracketed and labelled “Recursive”."),
 ("Swap Nodes in Pairs", "swap-nodes-in-pairs", 1163702, 23, [29], "e-done v-rewire s-time leap", "Before/after with the rest drawn as one “already done” box."),
 ("Swap Nodes in Pairs", "swap-nodes-in-pairs", 3531484, 7, [30, 31, 32, 33], "v-rewire a-cursor s-time", "curr/next links rewired over four frames."),
 ("Swap Nodes in Pairs", "swap-nodes-in-pairs", 580838, 7, [39], "v-rewire a-role s-time", "Input, before swap, after swap and result rows."),
 ("Reverse Nodes in k-Group", "reverse-nodes-in-k-group", 3431696, 7, [42], "v-rewire a-callstep s-time", "Each row labelled first, second, third recursive call."),
 ("Reorder List", "reorder-list", 1059115, 40, [69], "v-boxptr a-cursor c-side s-rep", "Code beside the list with head and temp pointers."),
 ("Reorder List", "reorder-list", 2194971, 6, [70], "state-stack a-ret a-cursor s-time ret-value", "Handwritten stack frames, each returning curr."),
 ("Remove Linked List Elements", "remove-linked-list-elements", 2655657, 16, [73], "v-boxptr a-ret f-round ret-value", "Return values written under arcs back along the list."),
 ("Reverse Linked List", "reverse-linked-list", 4907451, 12, [86, 87], "v-rewire leap s-time decomp-struct", "First/rest split; “reverse rest” trusted, then relinked."),
 ("Reverse Linked List", "reverse-linked-list", 2105240, 30, [91, 92, 93], "v-rewire s-time", "Three frames of node links being reversed."),
 ("Reverse Linked List", "reverse-linked-list", 2578707, 14, [94], "v-rewire v-table f-round ret-value", "Columns of head, newHead and head-off per level."),
 ("Power of Two", "power-of-two", 1741696, 78, [98], "f-round a-base base-edge n-call c-rec c-prose", "f(32) → f(16) → … → base case, return true back."),
 ("Palindrome Linked List", "palindrome-linked-list", 1345716, 15, [103], "f-up v-partition a-path", "Forward iteration vs. backward traversal using recursion."),
 ("Different Ways to Add Parentheses", "different-ways-to-add-parentheses", 5806427, 18, [104], "v-resulttree s-scen f-static decomp-gen", "All expression trees for small inputs; G(3) = 5."),
 ("Different Ways to Add Parentheses", "different-ways-to-add-parentheses", 1294189, 498, [107], "v-resulttree s-scen f-static", "Five expression trees for 2*3-4*5 with their answers."),
 ("Different Ways to Add Parentheses", "different-ways-to-add-parentheses", 5806873, 20, [110, 113, 114, 117, 118, 119, 120, 111, 115, 122, 109, 112, 116], "v-calltree f-round v-choicetree a-cursor a-callstep a-dup overlap c-side decomp-gen choice-branch a-prune e-unpat n-partial s-time base-edge a-base c-ids", "Recursion trees with numbered return arrows, split cases I–III, memoisation."),
 ("Different Ways to Add Parentheses", "different-ways-to-add-parentheses", 2369098, 21, [124], "v-calltree a-ret a-prune ret-compose decomp-gen choice-prune", "Each node annotated with its list of results."),
 ("Decode String", "decode-string", 1635529, 6, [128], "v-brackets v-subst f-round", "a2[b2[cd]]e2[f] expanded level by level, results arrowed back."),
 ("Predict the Winner", "predict-the-winner", 3827081, 6, [129], "v-statetree n-state a-choice choice-branch", "P1/P2 levels over (i, j) states."),
 ("Fibonacci Number", "fibonacci-number", 2244469, 11, [132], "v-calltree e-full f-down n-call c-ids", "fib(5) call tree, every call drawn."),
 ("K-th Symbol in Grammar", "k-th-symbol-in-grammar", 3243889, 6, [144, 145, 146, 147, 148], "leap a-base c-side base-edge", "Whiteboard hypothesis → induction → base condition → code."),
 ("K-th Symbol in Grammar", "k-th-symbol-in-grammar", 630113, 31, [149], "v-resulttree f-static", "The grammar rows drawn as a tree."),
 ("All Possible Full Binary Trees", "all-possible-full-binary-trees", 1541995, 30, [150, 151, 152, 153, 154, 155, 156, 157], "v-partition v-resulttree ret-compose s-time decomp-gen a-role", "Pick a root, box left and right groups, combine subtrees."),
 ("All Possible Full Binary Trees", "all-possible-full-binary-trees", 2534430, 14, [158], "v-resulttree s-scen e-full n-call", "All five tree shapes for F(7)."),
 ("Find Kth Bit in Nth Binary String", "find-kth-bit-in-nth-binary-string", 5935189, 9, [160, 161, 162, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176], "n-state v-indent v-metaphor f-round c-arrows a-base base-edge overlap cost-total c-side s-time", "(k, n, mid) reduced step by step; “normal world / mirror world”."),
 ("Find the Winner of the Circular Game", "find-the-winner-of-the-circular-game", 5437958, 37, [182], "v-mapping n-sym", "j(n−1, k, i) mapped onto j(n, k, i+1)."),
 ("Find the Winner of the Circular Game", "find-the-winner-of-the-circular-game", 2847011, 18, [183, 184, 185, 186, 187, 188, 189, 190], "v-mapping s-time", "Circle, elimination, then n = 7 renumbered onto n = 6 (+4)."),
 ("Find the Winner of the Circular Game", "find-the-winner-of-the-circular-game", 2149752, 17, [192], "v-mapping c-rec s-time", "Circles relabelled, then f(n, k) = (f(n−1, k) + k − 1) % n + 1."),
 ("Different Ways to Add Parentheses", "different-ways-to-add-parentheses", 1797052, 5, [107], "v-resulttree s-scen", "Expression trees (same figure as solution 1294189)."),
]

os.makedirs(os.path.join(SITE, "img"), exist_ok=True)
def save(kind, n):
    if kind == "d":
        f = [x for x in os.listdir(DOCX) if x.split(".")[0] == f"image{n}"][0]; src = os.path.join(DOCX, f); key = f"t{n}"
    else:
        f = [x for x in os.listdir(LCDIR) if x.split(".")[0] == f"{n:03d}"][0]; src = os.path.join(LCDIR, f); key = f"lc{n:03d}"
    out = os.path.join(SITE, "img", key + ".webp")
    if not os.path.exists(out):
        im = Image.open(src); im.seek(0)
        im = im.convert("RGBA"); bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg.convert("RGB")
        im.thumbnail((1400, 1400)); im.save(out, "WEBP", quality=82)
    w, h = Image.open(out).size
    return dict(src=f"img/{key}.webp", w=w, h=h, anim=f.endswith(".gif"))

examples = []
DROP = {"VisuAlgo", "RV", "Ours", "LC-cn"}
for src, title, note, imgs, link, codes in EX:
    if src in DROP: continue
    examples.append(dict(src=src, title=title, note=note, verdict="textbook", imgs=[save(*i) for i in imgs], link=link, codes=codes.split()))
for prob, slug, sid, votes, imgs, codes, note in LCS:
    v, why = REVIEW[sid]
    if v in ("misleading", "off"): continue
    ims = []
    for n in imgs:
        d = save("l", n)
        if n in IMGFLAG: d["flag"] = IMGFLAG[n]
        ims.append(d)
    examples.append(dict(src="LeetCode", title=prob, sub=f"Solution {sid} · {votes} votes", note=note, verdict=v, review=why,
                         imgs=ims, link=f"https://leetcode.com/problems/{slug}/solutions/{sid}/", codes=codes.split()))

ids = {c["id"] for d in DIMS for _, cs in d["groups"] for c in cs} | {s["id"] for d in DIMS for _, cs in d["groups"] for c in cs for s in c["subs"]}
bad = {c for e in examples for c in e["codes"] if c not in ids}
assert not bad, bad
icons = {k: v for k, v in ICON.items()}
SOURCES = [x for x in SOURCES if x[0] not in DROP]
SOURCES = [("LeetCode", "LeetCode solutions, vote ≥ 5", k) if a == "LC" else (a, b, k) for a, b, k in SOURCES]
data = dict(dims=DIMS, sources=[dict(id=a, name=b, kind=c) for a, b, c in SOURCES], examples=examples, icons=icons)
json.dump(data, open(os.path.join(SITE, "data.json"), "w"), ensure_ascii=False)
open(os.path.join(SITE, "defs.svg"), "w").write(DEFS)
print(len(examples), "examples,", len(os.listdir(os.path.join(SITE, "img"))), "images")
