"""Inserts/refreshes the landing's Package · 사용 방법 section (docs/index.html).
A one-screen manual: 3D model + step card with prev/next, phase tabs, step strip and autoplay.
Step texts and the parts table are read live from docs/package/index.html (= v8), so v8 updates flow in."""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import kit_icons
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CSS = '''
#package .pk-head{display:flex;flex-direction:column;gap:16px;max-width:760px}
#package .pk-card{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);border-radius:32px;overflow:hidden;background:#111113;box-shadow:0 0 0 1px #1c1c1e}
#package .pk-stage{position:relative;aspect-ratio:4 / 3;background:#eceef1;min-width:0}
#package .pk-stage iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
#package .pk-load{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#8a8f98;font-size:14px;pointer-events:none}
#package .pk-drag{position:absolute;left:16px;bottom:16px;height:30px;display:flex;align-items:center;padding:0 12px;border-radius:999px;background:rgba(255,255,255,.9);color:#555;font-size:12px;font-weight:500;pointer-events:none}
#package .pk-panel{display:flex;flex-direction:column;gap:24px;padding:32px;min-width:0}
#package .pk-tabs{display:flex;gap:4px;flex-wrap:wrap}
#package .pk-tab{height:30px;padding:0 11px;border:0;border-radius:999px;background:#1f1f22;color:#a3a3a3;font:500 13px Pretendard,system-ui,sans-serif;cursor:pointer;transition:background 200ms ease,color 200ms ease}
#package .pk-tab[aria-selected="true"]{background:#fff;color:#111}
#package .pk-body{flex:1;display:flex;flex-direction:column;gap:12px;min-height:200px}
#package .pk-no{display:flex;align-items:baseline;gap:10px;font-variant-numeric:tabular-nums}
#package .pk-no b{font-size:56px;line-height:1;font-weight:700;letter-spacing:-.02em;color:#fff}
#package .pk-no span{font-size:16px;color:#6c6c74}
#package .pk-no i{font-style:normal;font-size:13px;font-weight:600;color:#111;background:#d5ff44;border-radius:999px;padding:4px 10px;align-self:center}
#package .pk-t{margin:0;font-size:24px;line-height:34px;font-weight:600;color:#fff;text-wrap:pretty}
#package .pk-d{margin:0;font-size:16px;line-height:25px;color:#a3a3a3;text-wrap:pretty}
#package .pk-body.swap{animation:pk-in 360ms cubic-bezier(.2,.8,.2,1)}
@keyframes pk-in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
#package .pk-nav{display:flex;align-items:center;gap:8px}
#package .pk-btn{width:48px;height:48px;border:0;border-radius:999px;background:#1f1f22;color:#fff;font-size:20px;cursor:pointer;display:inline-flex;align-items:center;justify-content:center}
#package .pk-btn:disabled{opacity:.3;cursor:default}
#package .pk-play{height:48px;padding:0 20px;border:0;border-radius:999px;background:#fff;color:#111;font:600 15px Pretendard,system-ui,sans-serif;cursor:pointer;margin-left:auto;white-space:nowrap}
#package .pk-btn:focus-visible,#package .pk-play:focus-visible,#package .pk-tab:focus-visible,#package .pk-dot:focus-visible{outline:2px solid #7960ff;outline-offset:2px}
#package .pk-strip{grid-column:1 / -1;display:flex;gap:4px;padding:16px 20px 20px;border-top:1px solid #1c1c1e}
#package .pk-dot{flex:1;height:28px;border:0;padding:0;background:transparent;cursor:pointer;display:flex;flex-direction:column;justify-content:flex-end;gap:6px;color:#55555c;font:600 11px Pretendard,system-ui,sans-serif;font-variant-numeric:tabular-nums}
#package .pk-dot::before{content:"";display:block;height:4px;border-radius:9px;background:#2a2a2e;transition:background 300ms ease}
#package .pk-dot.done::before{background:#5a5a60}
#package .pk-dot.on::before{background:#d5ff44}
#package .pk-dot.on{color:#fff}
#package .pk-parts{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.3fr) minmax(0,1fr);border-top:1px solid #232326;font-size:15px;line-height:22px}
#package .pk-parts>div{display:contents}
#package .pk-parts span{padding:14px 12px 14px 0;border-bottom:1px solid #232326;color:#a3a3a3;min-width:0}
#package .pk-parts>div:first-child span{color:#6c6c74;font-size:13px;font-weight:600}
#package .pk-parts>div span:first-child{color:#fff;font-weight:600}
#package .pk-kit{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}
#package .pk-k{border-radius:20px;background:#111113;padding:14px 14px 16px;display:flex;flex-direction:column;gap:10px;min-width:0}
#package .pk-ki{height:112px;border-radius:14px;background:#1c1c1e}
#package .pk-kn{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
#package .pk-kn b{font-size:17px;font-weight:600}
#package .pk-kn span{font-size:13px;color:#8a8a90}
#package .pk-k p{margin:0;display:flex;flex-direction:column;gap:2px;font-size:13px;line-height:19px}
#package .pk-k p span:first-child{color:#8a8a90}
#package .pk-k p span:last-child{color:#d5ff44}
@media (max-width:600px){#package .pk-kit{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}#package .pk-ki{height:88px}}
#package .pk-foot{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
@media (max-width:900px){
 #package .pk-card{grid-template-columns:minmax(0,1fr);border-radius:24px}
 #package .pk-panel{padding:20px 20px 16px;gap:16px}
 #package .pk-body{min-height:168px}
 #package .pk-no b{font-size:40px}
 #package .pk-t{font-size:19px;line-height:28px}
 #package .pk-d{font-size:14px;line-height:22px}
 #package .pk-strip{padding:12px 16px 16px;gap:3px}
 #package .pk-dot{font-size:0;height:16px}
 #package .pk-parts{font-size:13px;line-height:19px}
}
'''
KIT = ''.join(f'<div class="pk-k"><div class="pk-ki">{svg}</div><div class="pk-kn"><b>{n}</b><span>× {c}</span></div><p><span>배송 · {a}</span><span>완성 · {b}</span></p></div>' for _, n, c, a, b, svg in kit_icons.ICONS)
HTML = '''<!-- package:start -->
  <style>''' + CSS + '''</style>
  <section id="package" class="sec"><div class="wrap" style="display: flex; flex-direction: column; gap: 48px;">
    <div class="pk-head reveal"><span class="eyebrow">Package · 사용 방법</span><h2 class="h-l">열면 선물,<br>조립하면 루모의 집.</h2><p class="lead" id="pkLead"></p></div>
    <div class="pk-card" role="region" aria-label="패키지 사용 방법">
      <div class="pk-stage"><div class="pk-load">3D 모형을 불러오는 중…</div><iframe id="pkFrame" src="package/?embed" title="RUMO 올인원 패키지 3D 모형" loading="lazy" tabindex="-1"></iframe><div class="pk-drag">드래그해서 돌려 보기</div></div>
      <div class="pk-panel">
        <div class="pk-tabs" role="tablist" aria-label="단계 묶음" id="pkTabs"></div>
        <div class="pk-body" id="pkBody" aria-live="polite"><div class="pk-no"><b id="pkNo">—</b><span id="pkOf"></span><i id="pkPh"></i></div><p class="pk-t" id="pkT"></p><p class="pk-d" id="pkD"></p></div>
        <div class="pk-nav"><button class="pk-btn" id="pkPrev" type="button" aria-label="이전 단계">‹</button><button class="pk-btn" id="pkNext" type="button" aria-label="다음 단계">›</button><button class="pk-play" id="pkPlay" type="button">▶ 처음부터 자동으로</button></div>
      </div>
      <div class="pk-strip" id="pkStrip"></div>
    </div>
    <div class="reveal" style="display: flex; flex-direction: column; gap: 20px;"><h3 style="margin: 0; font-size: 24px; line-height: 32px; font-weight: 600;">상자 속 구성품</h3><div class="pk-kit">''' + KIT + '''</div></div>
    <div class="pk-foot"><span style="color: #8a8a90; font-size: 14px;" id="pkNote"></span><span style="display: flex; gap: 8px; flex-wrap: wrap;"><a class="pill pill-ghost" href="package/kit.html" style="height: 48px; padding: 0 24px; font-size: 16px;">부품 하나하나</a><a class="pill" href="package/" style="height: 48px; padding: 0 24px; font-size: 16px;">3D로 크게 보기 →</a></span></div>
  </div></section>
  <script>
  (function () {
    var fr = document.getElementById('pkFrame'); if (!fr) return;
    var E = function (id) { return document.getElementById(id); };
    var steps = [], cur = -1, raf = 0, timer = 0, playing = false, N = 12, started = false;
    function esc(t) { return String(t).replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }
    function split(t) {
      var m = t.match(/^(.*?)(?:\\s+[—→]\\s+|\\s*\\()(.*)$/);
      if (!m) return [t, ''];
      return [m[1].trim(), m[2].replace(/\\)\\s*$/, '').trim()];
    }
    function go() {
      var d; try { d = fr.contentDocument; } catch (e) { return; }
      var ready = d && d.getElementById('s-kit') && d.getElementById('step') && d.getElementById('step').innerHTML.trim();
      if (started) return;
      if (!ready) { setTimeout(go, 250); return; }
      started = true;
      var $ = function (id) { return d.getElementById(id); };
      function val() { return { fold: +$('s-fold').value, door: +$('s-door').value, kit: +$('s-kit').value }; }
      function put(v) { ['fold', 'door', 'kit'].forEach(function (k) { var el = $('s-' + k); el.value = v[k]; el.dispatchEvent(new Event('input')); }); }
      function read() { var el = $('step'), b = el.querySelector('b'), bt = b ? b.textContent.trim() : '', all = el.textContent.trim();
        return { b: bt, rest: (bt && all.indexOf(bt) === 0 ? all.slice(bt.length) : all).trim() }; }
      N = +(($('v-kit').textContent.match(/\\/\\s*(\\d+)/) || [])[1] || 12);
      var sub = d.querySelector('aside .sub'); if (sub) E('pkLead').textContent = sub.innerHTML.split(/<br\\s*\\/?>/i).pop().replace(/<[^>]*>/g, '').trim();
      var h1 = d.querySelector('aside h1'); E('pkNote').textContent = h1 ? h1.textContent.trim() + ' 기준 · 탭·슬릿은 생략한 단순 모형이에요.' : '';
      // 받기 전 3단계
      put({ fold: 1, door: 0, kit: 0 }); var r = read(), sp = split(r.rest);
      steps.push({ ph: '받기', no: '받기', t: '배송 상태로 도착해요', d: sp[1] || sp[0], v: { fold: 1, door: 0, kit: 0 } });
      steps.unshift({ ph: '접기', no: '접기', t: '한 장의 판이 집 모양 상자로 접혀요', d: '바닥 → 측벽 → 지붕 → 손잡이 → 양문 순서로 세워져요. 테이프 없이 판끼리 맞물려요.', v: { fold: 0, door: 0, kit: 0 } });
      put({ fold: 1, door: 0.55, kit: 0 }); r = read();
      steps.push({ ph: '열기', no: '열기', t: '양문을 열면 선물세트', d: r.rest, v: { fold: 1, door: 0.55, kit: 0 } });
      for (var i = 1; i <= N; i++) { put({ fold: 1, door: 0.55, kit: (i - 0.5) / N }); r = read(); sp = split(r.rest);
        steps.push({ ph: i < 6 ? '꺼내기' : (i < N ? '조립' : '완성'), no: String(i).padStart(2, '0'), t: sp[0], d: sp[1], v: { fold: 1, door: 0.55, kit: i / N } }); }
      var phs = []; steps.forEach(function (s, k) { if (!phs.some(function (p) { return p[0] === s.ph; })) phs.push([s.ph, k]); });
      E('pkTabs').innerHTML = phs.map(function (p) { return '<button class="pk-tab" role="tab" type="button" data-k="' + p[1] + '" aria-selected="false">' + esc(p[0]) + '</button>'; }).join('');
      E('pkStrip').innerHTML = steps.map(function (s, k) { return '<button class="pk-dot" type="button" data-k="' + k + '" aria-label="' + esc((/\\d/.test(s.no) ? s.no + '단계 ' : '') + s.t) + '">' + esc(/\\d/.test(s.no) ? String(+s.no) : s.ph) + '</button>'; }).join('');
      var rows = d.querySelectorAll('aside .roles > div'), ph = '';
      [].forEach.call(rows, function (r) { ph += '<div>' + [].map.call(r.children, function (c) { return '<span>' + esc(c.textContent) + '</span>'; }).join('') + '</div>'; });
      var pp = E('pkParts'); if (pp) pp.innerHTML = ph;
      var load = document.querySelector('#package .pk-load'); if (load) load.remove();
      function tween(to) {
        cancelAnimationFrame(raf); var from = val(), t0 = performance.now();
        var dur = Math.min(3600, 800 + 1000 * Math.abs(to.kit - from.kit) * N + 1600 * Math.abs(to.fold - from.fold) + 500 * Math.abs(to.door - from.door));
        if (matchMedia('(prefers-reduced-motion: reduce)').matches) { put(to); return; }
        (function f(now) { var p = Math.min(1, (now - t0) / dur), e = p < .5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
          put({ fold: from.fold + (to.fold - from.fold) * e, door: from.door + (to.door - from.door) * e, kit: from.kit + (to.kit - from.kit) * e });
          if (p < 1) raf = requestAnimationFrame(f); })(t0);
      }
      function show(k, quiet) {
        k = Math.max(0, Math.min(steps.length - 1, k)); if (k === cur) return; cur = k; var s = steps[k], num = /\\d/.test(s.no);
        E('pkNo').textContent = s.no; E('pkOf').textContent = num ? '/ ' + String(N).padStart(2, '0') : ''; E('pkPh').textContent = num ? s.ph : '';
        E('pkPh').style.display = num ? '' : 'none';
        E('pkT').textContent = s.t; E('pkD').textContent = s.d || ''; E('pkD').style.display = s.d ? '' : 'none';
        var b = E('pkBody'); b.classList.remove('swap'); void b.offsetWidth; b.classList.add('swap');
        E('pkPrev').disabled = k === 0; E('pkNext').disabled = k === steps.length - 1;
        [].forEach.call(E('pkStrip').children, function (x, j) { x.classList.toggle('on', j === k); x.classList.toggle('done', j < k); });
        var curPh = s.ph; [].forEach.call(E('pkTabs').children, function (x) { x.setAttribute('aria-selected', x.textContent === curPh ? 'true' : 'false'); });
        if (quiet) put(s.v); else tween(s.v);
      }
      function stop() { playing = false; clearTimeout(timer); E('pkPlay').textContent = '▶ 처음부터 자동으로'; }
      function auto() { if (!playing) return; if (cur >= steps.length - 1) { stop(); return; } show(cur + 1); timer = setTimeout(auto, 3200); }
      E('pkPrev').onclick = function () { stop(); show(cur - 1); };
      E('pkNext').onclick = function () { stop(); show(cur + 1); };
      E('pkPlay').onclick = function () { if (playing) { stop(); return; } playing = true; E('pkPlay').textContent = '❚❚ 멈추기'; show(0, true); timer = setTimeout(auto, 1600); };
      E('pkStrip').onclick = function (e) { var b = e.target.closest('.pk-dot'); if (b) { stop(); show(+b.dataset.k); } };
      E('pkTabs').onclick = function (e) { var b = e.target.closest('.pk-tab'); if (b) { stop(); show(+b.dataset.k); } };
      document.querySelector('#package .pk-card').addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') { stop(); show(cur + 1); } if (e.key === 'ArrowLeft') { stop(); show(cur - 1); } });
      show(0, true);
    }
    fr.addEventListener('load', go); setTimeout(go, 600);
  })();
  </script>
  <!-- package:end -->
'''
p = os.path.join(REPO, 'docs', 'index.html'); s = open(p, encoding='utf-8').read()
if '<!-- package:start -->' in s:
    s = re.sub(r'<!-- package:start -->.*?<!-- package:end -->\n', lambda m: HTML, s, flags=re.S)
else:
    i = s.find('<section id="book"'); s = s[:i] + HTML.lstrip() + '\n  ' + s[i:]
nav = '<a class="l" href="#identity">Identity</a>'
if 'href="#package"' not in s and nav in s:
    s = s.replace(nav, nav + '<a class="l" href="#package">Package</a>', 1)
open(p, 'w', encoding='utf-8').write(s); print('ok')
