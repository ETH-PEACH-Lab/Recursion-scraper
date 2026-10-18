# Accuracy review of the 32 LeetCode solutions: verdict + reason; per-image flags.
# good = faithful to the recursive code, values check out, return/combine visible where it matters
# partial = correct, but shows only calls, one step, or the result structure, not the recursion
# misleading = wrong values, iteration drawn as recursion, or structure misrepresented
# off = the images do not depict the recursion at all
REVIEW = {
 4815625: ("partial", "Branching on * and the (i, j) states are right; the true/false results are never shown coming back."),
 2705782: ("good", "Each frame’s arguments sit on a stack next to the code, and the final return 12 is shown; matches the recursive code."),
 1774708: ("good", "States plainly that links 3→4 must be fixed first by the recursive call, then relinks 1 and 2; correct order."),
 2481145: ("partial", "Only the two hand drawings show the recursive version; the other five images are input/output or the iterative pairwise swap."),
 1163702: ("good", "Before/after with the rest drawn as an “already done” box: a clean leap-of-faith picture of the recursive step."),
 3531484: ("partial", "Shows the swap on a two-node list only; the recursive call on the rest never appears."),
 580838: ("partial", "One local swap plus the final list; the recursion on the next pair is a single unexplained arrow."),
 3431696: ("misleading", "A copied “groups of given size” figure that only swaps pairs, and its last row shows the original order 16 21 56 91 89 instead of the result; steps read as a forward loop."),
 1059115: ("off", "A code screenshot beside a static list with head/temp; nothing about the recursion is drawn (the promised animation is missing)."),
 2194971: ("good", "Handwritten stack frames, each with its pointers and the value it returns; faithful to the recursive code."),
 2655657: ("good", "Return values on the arcs (2, 2, NULL, NULL) are exactly what each call returns when removing 6."),
 4907451: ("partial", "The first GIF animates the iterative while-loop; only the second (first / reverse rest / link rest) is the recursion."),
 2105240: ("partial", "Relinking happens innermost-first, which is correct, but calls and returns are not shown."),
 2578707: ("good", "Columns of head, newHead and head-off per level show what each call returns while the list unwinds."),
 1741696: ("good", "f(32) → f(16) → … down to the base case, with true passed back up; values correct."),
 1345716: ("misleading", "The linked list is drawn as an array of 1–7 (not a palindrome), and the comparison made while the recursion unwinds is not shown."),
 5806427: ("partial", "Correct expression-tree counts (G(2) = 2, G(3) = 5), but it shows the answer space, not how the recursion builds it."),
 1294189: ("partial", "All five trees for 2*3-4*5 and their values (−34, −10, −14, 10, −10) are right; the splitting recursion itself is not drawn."),
 5806873: ("good", "Split-by-operator recursion trees with the resulting values (−34, −14, −10) checked, plus where memoisation helps; one opening slide is a generic Fibonacci tree."),
 2369098: ("good", "Every node carries its list of results, so the combine step is visible; values check out ([2] × [−17, −5] = [−34, −10])."),
 1635529: ("good", "a2[b2[cd]]e2[f] expands level by level and the inner results are arrowed back into the outer string; correct."),
 3827081: ("partial", "Correct (i, j) states for each player, but the scores that come back are not shown."),
 2244469: ("partial", "Correct fib(5) call tree, calls only; it motivates the iterative solution the post actually uses."),
 3243889: ("partial", "Correct hypothesis → induction → base-case reasoning, but the whiteboard is crowded and hard to follow."),
 630113: ("partial", "Draws the whole grammar tree; the recursion only walks one root-to-leaf path, which the picture does not distinguish."),
 1541995: ("partial", "Partition and subtree combination are right, but nodes are numbered 1–7 like a BST although full-binary-tree nodes carry no values."),
 2534430: ("partial", "All five shapes of F(7) are correct; it shows results, not the recursion."),
 5935189: ("good", "A careful step-by-step trace of (k, n, mid), including a deliberately wrong answer that is then corrected with the mirror idea."),
 5437958: ("partial", "The j(n−1, k, i) / j(n, k, i+1) notation is not explained, so the mapping is hard to verify from the picture."),
 2847011: ("good", "Renumbering n = 7 onto n = 6 with +4 (mod 7) is exactly the step the recursion undoes on return; values correct."),
 2149752: ("good", "Circles relabelled, then f(n, k) = (f(n−1, k) + k − 1) % n + 1 with f(1, k) = 1; correct."),
 1797052: ("partial", "Reuses the same expression-tree figure as solution 1294189; correct, but not this author’s own diagram."),
}
IMGFLAG = {22: "input only", 23: "iterative pairwise swap", 24: "output only", 27: "iterative (prev/curr)", 28: "iterative (prev/curr)", 86: "iterative while-loop", 110: "generic Fibonacci example"}
