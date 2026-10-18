"""
Generate a multi-page static HTML site from scraped LeetCode data.

Pages:
  output/index.html              — problem list
  output/problem_{slug}.html     — solutions for one problem
  output/solution_{id}.html      — full solution content
"""
import json
import re
from pathlib import Path
from datetime import datetime

import markdown as md_lib


def _title_to_slug(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

OUTPUT_DIR = Path("output")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_problems() -> list:
    f = OUTPUT_DIR / "recursion_problems.json"
    if not f.exists():
        return []
    with open(f, encoding="utf-8") as fh:
        return json.load(fh)


def load_filtered() -> set:
    """Return set of selected solution IDs from filtered.json, or empty set if file doesn't exist."""
    f = OUTPUT_DIR / "filtered.json"
    if not f.exists():
        return set()
    with open(f, encoding="utf-8") as fh:
        data = json.load(fh)
    return set(data.get("selected_ids", []))


def load_problems_cn() -> list:
    f = OUTPUT_DIR / "recursion_problems_cn.json"
    if not f.exists():
        return []
    with open(f, encoding="utf-8") as fh:
        return json.load(fh)


def load_filtered_cn() -> set:
    f = OUTPUT_DIR / "filtered_cn.json"
    if not f.exists():
        return set()
    with open(f, encoding="utf-8") as fh:
        data = json.load(fh)
    return set(data.get("selected_ids", []))


# ---------------------------------------------------------------------------
# Markdown → HTML
# ---------------------------------------------------------------------------

_YT_RE = re.compile(
    r"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)[^\s<\"']*"
)


_MD_IMG_RE = re.compile(r'!\[.*?\]\((https?://[^\)\s]+)\)')
_HTML_IMG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)


def _first_image(content: str) -> str:
    m = _MD_IMG_RE.search(content) or _HTML_IMG_RE.search(content)
    return m.group(1) if m else ""


def _all_images(content: str) -> list:
    seen, imgs = set(), []
    for url in _MD_IMG_RE.findall(content) + _HTML_IMG_RE.findall(content):
        if url not in seen:
            seen.add(url)
            imgs.append(url)
    return imgs


_VIMEO_IFRAME_RE = re.compile(
    r'<iframe[^>]+src=["\']https://player\.vimeo\.com/video/(\d+)[^"\']*["\'][^>]*>.*?</iframe>',
    re.IGNORECASE | re.DOTALL,
)
_VIMEO_URL_RE = re.compile(r'https?://(?:www\.)?vimeo\.com/(\d+)[^\s<"\']*')


def _embed_youtube(text: str) -> str:
    def repl(m):
        vid = m.group(1)
        url = f"https://www.youtube.com/watch?v={vid}"
        return (
            f'<div class="video-wrap">'
            f'<iframe src="https://www.youtube-nocookie.com/embed/{vid}" '
            f'width="100%" height="420" frameborder="0" allowfullscreen></iframe>'
            f'</div>'
            f'<div style="text-align:center;margin-top:4px;font-size:.82em">'
            f'<a href="{url}" target="_blank">↗ Open on YouTube</a></div>'
        )
    return _YT_RE.sub(repl, text)


def _embed_vimeo(text: str, editorial_url: str = "") -> str:
    def repl(m):
        url = editorial_url or f"https://vimeo.com/{m.group(1)}"
        label = "▶ Watch Video on LeetCode" if editorial_url else "▶ Watch on Vimeo"
        return (
            f'<a href="{url}" target="_blank" class="vimeo-link">'
            f'{label}'
            f'</a>'
        )
    return _VIMEO_IFRAME_RE.sub(repl, text)


def render_tutorial(raw: str, problem_url: str = "") -> str:
    """Render tutorial/editorial content — keeps math for MathJax, fixes relative images."""
    if not raw:
        return ""
    raw = raw.replace("\\n", "\n").replace("\\t", "\t").replace("\\'", "'").replace('\\"', '"')

    def _unescape(m):
        cp = int(m.group(1), 16)
        return chr(cp) if not (0xD800 <= cp <= 0xDFFF) else ''
    raw = re.sub(r'\\u([0-9a-fA-F]{4})', _unescape, raw)

    # Fix relative image paths ../Figures/... → absolute LeetCode URL
    raw = re.sub(r'\.\./Figures/', 'https://leetcode.com/articles/Figures/', raw)
    # Strip kramdown attribute syntax {:width="..."} that markdown lib can't handle
    raw = re.sub(r'\{:[^}]+\}', '', raw)
    # Remove 4-space indentation from HTML-tag lines — otherwise markdown treats
    # them as indented code blocks and escapes < > as &lt; &gt;
    raw = re.sub(r'\n {4}(<)', r'\n\1', raw)

    # Render markdown first (no nl2br — tutorials use proper paragraphs,
    # and nl2br breaks MathJax by inserting <br> inside $$...$$)
    renderer = md_lib.Markdown(
        extensions=["extra", "fenced_code", "tables", "sane_lists"]
    )
    html = renderer.convert(raw)

    # Replace Vimeo/YouTube iframes AFTER rendering so tags aren't escaped
    editorial_url = f"{problem_url}editorial/" if problem_url else ""
    html = _embed_vimeo(html, editorial_url=editorial_url)
    html = _embed_youtube(html)
    return html


def render_content(raw: str) -> str:
    if not raw:
        return ""
    # LeetCode API returns double-escaped sequences; unescape them
    raw = raw.replace("\\n", "\n").replace("\\t", "\t").replace("\\'", "'").replace('\\"', '"')
    # Decode \uXXXX unicode escapes (e.g. ⭐ → ⭐), skip surrogates
    def _unescape(m):
        cp = int(m.group(1), 16)
        return chr(cp) if not (0xD800 <= cp <= 0xDFFF) else ''
    raw = re.sub(r'\\u([0-9a-fA-F]{4})', _unescape, raw)
    # Strip LaTeX math delimiters $$...$$ — LeetCode users use them for styling,
    # but without KaTeX they show as literal text
    raw = re.sub(r'\$\$([^$]*)\$\$', r'\1', raw)
    # Remove markdown images with empty URLs — renders as <img src=""> which
    # the browser resolves to the current page, causing a security warning
    raw = re.sub(r'!\[[^\]]*\]\(\s*\)', '', raw)
    raw = _embed_youtube(raw)
    renderer = md_lib.Markdown(
        extensions=["extra", "fenced_code", "tables", "nl2br", "sane_lists"]
    )
    return renderer.convert(raw)


