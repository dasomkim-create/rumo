"""가변 로고를 랜딩에 넣어요 (여러 번 돌려도 같은 결과).
 1) 히어로 큰 로고의 꽃 → o 자리가 심볼마다 다른 인터랙션으로 바뀜
 2) Symbols 섹션 다음에 '가변 로고' 섹션 + '설명 자세히 보기' → logo/
 3) docs/logo/index.html 상세 페이지
  python3 tools/sync/varlogo_section.py"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import varlogo as V
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
P = os.path.join(REPO, 'docs', 'index.html')
s = open(P, encoding='utf-8').read()

def slot_groups(mono=None):
    # 히어로: 처음엔 꽃(기본 로고)이 머물다가, 8초마다 다음 심볼이 각자의 인터랙션으로 들어와요
    m = V.markup(mono=mono, step=8.0, names=['로고꽃'] + [n for n, _ in V.PICK if n != '꽃'])
    return m[m.index('"/>', m.index(V.LETTERS)) + 3:m.rindex('</svg>')]

# 1) 히어로
hero = f'<g class="vl-hero">{slot_groups()}</g>'
if '<g class="vl-hero">' in s:
    s = re.sub(r'<g class="vl-hero">.*?<!--/vl-hero-->', hero + '<!--/vl-hero-->', s, count=1, flags=re.S)
else:
    s, n = re.subn(r'(<svg class="hero-logo".*?<g class="h-fill"><path fill="#ffffff" d="[^"]+"></path>)<g class="spin-slow"><path fill="#ffc447" d="[^"]+"></path></g>',
                   lambda m: m.group(1) + hero + '<!--/vl-hero-->', s, count=1, flags=re.S)
    assert n == 1, 'hero logo not found'

# 2) 섹션
uses = ''.join(f'<div class="vl-use"><div class="vl-mini">{V.static(n)}</div><b>{t}</b><span>{d}</span></div>' for n, t, d in V.USES)
CSS = V.css() + '''
#variable-logo .vl-stage{border-radius:28px;background:#0b0b0b;box-shadow:0 0 0 1px #1c1c1e;display:grid;place-items:center;padding:clamp(56px,10vw,140px) 8%}
#variable-logo .vl-stage svg{width:min(100%,880px);height:auto;display:block}
#variable-logo .vl-uses{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}
#variable-logo .vl-use{border-radius:20px;background:#141414;padding:20px 16px;display:flex;flex-direction:column;gap:6px;min-width:0}
#variable-logo .vl-mini svg{width:100%;height:auto;display:block;margin-bottom:10px}
#variable-logo .vl-use b{font-size:16px;font-weight:600}
#variable-logo .vl-use span{font-size:14px;color:#a3a3a3}
#variable-logo .vl-head{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap}
@media (max-width:760px){#variable-logo .vl-uses{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''
SEC = f'''<!-- varlogo:start -->
  <style>{CSS}</style>
  <section id="variable-logo" class="sec"><div class="wrap" style="display: flex; flex-direction: column; gap: 32px;">
    <div class="vl-head reveal"><div style="display: flex; flex-direction: column; gap: 16px; min-width: 0;"><span class="eyebrow">Variable Logo</span><h2 class="h-l">o 자리는<br>루모의 지금이에요.</h2><p class="lead">r·u·m은 그대로, o 자리에 동그란 심볼이 각자의 방식으로 나타나요.</p></div>
    <a class="pill" href="logo/" style="height: 44px; padding: 0 20px; font-size: 15px;">설명 자세히 보기 →</a></div>
    <div class="vl-stage reveal">{V.markup()}</div>
    <div class="vl-uses reveal">{uses}</div>
  </div></section>
<!-- varlogo:end -->'''
if '<!-- varlogo:start -->' in s:
    s = re.sub(r'<!-- varlogo:start -->.*?<!-- varlogo:end -->', lambda m: SEC, s, count=1, flags=re.S)
else:
    i = s.find('<section id="symbols"'); j = s.find('</section>', i) + len('</section>')
    j2 = s.find('</script>', j)                 # 심볼 섹션 스크립트 뒤
    j = j2 + len('</script>') if 0 < j2 - j < 400 else j
    s = s[:j] + '\n' + SEC + s[j:]
# Identity 섹션: 가이드 원을 꽃(중심 462, 50 · 지름 100)에 맞추고, 꽃은 원래 로고처럼 천천히 돌아요
s = s.replace('d="M478 -11A61 61 0 1 1 477.9 -11"', 'd="M462 0A50 50 0 1 1 461.9 0"')
s = re.sub(r'(<g class="s-fill"><path fill="#ffffff" d="[^"]+"></path>)(<path fill="#ffc447" d="[^"]+"></path>)(</g>)',
           r'\1<g style="transform-box:fill-box;transform-origin:center;animation:vl-spin 14s linear infinite">\2</g>\3', s, count=1)
# 꽃잎 스케치 선도 꽃과 함께 돌아요 (선과 채움이 어긋나지 않게)
if '<g class="s-petals"' not in s:
    s = re.sub(r'((?:<path class="sl" pathLength="1" d="M4[0-9.]+ [0-9.]+L[^"]+" fill="none" stroke="#ffc447" stroke-width="1.2" ></path>){3})',
               r'<g class="s-petals" style="transform-box:fill-box;transform-origin:center;animation:vl-spin 14s linear infinite">\1</g>', s, count=1)
# 히어로용 CSS (섹션 CSS와 같은 키프레임 사용) — 섹션 블록이 페이지에 있으므로 따로 안 넣어요
open(P, 'w', encoding='utf-8').write(s)

# 3) 상세 페이지
font = '../fonts/PretendardVariable.woff2'
cards = ''.join(f'<div class="card"><div class="lg">{V.static(n)}</div><b>{k:02d} {n}</b><span>{V.meaning(n)}</span></div>' for k, (n, _) in enumerate(V.PICK, 1))
rule_svg = (f'<svg viewBox="-6 -24 560 148" aria-hidden="true"><path fill="#f4f4f2" d="{V.LETTERS}"/>'
            f'<rect x="{V.SLOT_CX - V.SLOT / 2}" y="{V.SLOT_CY - V.SLOT / 2}" width="{V.SLOT}" height="{V.SLOT}" fill="none" stroke="#d5ff44" stroke-width="2" stroke-dasharray="7 5"/>'
            f'<line x1="-6" x2="400" y1="100" y2="100" stroke="#4d8df6" stroke-width="1.5"/><line x1="-6" x2="400" y1="0" y2="0" stroke="#4d8df6" stroke-width="1.5"/>'
            f'<text x="{V.SLOT_CX}" y="{V.SLOT_CY + V.SLOT / 2 + 18}" fill="#d5ff44" font-size="16" text-anchor="middle">{V.SLOT} × {V.SLOT}</text>'
            f'</svg>')
PAGE = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>RUMO 가변 로고</title>
<style>
@font-face{{font-family:"Pretendard";src:url("{font}") format("woff2");font-weight:45 920;font-display:swap}}
:root{{--bg:#050505;--panel:#141414;--line:#1f1f1f;--fg:#fff;--sub:#a3a3a3;--lime:#d5ff44;--blue:#4d8df6;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:Pretendard,-apple-system,system-ui,sans-serif;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1120px;margin:0 auto;padding-block:32px 96px;padding-left:max(20px,env(safe-area-inset-left,0px));padding-right:max(20px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:72px}}
nav{{display:flex;justify-content:space-between;align-items:center}}
nav a{{color:var(--sub);text-decoration:none;font-size:15px}} nav a:hover{{color:#fff}}
.eyebrow{{font-size:16px;font-weight:600;color:var(--blue)}}
h1{{margin:12px 0 0;font-size:clamp(36px,6vw,72px);line-height:1.08;font-weight:600;letter-spacing:-.04em}}
h2{{margin:0 0 20px;font-size:24px;font-weight:600;letter-spacing:-.02em}}
.lead{{margin:16px 0 0;font-size:clamp(17px,1.5vw,21px);line-height:1.6;color:var(--sub);max-width:46ch}}
.stage{{border-radius:28px;background:#0b0b0b;box-shadow:0 0 0 1px var(--line);display:grid;place-items:center;padding:clamp(56px,10vw,140px) 8%}}
.stage svg{{width:min(100%,880px);height:auto;display:block}}
.rules{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}
.rule{{background:var(--panel);border-radius:22px;padding:22px;display:flex;flex-direction:column;gap:8px;min-width:0}}
.rule .n{{font-size:14px;color:var(--lime);font-weight:600}} .rule b{{font-size:18px;font-weight:600}} .rule p{{margin:0;color:var(--sub);font-size:15px;line-height:1.55}}
.rule svg{{width:100%;height:auto;margin-bottom:8px;font-family:Pretendard,sans-serif}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
.card{{background:var(--panel);border-radius:20px;padding:22px 18px 18px;display:flex;flex-direction:column;gap:4px;min-width:0}}
.card .lg svg{{width:100%;height:auto;display:block;margin-bottom:12px}}
.card b{{font-size:15px;font-weight:600}} .card span{{font-size:13px;color:var(--sub);line-height:1.45}}
.uses{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}}
@media (max-width:820px){{.rules{{grid-template-columns:1fr}}.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.uses{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
{V.css()}
</style>
<!--rumo-icons--><link rel="icon" href="../icon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="../apple-touch-icon.png"><!--/rumo-icons-->
</head><body><div class="wrap">
<nav><a href="../#variable-logo">← 랜딩으로</a><a href="../deck.html">브랜드 가이드</a></nav>
<header><span class="eyebrow">Variable Logo</span><h1>o 자리는<br>루모의 지금이에요.</h1>
<p class="lead">r·u·m은 그대로 두고, 마지막 o 자리에 동그란 심볼이 하나씩 들어와요. 심볼마다 그려지는 방식이 달라서, 로고가 바뀌는 순간에도 루모의 성격이 보여요.</p></header>
<div class="stage">{V.markup()}</div>
<section><h2>규칙 3가지</h2><div class="rules">
<div class="rule">{rule_svg}<span class="n">01</span><b>o는 글자보다 크게</b><p>o 자리 상자는 {V.SLOT} × {V.SLOT}. 글자 높이 100보다 크게 잡아야 눈으로 같은 무게로 보여요. 꽉 찬 원은 조금 작게, 성긴 모양은 조금 크게 넣어요.</p></div>
<div class="rule"><span class="n">02</span><b>r·u·m은 그대로</b><p>글자 모양과 간격은 바꾸지 않아요. 심볼 중심은 상자 가운데에 맞춰요.</p></div>
<div class="rule"><span class="n">03</span><b>한 화면에 o 하나</b><p>상황에 맞는 심볼 하나만 써요. 정할 게 없으면 기본인 꽃으로 돌아와요. 색은 심볼 원래 색, 또는 한 색.</p></div>
</div></section>
<section><h2>앱에서 이렇게 바뀌어요</h2><div class="uses">{''.join(f'<div class="card"><div class="lg">{V.static(n)}</div><b>{t}</b><span>{d}</span></div>' for n, t, d in V.USES)}</div></section>
<section><h2>o 자리에 들어가는 심볼 {len(V.PICK)}</h2><div class="grid">{cards}</div></section>
</div></body></html>
'''
os.makedirs(os.path.join(REPO, 'docs', 'logo'), exist_ok=True)
open(os.path.join(REPO, 'docs', 'logo', 'index.html'), 'w', encoding='utf-8').write(PAGE)
print('landing + logo/ updated')
