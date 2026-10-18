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