# ---------------------------------------------------------------------------
# Shared CSS + chrome
# ---------------------------------------------------------------------------

_CSS = """\
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
     background:#f6f8fa;color:#24292f;line-height:1.6}
a{color:#0969da;text-decoration:none}
a:hover{text-decoration:underline}

/* nav */
.topnav{background:#24292f;padding:14px 28px;display:flex;align-items:center;gap:10px;
        font-size:.9em;flex-wrap:wrap}
.topnav a{color:#cdd9e5}.topnav a:hover{color:#fff;text-decoration:none}
.topnav .sep{color:#555}.topnav .cur{color:#fff}

/* layout */
.wrap{max-width:900px;margin:32px auto;padding:0 16px}
.page-title{font-size:1.7em;font-weight:700;margin-bottom:6px}
.page-sub{color:#57606a;margin-bottom:28px;font-size:.95em}

/* card */
.card{background:#fff;border:1px solid #d0d7de;border-radius:8px;margin-bottom:10px;
      transition:box-shadow .15s}
.card:hover{box-shadow:0 4px 14px rgba(0,0,0,.1)}
.card-inner{padding:18px 22px}
.card-inner a{color:inherit}
.card-inner a:hover{text-decoration:none}
.card-title{font-size:1.05em;font-weight:600;margin-bottom:8px;color:#24292f}
.card-inner a:hover .card-title{color:#0969da}
.meta{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:.82em;color:#57606a}

/* badges */
.badge{display:inline-block;padding:2px 9px;border-radius:12px;font-size:.78em;font-weight:500;white-space:nowrap}
.b-easy{background:#dafbe1;color:#1a7f37}
.b-medium{background:#fff8c5;color:#9a6700}
.b-hard{background:#ffebe9;color:#cf222e}
.b-video{background:#ffebe9;color:#cf222e}
.b-image{background:#ddf4ff;color:#0969da}
.b-tag{background:#edf2ff;color:#3451b2;font-weight:400}

/* solution content */
.sol-header{background:#fff;border:1px solid #d0d7de;border-radius:8px;padding:22px 26px;margin-bottom:12px}
.sol-header .stitle{font-size:1.35em;font-weight:700;margin-bottom:10px}
.sol-body{background:#fff;border:1px solid #d0d7de;border-radius:8px;padding:26px}
.sol-body img{max-width:100%;border-radius:6px;margin:10px 0;display:block}
.sol-body h1,.sol-body h2,.sol-body h3{margin:20px 0 10px;font-weight:600}
.sol-body h1{font-size:1.4em}.sol-body h2{font-size:1.2em}.sol-body h3{font-size:1.05em}
.sol-body p{margin-bottom:12px}
.sol-body pre{background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;
              padding:14px 16px;overflow-x:auto;margin:12px 0;font-size:.88em}
.sol-body code{background:#f6f8fa;padding:2px 5px;border-radius:4px;
               font-size:.88em;font-family:'SFMono-Regular',Consolas,monospace}
.sol-body pre code{background:none;padding:0}
.sol-body ul,.sol-body ol{padding-left:24px;margin-bottom:12px}
.sol-body li{margin-bottom:4px}
.sol-body blockquote{border-left:3px solid #d0d7de;padding-left:14px;
                     color:#57606a;margin:12px 0}
.sol-body table{border-collapse:collapse;width:100%;margin:12px 0}
.sol-body th,.sol-body td{border:1px solid #d0d7de;padding:7px 12px;text-align:left}
.sol-body th{background:#f6f8fa;font-weight:600}
.sol-body hr{border:none;border-top:1px solid #d0d7de;margin:18px 0}
.sol-body strong{font-weight:600}
.video-wrap{margin:14px 0;border-radius:6px;overflow:hidden}
.video-wrap iframe{border-radius:6px}
.empty{text-align:center;padding:48px;color:#57606a;background:#fff;
       border:1px solid #d0d7de;border-radius:8px}
.lc-link{font-size:.8em;color:#0969da;white-space:nowrap}
.lc-link:hover{text-decoration:underline}
.sub-btns{display:flex;gap:10px;flex-wrap:wrap}
.sub-btn{display:inline-flex;align-items:center;gap:6px;padding:7px 16px;
         border-radius:6px;font-size:.88em;font-weight:500;text-decoration:none;
         transition:background .15s,transform .1s}
.sub-btn:hover{transform:translateY(-1px);text-decoration:none}
.sub-tut{background:#dafbe1;color:#1a7f37;border:1px solid #aef0b7}
.sub-tut:hover{background:#c6f0ce}
.sub-sol{background:#ddf4ff;color:#0550ae;border:1px solid #aad9f9}
.sub-sol:hover{background:#c5e8fa}
.sub-none{background:#f6f8fa;color:#8c959f;border:1px solid #d0d7de;cursor:default}
.sub-count{background:rgba(0,0,0,.08);border-radius:10px;padding:1px 7px;font-size:.85em}
.no-sol-section{margin-top:24px;border:1px solid #d0d7de;border-radius:8px;
                background:#fff;overflow:hidden}
.no-sol-section summary{padding:14px 20px;font-weight:600;font-size:.95em;
                         color:#57606a;cursor:pointer;user-select:none;
                         list-style:none;display:flex;align-items:center;gap:8px}
.no-sol-section summary::before{content:"▶";font-size:.7em;transition:transform .2s}
.no-sol-section[open] summary::before{transform:rotate(90deg)}
.no-sol-section summary:hover{background:#f6f8fa}
.no-sol-list{padding:12px 12px 4px;border-top:1px solid #d0d7de}

/* review page */
.review-bar{position:sticky;top:0;z-index:100;background:#24292f;
            padding:12px 24px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.review-bar .r-counter{color:#cdd9e5;font-size:.9em}
.review-bar button{padding:8px 18px;border:none;border-radius:6px;cursor:pointer;
                   font-size:.88em;font-weight:600}
.btn-export{background:#2ea043;color:#fff}.btn-export:hover{background:#3fb950}
.btn-clear{background:#444;color:#cdd9e5}.btn-clear:hover{background:#555}
.pagination{display:flex;align-items:center;gap:10px;justify-content:center;
            padding:24px 0 8px}
.pagination button{padding:7px 16px;border:1px solid #d0d7de;border-radius:6px;
                   background:#fff;cursor:pointer;font-size:.9em;font-weight:500}
.pagination button:hover:not(:disabled){background:#f6f8fa;border-color:#0969da;color:#0969da}
.pagination button:disabled{opacity:.4;cursor:default}
.pagination .page-info{color:#57606a;font-size:.88em;min-width:140px;text-align:center}
.page-input{width:54px;padding:5px 8px;border:1px solid #d0d7de;border-radius:6px;
            font-size:.9em;text-align:center;-moz-appearance:textfield}
.page-input::-webkit-inner-spin-button,.page-input::-webkit-outer-spin-button{-webkit-appearance:none}
.filter-btn{padding:5px 12px;border:1px solid #555;border-radius:6px;background:transparent;
            color:#cdd9e5;cursor:pointer;font-size:.82em;white-space:nowrap}
.filter-btn:hover{border-color:#aaa;color:#fff}
.filter-btn-active{background:#2ea043;border-color:#2ea043;color:#fff}
.r-problem{margin-bottom:28px}
.r-problem-title{font-size:1.05em;font-weight:700;padding:10px 0 8px;
                 border-bottom:2px solid #d0d7de;margin-bottom:10px;
                 display:flex;align-items:center;gap:10px}
.r-problem-title a{color:#0969da;font-size:.85em;font-weight:400}
.sol-row{padding:10px 14px;border:1px solid #d0d7de;border-radius:8px;
         margin-bottom:8px;background:#fff;transition:background .15s}
.sol-row.unselected{background:#f6f8fa;border-color:#d0d7de;opacity:.55}
.sol-row input[type=checkbox]{margin-top:4px;width:17px;height:17px;
                               flex-shrink:0;cursor:pointer;accent-color:#2ea043}
.sol-row .r-info{flex:1;min-width:0}
.sol-row .r-title{font-weight:600;font-size:.95em;margin-bottom:5px;
                  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sol-row .r-title a{color:#24292f}.sol-row .r-title a:hover{color:#0969da}
.sol-row .r-meta{font-size:.8em;color:#57606a;display:flex;gap:10px;flex-wrap:wrap}
.sol-row .r-thumbs{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.sol-row .r-thumbs img{width:120px;height:80px;object-fit:cover;border-radius:5px;
                        border:1px solid #d0d7de;cursor:zoom-in;transition:transform .15s}
.sol-row .r-thumbs img:hover{transform:scale(1.05);z-index:1;position:relative}
.sol-row .r-novid{display:inline-flex;align-items:center;justify-content:center;
                  width:120px;height:80px;border-radius:5px;border:1px solid #d0d7de;
                  font-size:2em;background:#f6f8fa}
</style>"""


