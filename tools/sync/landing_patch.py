"""Idempotent tweaks to docs/index.html: header (사용 방법 + mobile menu), Brand Book = cover only,
CTA without the GitHub button. Run after regenerating the landing."""
import os, re
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
p = os.path.join(REPO, 'docs', 'index.html'); s = open(p, encoding='utf-8').read()

# 1) header actions + menu
OLD = '<a class="pill" href="app/">앱 눌러 보기</a>\n    <span class="prog"'
NEW = ('<div class="nav-act"><a class="pill pill-ghost" href="#package">사용 방법<span class="nm-x">&nbsp;보기</span></a><a class="pill" href="app/">앱 눌러 보기</a>'
       '<button class="nav-menu" id="navMenu" type="button" aria-label="메뉴 열기" aria-expanded="false" aria-controls="navSheet"><i></i><i></i><i></i></button></div>\n    <span class="prog"')
if 'class="nav-act"' not in s:
    assert OLD in s; s = s.replace(OLD, NEW, 1)
SHEET = '''<div class="nav-sheet" id="navSheet" hidden><nav aria-label="전체 메뉴">
    <a href="#meet-rumo">Meet Rumo</a><a href="#how">How it works</a><a href="#confirm">Confirm</a><a href="#identity">Identity</a><a href="#symbols">Symbols</a><a href="#package">Package · 사용 방법</a><a href="deck.html">Brand Identity Guide</a>
    <span class="ns-row"><a class="pill" href="app/">앱 눌러 보기</a><a class="pill pill-ghost" href="package/kit.html">부품 하나하나</a></span></nav></div>
'''
if 'id="navSheet"' not in s:
    i = s.find('</header>') + len('</header>'); s = s[:i] + '\n  ' + SHEET + s[i:]
CSS = '''<style id="nav-extra">
.nav-act{display:flex;align-items:center;gap:8px}
.nav-menu{display:none;width:34px;height:34px;border:0;border-radius:999px;background:rgba(255,255,255,.12);cursor:pointer;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:0}
.nav-menu i{display:block;width:14px;height:1.5px;border-radius:2px;background:#fff;transition:transform 220ms ease,opacity 220ms ease}
.nav-menu[aria-expanded="true"] i:nth-child(1){transform:translateY(5.5px) rotate(45deg)}
.nav-menu[aria-expanded="true"] i:nth-child(2){opacity:0}
.nav-menu[aria-expanded="true"] i:nth-child(3){transform:translateY(-5.5px) rotate(-45deg)}
.nav-sheet{position:fixed;left:0;right:0;top:52px;bottom:0;z-index:19;background:rgba(0,0,0,.92);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px);padding:24px max(20px,4vw) calc(24px + env(safe-area-inset-bottom,0px));overflow:auto}
.nav-sheet nav{display:flex;flex-direction:column;gap:4px}
.nav-sheet nav>a{color:#fff;text-decoration:none;font-size:28px;line-height:36px;font-weight:600;padding:10px 0;border-bottom:1px solid #1c1c1e}
.nav-sheet .ns-row{display:flex;gap:8px;margin-top:24px}
.nav-sheet .ns-row .pill{height:48px;padding:0 22px;font-size:16px}
@media (max-width:760px){.nav-menu{display:inline-flex}.nav-act{gap:6px}.nav-act .pill{padding:0 13px}.nm-x{display:none}}
@media (min-width:761px){.nav-sheet{display:none!important}}
</style>
'''
if 'id="nav-extra"' not in s:
    s = s.replace('</head>', CSS + '</head>', 1)
JS = '''<script id="nav-extra-js">
(function(){var b=document.getElementById('navMenu'),sh=document.getElementById('navSheet');if(!b||!sh)return;
function set(o){sh.hidden=!o;b.setAttribute('aria-expanded',o?'true':'false');b.setAttribute('aria-label',o?'메뉴 닫기':'메뉴 열기');document.documentElement.style.overflow=o?'hidden':''}
b.addEventListener('click',function(){set(sh.hidden)});sh.addEventListener('click',function(e){if(e.target.closest('a'))set(false)});
document.addEventListener('keydown',function(e){if(e.key==='Escape')set(false)})})();
</script>
'''
if 'id="nav-extra-js"' not in s:
    s = s.replace('</body>', JS + '</body>', 1)

# 2) Brand Book: cover only
i = s.find('<section id="book"'); j = s.find('</section>', i) + len('</section>')
BOOK = '''<section id="book" class="sec"><div class="wrap" style="display: flex; flex-direction: column; gap: 32px;">
    <div class="reveal" style="display: flex; flex-direction: column; gap: 16px;"><span class="eyebrow">Brand Identity Guide</span><h2 class="h-l">브랜드 아이덴티티 가이드<br>보러가기 →</h2><p class="lead">로고·컬러·타입·보이스까지, 장표 안을 직접 눌러 볼 수 있어요.</p></div>
    <a class="bk-cover reveal" href="deck.html#1" aria-label="브랜드 아이덴티티 가이드 열기" style="position: relative; display: block; border-radius: 24px; overflow: hidden; box-shadow: 0 0 0 1px #1c1c1e; aspect-ratio: 16 / 9;"><img src="img/slide-01.jpg" alt="RUMO 브랜드 아이덴티티 가이드 표지" loading="lazy" style="width: 100%; height: 100%; object-fit: cover; display: block;"><span class="pill" style="position: absolute; right: 20px; bottom: 20px; height: 44px; padding: 0 20px; font-size: 15px;">보러가기</span></a>
  </div></section>'''
s = s[:i] + BOOK + s[j:]

# 3) CTA: no GitHub button; 장표 → 가이드, + 사용 방법
s = re.sub(r'<a class="pill pill-ghost" href="https://github.com/[^"]*"[^>]*>GitHub 소스</a>', '', s)
s = s.replace('<a class="pill pill-ghost" href="deck.html" style="height: 48px; padding: 0 24px; font-size: 16px;">장표로 보기</a>',
              '<a class="pill pill-ghost" href="#package" style="height: 48px; padding: 0 24px; font-size: 16px;">사용 방법 보기</a><a class="pill pill-ghost" href="deck.html" style="height: 48px; padding: 0 24px; font-size: 16px;">브랜드 가이드</a>')
s = s.replace('<a class="l" href="#book">Brand Book</a>', '<a class="l" href="#book">Guide</a>')
# 4) hero logo a little higher
s = s.replace('.hero-logo{position:absolute;left:50%;top:50%;', '.hero-logo{position:absolute;left:50%;top:43%;')
open(p, 'w', encoding='utf-8').write(s); print('patched')
