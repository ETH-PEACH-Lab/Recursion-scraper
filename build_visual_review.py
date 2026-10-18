"""Render manually reviewed image classifications and annotate the curated index.
Run after generate_curated.py. Evidence lives in output/image_review/classification.json.
"""
import json
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent / 'output'
EVIDENCE = ROOT / 'image_review/classification.json'

def build():
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text())
    rows = [r for r in data['solutions'] if r.get('includes_recursion')]
    images = {i['n']: i for i in data['images']}
    esc = html.escape
    groups = list(dict.fromkeys(r['group'] for r in rows))
    sections = []
    for group in groups:
        items = [r for r in rows if r['group'] == group]
        cards = []
        for r in items:
            evidence = []
            for n in r['image_numbers']:
                im = images[n]
                # Preserve GIF animations; local copies make the review reproducible.
                src = 'image_review/' + Path(im['path']).name
                evidence.append(f'<figure><a href="{src}" target="_blank"><img src="{src}" loading="lazy" alt="图片 {n}: {esc(im["observation"])}"></a><figcaption>#{n:03d} · {esc("、".join(im["categories"]))}<br>{esc(im["observation"])}</figcaption></figure>')
            cards.append(f'<article data-group="{esc(group)}" data-search="{esc(r["title"].lower())}"><h3><a href="{esc(r["id"])}" target="_blank">{esc(r["title"])}</a></h3><p><b>Vote {r["votes"]}</b> · {esc(" · ".join(r["categories"]))}</p><p>{esc(r["note"])}</p><details><summary>查看全部 {len(evidence)} 张图片与逐图判断</summary><div class="pictures">{"".join(evidence)}</div></details></article>')
        sections.append(f'<section><h2>{esc(group)} · {len(items)} 篇</h2>{"".join(cards)}</section>')
    options = ''.join(f'<option>{esc(g)}</option>' for g in groups)
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Vote ≥ 5 · Solution 图片分类</title><style>
body{font:15px/1.6 system-ui,sans-serif;color:#24292f;background:#f6f8fa;max-width:1180px;margin:32px auto;padding:0 22px}h1{font-size:28px}h2{margin-top:38px;border-bottom:1px solid #d0d7de;padding-bottom:8px}h3{font-size:17px;margin:0}a{color:#0969da}article{background:white;border:1px solid #d0d7de;border-radius:8px;padding:18px;margin:14px 0}article p{margin:10px 0}summary{cursor:pointer;color:#0969da}.pictures{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:15px;margin-top:16px}figure{margin:0;border:1px solid #d0d7de;padding:10px;overflow:hidden}img{max-width:100%;max-height:600px;object-fit:contain}figcaption{font-size:13px;color:#57606a}select,input{font:inherit;padding:8px;margin-right:12px;max-width:100%}.controls{position:sticky;top:0;background:#f6f8fa;padding:12px 0;border-bottom:1px solid #d0d7de}
</style><a href="index.html">返回原始首页</a><h1>Vote ≥ 5 · Solution 图片分类</h1><p>来源：output/index.html 中 vote ≥ 5 的 72 篇候选，逐图查看后再核对正文和代码；仅纳入 60 篇已确认含递归解法的文章。排除 9 篇非递归，3 篇本地代码缺失而待确认。投票是本地抓取快照，并非当前实时票数。</p><p>“递归相关图解”包含调用树、栈与返回、递归子问题分解和结构组合；不代表每篇都有完整调用栈。只看到视频封面的文章不评价视频内容。分类依据是图片实际内容，允许一篇有多个标签。</p><div class="controls"><select id="group"><option value="">全部分类</option>OPTIONS</select><input id="search" placeholder="搜索标题"><span id="count">60 篇</span></div>SECTIONS<script>
function filter(){let n=0;const g=document.getElementById('group').value,q=document.getElementById('search').value.toLowerCase();document.querySelectorAll('article').forEach(a=>{const ok=(!g||a.dataset.group===g)&&a.dataset.search.includes(q);a.hidden=!ok;if(ok)n++});document.querySelectorAll('section').forEach(s=>s.hidden=![...s.querySelectorAll('article')].some(a=>!a.hidden));document.getElementById('count').textContent=n+' 篇'}document.getElementById('group').onchange=filter;document.getElementById('search').oninput=filter;
</script></html>'''.replace('OPTIONS', options).replace('SECTIONS', ''.join(sections))
    (ROOT / 'classified_solutions.html').write_text(page)
    index_path = ROOT / 'index.html'
    text = index_path.read_text()
    text = re.sub(r'<!-- visual-review-start -->.*?<!-- visual-review-end -->', '', text, flags=re.S)
    for r in rows:
        href = re.escape(r['id'])
        pattern = r'(<a href="' + href + r'"[^>]*><div class="card-title">.*?</div></a>)'
        badge = f'<!-- visual-review-start --><p style="font-size:13px;color:#57606a"><b>{esc(r["group"])}</b> · {esc(r["note"])}</p><!-- visual-review-end -->'
        text = re.sub(pattern, lambda m: m[1] + badge, text, flags=re.S)
    banner = '<!-- visual-review-start --><div style="padding:16px;background:#ddf4ff;border-radius:8px;margin-bottom:20px"><b>仅递归解法 · Vote ≥ 5：60 篇</b> · <a href="classified_solutions.html">查看逐图分类与图片证据</a><p style="margin-bottom:0">有递归相关图解 32 · 图片未展示递归过程 28 · 已排除非递归及待确认条目</p></div><!-- visual-review-end -->'
    text = text.replace('<div class="card idx-prob-card"', banner + '<div class="card idx-prob-card"', 1)
    confirmed = [r['id'] for r in rows]
    text = text.replace("parseInt(card.dataset.votes || '0') >= threshold ?", "parseInt(card.dataset.votes || '0') >= Math.max(5, threshold) && card.dataset.recursion === '1' ?")
    text = text.replace("forEach(c => c.style.display = '');", "forEach(c => c.style.display = c.classList.contains('sol-card-wrap') && (c.dataset.recursion !== '1' || Number(c.dataset.votes)<5) ? 'none' : '');")
    script = '''<!-- visual-review-start --><script>
(function(){
const confirmed=new Set(CONFIRMED);
document.querySelectorAll('.sol-card-wrap').forEach(c=>{c.dataset.recursion=confirmed.has(c.querySelector('a').getAttribute('href'))?'1':'0'});
function initialFilter(){
 document.querySelectorAll('.sol-card-wrap').forEach(c=>c.style.display=Number(c.dataset.votes)>=5&&c.dataset.recursion==='1'?'':'none');
 document.querySelectorAll('.idx-prob-card').forEach(p=>p.style.display=[...p.querySelectorAll('.sol-card-wrap')].some(c=>c.style.display!=='none')?'':'none');
 if(window.applyVoteFilter)window.applyVoteFilter(5);
 const status=document.getElementById('filter-status');if(status)status.textContent='≥ 5 votes';
}initialFilter();
})();</script><!-- visual-review-end -->'''.replace('CONFIRMED', json.dumps(confirmed))
    text = text.replace('</body>', script + '</body>')
    index_path.write_text(text)

if __name__ == '__main__':
    build()