def _nav(*crumbs) -> str:
    parts = []
    for i, (label, href) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            parts.append(f'<span class="cur">{label}</span>')
        else:
            parts.append(f'<a href="{href}">{label}</a>')
        if i < len(crumbs) - 1:
            parts.append('<span class="sep">›</span>')
    inner = " ".join(parts)
    return f'<nav class="topnav">{inner}</nav>'


def _diff_badge(difficulty: str) -> str:
    cls = {"Easy": "b-easy", "Medium": "b-medium", "Hard": "b-hard"}.get(difficulty, "b-tag")
    return f'<span class="badge {cls}">{difficulty}</span>'


def _page(title: str, nav: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
{_CSS}
</head>
<body>
{nav}
<div class="wrap">
{body}
</div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Page generators
# ---------------------------------------------------------------------------

def _problem_card(p: dict) -> str:
    slug = p["title_slug"]
    sols = p.get("solutions") or []
    n = len(sols)
    has_video = any(s.get("has_video") for s in sols)
    has_image = any(s.get("has_image") for s in sols)

    tags = " ".join(
        f'<span class="badge b-tag">{t}</span>'
        for t in (p.get("topic_tags") or [])[:5]
    )
    media = ""
    if has_video:
        media += '<span class="badge b-video">📹</span>'
    if has_image:
        media += '<span class="badge b-image">🖼</span>'

    lc_link = f'<a href="{p.get("url","")}" target="_blank" class="lc-link">↗ LeetCode</a>'

    sub_btns = []
    if p.get("tutorial"):
        sub_btns.append(f'<a href="tutorial_{slug}.html" class="sub-btn sub-tut">📖 Tutorial</a>')
    if n > 0:
        sub_btns.append(f'<a href="problem_{slug}.html" class="sub-btn sub-sol">💬 Solutions <span class="sub-count">{n}</span></a>')
    if not sub_btns:
        sub_btns.append('<span class="sub-btn sub-none">No content yet</span>')

    return f"""<div class="card">
  <div class="card-inner">
    <div class="card-title">{p['question_id']}. {p['title']}</div>
    <div class="meta" style="margin-bottom:12px">
      {_diff_badge(p.get('difficulty',''))}
      {tags}
      {media}
      {lc_link}
    </div>
    <div class="sub-btns">{"".join(sub_btns)}</div>
  </div>
</div>"""


def gen_index(problems: list) -> str:
    total_sols = sum(len(p.get("solutions") or []) for p in problems)
    with_sols = sum(1 for p in problems if p.get("solutions"))

    with_cards = [_problem_card(p) for p in problems if p.get("solutions")]
    without_cards = [_problem_card(p) for p in problems if not p.get("solutions")]

    main_section = "".join(with_cards) if with_cards else '<div class="empty">暂无数据，请先运行 python scraper.py</div>'

    collapsed = ""
    if without_cards:
        collapsed = f"""<details class="no-sol-section">
  <summary>暂无 Solutions 的题目（{len(without_cards)} 道）</summary>
  <div class="no-sol-list">{"".join(without_cards)}</div>
</details>"""

    body = f"""<div class="page-title">LeetCode Recursion Solutions</div>
<div class="page-sub">{len(problems)} 道题 &nbsp;·&nbsp; {with_sols} 道有 Solutions &nbsp;·&nbsp; {total_sols} 个包含图片/视频的 Solutions</div>
{main_section}
{collapsed}"""

    return _page(
        "LeetCode Recursion Solutions",
        _nav(("🔄 Recursion Solutions", "index.html")),
        body,
    )


_MATHJAX = """\
<script>
MathJax = {
  tex: { inlineMath: [['$','$'],['\\\\(','\\\\)']], displayMath: [['$$','$$'],['\\\\[','\\\\]']] },
  options: { skipHtmlTags: ['script','noscript','style','textarea','pre'] }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>"""

_VIMEO_EXTRA_CSS = """\
.vimeo-link{display:inline-flex;align-items:center;gap:8px;
            background:#1ab7ea;color:#fff;font-weight:600;
            padding:10px 20px;border-radius:6px;margin:12px 0;font-size:.95em}
.vimeo-link:hover{background:#0d9bd4;color:#fff;text-decoration:none}"""


def gen_tutorial_page(p: dict) -> str:
    slug = p["title_slug"]
    tags = " ".join(
        f'<span class="badge b-tag">{t}</span>'
        for t in (p.get("topic_tags") or [])
    )
    content_html = render_tutorial(p.get("tutorial", ""), problem_url=p.get("url", ""))

    body = f"""<div class="page-title">{p['question_id']}. {p['title']} — Official Editorial</div>
<div class="page-sub" style="margin-bottom:20px">
  {_diff_badge(p.get('difficulty',''))} {tags}
  &nbsp;
  <a href="{p.get('url','')}" target="_blank" style="font-size:.85em">↗ Problem</a>
  &nbsp;·&nbsp;
  <a href="problem_{slug}.html" style="font-size:.85em">💬 Community Solutions</a>
</div>
<div class="sol-body">
  {content_html or '<p style="color:#57606a">No editorial available.</p>'}
</div>"""

    # Tutorial page gets its own template with MathJax + Vimeo CSS
    nav = _nav(
        ("🔄 Recursion Solutions", "index.html"),
        (p["title"], f"problem_{slug}.html"),
        ("Editorial", f"tutorial_{slug}.html"),
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{p['title']} – Editorial</title>
{_CSS}
<style>{_VIMEO_EXTRA_CSS}</style>
{_MATHJAX}
</head>
<body>
{nav}
<div class="wrap">{body}</div>
</body>
</html>"""


def gen_problem_page(p: dict) -> str:
    slug = p["title_slug"]
    sols = p.get("solutions") or []

    tags = " ".join(
        f'<span class="badge b-tag">{t}</span>'
        for t in (p.get("topic_tags") or [])
    )

    cards = []
    for s in sols:
        sid = s.get("id", "")
        media = ""
        if s.get("has_video"):
            media += '<span class="badge b-video">📹</span>'
        if s.get("has_image"):
            media += '<span class="badge b-image">🖼</span>'
        cards.append(f"""<div class="card">
  <div class="card-inner">
    <a href="solution_{sid}.html"><div class="card-title">{s.get('title','Untitled')}</div></a>
    <div class="meta">
      <span>👤 {s.get('author','Unknown')}</span>
      <span>👍 {s.get('votes',0)}</span>
      {media}
    </div>
  </div>
</div>""")

    tutorial_link = (
        f'&nbsp;·&nbsp;<a href="tutorial_{slug}.html" style="font-size:.85em">📖 Official Editorial</a>'
        if p.get("tutorial") else ""
    )
    body = f"""<div class="page-title">{p['question_id']}. {p['title']}</div>
<div class="page-sub">
  {_diff_badge(p.get('difficulty',''))} {tags}
  &nbsp;
  <a href="{p.get('url','')}" target="_blank" style="font-size:.85em">↗ Problem</a>
  {tutorial_link}
</div>
{"".join(cards) if cards else '<div class="empty">No solutions found.</div>'}"""

    return _page(
        f"{p['title']} – Solutions",
        _nav(
            ("🔄 Recursion Solutions", "index.html"),
            (p["title"], f"problem_{slug}.html"),
        ),
        body,
    )


def gen_solution_page(s: dict, problem: dict) -> str:
    slug = problem["title_slug"]
    ptitle = problem["title"]
    sid = s.get("id", "")

    content_html = render_content(s.get("content", ""))

    media = ""
    if s.get("has_video"):
        media += '<span class="badge b-video">📹</span>'
    if s.get("has_image"):
        media += '<span class="badge b-image">🖼</span>'

    created = s.get("created_at", "")
    if created and str(created).isdigit():
        created = datetime.fromtimestamp(int(created)).strftime("%Y-%m-%d")

    body = f"""<div class="sol-header">
  <div class="stitle">{s.get('title','Solution')}</div>
  <div class="meta">
    <span>👤 {s.get('author','Unknown')}</span>
    <span>👍 {s.get('votes',0)}</span>
    {f'<span>{created}</span>' if created else ''}
    {media}
    <a href="https://leetcode.com/problems/{slug}/solutions/{sid}/{_title_to_slug(s.get('title',''))}/" target="_blank" style="font-size:.85em">↗ 查看原 Solution</a>
  </div>
</div>
<div class="sol-body">
  {content_html or '<p style="color:#57606a">内容为空，请重新运行 scraper.py 获取完整内容。</p>'}
</div>"""

    return _page(
        f"{s.get('title','Solution')} – {ptitle}",
        _nav(
            ("🔄 Recursion Solutions", "index.html"),
            (ptitle, f"problem_{slug}.html"),
            (s.get("title", "Solution"), f"solution_{sid}.html"),
        ),
        body,
    )


# ---------------------------------------------------------------------------
# CN solution page
# ---------------------------------------------------------------------------

_BILI_RE = re.compile(
    r'https?://(?:www\.)?(?:bilibili\.com/video|b23\.tv)/([\w]+)[^\s<"\']*',
    re.IGNORECASE,
)


def _render_content_cn(raw: str) -> str:
    """Render CN solution content — handles bilibili embeds and CN image CDNs."""
    if not raw:
        return ""
    raw = raw.replace("\\n", "\n").replace("\\t", "\t").replace("\\'", "'").replace('\\"', '"')

    def _unescape(m):
        cp = int(m.group(1), 16)
        return chr(cp) if not (0xD800 <= cp <= 0xDFFF) else ''
    raw = re.sub(r'\\u([0-9a-fA-F]{4})', _unescape, raw)
    raw = re.sub(r'\$\$([^$]*)\$\$', r'\1', raw)
    raw = re.sub(r'!\[[^\]]*\]\(\s*\)', '', raw)

    # Bilibili embed
    def _bili_repl(m):
        bid = m.group(1)
        url = f"https://www.bilibili.com/video/{bid}"
        return (
            f'<a href="{url}" target="_blank" class="vimeo-link" style="background:#00a1d6">'
            f'▶ 在 Bilibili 观看'
            f'</a>'
        )
    raw = _BILI_RE.sub(_bili_repl, raw)
    raw = _embed_youtube(raw)

    renderer = md_lib.Markdown(
        extensions=["extra", "fenced_code", "tables", "nl2br", "sane_lists"]
    )
    return renderer.convert(raw)


def gen_solution_page_cn(s: dict, problem: dict) -> str:
    slug = problem["title_slug"]
    ptitle = problem.get("title", "")
    title_cn = problem.get("title_cn", "")
    sid = s.get("id", "")

    content_html = _render_content_cn(s.get("content", ""))

    badges = ""
    if s.get("is_official"):
        badges += '<span class="badge" style="background:#fff3c4;color:#9a6700">🏆 Official</span>'
    if s.get("has_video"):
        badges += '<span class="badge b-video">📹</span>'
    if s.get("has_image"):
        badges += '<span class="badge b-image">🖼</span>'
    if s.get("has_slide"):
        badges += '<span class="badge" style="background:#f0f0ff;color:#5b21b6">🎞 Slide</span>'

    created = s.get("created_at", "")
    if created:
        try:
            created = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except:
            created = str(created)[:10]

    prob_label = f"{ptitle} / {title_cn}" if title_cn else ptitle

    body = f"""<div class="sol-header">
  <div class="stitle">{s.get('title','Solution')}</div>
  <div class="meta">
    <span>👤 {s.get('author','Unknown')}</span>
    <span>👍 {s.get('votes',0)}</span>
    {f'<span>{created}</span>' if created else ''}
    {badges}
    <a href="{s.get('url','')}" target="_blank" style="font-size:.85em">↗ 查看原 Solution</a>
  </div>
</div>
<div class="sol-body">
  {content_html or '<p style="color:#57606a">内容为空。</p>'}
</div>"""

    return _page(
        f"{s.get('title','Solution')} – {ptitle}",
        _nav(
            ("🔄 Recursion Solutions", "index.html"),
            (prob_label, f"problem_{slug}.html"),
            (s.get("title", "Solution"), f"solution_cn_{sid}.html"),
        ),
        body,
    )


# ---------------------------------------------------------------------------
# Review page
# ---------------------------------------------------------------------------

def gen_review(problems: list) -> str:
    rows_by_problem = []
    total = 0

    for p in problems:
        sols = p.get("solutions") or []
        if not sols:
            continue
        rows = []
        for s in sols:
            sid = s.get("id", "")
            content = s.get("content", "")
            all_imgs = _all_images(content)
            yt_matches = _YT_RE.findall(content)

            thumbs = []
            for url in all_imgs:
                thumbs.append(f'<img src="{url}" loading="lazy" onerror="this.style.display=\'none\'" title="{url}">')
            for vid_id in yt_matches:
                thumbs.append(f'<img src="https://img.youtube.com/vi/{vid_id}/default.jpg" loading="lazy" onerror="this.style.display=\'none\'" title="YouTube: {vid_id}">')
            if not thumbs and s.get("has_video"):
                thumbs.append('<span class="r-novid">📹</span>')

            thumb_html = f'<div class="r-thumbs">{"".join(thumbs)}</div>' if thumbs else ""

            created = s.get("created_at", "")
            if created and str(created).isdigit():
                created = datetime.fromtimestamp(int(created)).strftime("%Y-%m-%d")

            media_badges = ""
            if s.get("has_video"):
                media_badges += '<span class="badge b-video">📹</span>'
            if s.get("has_image"):
                media_badges += '<span class="badge b-image">🖼</span>'

            votes = s.get('votes', 0)
            dv = "1" if s.get("has_video") else "0"
            di = "1" if s.get("has_image") else "0"
            rows.append(f"""<div class="sol-row" id="row-{sid}" data-id="{sid}" data-votes="{votes}" data-video="{dv}" data-image="{di}">
  <div style="display:flex;align-items:flex-start;gap:10px">
    <input type="checkbox" id="cb-{sid}" checked onchange="toggle('{sid}',this.checked)" style="margin-top:3px">
    <div class="r-info">
      <div class="r-title"><a href="solution_{sid}.html" target="_blank">{s.get('title','Untitled')}</a></div>
      <div class="r-meta">
        <span>👤 {s.get('author','Unknown')}</span>
        <span>👍 {votes}</span>
        {f'<span>{created}</span>' if created else ''}
        {media_badges}
      </div>
    </div>
  </div>
  {thumb_html}
</div>""")
            total += 1

        slug = p["title_slug"]
        rows_by_problem.append(f"""<div class="r-problem">
  <div class="r-problem-title">
    {p['question_id']}. {p['title']}
    {_diff_badge(p.get('difficulty',''))}
    <a href="problem_{slug}.html" target="_blank">↗ View Solutions</a>
  </div>
  {"".join(rows)}
</div>""")

    review_js = """
<script>
const KEY = 'lc-selected';
const PAGE_SIZE = 20;
let currentPage = 1;
const activeFilters = new Set(); // 'selected' | 'unselected' | 'video' | 'image'

function allIds() {
  return [...document.querySelectorAll('.sol-row')].map(r => r.dataset.id);
}
function loadSel() {
  const saved = localStorage.getItem(KEY);
  if (saved !== null) { try { return new Set(JSON.parse(saved)); } catch {} }
  return new Set(allIds());
}
function saveSel(s) { localStorage.setItem(KEY, JSON.stringify([...s])); }

function minVotes() {
  return parseInt(document.getElementById('votes-slider').value || '0');
}
function filteredRows() {
  const mv = minVotes();
  const sel = loadSel();
  return [...document.querySelectorAll('.sol-row')].filter(r => {
    if (parseInt(r.dataset.votes || '0') < mv) return false;
    if (activeFilters.has('selected')   && !sel.has(r.dataset.id))    return false;
    if (activeFilters.has('unselected') && sel.has(r.dataset.id))     return false;
    if (activeFilters.has('video')      && r.dataset.video !== '1')   return false;
    if (activeFilters.has('image')      && r.dataset.image !== '1')   return false;
    return true;
  });
}
function toggleFilter(f) {
  activeFilters.has(f) ? activeFilters.delete(f) : activeFilters.add(f);
  currentPage = 1;
  document.querySelectorAll('.filter-btn').forEach(b => {
    b.classList.toggle('filter-btn-active', activeFilters.has(b.dataset.filter));
  });
  render();
}

function render() {
  const rows = filteredRows();
  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  if (currentPage > totalPages) currentPage = totalPages;

  const pageSet = new Set(
    rows.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)
        .map(r => r.dataset.id)
  );
  const mv = minVotes();

  document.querySelectorAll('.sol-row').forEach(r => {
    const votes = parseInt(r.dataset.votes || '0');
    r.style.display = (votes >= mv && pageSet.has(r.dataset.id)) ? '' : 'none';
  });
  document.querySelectorAll('.r-problem').forEach(sec => {
    sec.style.display = [...sec.querySelectorAll('.sol-row')]
      .some(r => r.style.display !== 'none') ? '' : 'none';
  });

  const sel = loadSel();
  document.getElementById('r-counter').textContent =
    `${document.querySelectorAll('.sol-row').length} total · ${sel.size} selected`;
  document.getElementById('votes-label').textContent =
    `≥ ${mv} votes: ${rows.length} solutions`;
  document.querySelectorAll('.page-input').forEach(el => el.value = currentPage);
  document.querySelectorAll('.page-total').forEach(el => el.textContent = totalPages);
  document.querySelectorAll('.btn-prev').forEach(b => b.disabled = currentPage <= 1);
  document.querySelectorAll('.btn-next').forEach(b => b.disabled = currentPage >= totalPages);
}

function toggle(id, checked) {
  const sel = loadSel();
  checked ? sel.add(id) : sel.delete(id);
  saveSel(sel);
  const row = document.getElementById('row-' + id);
  if (row) row.classList.toggle('unselected', !checked);
  document.getElementById('r-counter').textContent =
    `${document.querySelectorAll('.sol-row').length} total · ${sel.size} selected`;
}
function exportFiltered() {
  const sel = loadSel();
  const blob = new Blob(
    [JSON.stringify({selected_ids:[...sel], exported_at:new Date().toISOString()}, null, 2)],
    {type:'application/json'}
  );
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'filtered.json';
  a.click();
}
function resetAll() {
  if (!confirm('Reset all selections?')) return;
  localStorage.removeItem(KEY);
  document.querySelectorAll('.sol-row input').forEach(cb => { cb.checked = true; });
  document.querySelectorAll('.sol-row').forEach(r => r.classList.remove('unselected'));
  render();
}
function prevPage() { if (currentPage > 1) { currentPage--; render(); scrollToTop(); } }
function nextPage() { currentPage++; render(); scrollToTop(); }
function goToPage(val) {
  const rows = filteredRows();
  const total = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  const n = parseInt(val);
  if (!isNaN(n) && n >= 1 && n <= total) { currentPage = n; render(); scrollToTop(); }
}
function clearFilters() {
  activeFilters.clear();
  currentPage = 1;
  document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.remove('filter-btn-active'));
  render();
}
function scrollToTop() { document.querySelector('.wrap').scrollIntoView({behavior:'smooth'}); }

