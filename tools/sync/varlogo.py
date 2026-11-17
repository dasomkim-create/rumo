"""RUMO 가변 로고 — r·u·m은 고정, o 자리에 동그란 심볼이 번갈아 들어와요.
심볼마다 BrandSymbols 장표의 등장 인터랙션(rs-* 키프레임)을 그대로 쓰고, CSS만으로 돌아가요 (JS 없음).
랜딩 · 상세 페이지 · 장표 · 아티팩트가 모두 이 파일의 markup()을 써요.
  python3 tools/sync/varlogo.py   → 점검용 미리보기 출력"""
import re, json, os, subprocess, tempfile
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
_src = open(os.path.join(REPO, 'project', 'BrandSymbols.dc.html')).read()
KEYFRAMES = '\n'.join(re.findall(r'@keyframes rs-[a-z-]+\{.*?\}\}', _src.split('</helmet>')[0], re.S))
_lg = _src[_src.find('class Component'):]
_j = _lg.find('const S = ') + len('const S = '); _k = _lg.find('];\n', _j) + 1
SYM = {s['name']: s for s in json.loads(_lg[_j:_k])}
# 원래 로고의 꽃 (BrandLogo 장표와 같은 모양 · 같은 자리) — 히어로에서 스케치로 그려진 뒤 첫 o가 돼요
FLOWER = re.search(r'class="spin" fill="#ffc447" d="(M425[^"]+)"', open(os.path.join(REPO, 'project', 'BrandLogo.dc.html')).read()).group(1)
LETTERS = ('M0 100V50A50 50 0 0 1 50 0H70V20H50A30 30 0 0 0 20 50V100ZM104 0H124V50A30 30 0 0 0 184 50V0H204V50A50 50 0 0 1 104 50Z'
           'M228 100V45A45 45 0 0 1 318 45V100H298V45A25 25 0 0 0 248 45V100ZM298 100V45A45 45 0 0 1 388 45V100H368V45A25 25 0 0 0 318 45V100Z')

# o 자리: 글자 높이(100)보다 크게 잡아야 눈으로 같은 무게가 돼요 (시각 보정)
SLOT_CX, SLOT_CY, SLOT = 478, 50, 122
STEP = 3.0   # 심볼 하나가 머무는 시간(초) — 등장 0.6 · 머묾 · 퇴장
# (이름, 시각 보정 배율) — 꽉 찬 원은 작게, 성긴 모양은 크게
PICK = [('꽃', 1.0), ('링', .86), ('물결 원', .9), ('네잎', .9), ('선버스트', 1.02), ('햇빛', 1.04), ('여덟 잎', 1.06), ('여덟 꼭지 별', 1.02),
        ('별표', .98), ('쪼갠 원', .86), ('원과 반달', 1.0), ('다섯 점', 1.04), ('도트', .9), ('바람개비', 1.02), ('달걀', .88), ('육각형', .9)]
USES = [('꽃', '기본', '앱 아이콘 · 첫 화면'), ('선버스트', '지금 먹을 시간', '알림이 울리는 중'), ('도트', '듣는 중', '"먹었어"를 기다릴 때'),
        ('네잎', '교감', '루모와 대화한 뒤'), ('햇빛', '오늘', '하루가 시작될 때')]

_bbox_cache = {}
def _bbox(name):
    """92 상자 안에서 실제로 칠해진 영역 (렌더로 측정)."""
    if name in _bbox_cache: return _bbox_cache[name]
    s = SYM[name]
    body = ''.join(f'<path fill="#000" fill-rule="{p["fr"]}" d="{p["d"]}"/>' for p in s['parts'] if p['d'] != 'M0 0')
    body += ''.join(f'<path fill="none" stroke="#000" stroke-width="{p["sw"]}" stroke-linecap="{p["cap"]}" d="{p["sd"]}"/>' for p in s['parts'] if p['d'] == 'M0 0')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 92 92" width="368" height="368"><g transform="{s["tr"]}">{body}</g></svg>'
    with tempfile.TemporaryDirectory() as d:
        open(d + '/a.svg', 'w').write(svg); subprocess.run(['rsvg-convert', d + '/a.svg', '-o', d + '/a.png'], check=True)
        from PIL import Image
        b = Image.open(d + '/a.png').getbbox()
    _bbox_cache[name] = tuple(v / 4 for v in b); return _bbox_cache[name]

