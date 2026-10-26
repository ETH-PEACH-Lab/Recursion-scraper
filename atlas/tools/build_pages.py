"""Render the English (index.html) and Chinese (zh/index.html) pages from template.html."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
T_EN = """{
 new:'new', hConcept:'Concept', hDim:'Dimension', hCode:'Coding', sources:'Sources', showAll:'Show all', check:'Check:', also:'Also coded as', open:'Open original ↗',
 close:'Close', viewer:'Image viewer', closeViewer:'Close viewer', prev:'Previous image', next:'Next image', emptyNone:'No example coded yet.',
 nEx:n => n + ' examples',
 lede:(c, e, i, f) => `<b>${c} codings</b>, organised as recursion type → concept → how it is drawn, backed by <b>${e} examples</b> and <b>${i} source images</b>${f ? ' in the selected sources' : ' from textbooks and LeetCode'}. Select a coding to see the figures behind it.`,
 emptyFiltered:n => `No examples in the selected sources. Clear the source filter to see the ${n} others.`,
 includes:k => ' Includes ' + k.join(', ') + '.',
 count:(n, i, f) => `${n} examples · ${i} images${f ? ' · filtered' : ''}`,
 enlarge:(j, t) => `Enlarge image ${j} of ${t}`, alt:(t, j) => `${t}, image ${j}`, imgOf:(i, n) => `image ${i} of ${n}`
}"""
T_ZH = """{
 new:'新增', hConcept:'概念', hDim:'维度', hCode:'编码', sources:'来源', showAll:'显示全部', check:'核对：', also:'同时编码为', open:'查看原文 ↗',
 close:'关闭', viewer:'图片查看', closeViewer:'关闭图片', prev:'上一张', next:'下一张', emptyNone:'还没有编码到例子。',
 nEx:n => n + ' 个例子',
 lede:(c, e, i, f) => `共 <b>${c} 个编码</b>，按“递归类型 → 概念 → 怎么画”组织，有 <b>${e} 个例子</b>、<b>${i} 张来源图片</b>${f ? '（已按来源筛选）' : '，来自教材和 LeetCode'}。点击任意编码，查看它背后的原图。`,
 emptyFiltered:n => `所选来源里没有例子。清除来源筛选可以看到另外 ${n} 个。`,
 includes:k => ' 包括' + k.join('、') + '。',
 count:(n, i, f) => `${n} 个例子 · ${i} 张图${f ? ' · 已筛选' : ''}`,
 enlarge:(j, t) => `放大 ${t} 的第 ${j} 张图`, alt:(t, j) => `${t}，第 ${j} 张图`, imgOf:(i, n) => `第 ${i} / ${n} 张`
}"""
PAGES = [
 dict(out="index.html", data="data.json", T=T_EN, title="Recursion Diagram Atlas", langhref="zh/index.html", langcode="zh", langlabel="中文",
      filter="Filter by source", lang="en",
      note="Coding is a first pass by one reviewer; each LeetCode diagram was checked against the solution’s recursive code, and three solutions with misleading or no recursion diagrams were left out. LeetCode = solutions with 5 or more votes from the local scrape (votes are the snapshot). Images are copies kept for review; follow “Open original” for the source."),
 dict(out="zh/index.html", data="data_zh.json", T=T_ZH, title="递归图示图谱", langhref="../", langcode="en", langlabel="English", showlang=True,
      filter="按来源筛选", lang="zh-CN",
      note="编码是一位评审者的第一轮结果；每个 LeetCode 图示都对照题解的递归代码核对过，图示有误导或没画递归的三篇题解已去掉。LeetCode = 本地抓取中 vote ≥ 5 的题解（票数为抓取时的快照）。图片是为评审保存的副本，原始出处请点“查看原文”。"),
]
t = open(os.path.join(HERE, "template.html")).read()
defs = open(os.path.join(HERE, "defs.svg")).read()
for p in PAGES:
    d = open(os.path.join(HERE, p["data"])).read().replace("</", "<\\/")
    html = (t.replace("__DATA__", d).replace("__T__", p["T"]).replace("__DEFS__", defs).replace("__TITLE__", p["title"])
             .replace("__LANGHREF__", p["langhref"]).replace("__LANGCODE__", p["langcode"]).replace("__LANGLABEL__", p["langlabel"])
             .replace("__FILTERLABEL__", p["filter"]).replace("__NOTE__", p["note"]))
    if not p.get("showlang"):
        html = html.replace('<a class="lang" href="%s" hreflang="%s">%s</a>' % (p["langhref"], p["langcode"], p["langlabel"]), '<a class="lang" hidden></a>')
    os.makedirs(os.path.dirname(os.path.join(HERE, p["out"])) or HERE, exist_ok=True)
    open(os.path.join(HERE, p["out"]), "w").write(html)
    # standalone copy for the repo (own doctype + head)
    i = html.index("<div hidden>")
    head = f'<!doctype html>\n<html lang="{p["lang"]}">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0;font:14px system-ui,sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>\n'
    sa = os.path.join(HERE, "standalone", p["out"]); os.makedirs(os.path.dirname(sa), exist_ok=True)
    open(sa, "w").write(head + html[:i] + "</head>\n<body>\n" + html[i:] + "\n</body>\n</html>\n")
print("built")