window.addEventListener('DOMContentLoaded', () => {
  const allVotes = [...document.querySelectorAll('.sol-row')]
    .map(r => parseInt(r.dataset.votes||'0'));
  document.getElementById('votes-slider').max = Math.max(...allVotes, 0);
  document.getElementById('votes-slider').addEventListener('input', () => {
    currentPage = 1; render();
  });

  const sel = loadSel();
  document.querySelectorAll('.sol-row').forEach(row => {
    const id = row.dataset.id;
    if (!sel.has(id)) {
      const cb = document.getElementById('cb-' + id);
      if (cb) cb.checked = false;
      row.classList.add('unselected');
    }
  });
  render();
});
</script>"""

    pagination_top = """<div class="pagination" style="padding:8px 0 0">
  <button class="btn-prev" onclick="prevPage()">← Prev</button>
  <input class="page-input" type="number" min="1" value="1"
    onchange="goToPage(this.value)"
    onkeydown="if(event.key==='Enter')goToPage(this.value)">
  <span style="color:#57606a;font-size:.88em">/ <span class="page-total">—</span></span>
  <button class="btn-next" onclick="nextPage()">Next →</button>
</div>"""

    pagination_bot = """<div class="pagination">
  <button class="btn-prev" onclick="prevPage()">← Prev</button>
  <input class="page-input" type="number" min="1" value="1"
    onchange="goToPage(this.value)"
    onkeydown="if(event.key==='Enter')goToPage(this.value)">
  <span style="color:#57606a;font-size:.88em">/ <span class="page-total">—</span></span>
  <button class="btn-next" onclick="nextPage()">Next →</button>
