"""Chinese strings for the atlas. Builds data_zh.json from data.json (image paths point one level up)."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))

DIM = {
 "concepts": ("概念", "图里表达的是递归的哪个方面？"), "node": ("节点内容", "节点里放什么？"),
 "visual": ("视觉编码", "用什么视觉结构？"), "flow": ("信息流向", "信息往哪个方向走？"),
 "annot": ("标注", "在结构上额外标了什么？"), "elision": ("省略", "规模大时怎么处理？"),
 "subd": ("子图", "为什么用多个面板？"), "code": ("与代码对应", "图怎么和代码对应起来？"),
}
GRP = {"Structure": "结构", "Process": "过程"}
COD = {  # id: (中文名, 说明)
 "selfref": ("自指数据", "数据类型的定义引用了自身。"), "selfref-list": ("列表", ""), "selfref-tree": ("树", ""), "selfref-doll": ("套娃", ""),
 "decomp": ("分解", "把问题拆成更小的同类问题。"), "decomp-struct": ("结构递归", ""), "decomp-gen": ("生成递归", ""),
 "base": ("基本情况", "递归在哪里停下。"), "base-edge": ("边界条件", ""), "base-prune": ("剪枝叶子", ""),
 "leap": ("信任递归结果", "直接使用递归调用的结果，不追踪其内部。"),
 "retcomb": ("返回与合并", "子问题的结果传回并合并。"), "ret-value": ("值的回传", ""), "ret-compose": ("结果组合", ""),
 "choice": ("选择 / 搜索", "每次调用在几个选项中做选择。"), "choice-branch": ("分支", ""), "choice-prune": ("剪枝", ""), "choice-back": ("回溯", ""),
 "overlap": ("重叠子问题", "同一个子调用反复出现。"),
 "state": ("执行状态", "运行时保存了什么。"), "state-stack": ("调用栈", ""), "state-acc": ("累加器", ""),
 "cost": ("代价", "每次调用或每层的工作量。"), "cost-level": ("每层代价", ""), "cost-total": ("总代价", ""),
 "n-data": ("具体数据", "节点里是输入本身的值。"), "n-call": ("带参数的调用", "按代码写出的调用，参数是具体值。"),
 "n-state": ("状态元组", "只写出变化的参数。"), "n-partial": ("部分求值表达式", "算到一半的表达式，像代换轨迹里那样。"),
 "n-sym": ("符号化", "用参数表示规模，像递推式里那样。"),
 "nested": ("嵌套包含", "被调用者画在调用者内部。"), "v-boxbox": ("盒中盒", ""), "v-brackets": ("括号嵌套", ""), "v-treemap": ("树图", ""),
 "tree": ("树（节点-连线）", "调用和它的子调用用连线相连。"), "v-calltree": ("调用树", ""), "v-statetree": ("状态树", ""),
 "v-choicetree": ("选择树", ""), "v-resulttree": ("结果树", ""),
 "chain": ("线性链", "由节点和指针组成的链表。"), "v-boxptr": ("盒子与指针", ""), "v-rewire": ("指针重连", ""),
 "v-stack": ("栈", "按深度堆起来的栈帧。"), "v-subst": ("代换轨迹", "表达式不断改写，直到得出值。"),
 "v-indent": ("缩进阶梯", "用缩进表示深度。"), "v-table": ("表格", "参数、中间值和结果列成表。"),
 "v-partition": ("输入划分", "把输入切成几块并框起来。"), "v-mapping": ("规模映射", "规模 n 与规模 n−1 对齐。"),
 "v-metaphor": ("隐喻 / 图画", "套娃、镜像、螺旋等。"),
 "f-static": ("静态", "只有结构，没有方向。"), "f-down": ("只向下", "只画调用，没画返回。"),
 "f-up": ("只向上", "只画结果向根合并。"), "f-round": ("往返", "下到基本情况，再返回上来。"),
 "f-rewrite": ("原地改写", "时间顺序就是从上到下的行。"),
 "a-base": ("基本情况标记", "标出递归停下的地方。"), "a-ret": ("返回值", "在回传路上写出值。"),
 "a-prune": ("剪枝 / 失败 + 图例", "死路分支，用图例说明。"), "a-role": ("角色配色", "按角色上色（如 pivot、已就位）。"),
 "a-cursor": ("游标 / 指针", "指向数据的下标。"), "a-choice": ("选择标签", "在连线上写出所做的选择。"),
 "a-callstep": ("调用步骤编号", "给每一帧或每一步编号。"), "a-dup": ("重复标记", "圈出重复的子问题。"),
 "a-path": ("遍历路径", "画出求值的顺序。"),
 "e-full": ("完全展开", "输入较小，每次调用都画出来。"), "e-unpat": ("无规律省略", "用“…”省略，看不出规律。"),
 "e-pat": ("有规律省略", "画几层，规律可以推出来。"), "e-black": ("黑箱叶子", "叶子画成不透明的方块。"),
 "deferred": ("延迟调用", "子调用先不展开。"), "e-trace": ("轨迹中的未展开项", ""), "e-done": ("“已完成”框", ""),
 "s-rep": ("多种表示", "同一递归用两种编码画。"), "s-scen": ("多种情形", "同一步的不同情况并排。"), "s-time": ("随时间", "同一次运行的多张快照。"),
 "c-is": ("图就是代码", "轨迹用程序本身的语法写成。"), "c-side": ("并排", "图放在代码或公式旁边。"),
 "c-arrows": ("箭头指向代码", "用箭头把图的部分连到代码。"), "c-ids": ("共享标识符", "节点里沿用函数名和参数名。"),
 "c-rec": ("只有递推式", "对应的是方程，而不是代码。"), "c-prose": ("只有文字", "通过文字说明对应。"),
}
# concept-first structure (restructure.py)
DIM.update({
 "type": ("递归类型", "这是哪种递归？"),
 "selfref": ("自指数据", "哪种数据引用了自身？一个节点里放什么？"),
 "decomp": ("分解", "更小的子问题怎么排布？画出多少次调用？"),
 "retcomb": ("传回合并", "结果怎么传回来？画出多少次返回？"),
 "base": ("基本情况", "递归停下的地方有没有画出来？怎么画？"),
 "global": ("全局选择", "针对整张图的选择，不属于某个概念。"),
 "other": ("其他", "具体题目或算法分析用的标注，不属于递归概念。"),
})
GRP.update({
 "Source (HtDP, MIT 6.102)": "来源（HtDP、MIT 6.102）", "Calls per step (SICP §1.2)": "每步调用次数（SICP §1.2）",
 "Process (SICP §1.2.1)": "过程（SICP §1.2.1）", "Data": "数据", "Node content": "节点内容", "Choices": "选择",
 "Elision (calls)": "省略（调用）", "Flow": "流向", "Marks": "标注", "Elision (returns)": "省略（返回）",
 "Instance": "实例", "Panels": "面板", "Marking": "标记方式", "Marks": "标注", "Link": "对应方式",
})
COD.update({
 "t-struct": ("结构递归", "按数据定义拆分：first/rest、左/右子树。"), "t-gen": ("生成递归", "子问题是算出来的，不是数据本身的一部分。"),
 "t-linear": ("线性递归", "每一步只递归调用一次。"), "t-tree": ("树形递归", "每一步递归调用两次或更多。"),
 "t-recproc": ("递归过程", "运算推迟到回程再做。"), "t-iterproc": ("迭代过程", "状态一路往下带，返回时没有剩下的运算。"),
 "selfref-list": ("列表", "rest 仍然是一个列表。"), "selfref-tree": ("树", "孩子仍然是树。"), "selfref-doll": ("套娃", "图画里的物体装着更小的自己。"),
 "leap": ("信任子调用", "直接使用子调用的结果，不画它的内部（leap of faith）。"),
 "ret-compose": ("合并步骤", "画出子结果怎样合并。"),
 "r-full": ("画出全部返回", "每次调用的结果都画出传回。"), "r-partial": ("画出部分返回", "只画一部分结果，比如最后的结果。"),
 "r-none": ("不画返回", "只画调用；对递归过程来说缺了回程。"),
 "a-base": ("有标记", "作为基本情况标出或高亮。"), "base-edge": ("画到但没标记", "画出了最后一次调用，但没有特别标出。"),
 "base-prune": ("死路叶子", "失败的分支让递归停下。"),
 "g-concrete": ("具体实例", "用真实的输入值。"),
 "c-link": ("连到代码", "放在代码旁边、用箭头指向代码，或沿用代码里的名字。"),
 "c-text": ("通过公式或文字", "对应的是方程或文字说明，而不是代码。"),
})
SRC = {"LYAH": "Learn You a Haskell（Haskell 教材）", "SICP": "计算机程序的构造和解释（SICP）", "HtDP": "程序设计方法（HtDP）",
       "DCIC": "A Data-Centric Introduction to Computing", "CLRS": "算法导论（CLRS）", "Software Construction": "MIT 软件构造（Software Construction）课程讲义",
       "LeetCode": "LeetCode 题解，vote ≥ 5"}
TITLE = {
 "NumList data definition": "NumList 数据定义", "nl-link nesting": "nl-link 嵌套", "Fig 44 · Building a list": "图 44 · 构造列表",
 "Fig 45 · Drawing a list": "图 45 · 画出列表", "Russian dolls": "俄罗斯套娃", "Fig 51 · Self-reference arrows": "图 51 · 自指箭头",
 "Fig 55 · Tabulating": "图 55 · 列表格", "Figs 48–50 · Computing with lists": "图 48–50 · 列表上的计算",
 "quick-sort< by hand": "手算 quick-sort<", "Fig 153 · Structural vs generative": "图 153 · 结构递归与生成递归",
 "maximum, rewritten": "maximum 的逐步改写", "Fig 1.3 · Linear recursive process": "图 1.3 · 线性递归过程",
 "Fig 1.5 · Tree-recursive process": "图 1.5 · 树形递归过程", "maximum'": "maximum'", "quicksort": "quicksort",
 "Painter painting himself": "画自己的画家", "Fig 4.7 · Recursion tree": "图 4.7 · 递归树", "Tree-like patterns": "树形结构",
 "sum_nested as a tree": "把 sum_nested 画成树",
 "Regular Expression Matching": "正则表达式匹配", "Merge Two Sorted Lists": "合并两个有序链表", "Swap Nodes in Pairs": "两两交换链表中的节点",
 "Reorder List": "重排链表", "Remove Linked List Elements": "移除链表元素", "Reverse Linked List": "反转链表", "Power of Two": "2 的幂",
 "Different Ways to Add Parentheses": "为运算表达式设计优先级", "Decode String": "字符串解码", "Predict the Winner": "预测赢家",
 "Fibonacci Number": "斐波那契数", "K-th Symbol in Grammar": "第 K 个语法符号", "All Possible Full Binary Trees": "所有可能的真二叉树",
 "Find Kth Bit in Nth Binary String": "找出第 N 个二进制字符串中的第 K 位", "Find the Winner of the Circular Game": "找出游戏的获胜者",
}
NOTE = {
 "Hand-drawn definition; the rest field points back to NumList.": "手绘的数据定义，rest 字段用箭头指回 NumList。",
 "Each nested nl-link indented one step further.": "每一层嵌套的 nl-link 多缩进一格。",
 "cons cells drawn as boxes inside boxes, next to their expressions.": "cons 单元画成盒中盒，旁边是对应的表达式。",
 "The same list as a chain of first/rest boxes.": "同一个列表画成 first/rest 盒子组成的链。",
 "A doll contains a smaller doll; used to introduce RD data.": "大娃娃里装着小娃娃，用来引入 RD 数据定义。",
 "Arrows tie the self-reference in the data definition to the recursive call in the template.": "箭头把数据定义里的自指连到模板里的递归调用。",
 "Arguments, intermediate values and results in a table.": "把参数、中间值和结果列成一张表。",
 "Step-by-step rewriting of contains-flatt?, the recursive call left unexpanded until its turn.": "逐步改写 contains-flatt?，递归调用轮到时才展开。",
 "Substitution trace of quicksort; sorted pieces are appended back together.": "quicksort 的代换轨迹，排好序的部分再拼回一起。",
 "The generative template next to the structural one.": "生成递归模板和结构递归模板并排对比。",
 "Each line rewrites the previous one until a value remains.": "每一行改写上一行，直到只剩一个值。",
 "factorial 6 expands into deferred multiplications, then collapses.": "factorial 6 先展开成一串延迟的乘法，再收缩回来。",
 "fib 5 call tree with a dotted line tracing evaluation order.": "fib 5 的调用树，虚线描出求值顺序。",
 "Each call bracketed inside its caller: max 2 (maximum' [5,1]).": "每次调用用括号套在调用者里面：max 2 (maximum' [5,1])。",
 "Pivots in green, placed elements in orange, smaller and bigger lists below.": "pivot 用绿色，已就位的元素用橙色，下面是较小和较大的子列表。",
 "Pictorial metaphor for self-reference.": "用图画比喻自指。",
 "Symbolic nodes f(n/b), cost per level summed on the right.": "节点是符号 f(n/b)，右侧把每层代价加起来。",
 "Root A with subtrees; leaves have no children.": "根 A 带着子树，叶子没有孩子。",
 "A nested Python list drawn as a tree of lists.": "把嵌套的 Python 列表画成列表组成的树。",
 "String states with (i, j) labels; dead branches crossed out.": "字符串状态标上 (i, j)，死路分支打叉。",
 "Six numbered steps push frames onto a stack, then return 12.": "六个编号步骤把栈帧压栈，最后返回 12。",
 "Links redrawn; the rest is said to be handled by the recursion.": "重画指针，并说明剩下的部分交给递归处理。",
 "The rest of the list bracketed and labelled “Recursive”.": "把链表剩余部分括起来，标上“Recursive”。",
 "Before/after with the rest drawn as one “already done” box.": "前后对比，剩余部分画成一个“already done”框。",
 "curr/next links rewired over four frames.": "四帧画出 curr/next 指针的改连。",
 "Input, before swap, after swap and result rows.": "分别画出输入、交换前、交换后和结果四行。",
 "Handwritten stack frames, each returning curr.": "手写的栈帧，每一帧返回 curr。",
 "Return values written under arcs back along the list.": "返回值写在沿链表往回的弧线下方。",
 "First/rest split; “reverse rest” trusted, then relinked.": "拆成 first/rest，先信任“reverse rest”的结果，再改连。",
 "Three frames of node links being reversed.": "三帧画出节点指针被反转的过程。",
 "Columns of head, newHead and head-off per level.": "每一层列出 head、newHead 和断开的 head。",
 "f(32) → f(16) → … → base case, return true back.": "f(32) → f(16) → … → 基本情况，再把 true 传回去。",
 "All expression trees for small inputs; G(3) = 5.": "小输入的所有表达式树；G(3) = 5。",
 "Five expression trees for 2*3-4*5 with their answers.": "2*3-4*5 的五棵表达式树及各自的结果。",
 "Recursion trees with numbered return arrows, split cases I–III, memoisation.": "带编号返回箭头的递归树、I–III 三种切分情况，以及记忆化。",
 "Each node annotated with its list of results.": "每个节点都标出它的结果列表。",
 "a2[b2[cd]]e2[f] expanded level by level, results arrowed back.": "逐层展开 a2[b2[cd]]e2[f]，结果用箭头传回。",
 "P1/P2 levels over (i, j) states.": "在 (i, j) 状态上按 P1/P2 分层。",
 "fib(5) call tree, every call drawn.": "fib(5) 的调用树，每次调用都画出来。",
 "Whiteboard hypothesis → induction → base condition → code.": "白板推导：假设 → 归纳 → 基本条件 → 代码。",
 "The grammar rows drawn as a tree.": "把语法的各行画成一棵树。",
 "Pick a root, box left and right groups, combine subtrees.": "选一个根，左右两组分别框起来，再组合子树。",
 "All five tree shapes for F(7).": "F(7) 的全部五种树形。",
 "(k, n, mid) reduced step by step; “normal world / mirror world”.": "逐步缩小 (k, n, mid)，用“正常世界 / 镜像世界”来解释。",
 "j(n−1, k, i) mapped onto j(n, k, i+1).": "把 j(n−1, k, i) 映射到 j(n, k, i+1)。",
 "Circle, elimination, then n = 7 renumbered onto n = 6 (+4).": "画成圆圈、淘汰，再把 n = 7 重新编号映射到 n = 6（+4）。",
 "Circles relabelled, then f(n, k) = (f(n−1, k) + k − 1) % n + 1.": "圆圈重新编号，再写出 f(n, k) = (f(n−1, k) + k − 1) % n + 1。",
 "Expression trees (same figure as solution 1294189).": "表达式树（与题解 1294189 是同一张图）。",
}
REVIEW = {
 "Branching on * and the (i, j) states are right; the true/false results are never shown coming back.": "按 * 分支和 (i, j) 状态都对，但没画出 true/false 结果怎么传回。",
 "Each frame’s arguments sit on a stack next to the code, and the final return 12 is shown; matches the recursive code.": "每一帧的参数压在代码旁边的栈里，并画出最后返回 12，与递归代码一致。",
 "States plainly that links 3→4 must be fixed first by the recursive call, then relinks 1 and 2; correct order.": "明确说明 3→4 要先由递归调用处理好，再改连 1 和 2，顺序正确。",
 "Only the two hand drawings show the recursive version; the other five images are input/output or the iterative pairwise swap.": "只有两张手绘图是递归版本，其余五张是输入/输出或迭代的两两交换。",
 "Before/after with the rest drawn as an “already done” box: a clean leap-of-faith picture of the recursive step.": "前后对比，剩余部分画成“already done”框，干净地表达了信任递归结果的那一步。",
 "Shows the swap on a two-node list only; the recursive call on the rest never appears.": "只画了两个节点的交换，对剩余部分的递归调用没有出现。",
 "One local swap plus the final list; the recursion on the next pair is a single unexplained arrow.": "只画了一次局部交换和最终链表，对下一对的递归只有一个没解释的箭头。",
 "Handwritten stack frames, each with its pointers and the value it returns; faithful to the recursive code.": "手写栈帧，每一帧都有指针和它返回的值，忠实于递归代码。",
 "Return values on the arcs (2, 2, NULL, NULL) are exactly what each call returns when removing 6.": "弧线上的返回值 (2, 2, NULL, NULL) 正是删除 6 时每次调用的返回值。",
 "The first GIF animates the iterative while-loop; only the second (first / reverse rest / link rest) is the recursion.": "第一张 GIF 画的是迭代的 while 循环，只有第二张（first / reverse rest / link rest）是递归。",
 "Relinking happens innermost-first, which is correct, but calls and returns are not shown.": "改连从最内层开始，这是对的，但没画出调用和返回。",
 "Columns of head, newHead and head-off per level show what each call returns while the list unwinds.": "每层列出 head、newHead 和断开的 head，显示回退时每次调用返回什么。",
 "f(32) → f(16) → … down to the base case, with true passed back up; values correct.": "f(32) → f(16) → … 一直到基本情况，再把 true 传回，数值正确。",
 "Correct expression-tree counts (G(2) = 2, G(3) = 5), but it shows the answer space, not how the recursion builds it.": "表达式树的数量正确（G(2) = 2，G(3) = 5），但画的是答案空间，不是递归怎么构造出来的。",
 "All five trees for 2*3-4*5 and their values (−34, −10, −14, 10, −10) are right; the splitting recursion itself is not drawn.": "2*3-4*5 的五棵树和结果（−34, −10, −14, 10, −10）都对，但没画切分的递归过程本身。",
 "Split-by-operator recursion trees with the resulting values (−34, −14, −10) checked, plus where memoisation helps; one opening slide is a generic Fibonacci tree.": "按运算符切分的递归树，结果（−34, −14, −10）已核对，还说明了记忆化的作用；开头有一张是通用的斐波那契树。",
 "Every node carries its list of results, so the combine step is visible; values check out ([2] × [−17, −5] = [−34, −10]).": "每个节点都带着结果列表，所以能看到合并步骤；数值正确（[2] × [−17, −5] = [−34, −10]）。",
 "a2[b2[cd]]e2[f] expands level by level and the inner results are arrowed back into the outer string; correct.": "a2[b2[cd]]e2[f] 逐层展开，内层结果用箭头传回外层字符串，正确。",
 "Correct (i, j) states for each player, but the scores that come back are not shown.": "每个玩家的 (i, j) 状态都对，但没画出传回的分数。",
 "Correct fib(5) call tree, calls only; it motivates the iterative solution the post actually uses.": "fib(5) 调用树正确，只画了调用；它是用来引出题解实际采用的迭代解法。",
 "Correct hypothesis → induction → base-case reasoning, but the whiteboard is crowded and hard to follow.": "假设 → 归纳 → 基本情况的推理正确，但白板很挤，不容易看懂。",
 "Draws the whole grammar tree; the recursion only walks one root-to-leaf path, which the picture does not distinguish.": "画了整棵语法树，但递归只走一条从根到叶的路径，图里没有区分出来。",
 "Partition and subtree combination are right, but nodes are numbered 1–7 like a BST although full-binary-tree nodes carry no values.": "划分和子树组合都对，但节点像二叉搜索树那样编号 1–7，而真二叉树的节点其实没有值。",
 "All five shapes of F(7) are correct; it shows results, not the recursion.": "F(7) 的五种树形都对；画的是结果，不是递归过程。",
 "A careful step-by-step trace of (k, n, mid), including a deliberately wrong answer that is then corrected with the mirror idea.": "仔细逐步追踪 (k, n, mid)，还故意先给出一个错误答案，再用镜像的思路纠正。",
 "The j(n−1, k, i) / j(n, k, i+1) notation is not explained, so the mapping is hard to verify from the picture.": "j(n−1, k, i) / j(n, k, i+1) 这个记号没有解释，从图上很难核对映射。",
 "Renumbering n = 7 onto n = 6 with +4 (mod 7) is exactly the step the recursion undoes on return; values correct.": "把 n = 7 按 +4（mod 7）重新编号到 n = 6，正是递归返回时要撤回的那一步；数值正确。",
 "Circles relabelled, then f(n, k) = (f(n−1, k) + k − 1) % n + 1 with f(1, k) = 1; correct.": "圆圈重新编号，再写出 f(n, k) = (f(n−1, k) + k − 1) % n + 1，f(1, k) = 1，正确。",
 "Reuses the same expression-tree figure as solution 1294189; correct, but not this author’s own diagram.": "沿用题解 1294189 的同一张表达式树图，内容正确，但不是作者自己画的。",
}
FLAG = {"input only": "仅输入", "iterative pairwise swap": "迭代：两两交换", "output only": "仅输出",
        "iterative (prev/curr)": "迭代（prev/curr）", "iterative while-loop": "迭代 while 循环", "generic Fibonacci example": "通用斐波那契示例"}

D = json.load(open(os.path.join(HERE, "data.json")))
for d in D["dims"]:
    d["name"], d["q"] = DIM[d["id"]]
    newg = []
    for g, cs in d["groups"]:
        for c in cs:
            c["en"] = c["name"]; c["name"], c["desc"] = COD[c["id"]]
            for s in c["subs"]:
                s["en"] = s["name"]; s["name"] = COD[s["id"]][0]
        newg.append([GRP.get(g, g) if g else g, cs])
    d["groups"] = newg
for s in D["sources"]:
    s["name"] = SRC[s["id"]]
for e in D["examples"]:
    en = e["title"]; e["title"] = TITLE[en]
    if e["src"] == "LeetCode":
        m = re.match(r"Solution (\d+) · (\d+) votes", e["sub"])
        e["sub"] = f"{en} · 题解 {m[1]} · {m[2]} 票"
    e["note"] = NOTE[e["note"]]
    if e.get("review"): e["review"] = REVIEW[e["review"]]
    for im in e["imgs"]:
        im["src"] = "../" + im["src"]
        if im.get("flag"): im["flag"] = FLAG[im["flag"]]
json.dump(D, open(os.path.join(HERE, "data_zh.json"), "w"), ensure_ascii=False)
print("ok", len(D["examples"]))