def _anim(a, shift, stagger, step=None):
    """'rs-pop 6s ease 0.29s infinite both' → STEP초 주기 · 위치 맞춘 delay"""
    if a == 'none': return 'none'
    m = re.match(r'(\S+) ([\d.]+)s (.+) ([\d.]+)s infinite both$', a)
    name, _, ease, _d = m.groups()
    return f'{name} {step or STEP}s {ease} {shift + stagger:.2f}s infinite both'

def variant(name, k, n, letc=None, mono=None, step=None, delay=0.0):
    """심볼 하나(o 자리) — k번째, 전체 n개. 비어 있을 땐 숨김."""
    if name == '로고꽃':                 # 원래 로고 꽃: 처음 그려진 그대로 머물다 꽃 인터랙션(rs-bloom)으로 퇴장·재등장
        step = step or STEP; shift = k * step - n * step + delay
        m = re.match(r'(\S+) [\d.]+s (.+) [\d.]+s infinite both$', SYM['꽃']['parts'][0]['anim'])
        an = f'{m.group(1)} {step}s {m.group(2)} {shift:.2f}s infinite both'
        win = f'animation:vl-win {n * step}s linear {shift:.2f}s infinite both'
        # 원래 로고처럼 14초에 한 바퀴 천천히 돌아요 (바깥 g = 회전, 안쪽 path = 꽃 인터랙션)
        return (f'<g class="vl-o" data-n="{name}" style="{win}"><g style="transform-box:fill-box;transform-origin:center;animation:vl-spin 14s linear infinite">'
                f'<path fill="{mono or "#ffc447"}" d="{FLOWER}" style="transform-box:fill-box;transform-origin:50% 50%;animation:{an}"/></g></g>')
    s = SYM[name]; opt = dict(PICK)[name]
    x0, y0, x1, y1 = _bbox(name); sc = SLOT * opt / max(x1 - x0, y1 - y0)
    tr = f'translate({SLOT_CX} {SLOT_CY}) scale({sc:.4f}) translate({-(x0 + x1) / 2:.2f} {-(y0 + y1) / 2:.2f}) {s["tr"]}'
    step = step or STEP
    shift = k * step - n * step + delay  # 음수 delay → 처음부터 제 차례에 맞춰 돌아요 (delay: 첫 심볼이 시작하는 시각)
    ds = [float(re.search(r' ([\d.]+)s infinite', p[a]).group(1)) for p in s['parts'] for a in ('anim', 'sanim') if p[a] != 'none']
    d0 = min(ds) if ds else 0
    out = []
    for p in s['parts']:
        st = lambda a: (float(re.search(r' ([\d.]+)s infinite', p[a]).group(1)) - d0) * .5 if p[a] != 'none' else 0
        col = mono or p['fill']; scol = mono or p['sc'] if p['sc'] != 'none' else 'none'
        out.append(f'<path d="{p["sd"]}" fill="none" stroke="{scol}" stroke-width="{p["sw"]}" stroke-linecap="{p["cap"]}" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" style="animation:{_anim(p["sanim"], shift, st("sanim"), step)}"/>')
        out.append(f'<path d="{p["d"]}" fill="{col}" fill-rule="{p["fr"]}" style="transform-box:fill-box;transform-origin:{p["origin"]};animation:{_anim(p["anim"], shift, st("anim"), step)}"/>')
    win = f'animation:vl-win {n * step}s linear {shift:.2f}s infinite both'
    return f'<g class="vl-o" data-n="{name}" style="{win}"><g transform="{tr}">{"".join(out)}</g></g>'

CSS = KEYFRAMES + '''
@keyframes vl-spin{to{transform:rotate(360deg)}}
@keyframes vl-win{0%,6.249%{visibility:visible}6.25%,100%{visibility:hidden}}
.vl-still{display:none}
@media (prefers-reduced-motion: reduce){.vl-o{display:none}.vl-still{display:inline}}
.vl.pick .vl-o{animation:none!important;visibility:hidden}.vl.pick .vl-o.on{visibility:visible}.vl.pick .vl-still{display:none}
[data-vl-pick]{cursor:pointer;transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .25s}
[data-vl-pick]:hover,[data-vl-pick].on{transform:translateY(-3px);box-shadow:inset 0 0 0 1.5px #d5ff44}
'''
def css(n=len(PICK)):
    return CSS.replace('6.249%', f'{100 / n - .001:.3f}%').replace('6.25%', f'{100 / n:.3f}%')