</div>"""

    content = "".join(rows_by_problem) if rows_by_problem else '<div class="empty">No data — run scraper.py first</div>'

    body = f"""<div class="review-bar">
  <span id="r-counter" class="r-counter">Loading…</span>
  <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
    <button class="filter-btn" data-filter="selected"   onclick="toggleFilter('selected')">✅ Selected</button>
    <button class="filter-btn" data-filter="unselected" onclick="toggleFilter('unselected')">☐ Unselected</button>
    <button class="filter-btn" data-filter="video"      onclick="toggleFilter('video')">📹 Video</button>
    <button class="filter-btn" data-filter="image"      onclick="toggleFilter('image')">🖼 Image</button>
    <button class="filter-btn" onclick="clearFilters()" style="opacity:.7">✕ Clear</button>
  </div>
  <div style="display:flex;align-items:center;gap:8px">
    <label style="color:#cdd9e5;font-size:.85em;white-space:nowrap">Min votes</label>
    <input id="votes-slider" type="range" min="0" max="1000" value="0"
           style="width:140px;accent-color:#2ea043">
    <span id="votes-label" style="color:#2ea043;font-size:.85em;white-space:nowrap;min-width:120px">≥ 0 votes</span>
  </div>
  {pagination_top}
  <button class="btn-export" onclick="exportFiltered()">⬇ Export filtered</button>
  <button class="btn-clear" onclick="resetAll()">Reset</button>
