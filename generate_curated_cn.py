"""
Generate a curated site for LeetCode CN scraped solutions.

Run after:
  1. python scraper_cn.py          — scrape CN solutions
  2. open review_cn.html + export  — produce output/filtered_cn.json
  3. python generate_curated_cn.py — build the curated CN site
"""
import json as _json
import math as _math
from generate_html import (
    load_problems_cn, load_filtered_cn,
    gen_solution_page_cn,
    _render_content_cn,
    _CSS, _page, _nav, _diff_badge,
    OUTPUT_DIR,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _media_counts(sols: list) -> tuple:
    return (
        sum(1 for s in sols if s.get("has_video")),
        sum(1 for s in sols if s.get("has_image")),
        sum(1 for s in sols if s.get("is_official")),
    )


def _media_note(v: int, i: int, off: int = 0) -> str:
    parts = []
    if off: parts.append(f"🏆 {off}")
    if v:   parts.append(f"📹 {v}")
    if i:   parts.append(f"🖼 {i}")
    return f'<span style="color:#57606a;font-size:.82em">({", ".join(parts)})</span>' if parts else ""


def _sol_card(s: dict, problem: dict, faded: bool = False) -> str:
    sid   = s.get("id", "")
    votes = s.get("votes", 0)

    badges = ""
    if s.get("is_official"):
        badges += '<span class="badge" style="background:#fff3c4;color:#9a6700">🏆 Official</span>'
    if s.get("has_video"):
        badges += '<span class="badge b-video">📹</span>'
    if s.get("has_image"):
        badges += '<span class="badge b-image">🖼</span>'
    if s.get("has_slide"):
        badges += '<span class="badge" style="background:#f0f0ff;color:#5b21b6">🎞</span>'

    thumbnail = s.get("thumbnail", "")
    thumb_html = (
        f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:10px">'
        f'<img src="{thumbnail}" loading="lazy" '
        f'style="height:80px;width:auto;border-radius:5px;border:1px solid #d0d7de;object-fit:cover" '
        f'onerror="this.style.display=\'none\'"></div>'
    ) if thumbnail else ""

    style = ' style="opacity:.45;filter:grayscale(.4)"' if faded else ""
    dv = "1" if s.get("has_video") else "0"
    di = "1" if s.get("has_image") else "0"
    dk = "0" if faded else "1"

    return f"""<div class="card sol-card-wrap" data-votes="{votes}" data-video="{dv}" data-image="{di}" data-kept="{dk}"{style}>
  <div class="card-inner">
    <a href="solution_cn_{sid}.html" target="_blank"><div class="card-title">{s.get('title','Untitled')}</div></a>
    <div class="meta">
      <span>👤 {s.get('author','Unknown')}</span>
      <span>👍 {votes}</span>
      {badges}
    </div>
    {thumb_html}
  </div>
</div>"""


# ---------------------------------------------------------------------------
# Vote distribution chart with drag-to-filter
# ---------------------------------------------------------------------------

def _build_chart(problems: list, filtered_ids: set) -> str:
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
    thresholds = sorted(set(
        [0] + [int(10 ** (i * 0.15)) for i in range(int(_math.log10(max(max_v, 1)) / 0.15) + 2)]
    ))
    thresholds = [t for t in thresholds if t <= max_v] + [max_v]
    thresholds = sorted(set(thresholds))

    def cdf(lst, t):
        return sum(1 for v in lst if v >= t)

    labels        = _json.dumps([str(t) for t in thresholds])
    data_total    = _json.dumps([cdf(all_votes,     t) for t in thresholds])
    data_kept     = _json.dumps([cdf(kept_votes,    t) for t in thresholds])
    data_removed  = _json.dumps([cdf(removed_votes, t) for t in thresholds])
    show_removed  = "true" if filtered_ids else "false"
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
    {{label:'Total',data:{data_total},borderColor:'#57606a',backgroundColor:'rgba(87,96,106,.08)',borderWidth:2,pointRadius:2,fill:false,tension:.3}},
    {{label:'Kept',data:{data_kept},borderColor:'#1a7f37',backgroundColor:'rgba(26,127,55,.08)',borderWidth:2,pointRadius:2,fill:false,tension:.3}},
    ...(showRemoved?[{{label:'Removed',data:{data_removed},borderColor:'#cf222e',backgroundColor:'rgba(207,34,46,.08)',borderWidth:2,pointRadius:2,fill:false,tension:.3}}]:[]),
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
        x: {{ title: {{ display: true, text: 'Min votes threshold', font: {{ size: 12 }} }}, ticks: {{ maxTicksLimit: 12, font: {{ size: 11 }} }} }},
        y: {{ title: {{ display: true, text: 'Number of solutions', font: {{ size: 12 }} }}, beginAtZero: true, ticks: {{ font: {{ size: 11 }} }} }},
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

def gen_index(problems: list, filtered_ids: set) -> str:
    all_sols     = [s for p in problems for s in (p.get("solutions") or []) if not s.get("is_official")]
    kept_sols    = [s for s in all_sols if not filtered_ids or str(s.get("id","")) in filtered_ids]
    removed_sols = [s for s in all_sols if filtered_ids and str(s.get("id","")) not in filtered_ids]

    n_all, n_kept, n_rem = len(all_sols), len(kept_sols), len(removed_sols)
    va, ia, _ = _media_counts(all_sols)
    vk, ik, _ = _media_counts(kept_sols)
    vr, ir, _ = _media_counts(removed_sols)

    summary = f"""<div style="display:flex;gap:20px;flex-wrap:wrap;margin-bottom:28px;
                              background:#fff;border:1px solid #d0d7de;border-radius:8px;
                              padding:18px 24px;font-size:.95em;align-items:center">
  <span>📦 Total: <b>{n_all}</b> {_media_note(va, ia)}</span>
  <span style="color:#1a7f37">✅ Kept: <b>{n_kept}</b> {_media_note(vk, ik)}</span>
  <span style="color:#cf222e">🚫 Removed: <b>{n_rem}</b> {_media_note(vr, ir)}</span>
  <span style="color:#57606a">📋 Problems: {len(problems)}</span>
</div>"""

    _btn_style = "border:none;padding:3px 10px;font-size:.8em"

    cards = []
    for p in problems:
        slug = p["title_slug"]
        sols = p.get("solutions") or []
        official  = [s for s in sols if s.get("is_official")]
        community = [s for s in sols if not s.get("is_official")]
        kept      = [s for s in community if not filtered_ids or str(s.get("id","")) in filtered_ids]

        title_cn = p.get("title_cn", "")
        title_display = (
            f'{p.get("title","")} <span style="color:#57606a;font-weight:400;font-size:.9em">/ {title_cn}</span>'
            if title_cn else p.get("title", "")
        )

        tags = " ".join(
            f'<span class="badge b-tag">{t}</span>'
            for t in (p.get("topic_tags") or [])[:5]
        )
        lc_link = f'<a href="{p.get("url","")}" target="_blank" class="lc-link">↗ LeetCode CN</a>'

        ed_btn  = f'<a href="tutorial_cn_{slug}.html" class="sub-btn sub-sol" style="{_btn_style}">📖 Editorial</a>' if official else ""
        sol_btn = (
            f'<button onclick="toggleSols(\'{slug}\')" id="btn-{slug}" '
            f'class="sub-btn sub-sol" style="{_btn_style};cursor:pointer">Solutions ▾</button>'
        ) if community else ""

        vk2, ik2, _ = _media_counts(kept)
        media_note = _media_note(vk2, ik2)

        kept_cards_html = "".join(_sol_card(s, p) for s in kept)
        no_content = '<div class="empty" style="margin:0;font-size:.88em">No solutions.</div>' if not community and not official else ""

        diff_val = (p.get("difficulty") or "").lower()
        cards.append(f"""<div class="card idx-prob-card" data-diff="{diff_val}">
  <div class="card-inner">
    <div class="card-title">{p.get('question_id','')}. {title_display}</div>
    <div class="meta" style="margin-bottom:10px">
      {_diff_badge(p.get('difficulty',''))} {tags} {lc_link}
      {ed_btn}
      {sol_btn}
      {media_note}
    </div>
    <div id="sols-{slug}">
      {kept_cards_html}
      {no_content}
    </div>
  </div>
</div>""")

    chart = _build_chart(problems, filtered_ids)

    body = f"""<div class="page-title">LeetCode CN Recursion — Curated</div>
<div class="page-sub">Filtered view · filtered_cn.json applied</div>
{summary}
{chart}
{"".join(cards)}
<script>
function toggleSols(slug) {{
  const div = document.getElementById('sols-' + slug);
  const btn = document.getElementById('btn-' + slug);
  if (!div || !btn) return;
  const collapsed = div.style.display === 'none';
  div.style.display = collapsed ? '' : 'none';
  btn.textContent = collapsed ? 'Solutions ▾' : 'Solutions ▸';
}}
</script>"""

    return _page(
        "LeetCode CN Recursion — Curated",
        _nav(("🔄 CN Recursion Solutions", "index_cn.html")),
        body,
    )


# ---------------------------------------------------------------------------
# Editorial page (official solutions)
# ---------------------------------------------------------------------------

def gen_tutorial_page_cn(p: dict, official_sols: list) -> str:
    slug = p["title_slug"]
    title_cn = p.get("title_cn", "")
    tags = " ".join(
        f'<span class="badge b-tag">{t}</span>'
        for t in (p.get("topic_tags") or [])
    )
    title_display = f'{p.get("title","")} / {title_cn}' if title_cn else p.get("title","")

    sections = []
    for s in official_sols:
        content_html = _render_content_cn(s.get("content", ""))
        created = s.get("created_at", "")
        if created:
            try:
                from datetime import datetime
                created = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%Y-%m-%d")
            except Exception:
                created = str(created)[:10]
        sections.append(f"""<div class="sol-header" style="margin-bottom:12px">
  <div class="stitle">{s.get('title','Official Solution')}</div>
  <div class="meta">
    <span>🏆 Official</span>
    <span>👍 {s.get('votes',0)}</span>
    {f'<span>{created}</span>' if created else ''}
    <a href="{s.get('url','')}" target="_blank" style="font-size:.85em">↗ 查看原 Solution</a>
  </div>
</div>
<div class="sol-body" style="margin-bottom:32px">
  {content_html or '<p style="color:#57606a">内容为空。</p>'}
</div>""")

    body = f"""<div class="page-title">{p.get('question_id','')}. {title_display} — Official Editorial</div>
<div class="page-sub" style="margin-bottom:20px">
  {_diff_badge(p.get('difficulty',''))} {tags}
  &nbsp;
  <a href="{p.get('url','')}" target="_blank" style="font-size:.85em">↗ LeetCode CN</a>
  &nbsp;·&nbsp;
  <a href="index_cn.html" style="font-size:.85em">← Back</a>
</div>
{"".join(sections)}"""

    return _page(
        f"{p.get('title','')} – CN Editorial",
        _nav(
            ("🔄 CN Recursion Solutions", "index_cn.html"),
            ("Editorial", f"tutorial_cn_{slug}.html"),
        ),
        body,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    problems = load_problems_cn()
    if not problems:
        print("No CN data found. Run python scraper_cn.py first.")
        return

    filtered_ids = load_filtered_cn()
    community_total = sum(
        sum(1 for s in (p.get("solutions") or []) if not s.get("is_official"))
        for p in problems
    )
    kept_n = sum(
        sum(1 for s in (p.get("solutions") or [])
            if not s.get("is_official") and str(s.get("id","")) in filtered_ids)
        for p in problems
    ) if filtered_ids else community_total

    print(f"Loaded {len(problems)} CN problems, {community_total} community solutions")
    if filtered_ids:
        print(f"filtered_cn.json: keeping {kept_n} / {community_total} ({community_total - kept_n} removed)")
    else:
        print("No filtered_cn.json — showing all solutions as kept")

    OUTPUT_DIR.mkdir(exist_ok=True)

    (OUTPUT_DIR / "index_cn.html").write_text(
        gen_index(problems, filtered_ids), encoding="utf-8"
    )

    tut_count = sol_count = 0
    for p in problems:
        slug = p["title_slug"]
        sols = p.get("solutions") or []
        official  = [s for s in sols if s.get("is_official")]
        community = [s for s in sols if not s.get("is_official")]

        if official:
            (OUTPUT_DIR / f"tutorial_cn_{slug}.html").write_text(
                gen_tutorial_page_cn(p, official), encoding="utf-8"
            )
            tut_count += 1

        for s in community:
            sid = s.get("id", "")
            (OUTPUT_DIR / f"solution_cn_{sid}.html").write_text(
                gen_solution_page_cn(s, p), encoding="utf-8"
            )
            sol_count += 1

    print(f"Generated: index_cn.html + {tut_count} editorial pages + {sol_count} solution pages")
    print(f"\nOpen: open {(OUTPUT_DIR / 'index_cn.html').absolute()}")


if __name__ == "__main__":
    main()