def markup(letc='#ffffff', mono=None, names=None, viewbox='-6 -16 560 132', step=None, delay=0.0):
    """<svg> 한 개: 글자 + 돌아가는 o. 같은 페이지에 여러 개 넣어도 돼요 (css()는 한 번만)."""
    names = names or [n for n, _ in PICK]
    vs = ''.join(variant(nm, k, len(names), mono=mono, step=step, delay=delay) for k, nm in enumerate(names))
    still = re.sub(r' style="[^"]*animation:[^"]*"', '', variant('꽃', 0, 1, mono=mono)).replace('class="vl-o"', 'class="vl-still"')
    return (f'<svg class="vl" viewBox="{viewbox}" role="img" aria-label="rumo 가변 로고 — o 자리에 심볼이 바뀌어 들어와요" style="overflow:visible">'
            f'<path fill="{letc}" d="{LETTERS}"/>{vs}{still}</svg>')

def static(name, letc='#ffffff', mono=None, viewbox='-6 -16 560 132'):
    """멈춘 로고 한 장 (심볼 하나, 애니메이션 없음)."""
    v = re.sub(r' style="[^"]*animation:[^"]*"', '', variant(name, 0, 1, mono=mono)).replace(' class="vl-o"', '').replace(f' data-n="{name}"', '')
    return f'<svg viewBox="{viewbox}" role="img" aria-label="rum + {name}" style="overflow:visible"><path fill="{letc}" d="{LETTERS}"/>{v}</svg>'

# 심볼 카드에 올리면(폰은 탭) 큰 로고의 o가 그 심볼로 — 그 심볼의 등장 인터랙션이 처음부터 재생되고 머물러요.
# 카드: data-vl-pick="이름", 같은 섹션 안의 svg.vl 이 대상. 손을 떼면 원래 순서로 돌아가요.
HOVER_JS = r"""<script>(function(){
var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
function host(el){var s=el.closest('section');return (s&&s.querySelector('svg.vl'))||document.querySelector('svg.vl')}
function clear(svg){if(!svg)return;svg.classList.remove('pick');svg.querySelectorAll('.vl-o.on').forEach(function(g){g.classList.remove('on');g.querySelectorAll('path').forEach(function(p){if(p.dataset.a!=null){p.style.animation=p.dataset.a;delete p.dataset.a}})})}
function pick(el){var svg=host(el);if(!svg)return;clear(svg);var g=svg.querySelector('.vl-o[data-n="'+el.dataset.vlPick+'"]');if(!g)return;
 svg.classList.add('pick');g.classList.add('on');
 g.querySelectorAll('path').forEach(function(p){var a=p.style.animation;if(!a||a==='none'||a.indexOf('vl-spin')>=0)return;p.dataset.a=a;
  var m=a.match(/^(\S+) ([\d.]+)s (.+) (-?[\d.]+)s infinite both$/);if(!m)return;var d=parseFloat(m[2]);
  p.style.animation='none';void p.getBoundingClientRect();
  if(reduce){p.style.animation='none';return}
  p.style.animation=m[1]+' '+d+'s '+m[3]+' 0s 1 both';
  setTimeout(function(){if(p.dataset.a!=null)p.style.animationPlayState='paused'},d*1000*.5)})}
document.querySelectorAll('[data-vl-pick]').forEach(function(el){
 el.addEventListener('mouseenter',function(){pick(el)});
 el.addEventListener('mouseleave',function(){clear(host(el));el.classList.remove('on')});
 el.addEventListener('click',function(){var on=el.classList.contains('on');document.querySelectorAll('[data-vl-pick].on').forEach(function(o){o.classList.remove('on')});if(on){clear(host(el))}else{el.classList.add('on');pick(el)}});});
})();</script>"""

def meaning(name):
    s = SYM[name]; return s['mean'] if s['g'] != 'mark' else '영양제 표식'

if __name__ == '__main__':
    out = os.environ.get('OUT', '/tmp/vl-preview.html')
    open(out, 'w').write(f'<!doctype html><meta charset="utf-8"><style>body{{background:#141414;margin:40px}}{css()}</style>{markup()}<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:40px">' + ''.join(static(n) for n, _ in PICK) + '</div>')
    print(out)