</div>
<div class="wrap">
{content}
{pagination_bot}
</div>
{review_js}"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Solution Review</title>
{_CSS}
</head>
<body>
{body}
</body>
</html>"""


# ---------------------------------------------------------------------------
# CN Review page
# ---------------------------------------------------------------------------

def gen_review_cn(problems: list) -> str:
    """Generate review_cn.html for LeetCode CN scraped solutions."""
    rows_by_problem = []

    for p in problems:
        sols = p.get("solutions") or []
        if not sols:
            continue
        rows = []
        for s in sols:
            sid = s.get("id", "")
            content = s.get("content", "")
            thumbnail = s.get("thumbnail", "")

            # Use API thumbnail first; fall back to all images from content
            thumb_urls = []
            if thumbnail:
                thumb_urls.append(thumbnail)
            else:
                thumb_urls = _all_images(content)
            for vid_id in _YT_RE.findall(content):
                thumb_urls.append(f"https://img.youtube.com/vi/{vid_id}/default.jpg")

            thumbs = [
                f'<img src="{u}" loading="lazy" '
                f'style="height:80px;width:auto;max-width:160px;border-radius:5px;'
                f'border:1px solid #d0d7de;object-fit:cover;display:block" '
                f'onerror="this.remove()">'
                for u in thumb_urls
            ]
            thumb_html = (
                f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">{"".join(thumbs)}</div>'
                if thumbs else ""
            )

            created = s.get("created_at", "")
            if created:
                try:
                    from datetime import datetime, timezone
                    created = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                except:
                    created = str(created)[:10]

            badges = ""
            if s.get("is_official"):
                badges += '<span class="badge" style="background:#fff3c4;color:#9a6700">🏆 Official</span>'
            if s.get("has_video"):
                badges += '<span class="badge b-video">📹</span>'
            if s.get("has_image"):
                badges += '<span class="badge b-image">🖼</span>'
            if s.get("has_slide"):
                badges += '<span class="badge" style="background:#f0f0ff;color:#5b21b6">🎞 Slide</span>'

            votes = s.get("votes", 0)
            dv = "1" if s.get("has_video") else "0"
            di = "1" if s.get("has_image") else "0"

            rows.append(f"""<div class="sol-row" id="row-{sid}" data-id="{sid}" data-votes="{votes}" data-video="{dv}" data-image="{di}">
  <div style="display:flex;align-items:flex-start;gap:10px">
    <input type="checkbox" id="cb-{sid}" checked onchange="toggle('{sid}',this.checked)" style="margin-top:3px">
    <div class="r-info">
      <div class="r-title"><a href="solution_cn_{sid}.html" target="_blank">{s.get('title','Untitled')}</a></div>
      <div class="r-meta">
        <span>👤 {s.get('author','Unknown')}</span>
        <span>👍 {votes}</span>
        {f'<span>{created}</span>' if created else ''}
        {badges}
      </div>
    </div>
  </div>
  {thumb_html}
