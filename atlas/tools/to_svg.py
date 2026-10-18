"""Convert the rendered HTML figure into a clean, editable SVG (real <text> lines, rects, vector icons)."""
import sys, json
from playwright.sync_api import sync_playwright

JS = r"""
() => {
  const out = [];
  const cv = document.createElement('canvas').getContext('2d');
  const hex = c => { const m = c.match(/rgba?\(([^)]*)\)/); if (!m) return [c, 1]; const v = m[1].split(',').map(x => parseFloat(x)); const h = '#' + v.slice(0,3).map(x => Math.round(x).toString(16).padStart(2,'0')).join(''); return [h, v.length > 3 ? v[3] : 1]; };
  const F = (attr, c) => { const [h, a] = hex(c); return `${attr}="${h}"` + (a < 1 ? ` ${attr}-opacity="${a}"` : ''); };
  const isClear = c => !c || c === 'transparent' || /rgba\(.*,\s*0\)$/.test(c);
  const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const secOf = el => { const s = el.closest('.sec'); return s ? s.querySelector('h2').textContent.trim() : (el.closest('.legend') ? 'Legend' : (el.closest('.cap') ? 'Caption' : 'Page')); };
  const push = (sec, s) => out.push([sec, s]);
  const all = document.body.querySelectorAll('*');
  for (const el of all) {
    if (el.closest('svg')) continue;
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const sec = secOf(el);
    const rad = parseFloat(cs.borderTopLeftRadius) || 0;
    if (!isClear(cs.backgroundColor)) push(sec, `<rect x="${r.left}" y="${r.top}" width="${r.width}" height="${r.height}" rx="${rad}" ${F("fill", cs.backgroundColor)}/>`);
    // inset box-shadow underline used on section titles
    const m = cs.boxShadow.match(/(rgba?\([^)]*\))\s+0px\s+-(\d+)px\s+0px\s+0px\s+inset/);
    if (m) push(sec, `<rect x="${r.left}" y="${r.bottom - +m[2]}" width="${r.width}" height="${m[2]}" ${F("fill", m[1])}/>`);
    const sides = [['Top', r.left, r.top, r.right, r.top], ['Bottom', r.left, r.bottom, r.right, r.bottom], ['Left', r.left, r.top, r.left, r.bottom], ['Right', r.right, r.top, r.right, r.bottom]];
    const uniform = ['Top','Bottom','Left','Right'].every(s => cs['border'+s+'Width'] === cs.borderTopWidth && cs['border'+s+'Style'] === cs.borderTopStyle && cs['border'+s+'Color'] === cs.borderTopColor);
    if (uniform && rad > 0 && parseFloat(cs.borderTopWidth) > 0 && cs.borderTopStyle !== 'none') {
      const w = parseFloat(cs.borderTopWidth), dash = cs.borderTopStyle === 'dashed' ? ' stroke-dasharray="4 3"' : cs.borderTopStyle === 'dotted' ? ' stroke-dasharray="1.5 2"' : '';
      push(sec, `<rect x="${r.left + w/2}" y="${r.top + w/2}" width="${r.width - w}" height="${r.height - w}" rx="${rad}" fill="none" ${F("stroke", cs.borderTopColor)} stroke-width="${w}"${dash}/>`);
    } else {
      for (const [s, x1, y1, x2, y2] of sides) {
        const w = parseFloat(cs['border'+s+'Width']);
        if (!w || cs['border'+s+'Style'] === 'none') continue;
        const o = (s === 'Top' || s === 'Left') ? w/2 : -w/2;
        const [ax, ay, bx, by] = (s === 'Top' || s === 'Bottom') ? [x1, y1+o, x2, y2+o] : [x1+o, y1, x2+o, y2];
        push(sec, `<line x1="${ax}" y1="${ay}" x2="${bx}" y2="${by}" ${F("stroke", cs['border'+s+'Color'])} stroke-width="${w}"/>`);
      }
    }
  }
  // icons
  for (const svg of document.querySelectorAll('.ic svg, svg[viewBox]')) {
    if (svg.closest('.ic') === null && svg.parentElement !== document.body) continue;
    const r = svg.getBoundingClientRect(); if (!r.width) continue;
    const inner = svg.innerHTML;
    const vb = svg.getAttribute('viewBox').split(/\s+/).map(Number); push(secOf(svg), `<g transform="translate(${r.left} ${r.top}) scale(${r.width / vb[2]} ${r.height / vb[3]})">${inner}</g>`);
  }
  // text, one <text> per rendered line
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    const p = node.parentElement;
    if (!p || p.closest('svg') || p.closest('style') || p.closest('script')) continue;
    const raw = node.textContent; if (!raw.trim()) continue;
    const cs = getComputedStyle(p);
    let txt = raw; if (cs.textTransform === 'uppercase') txt = txt.toUpperCase();
    const font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    cv.font = font; const asc = cv.measureText('Hg').fontBoundingBoxAscent;
    const lines = []; const re = /\S+\s*/g; let mm;
    while ((mm = re.exec(raw))) {
      const rg = document.createRange(); rg.setStart(node, mm.index); rg.setEnd(node, mm.index + mm[0].trimEnd().length);
      const rr = rg.getClientRects()[0]; if (!rr) continue;
      const word = txt.substr(mm.index, mm[0].length);
      const L = lines.find(l => Math.abs(l.top - rr.top) < 2);
      if (L) L.s += word; else lines.push({top: rr.top, left: rr.left, s: word});
    }
    const ls = cs.letterSpacing === 'normal' ? '' : ` letter-spacing="${cs.letterSpacing}"`;
    const fam = cs.fontFamily.includes('Mono') ? 'DejaVu Sans Mono, monospace' : cs.fontFamily.includes('Serif') ? 'DejaVu Serif, Georgia, serif' : 'Inter, Helvetica, Arial, sans-serif';
    for (const l of lines) push(secOf(p), `<text x="${l.left.toFixed(2)}" y="${(l.top + asc).toFixed(2)}" font-family="${fam}" font-size="${cs.fontSize}" font-weight="${cs.fontWeight}"${cs.fontStyle === 'italic' ? ' font-style="italic"' : ''}${ls} ${F("fill", cs.color)}>${esc(l.s.trimEnd())}</text>`);
  }
  const defs = document.querySelector('body > svg defs');
  return {items: out, defs: defs ? defs.innerHTML : '', w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight};
}
"""

src, dst = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1800, 'height': 1000})
    pg.goto('file://' + src); pg.wait_for_timeout(300)
    d = pg.evaluate(JS); b.close()

groups = {}
for sec, s in d['items']:
    groups.setdefault(sec, []).append(s)
order = list(dict.fromkeys(sec for sec, _ in d['items']))
body = ''.join(f'<g id="{sec.replace(" ", "_")}">' + ''.join(groups[sec]) + '</g>' for sec in order)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{d["w"]}" height="{d["h"]}" viewBox="0 0 {d["w"]} {d["h"]}">'
       f'<defs>{d["defs"]}</defs><rect width="100%" height="100%" fill="#ffffff"/>{body}</svg>')
open(dst, 'w').write(svg)
print(len(d['items']), d['w'], d['h'], len(svg))
