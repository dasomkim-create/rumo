"""Inserts/refreshes the landing's Package manual section (docs/index.html).
Step texts, parts table and intro are read live from docs/package/index.html, so v8 updates flow in."""
import os, re
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CSS = '''
#package .pk-head{display:flex;flex-direction:column;gap:16px;max-width:760px}
#package .pk-grid{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:48px;align-items:start}
#package .pk-stage{position:sticky;top:88px;height:calc(100vh - 150px);max-height:680px;border-radius:28px;overflow:hidden;background:#eceef1;box-shadow:0 0 0 1px #1c1c1e}
#package .pk-stage iframe{display:block;width:100%;height:100%;border:0}
#package .pk-badge{position:absolute;left:20px;top:20px;display:flex;align-items:center;gap:10px;height:36px;padding:0 14px;border-radius:999px;background:#111;color:#fff;font-size:14px;font-weight:600;font-variant-numeric:tabular-nums;pointer-events:none}
#package .pk-badge i{font-style:normal;color:#d5ff44}
#package .pk-bar{position:absolute;left:20px;right:20px;bottom:20px;height:4px;border-radius:9px;background:rgba(0,0,0,.08);overflow:hidden;pointer-events:none}
#package .pk-bar span{display:block;height:100%;width:0;background:#111;border-radius:9px;transition:width 600ms cubic-bezier(.2,.8,.2,1)}
#package .pk-drag{position:absolute;right:20px;top:20px;height:36px;display:flex;align-items:center;padding:0 14px;border-radius:999px;background:rgba(255,255,255,.85);color:#555;font-size:13px;pointer-events:none}
#package .pk-steps{display:flex;flex-direction:column;gap:0;counter-reset:pk}
#package .pk-group{font-size:13px;font-weight:600;letter-spacing:.04em;color:#6c6c74;padding:40px 0 8px}
#package .pk-group:first-child{padding-top:0}
#package .pk-step{min-height:62vh;display:flex;flex-direction:column;justify-content:center;gap:14px;padding:24px 0;border-top:1px solid #232326;opacity:.32;transition:opacity 400ms ease}
#package .pk-step.on{opacity:1}
#package .pk-num{font-size:64px;line-height:1;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums;color:#fff}
#package .pk-step.pre .pk-num{font-size:20px;line-height:28px;color:#d5ff44}
#package .pk-txt{font-size:22px;line-height:34px;font-weight:500;color:#e5e5e5;text-wrap:pretty}
#package .pk-parts{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.3fr) minmax(0,1fr);border-top:1px solid #232326;font-size:15px;line-height:22px}
#package .pk-parts>div{display:contents}
#package .pk-parts span{padding:14px 12px 14px 0;border-bottom:1px solid #232326;color:#a3a3a3;min-width:0}
#package .pk-parts>div:first-child span{color:#6c6c74;font-size:13px;font-weight:600}
#package .pk-parts>div span:first-child{color:#fff;font-weight:600}
#package .pk-foot{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
@media (max-width:860px){
 #package .pk-grid{grid-template-columns:minmax(0,1fr);gap:0}
 #package .pk-stage{top:64px;height:44vh;z-index:2;border-radius:22px}
 #package .pk-stage iframe{pointer-events:none}
 #package .pk-drag{display:none}
 #package .pk-step{min-height:46vh}
 #package .pk-num{font-size:44px}
 #package .pk-txt{font-size:18px;line-height:28px}
 #package .pk-parts{font-size:13px;line-height:19px}
}
'''
HTML = '''<!-- package:start -->
  <style>''' + CSS + '''</style>
  <section id="package" class="sec"><div class="wrap" style="display: flex; flex-direction: column; gap: 56px;">
    <div class="pk-head reveal"><span class="eyebrow">Package · 사용설명서</span><h2 class="h-l">열면 선물,<br>조립하면 루모의 집.</h2><p class="lead" id="pkLead"></p></div>
    <div class="pk-grid">
      <div class="pk-stage"><iframe id="pkFrame" src="package/?embed" title="RUMO 올인원 패키지 3D 모형" loading="lazy"></iframe><div class="pk-badge" aria-live="polite"><i id="pkNo">—</i><span id="pkOf"></span></div><div class="pk-drag">드래그해서 돌려 보기</div><div class="pk-bar"><span id="pkBar"></span></div></div>
      <ol class="pk-steps" id="pkSteps" style="list-style: none; margin: 0; padding: 0;"></ol>
    </div>
    <div class="reveal" style="display: flex; flex-direction: column; gap: 20px;"><h3 style="margin: 0; font-size: 24px; line-height: 32px; font-weight: 600;">구성품이 하는 일</h3><div class="pk-parts" id="pkParts"></div></div>
    <div class="pk-foot"><span style="color: #8a8a90; font-size: 14px;" id="pkNote"></span><a class="pill" href="package/" style="height: 48px; padding: 0 24px; font-size: 16px;">3D로 직접 돌려 보기 →</a></div>
  </div></section>
  <script>
  (function () {
    var fr = document.getElementById('pkFrame'); if (!fr) return;
    var list = document.getElementById('pkSteps'), no = document.getElementById('pkNo'), of = document.getElementById('pkOf'), bar = document.getElementById('pkBar');
    var steps = [], cur = -1, raf = 0;
    function go() {
      var d; try { d = fr.contentDocument; } catch (e) { return; }
      if (!d || !d.getElementById('s-kit') || !d.getElementById('step')) { setTimeout(go, 300); return; }
      var $ = function (id) { return d.getElementById(id); };
      function val() { return { fold: +$('s-fold').value, door: +$('s-door').value, kit: +$('s-kit').value }; }
      function put(v) { ['fold', 'door', 'kit'].forEach(function (k) { var el = $('s-' + k); el.value = v[k]; el.dispatchEvent(new Event('input')); }); }
      function txt() { return ($('step').textContent || '').replace(/^\\s*\\d+\\s*/, '').trim(); }
      var N = +(($('v-kit').textContent.match(/\\/\\s*(\\d+)/) || [])[1] || 12);
      var sub = d.querySelector('aside .sub'); if (sub) document.getElementById('pkLead').textContent = sub.innerHTML.split(/<br\\s*\\/?>/i).pop().replace(/<[^>]*>/g, '').trim();
      document.getElementById('pkNote').textContent = (d.querySelector('aside h1') || {}).textContent ? d.querySelector('aside h1').textContent + ' 기준 · 탭·슬릿은 생략한 단순 모형이에요.' : '';
      var pre = [['전개도', { fold: 0, door: 0, kit: 0 }], ['배송', { fold: 1, door: 0, kit: 0 }], ['개봉', { fold: 1, door: 0.55, kit: 0 }]];
      pre.forEach(function (p) { put(p[1]); steps.push({ pre: p[0], v: p[1], t: txt() }); });
      for (var i = 1; i <= N; i++) { var v = { fold: 1, door: 0.55, kit: (i - 0.5) / N }; put(v); steps.push({ n: i, v: { fold: 1, door: 0.55, kit: i / N }, t: txt() }); }
      steps[0].t = '한 장으로 펼쳐진 하우스 박스가 바닥 → 측벽 → 지붕 → 손잡이 → 양문 순서로 접혀요.';
      var html = '<li class="pk-group">펼치고, 받고, 열기</li>';
      steps.forEach(function (s, k) {
        if (k === 3) html += '<li class="pk-group">조립하기 · ' + N + '단계</li>';
        html += '<li class="pk-step' + (s.pre ? ' pre' : '') + '" data-k="' + k + '"><span class="pk-num">' + (s.pre ? s.pre : String(s.n).padStart(2, '0')) + '</span><p class="pk-txt"></p></li>';
      });
      list.innerHTML = html;
      [].forEach.call(list.querySelectorAll('.pk-step'), function (li) { li.querySelector('.pk-txt').textContent = steps[+li.dataset.k].t; });
      var rows = d.querySelectorAll('aside .roles > div'), ph = '';
      [].forEach.call(rows, function (r) { ph += '<div>' + [].map.call(r.children, function (c) { return '<span>' + c.textContent.replace(/[<>&]/g, '') + '</span>'; }).join('') + '</div>'; });
      document.getElementById('pkParts').innerHTML = ph;
      put(steps[0].v); show(0, true);
      function tween(to) {
        cancelAnimationFrame(raf); var from = val(), t0 = performance.now();
        var dur = Math.min(4200, 900 + 1100 * Math.abs(to.kit - from.kit) * N + 1400 * Math.abs(to.fold - from.fold));
        if (matchMedia('(prefers-reduced-motion: reduce)').matches) { put(to); return; }
        (function f(now) { var p = Math.min(1, (now - t0) / dur), e = p < .5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
          put({ fold: from.fold + (to.fold - from.fold) * e, door: from.door + (to.door - from.door) * e, kit: from.kit + (to.kit - from.kit) * e });
          if (p < 1) raf = requestAnimationFrame(f); })(t0);
      }
      function show(k, now) {
        if (k === cur) return; cur = k; var s = steps[k];
        [].forEach.call(list.querySelectorAll('.pk-step'), function (li) { li.classList.toggle('on', +li.dataset.k === k); });
        no.textContent = s.pre ? s.pre : 'STEP ' + String(s.n).padStart(2, '0'); of.textContent = s.pre ? '' : '/ ' + N;
        bar.style.width = (100 * k / (steps.length - 1)) + '%';
        if (!now) tween(s.v);
      }
      var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) show(+e.target.dataset.k); }); }, { rootMargin: '-45% 0px -45% 0px' });
      [].forEach.call(list.querySelectorAll('.pk-step'), function (li) { io.observe(li); });
    }
    if (fr.contentDocument && fr.contentDocument.readyState === 'complete') go(); else fr.addEventListener('load', go);
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