</div>""")

        slug = p["title_slug"]
        title_cn = p.get("title_cn") or p.get("title", "")
        rows_by_problem.append(f"""<div class="r-problem">
  <div class="r-problem-title">
    {p.get('question_id','')}. {p.get('title','')} <span style="color:#57606a;font-weight:400">/ {title_cn}</span>
    {_diff_badge(p.get('difficulty',''))}
    <a href="{p.get('url','')}" target="_blank">↗ LeetCode CN</a>
  </div>
  {"".join(rows)}
</div>""")

    # Reuse the same JS but with different localStorage key and export filename
    review_js = """
<script>
const KEY = 'lc-selected-cn';
const PAGE_SIZE = 20;
let currentPage = 1;
const activeFilters = new Set();

function allIds() { return [...document.querySelectorAll('.sol-row')].map(r => r.dataset.id); }
function loadSel() {
  const saved = localStorage.getItem(KEY);
  if (saved !== null) { try { return new Set(JSON.parse(saved)); } catch {} }
  return new Set(allIds());
}
function saveSel(s) { localStorage.setItem(KEY, JSON.stringify([...s])); }
function minVotes() { return parseInt(document.getElementById('votes-slider').value || '0'); }
function filteredRows() {
  const mv = minVotes(); const sel = loadSel();
  return [...document.querySelectorAll('.sol-row')].filter(r => {
    if (parseInt(r.dataset.votes||'0') < mv) return false;
    if (activeFilters.has('selected')   && !sel.has(r.dataset.id))  return false;
    if (activeFilters.has('unselected') && sel.has(r.dataset.id))   return false;
    if (activeFilters.has('video')      && r.dataset.video !== '1') return false;
    if (activeFilters.has('image')      && r.dataset.image !== '1') return false;
    return true;
  });
}
function toggleFilter(f) {
  activeFilters.has(f) ? activeFilters.delete(f) : activeFilters.add(f);
  currentPage = 1;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.toggle('filter-btn-active', activeFilters.has(b.dataset.filter)));
  render();
}
function render() {
  const rows = filteredRows();
  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  if (currentPage > totalPages) currentPage = totalPages;
  const pageSet = new Set(rows.slice((currentPage-1)*PAGE_SIZE, currentPage*PAGE_SIZE).map(r=>r.dataset.id));
  const mv = minVotes();
  document.querySelectorAll('.sol-row').forEach(r => {
    const votes = parseInt(r.dataset.votes||'0');
    r.style.display = (votes>=mv && pageSet.has(r.dataset.id)) ? '' : 'none';
  });
  document.querySelectorAll('.r-problem').forEach(sec => {
    sec.style.display = [...sec.querySelectorAll('.sol-row')].some(r=>r.style.display!=='none') ? '' : 'none';
  });
  const sel = loadSel();
  document.getElementById('r-counter').textContent = `${document.querySelectorAll('.sol-row').length} total · ${sel.size} selected`;
  document.getElementById('votes-label').textContent = `≥ ${mv} votes: ${rows.length} solutions`;
  document.querySelectorAll('.page-input').forEach(el => el.value = currentPage);
  document.querySelectorAll('.page-total').forEach(el => el.textContent = totalPages);
  document.querySelectorAll('.btn-prev').forEach(b => b.disabled = currentPage<=1);
  document.querySelectorAll('.btn-next').forEach(b => b.disabled = currentPage>=totalPages);
}
function toggle(id, checked) {
  const sel = loadSel();
  checked ? sel.add(id) : sel.delete(id);
  saveSel(sel);
  const row = document.getElementById('row-'+id);
  if (row) row.classList.toggle('unselected', !checked);
  document.getElementById('r-counter').textContent = `${document.querySelectorAll('.sol-row').length} total · ${sel.size} selected`;
}
function exportFiltered() {
  const sel = loadSel();
  const blob = new Blob([JSON.stringify({selected_ids:[...sel],exported_at:new Date().toISOString()},null,2)],{type:'application/json'});
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download='filtered_cn.json'; a.click();
}
function resetAll() {
  if (!confirm('Reset all selections?')) return;
  localStorage.removeItem(KEY);
  document.querySelectorAll('.sol-row input').forEach(cb=>{cb.checked=true;});
  document.querySelectorAll('.sol-row').forEach(r=>r.classList.remove('unselected'));
  render();
}
function clearFilters() {
  activeFilters.clear(); currentPage=1;
  document.querySelectorAll('.filter-btn[data-filter]').forEach(b=>b.classList.remove('filter-btn-active'));
  render();
}
function prevPage() { if(currentPage>1){currentPage--;render();scrollToTop();} }
function nextPage() { currentPage++;render();scrollToTop(); }
function goToPage(val) {
  const total=Math.max(1,Math.ceil(filteredRows().length/PAGE_SIZE));
  const n=parseInt(val);
  if(!isNaN(n)&&n>=1&&n<=total){currentPage=n;render();scrollToTop();}
}
function scrollToTop() { document.querySelector('.wrap').scrollIntoView({behavior:'smooth'}); }

