"""Builds the landing's Symbols section (docs/index.html) from project/BrandSymbols.dc.html.
Re-run after the symbols slide changes: python3 tools/sync/symbols_section.py"""
import re, json, os
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src = open(os.path.join(REPO, 'project', 'BrandSymbols.dc.html')).read()
kf = '\n'.join(re.findall(r'@keyframes rs-[a-z-]+\{.*?\}\}', src.split('</helmet>')[0], re.S))
lg = src[src.find('class Component'):]
G = json.loads(re.search(r'const G = (\{.*?\});', lg, re.S).group(1))
j = lg.find('const S = ') + len('const S = '); k = lg.find('];\n', j) + 1
S = json.loads(lg[j:k])
data = [{'g': r['g'], 'n': r['name'], 'c': r['code'], 'm': r['mean'], 'mo': r['motion'], 'tr': r['tr'],
         'p': [{k2: p[k2] for k2 in ('d', 'fill', 'fr', 'anim', 'origin', 'sanim', 'sc', 'sw', 'cap')} | ({'sd': p['sd']} if p['sd'] != p['d'] else {}) for p in r['parts']]} for r in S]
CSS = kf + '''
#symbols .sy-top{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap}
#symbols .sy-ctl{display:flex;flex-direction:column;align-items:flex-end;gap:10px}
#symbols .sy-row{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
#symbols .sy-chip{height:38px;padding:0 16px;border:0;border-radius:999px;cursor:pointer;font:500 15px Pretendard,system-ui,sans-serif;background:#1f1f1f;color:#d4d4d4;transition:background 200ms ease,color 200ms ease}
#symbols .sy-chip[aria-pressed="true"]{background:#fff;color:#111}
#symbols .sy-act{height:44px;padding:0 20px;font-weight:600;font-size:16px;background:#fff;color:#111}
#symbols .sy-act.alt{background:#1f1f1f;color:#fff}#symbols .sy-act.alt[aria-pressed="true"]{background:#d5ff44;color:#111}
#symbols .sy-grid{position:relative;display:grid;grid-template-columns:repeat(auto-fill,minmax(108px,1fr));gap:12px}
#symbols .sym{position:relative;height:124px;border-radius:22px;background:#141414;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;border:0;padding:0;color:inherit;font:inherit;cursor:pointer;transition:opacity 300ms ease,background 500ms ease}
#symbols .sym.dim{opacity:.15}
#symbols .sy-grid.scatter .sym{background:rgba(20,20,20,0)}
#symbols .sy-grid.scatter .sym-label{opacity:0}
#symbols .sy-mv{transition:transform 900ms cubic-bezier(.2,.8,.2,1)}
#symbols .glyph{position:relative;width:56px;height:56px}
#symbols .glyph svg{position:absolute;inset:0;width:56px;height:56px;overflow:visible}
#symbols .sy-grid.spin .glyph{animation:rumo-spin var(--sd) linear infinite var(--dir)}
#symbols .sym:hover .glyph,#symbols .sym.open .glyph{animation:rumo-wiggle 700ms ease-in-out infinite}
#symbols .sym-label{font-size:14px;line-height:20px;font-weight:500;color:#a3a3a3;transition:opacity 400ms ease}
#symbols .tip{position:absolute;left:50%;bottom:calc(100% + 10px);width:240px;margin-left:-120px;box-sizing:border-box;padding:14px 16px;border-radius:18px;background:#fff;color:#111;box-shadow:0 16px 40px rgba(0,0,0,.4);display:flex;flex-direction:column;gap:4px;text-align:left;opacity:0;transform:translateY(8px);pointer-events:none;transition:opacity 200ms ease,transform 260ms cubic-bezier(.2,.8,.2,1);z-index:6}
#symbols .sym:hover .tip,#symbols .sym:focus-visible .tip,#symbols .sym.open .tip{opacity:1;transform:none}
#symbols .sym:hover,#symbols .sym.open{z-index:5}
#symbols .tip b{font-size:12px;line-height:16px;font-weight:600}
#symbols .tip strong{font-size:18px;line-height:26px;font-weight:600}
#symbols .tip span{font-size:14px;line-height:21px;color:#4a4a4a}
#symbols .tip i{font-style:normal;font-size:13px;line-height:19px;color:#6b6b6b}
#symbols .sy-legend{display:flex;gap:18px;flex-wrap:wrap;font-size:14px;color:#a3a3a3}
#symbols .sy-legend span{display:inline-flex;align-items:center;gap:8px}
#symbols .sy-legend span::before{content:"";width:8px;height:8px;border-radius:99px;background:var(--c)}
@keyframes rumo-wiggle{0%,100%{transform:rotate(-10deg)}50%{transform:rotate(10deg)}}
@keyframes rumo-spin{to{transform:rotate(360deg)}}
@media (max-width:640px){#symbols .sy-ctl{align-items:flex-start}#symbols .sy-row{justify-content:flex-start}#symbols .sy-grid{grid-template-columns:repeat(auto-fill,minmax(72px,1fr));gap:8px}#symbols .sym{height:92px;border-radius:16px;gap:6px}#symbols .glyph,#symbols .glyph svg{width:40px;height:40px}#symbols .sym-label{font-size:12px;line-height:16px}#symbols .tip{width:200px;margin-left:-100px}}
@media (prefers-reduced-motion: reduce){#symbols *{animation:none!important;transition:none!important}}
'''
legend = ''.join(f'<span style="--c: {c}">{n}</span>' for k, (n, c) in G.items())
chips = ''.join(f'<button type="button" class="sy-chip" data-g="{g}" aria-pressed="{"true" if g=="all" else "false"}">{l}</button>' for g, l in [('all', '전체'), ('role', '역할'), ('state', '상태'), ('ctx', '맥락'), ('mark', '표식')])
HTML = f'''<!-- symbols:start -->
  <style>{CSS}</style>
  <section id="symbols" class="sec"><div class="wrap" style="display: flex; flex-direction: column; gap: 40px;">
    <div class="sy-top reveal"><div style="display: flex; flex-direction: column; gap: 16px; min-width: 0;"><span class="eyebrow">Symbols &amp; Motion</span><h2 class="h-l">모양마다<br>그려지는 방식이 달라요.</h2><p class="lead">올려보면 뜻이, 흩어보면 리듬이 보여요. 휴대폰에서는 눌러 보세요.</p><div class="sy-legend">{legend}</div></div>
    <div class="sy-ctl"><div class="sy-row" role="group" aria-label="심볼 분류">{chips}</div><div class="sy-row"><button type="button" class="sy-chip sy-act" id="syScatter" aria-pressed="false">흩어지기</button><button type="button" class="sy-chip sy-act alt" id="sySpin" aria-pressed="false">계속 회전</button></div></div></div>
    <div class="sy-grid reveal" id="syGrid"></div>
  </div></section>
  <script>
  (function () {{
    var G = {json.dumps({k: v for k, v in G.items()}, ensure_ascii=False)};
    var S = {json.dumps(data, ensure_ascii=False, separators=(',', ':'))};
    var grid = document.getElementById('syGrid'); if (!grid) return;
    function esc(t) {{ return String(t).replace(/[&<>"]/g, function (c) {{ return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]; }}); }}
    grid.innerHTML = S.map(function (r, i) {{
      var svg = r.p.map(function (p) {{
        return '<svg viewBox="0 0 92 92" aria-hidden="true"><g transform="' + r.tr + '"><path d="' + (p.sd || p.d) + '" fill="none" stroke="' + p.sc + '" stroke-width="' + p.sw + '" stroke-linecap="' + p.cap + '" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" style="animation:' + p.sanim + '"></path><path d="' + p.d + '" fill="' + p.fill + '" fill-rule="' + p.fr + '" style="transform-box:fill-box;transform-origin:' + p.origin + ';animation:' + p.anim + '"></path></g></svg>';
      }}).join('');
      var g = G[r.g];
      return '<button type="button" class="sym" data-g="' + r.g + '" aria-label="' + esc(r.n + ' — ' + r.m) + '"><div class="sy-mv"><div class="glyph" style="--sd:' + (6 + (i % 5) * 2) + 's;--dir:' + (i % 2 ? 'reverse' : 'normal') + '">' + svg + '</div></div><span class="sym-label">' + esc(r.n) + '</span><span class="tip" role="tooltip"><b style="color:' + g[1] + '">' + esc(g[0]) + '</b><strong>' + esc(r.n) + ' · ' + esc(r.c) + '</strong><span>' + esc(r.m) + '</span><i>모션 · ' + esc(r.mo) + '</i></span></button>';
    }}).join('');
    var cards = [].slice.call(grid.children), chips = [].slice.call(document.querySelectorAll('#symbols .sy-chip[data-g]'));
    chips.forEach(function (c) {{ c.addEventListener('click', function () {{
      chips.forEach(function (o) {{ o.setAttribute('aria-pressed', o === c ? 'true' : 'false'); }});
      cards.forEach(function (k) {{ k.classList.toggle('dim', c.dataset.g !== 'all' && k.dataset.g !== c.dataset.g); }});
    }}); }});
    cards.forEach(function (k) {{ k.addEventListener('click', function () {{ var o = k.classList.contains('open'); cards.forEach(function (x) {{ x.classList.remove('open'); }}); if (!o) k.classList.add('open'); }}); }});
    document.addEventListener('click', function (e) {{ if (!grid.contains(e.target)) cards.forEach(function (x) {{ x.classList.remove('open'); }}); }});
    var sc = document.getElementById('syScatter'), sp = document.getElementById('sySpin'), scattered = false;
    function place() {{
      var W = grid.clientWidth, H = grid.clientHeight, gr = grid.getBoundingClientRect();
      cards.forEach(function (k, i) {{
        var mv = k.firstChild;
        if (!scattered) {{ mv.style.transform = ''; return; }}
        var r = k.getBoundingClientRect(), cx = r.left - gr.left + r.width / 2, cy = r.top - gr.top + r.height / 2;
        var fx = ((i * 137) % 997) / 997, fy = ((i * 211) % 991) / 991;
        var tx = 40 + fx * (W - 80) - cx, ty = 40 + fy * (H - 80) - cy, rot = ((i * 73) % 720) - 360;
        mv.style.transform = 'translate(' + Math.round(tx) + 'px,' + Math.round(ty) + 'px) rotate(' + rot + 'deg) scale(' + (0.7 + (i % 4) * 0.25) + ')';
      }});
    }}
    sc.addEventListener('click', function () {{ scattered = !scattered; grid.classList.toggle('scatter', scattered); sc.textContent = scattered ? '모으기' : '흩어지기'; sc.setAttribute('aria-pressed', String(scattered)); place(); }});
    sp.addEventListener('click', function () {{ var on = !grid.classList.contains('spin'); grid.classList.toggle('spin', on); sp.textContent = on ? '회전 멈추기' : '계속 회전'; sp.setAttribute('aria-pressed', String(on)); }});
    window.addEventListener('resize', place);
  }})();
  </script>
  <!-- symbols:end -->
'''
p = os.path.join(REPO, 'docs', 'index.html'); s = open(p).read()
if '<!-- symbols:start -->' in s:
    s = re.sub(r'<!-- symbols:start -->.*?<!-- symbols:end -->\n', HTML, s, flags=re.S)
else:
    i = s.find('<section id="identity"'); j = s.find('<section', i + 10)
    s = s[:j] + HTML.lstrip() + '\n  ' + s[j:]
open(p, 'w').write(s); print('symbols:', len(S), 'html bytes', len(HTML))
