"""
Generate a curated site that shows both kept and filtered-out solutions.

Run after:
  1. python scraper.py          — scrape all solutions
  2. review.html + export       — produce output/filtered.json
  3. python generate_curated.py — build the curated site

Output overwrites output/index.html and output/problem_*.html
but never touches the raw data JSON files.
"""
import json as _json
import math as _math
from generate_html import (
    load_problems, load_filtered, render_content,
    gen_tutorial_page, _title_to_slug,
    _CSS, _page, _nav, _diff_badge,
    OUTPUT_DIR,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sol_card(s: dict, problem: dict, faded: bool = False) -> str:
    from generate_html import _all_images, _YT_RE
    sid = s.get("id", "")
    media = ""
    if s.get("has_video"):
        media += '<span class="badge b-video">📹</span>'
    if s.get("has_image"):
        media += '<span class="badge b-image">🖼</span>'
    style = ' style="opacity:.45;filter:grayscale(.4)"' if faded else ""

    content = s.get("content", "")
    thumb_imgs = []
    for url in _all_images(content):
        thumb_imgs.append(url)
    for vid_id in _YT_RE.findall(content):
        thumb_imgs.append(f"https://img.youtube.com/vi/{vid_id}/default.jpg")

    thumbs_html = ""
    if thumb_imgs:
        imgs = "".join(
            f'<img src="{u}" loading="lazy" '
            f'style="height:80px;width:auto;border-radius:5px;'
            f'border:1px solid #d0d7de;object-fit:cover" '
            f'onerror="this.style.display=\'none\'">'
            for u in thumb_imgs
        )
        thumbs_html = f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:10px">{imgs}</div>'

    votes = s.get('votes', 0)
    dv = "1" if s.get("has_video") else "0"
    di = "1" if s.get("has_image") else "0"
    dk = "0" if faded else "1"
    return f"""<div class="card sol-card-wrap" data-votes="{votes}" data-video="{dv}" data-image="{di}" data-kept="{dk}"{style}>
  <div class="card-inner">
    <a href="solution_{sid}.html" target="_blank"><div class="card-title">{s.get('title','Untitled')}</div></a>
    <div class="meta">
      <span>👤 {s.get('author','Unknown')}</span>
      <span>👍 {votes}</span>
      {media}
    </div>
    {thumbs_html}
  </div>
</div>"""


def _section(title: str, count: int, cards: list, color: str, collapsed: bool = False) -> str:
    det_open = "" if collapsed else " open"
    header_style = f"color:{color};border-left:3px solid {color};padding-left:10px;margin:24px 0 12px"
    return f"""<details{det_open}>
  <summary style="{header_style};cursor:pointer;list-style:none;font-weight:600;font-size:1.05em">
    {title} <span style="font-weight:400;font-size:.9em;margin-left:6px">{count}</span>
  </summary>
  {"".join(cards) if cards else '<div class="empty" style="margin:0">None.</div>'}
</details>"""


# ---------------------------------------------------------------------------
# Vote distribution chart
# ---------------------------------------------------------------------------

def _build_chart_data(problems: list, filtered_ids: set) -> str:
    """Return a Chart.js config JSON string for the vote distribution chart."""
    all_votes, kept_votes, removed_votes = [], [], []
    for p in problems:
        for s in (p.get("solutions") or []):
            v = s.get("votes", 0)
            all_votes.append(v)
            if filtered_ids:
                (kept_votes if str(s.get("id","")) in filtered_ids else removed_votes).append(v)
            else:
                kept_votes.append(v)

    if not all_votes:
        return ""

    max_v = max(all_votes)
    # Build log-scale thresholds for a smooth curve
    thresholds = sorted(set(
        [0] +
        [int(10 ** (i * 0.15)) for i in range(int(_math.log10(max(max_v, 1)) / 0.15) + 2)]
    ))
    thresholds = [t for t in thresholds if t <= max_v] + [max_v]
    thresholds = sorted(set(thresholds))

    def cdf(votes_list, t):
        return sum(1 for v in votes_list if v >= t)

    labels = _json.dumps([str(t) for t in thresholds])
    data_total  = _json.dumps([cdf(all_votes,     t) for t in thresholds])
    data_kept   = _json.dumps([cdf(kept_votes,    t) for t in thresholds])
    data_removed= _json.dumps([cdf(removed_votes, t) for t in thresholds])

    show_removed = "true" if filtered_ids else "false"

    thresholds_json = _json.dumps(thresholds)

    return f"""
<div style="background:#fff;border:1px solid #d0d7de;border-radius:8px;
            padding:20px 24px;margin-bottom:28px">
  <div style="font-weight:600;font-size:1em;margin-bottom:8px">Vote Distribution</div>
  <canvas id="voteChart" height="90" style="cursor:ew-resize;user-select:none"></canvas>
  <div style="font-size:.82em;color:#57606a;margin-top:10px;display:flex;align-items:center;gap:10px">
    <span>Solutions with ≥ X votes (cumulative) · <span id="filter-status" style="color:#0969da">Drag to filter</span></span>
    <button id="filter-reset" onclick="resetVoteFilter()"
      style="display:none;font-size:.82em;padding:1px 8px;cursor:pointer;
             border:1px solid #d0d7de;border-radius:4px;background:#f6f8fa">✕ Reset</button>
  </div>
  <div id="live-stats" style="margin-top:8px;padding:8px 14px;background:#f6f8fa;
       border:1px solid #d0d7de;border-radius:6px;font-size:.82em;
       display:grid;grid-template-columns:72px 80px 100px 72px 16px 72px;
       row-gap:5px;column-gap:0;align-items:center">
    <span style="color:#57606a;font-weight:500">Problems</span>
    <span style="color:#1a7f37">Easy <b id="ls-easy-p">—</b></span>
    <span style="color:#e3ab05">Medium <b id="ls-medium-p">—</b></span>
    <span style="color:#cf222e">Hard <b id="ls-hard-p">—</b></span>
    <span style="color:#d0d7de;text-align:center">·</span>
    <span style="color:#57606a">Total <b id="ls-probs">—</b></span>
    <span style="color:#57606a;font-weight:500">Solutions</span>
    <span style="color:#1a7f37">Easy <b id="ls-easy-s">—</b></span>
    <span style="color:#e3ab05">Medium <b id="ls-medium-s">—</b></span>
    <span style="color:#cf222e">Hard <b id="ls-hard-s">—</b></span>
    <span style="color:#d0d7de;text-align:center">·</span>
    <span style="color:#57606a">Total <b id="ls-sols">—</b></span>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<script>
(function() {{
  const labels = {labels};
  const thresholds = {thresholds_json};
  const showRemoved = {show_removed};
  const datasets = [
    {{
      label: 'Total',
      data: {data_total},
      borderColor: '#57606a',
      backgroundColor: 'rgba(87,96,106,.08)',
      borderWidth: 2,
      pointRadius: 2,
      fill: false,
      tension: 0.3,
    }},
    {{
      label: 'Kept',
      data: {data_kept},
      borderColor: '#1a7f37',
      backgroundColor: 'rgba(26,127,55,.08)',
      borderWidth: 2,
      pointRadius: 2,
      fill: false,
      tension: 0.3,
    }},
    ...(showRemoved ? [{{
      label: 'Removed',
      data: {data_removed},
      borderColor: '#cf222e',
      backgroundColor: 'rgba(207,34,46,.08)',
      borderWidth: 2,
      pointRadius: 2,
      fill: false,
      tension: 0.3,
    }}] : []),
  ];

  const crosshairPlugin = {{
    id: 'crosshair',
    afterDraw(chart) {{
      if (chart._cx === undefined) return;
      const {{ctx, chartArea: {{top, bottom}}}} = chart;
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(chart._cx, top);
      ctx.lineTo(chart._cx, bottom);
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = 'rgba(9,105,218,0.65)';
      ctx.setLineDash([5, 3]);
      ctx.stroke();
      ctx.restore();
    }},
  }};

  const myChart = new Chart(document.getElementById('voteChart'), {{
    type: 'line',
    data: {{ labels, datasets }},
    plugins: [crosshairPlugin],
    options: {{
      responsive: true,
      interaction: {{ intersect: false, mode: 'index' }},
      plugins: {{
        legend: {{ position: 'top', labels: {{ boxWidth: 14, font: {{ size: 12 }} }} }},
        tooltip: {{ callbacks: {{
          title: ctx => `≥ ${{ctx[0].label}} votes`,
          label: ctx => ` ${{ctx.dataset.label}}: ${{ctx.parsed.y}} solutions`,
        }} }},
      }},
      scales: {{
        x: {{
          title: {{ display: true, text: 'Min votes threshold', font: {{ size: 12 }} }},
          ticks: {{ maxTicksLimit: 12, font: {{ size: 11 }} }},
        }},
        y: {{
          title: {{ display: true, text: 'Number of solutions', font: {{ size: 12 }} }},
          beginAtZero: true,
          ticks: {{ font: {{ size: 11 }} }},
        }},
      }},
    }},
  }});

  const canvas = document.getElementById('voteChart');
  let _dragging = false;
  let _rafPending = false;

  function pixelToThreshold(x) {{
    const idx = myChart.scales.x.getValueForPixel(x);
    const clamped = Math.max(0, Math.min(thresholds.length - 1, Math.round(idx)));
    return thresholds[clamped];
  }}
  function clampToChart(x) {{
    return Math.max(myChart.chartArea.left, Math.min(myChart.chartArea.right, x));
  }}
  function updateFromX(rawX) {{
    const x = clampToChart(rawX);
    myChart._cx = x;
    if (!_rafPending) {{
      _rafPending = true;
      requestAnimationFrame(() => {{
        myChart.draw();
        applyVoteFilter(pixelToThreshold(x));
        _rafPending = false;
      }});
    }}
  }}

  // Initialise line at leftmost position and apply filter once chart is laid out
  requestAnimationFrame(() => {{
    myChart._cx = myChart.scales.x.getPixelForValue(0);
    myChart.draw();
    applyVoteFilter(thresholds[0]);
  }});

  canvas.addEventListener('mousedown', e => {{
    _dragging = true;
    canvas.style.cursor = 'grabbing';
    document.body.style.cursor = 'grabbing';
    const rect = canvas.getBoundingClientRect();
    updateFromX(e.clientX - rect.left);
  }});
  document.addEventListener('mousemove', e => {{
    if (!_dragging) return;
    const rect = canvas.getBoundingClientRect();
    updateFromX(e.clientX - rect.left);
  }});
  document.addEventListener('mouseup', () => {{
    if (_dragging) {{
      _dragging = false;
      canvas.style.cursor = 'ew-resize';
      document.body.style.cursor = '';
    }}
  }});

  function updateStats() {{
    const visProbs = [...document.querySelectorAll('.idx-prob-card')].filter(p => p.style.display !== 'none');
    let totalSols = 0;
    const byDiff = {{ easy: {{p:0,s:0}}, medium: {{p:0,s:0}}, hard: {{p:0,s:0}} }};
    for (const prob of visProbs) {{
      const d = prob.dataset.diff;
      if (byDiff[d]) byDiff[d].p++;
      const s = [...prob.querySelectorAll('.sol-card-wrap')].filter(c => c.style.display !== 'none').length;
      if (byDiff[d]) byDiff[d].s += s;
      totalSols += s;
    }}
    document.getElementById('ls-easy-p').textContent   = byDiff.easy.p;
    document.getElementById('ls-easy-s').textContent   = byDiff.easy.s;
    document.getElementById('ls-medium-p').textContent = byDiff.medium.p;
    document.getElementById('ls-medium-s').textContent = byDiff.medium.s;
    document.getElementById('ls-hard-p').textContent   = byDiff.hard.p;
    document.getElementById('ls-hard-s').textContent   = byDiff.hard.s;
    document.getElementById('ls-probs').textContent    = visProbs.length;
    document.getElementById('ls-sols').textContent     = totalSols;
  }}

  window.applyVoteFilter = function(threshold) {{
    document.getElementById('filter-status').textContent = `≥ ${{threshold}} votes`;
    document.getElementById('filter-reset').style.display = '';
    document.querySelectorAll('.sol-card-wrap').forEach(card => {{
      card.style.display = parseInt(card.dataset.votes || '0') >= threshold ? '' : 'none';
    }});
    document.querySelectorAll('.idx-prob-card').forEach(prob => {{
      const any = [...prob.querySelectorAll('.sol-card-wrap')].some(c => c.style.display !== 'none');
      prob.style.display = any ? '' : 'none';
    }});
    updateStats();
  }};

  window.resetVoteFilter = function() {{
    myChart._cx = myChart.scales.x.getPixelForValue(0);
    myChart.draw();
    document.getElementById('filter-status').textContent = 'Drag to filter';
    document.getElementById('filter-reset').style.display = 'none';
    document.querySelectorAll('.sol-card-wrap').forEach(c => c.style.display = '');
    document.querySelectorAll('.idx-prob-card').forEach(c => c.style.display = '');
    updateStats();
  }};
}})();
</script>"""


# ---------------------------------------------------------------------------
# Index page
# ---------------------------------------------------------------------------

def _media_counts(sols: list) -> tuple:
    """Return (video_count, image_count) for a list of solutions."""
    return (
        sum(1 for s in sols if s.get("has_video")),
        sum(1 for s in sols if s.get("has_image")),
    )


def _media_note(v: int, p: int) -> str:
    parts = []
    if v: parts.append(f"📹 {v}")
    if p: parts.append(f"🖼 {p}")
    return f'<span style="color:#57606a;font-size:.82em">({", ".join(parts)})</span>' if parts else ""


def _thumbs_strip(sols: list) -> str:
    from generate_html import _all_images, _YT_RE
    imgs = []
    for s in sols:
        c = s.get("content", "")
        for url in _all_images(c):
            imgs.append(url)
        for vid_id in _YT_RE.findall(c):
            imgs.append(f"https://img.youtube.com/vi/{vid_id}/default.jpg")
    if not imgs:
        return ""
    thumbs = "".join(
        f'<img src="{u}" loading="lazy" style="height:72px;width:auto;border-radius:4px;'
        f'border:1px solid #d0d7de;object-fit:cover" onerror="this.style.display=\'none\'">'
        for u in imgs
    )
    return f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:10px">{thumbs}</div>'


def gen_index(problems: list, filtered_ids: set) -> str:
    all_sols  = [s for p in problems for s in (p.get("solutions") or [])]
    kept_sols = [s for s in all_sols if not filtered_ids or str(s.get("id","")) in filtered_ids]
    removed_sols = [s for s in all_sols if filtered_ids and str(s.get("id","")) not in filtered_ids]

    total_all, total_kept, total_removed = len(all_sols), len(kept_sols), len(removed_sols)
    v_all,  p_all  = _media_counts(all_sols)
    v_kept, p_kept = _media_counts(kept_sols)
    v_rem,  p_rem  = _media_counts(removed_sols)

    cards = []
    for prob in problems:
        slug = prob["title_slug"]
        sols = prob.get("solutions") or []
        kept  = [s for s in sols if not filtered_ids or str(s.get("id","")) in filtered_ids]
        n_all = len(sols)

        tags = " ".join(
            f'<span class="badge b-tag">{t}</span>'
            for t in (prob.get("topic_tags") or [])[:5]
        )
        lc_link = f'<a href="{prob.get("url","")}" target="_blank" class="lc-link">↗ LeetCode</a>'

        _btn_style = "border:none;padding:3px 10px;font-size:.8em"
        tut_btn = f'<a href="tutorial_{slug}.html" class="sub-btn sub-sol" style="{_btn_style}">📖 Tutorial</a>' if prob.get("tutorial") else ""

        vk, pk = _media_counts(kept)
        media_note = _media_note(vk, pk)

        kept_cards_html = "".join(_sol_card(s, prob) for s in kept)
        no_content = '<div class="empty" style="margin:0;font-size:.88em">No solutions.</div>' if n_all == 0 and not prob.get("tutorial") else ""

        diff_val = (prob.get('difficulty') or '').lower()
        cards.append(f"""<div class="card idx-prob-card" data-diff="{diff_val}">
  <div class="card-inner">
    <div class="card-title">{prob['question_id']}. {prob['title']}</div>
    <div class="meta" style="margin-bottom:10px">
      {_diff_badge(prob.get('difficulty',''))} {tags} {lc_link}
      {tut_btn}
      <button onclick="toggleSols('{slug}')" id="btn-{slug}"
        class="sub-btn sub-sol" style="{_btn_style};cursor:pointer">Solutions ▾</button>
      {media_note}
    </div>
    <div id="sols-{slug}">
      {kept_cards_html}
      {no_content}
    </div>
  </div>
</div>""")

    summary = f"""<div style="display:flex;gap:20px;flex-wrap:wrap;margin-bottom:28px;
                              background:#fff;border:1px solid #d0d7de;border-radius:8px;
                              padding:18px 24px;font-size:.95em;align-items:center">
  <span>📦 Total: <b>{total_all}</b> {_media_note(v_all, p_all)}</span>
  <span style="color:#1a7f37">✅ Kept: <b>{total_kept}</b> {_media_note(v_kept, p_kept)}</span>
  <span style="color:#cf222e">🚫 Removed: <b>{total_removed}</b> {_media_note(v_rem, p_rem)}</span>
  <span style="color:#57606a">📋 Problems: {len(problems)}</span>
</div>"""

    chart = _build_chart_data(problems, filtered_ids)

    body = f"""<div class="page-title">LeetCode Recursion — Curated</div>
<div class="page-sub">Filtered view · filtered.json applied</div>
{summary}
{chart}
{"".join(cards)}
<script>
function toggleSols(slug) {{
  const div = document.getElementById('sols-' + slug);
  const btn = document.getElementById('btn-' + slug);
  const collapsed = div.style.display === 'none';
  div.style.display = collapsed ? '' : 'none';
  btn.textContent = collapsed ? 'Solutions ▾' : 'Solutions ▸';
}}
</script>"""

    return _page(
        "LeetCode Recursion — Curated",
        _nav(("🔄 Recursion Solutions", "index.html")),
        body,
    )


# ---------------------------------------------------------------------------
# Problem page
# ---------------------------------------------------------------------------

def gen_problem_page(p: dict, filtered_ids: set) -> str:
    slug = p["title_slug"]
    sols = p.get("solutions") or []

    if filtered_ids:
        kept = [s for s in sols if str(s.get("id","")) in filtered_ids]
        removed = [s for s in sols if str(s.get("id","")) not in filtered_ids]
    else:
        kept, removed = sols, []

    tags = " ".join(
        f'<span class="badge b-tag">{t}</span>'
        for t in (p.get("topic_tags") or [])
    )
    tutorial_link = (
        f'&nbsp;·&nbsp;<a href="tutorial_{slug}.html" style="font-size:.85em">📖 Tutorial</a>'
        if p.get("tutorial") else ""
    )

    stats = f"""<div style="display:flex;gap:20px;flex-wrap:wrap;font-size:.88em;
                             background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;
                             padding:12px 16px;margin-bottom:20px">
  <span>Total: <b>{len(sols)}</b></span>
  <span style="color:#1a7f37">✅ Kept: <b>{len(kept)}</b></span>
  <span style="color:#cf222e">🚫 Removed: <b>{len(removed)}</b></span>
</div>""" if filtered_ids else ""

    kept_section = _section(
        "✅ Kept Solutions", len(kept),
        [_sol_card(s, p) for s in kept],
        color="#1a7f37", collapsed=False
    )
    removed_section = _section(
        "🚫 Filtered Out", len(removed),
        [_sol_card(s, p, faded=True) for s in removed],
        color="#cf222e", collapsed=True
    ) if removed else ""

    body = f"""<div class="page-title">{p['question_id']}. {p['title']}</div>
<div class="page-sub">
  {_diff_badge(p.get('difficulty',''))} {tags}
  &nbsp;
  <a href="{p.get('url','')}" target="_blank" style="font-size:.85em">↗ LeetCode</a>
  {tutorial_link}
</div>
{stats}
{kept_section}
{removed_section}"""

    return _page(
        f"{p['title']} – Solutions",
        _nav(
            ("🔄 Recursion Solutions", "index.html"),
            (p["title"], f"problem_{slug}.html"),
        ),
        body,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    problems = load_problems()
    if not problems:
        print("No data found. Run python scraper.py first.")
        return

    filtered_ids = load_filtered()
    total = sum(len(p.get("solutions") or []) for p in problems)
    kept = sum(
        sum(1 for s in (p.get("solutions") or []) if str(s.get("id","")) in filtered_ids)
        for p in problems
    ) if filtered_ids else total

    print(f"Loaded {len(problems)} problems, {total} solutions")
    if filtered_ids:
        print(f"filtered.json: keeping {kept} / {total} ({total - kept} removed)")
    else:
        print("No filtered.json found — showing all solutions as kept")

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Index
    (OUTPUT_DIR / "index.html").write_text(
        gen_index(problems, filtered_ids), encoding="utf-8"
    )

    # Tutorial pages (unchanged)
    tut_count = 0
    for p in problems:
        if p.get("tutorial"):
            (OUTPUT_DIR / f"tutorial_{p['title_slug']}.html").write_text(
                gen_tutorial_page(p), encoding="utf-8"
            )
            tut_count += 1

    # Problem pages + solution pages
    sol_count = 0
    for p in problems:
        slug = p["title_slug"]
        sols = p.get("solutions") or []
        if sols or p.get("tutorial"):
            (OUTPUT_DIR / f"problem_{slug}.html").write_text(
                gen_problem_page(p, filtered_ids), encoding="utf-8"
            )
        for s in sols:
            sid = s.get("id", "")
            (OUTPUT_DIR / f"solution_{sid}.html").write_text(
                _build_solution_page(s, p), encoding="utf-8"
            )
            sol_count += 1

    from build_visual_review import build as build_visual_review
    build_visual_review()

    print(f"Generated: index.html + {tut_count} tutorial pages + {sol_count} solution pages")
    print(f"\nOpen: open {(OUTPUT_DIR / 'index.html').absolute()}")


def _build_solution_page(s: dict, problem: dict) -> str:
    """Thin wrapper — reuse generate_html's gen_solution_page."""
    from generate_html import gen_solution_page
    return gen_solution_page(s, problem)


if __name__ == "__main__":
    main()