window.addEventListener('DOMContentLoaded', () => {
  const allVotes = [...document.querySelectorAll('.sol-row')].map(r=>parseInt(r.dataset.votes||'0'));
  document.getElementById('votes-slider').max = Math.max(...allVotes, 0);
  document.getElementById('votes-slider').addEventListener('input', ()=>{currentPage=1;render();});
  const sel = loadSel();
  document.querySelectorAll('.sol-row').forEach(row => {
    const id = row.dataset.id;
    if (!sel.has(id)) { const cb=document.getElementById('cb-'+id); if(cb) cb.checked=false; row.classList.add('unselected'); }
  });
  render();
});
</script>"""

    pagination = """<div class="pagination" style="padding:8px 0 0">
  <button class="btn-prev" onclick="prevPage()">← Prev</button>
  <input class="page-input" type="number" min="1" value="1" onchange="goToPage(this.value)" onkeydown="if(event.key==='Enter')goToPage(this.value)">
  <span style="color:#57606a;font-size:.88em">/ <span class="page-total">—</span></span>
  <button class="btn-next" onclick="nextPage()">Next →</button>
</div>"""

    content = "".join(rows_by_problem) if rows_by_problem else '<div class="empty">No data — run scraper_cn.py first</div>'

    body = f"""<div class="review-bar">
  <span id="r-counter" class="r-counter">Loading…</span>
  <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
    <button class="filter-btn" data-filter="selected"   onclick="toggleFilter('selected')">✅ Selected</button>
    <button class="filter-btn" data-filter="unselected" onclick="toggleFilter('unselected')">☐ Unselected</button>
    <button class="filter-btn" data-filter="video"      onclick="toggleFilter('video')">📹 Video</button>
    <button class="filter-btn" data-filter="image"      onclick="toggleFilter('image')">🖼 Image</button>
    <button class="filter-btn" onclick="clearFilters()" style="opacity:.7">✕ Clear</button>
  </div>
  <div style="display:flex;align-items:center;gap:8px">
    <label style="color:#cdd9e5;font-size:.85em;white-space:nowrap">Min votes</label>
    <input id="votes-slider" type="range" min="0" max="1000" value="0" style="width:140px;accent-color:#2ea043">
    <span id="votes-label" style="color:#2ea043;font-size:.85em;white-space:nowrap;min-width:120px">≥ 0 votes</span>
  </div>
  {pagination}
  <button class="btn-export" onclick="exportFiltered()">⬇ Export filtered_cn.json</button>
  <button class="btn-clear" onclick="resetAll()">Reset</button>
  <span style="color:#8b949e;font-size:.78em">Place filtered_cn.json in output/, then run python generate_curated.py</span>
</div>
<div class="wrap">
{content}
{pagination.replace('padding:8px 0 0','')}
</div>
{review_js}"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Solution Review — CN</title>
{_CSS}
</head>
<body>
{body}
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    problems = load_problems()
    if not problems:
        print("No data found. Run python scraper.py first.")
        return

    filtered_ids = load_filtered()
    total_sols = sum(len(p.get("solutions") or []) for p in problems)
    print(f"Loaded {len(problems)} problems, {total_sols} solutions")
    if filtered_ids:
        print(f"filtered.json found: keeping {len(filtered_ids)} selected solutions")

    OUTPUT_DIR.mkdir(exist_ok=True)

    def filter_sols(sols):
        if not filtered_ids:
            return list(sols or [])
        return [s for s in (sols or []) if str(s.get("id", "")) in filtered_ids]

    filtered_problems = [
        {**p, "solutions": filter_sols(p.get("solutions"))}
        for p in problems
    ]

    # review page (always uses full unfiltered data)
    (OUTPUT_DIR / "review.html").write_text(gen_review(problems), encoding="utf-8")

    # CN review page + solution pages (if CN data exists)
    problems_cn = load_problems_cn()
    if problems_cn:
        total_cn = sum(len(p.get("solutions") or []) for p in problems_cn)
        print(f"CN data: {len(problems_cn)} problems, {total_cn} solutions")
        (OUTPUT_DIR / "review_cn.html").write_text(gen_review_cn(problems_cn), encoding="utf-8")
        cn_sol_count = 0
        for p in problems_cn:
            for s in (p.get("solutions") or []):
                sid = s.get("id", "")
                (OUTPUT_DIR / f"solution_cn_{sid}.html").write_text(
                    gen_solution_page_cn(s, p), encoding="utf-8"
                )
                cn_sol_count += 1
        print(f"Generated: review_cn.html + {cn_sol_count} CN solution pages")

    # index
    (OUTPUT_DIR / "index.html").write_text(gen_index(filtered_problems), encoding="utf-8")

    # tutorial pages (use unfiltered so editorial is always available)
    tut_count = 0
    for p in problems:
        if p.get("tutorial"):
            slug = p["title_slug"]
            (OUTPUT_DIR / f"tutorial_{slug}.html").write_text(
                gen_tutorial_page(p), encoding="utf-8"
            )
            tut_count += 1

    # per-problem and per-solution pages
    sol_count = 0
    for p in filtered_problems:
        slug = p["title_slug"]
        sols = p.get("solutions") or []
        if sols:
            (OUTPUT_DIR / f"problem_{slug}.html").write_text(
                gen_problem_page(p), encoding="utf-8"
            )
            for s in sols:
                sid = s.get("id", "")
                (OUTPUT_DIR / f"solution_{sid}.html").write_text(
                    gen_solution_page(s, p), encoding="utf-8"
                )
                sol_count += 1

    print(f"Generated: review.html + index.html + {tut_count} tutorial pages + {sol_count} solution pages")
    print(f"\nOpen review page to curate:")
    print(f"  open {(OUTPUT_DIR / 'review.html').absolute()}")


if __name__ == "__main__":
    main()
