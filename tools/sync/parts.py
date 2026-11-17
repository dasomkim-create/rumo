"""조립 세트 — 부품 하나하나 (v8 기준). docs/package/kit.html 을 만들어요.
각 부품을 따로 그린 2D 도면(인쇄 무늬 포함) + 코드 · 크기 · 쓰는 단계 · 완성 후 역할."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dieline import Sh, rect, ribbon, tray, PI, runner_parts
import re
import kit_icons
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
GREEN, BLUE, GRAY, DARK, KIT = '#A8D14B', '#8EA8EA', '#C9CDD3', '#2B2E33', '#FFFFFF'
ST = 'stroke="#9AA0A8" stroke-width="{w}" stroke-linejoin="round"'
FONT = 'Pretendard,sans-serif'

def svg(body, x0, y0, w, h, pad=10, sw=1.2):
    return (f'<svg viewBox="{x0-pad:.1f} {y0-pad:.1f} {w+2*pad:.1f} {h+2*pad:.1f}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" aria-hidden="true">'
            + body.replace('{w}', str(sw)) + '</svg>')
def P(sh, fill=KIT): return f'<path d="{sh.path()}" fill="{fill}" fill-rule="evenodd" {ST}/>'

def runner_part(i, code, overlay=None, sw=1.6, pad=8):
    """런너 i 에서 code 로 시작하는 부품을 탭·홈 그대로 따로 그려요."""
    for fn, lab, _ in runner_parts(i):
        if lab.startswith(code):
            sh = fn(Sh(0, 0)); d = sh.path()
            nums = [(float(a), float(b)) for a, b in re.findall(r'[ML]\s*(-?[\d.]+) (-?[\d.]+)', d)]
            xs = [a for a, _ in nums]; ys = [b for _, b in nums]
            x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
            body = f'<path d="{d}" fill="{KIT}" fill-rule="evenodd" {ST}/>' + (overlay(x0, y0, x1, y1) if overlay else '')
            return svg(body, x0, y0, x1 - x0, y1 - y0, pad, sw)
    raise KeyError(code)
def sign_ov(x0, y0, x1, y1):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return f'<text x="{cx:.1f}" y="{cy+7:.1f}" font-family="{FONT}" font-size="20" font-weight="800" fill="{DARK}" text-anchor="middle">RUMO</text><circle cx="{cx+36:.1f}" cy="{cy-12:.1f}" r="2.6" fill="{GREEN}"/>'
def wall_ov(x0, y0, x1, y1):
    xl, yb = x0 + (x1 - x0 - 30) / 2 if False else None, None
    return ''
def arch_panel():
    s = Sh(0, 0); s.M(-132, 0).L(-102, 0).L(-102, 115); s.A(-27, 115, 75, PI, 0, True); s.L(48, 0).L(78, 0).L(78, 200).L(-132, 200).Z()
    return svg(P(s), -132, -200, 210, 200, 8, 2)
def plate(w, h, fill=KIT, extra=''): return svg(f'<rect x="0" y="0" width="{w}" height="{h}" fill="{fill}" {ST}/>' + extra, 0, 0, w, h, 8, 2 if max(w, h) > 120 else 1)
def sign():
    t = f'<text x="45" y="27" font-family="{FONT}" font-size="20" font-weight="800" fill="{DARK}" text-anchor="middle">RUMO</text><circle cx="81" cy="8" r="2.6" fill="{GREEN}"/>'
    return plate(90, 40, KIT, t)
def chimney_wall():
    st = ''.join(f'<rect x="0" y="{70-(r+1)*7}" width="30" height="7" fill="{DARK}"/>' for r in range(10) if r % 2 == 0)
    return plate(30, 70, KIT, st)
def rib(kind, col, amp):
    s = ribbon(Sh(0, 0), 0, 0, False, amp)
    if kind == 'clover': top = ''.join(f'<circle cx="{0+a*7.2:.1f}" cy="{-103+b*7.2:.1f}" r="8" fill="{GREEN}"/>' for a, b in [(-1, 0), (1, 0), (0, -1), (0, 1)])
    elif kind == 'dot': top = f'<circle cx="0" cy="-103" r="8" fill="none" stroke="{BLUE}" stroke-width="6"/>'
    else: top = f'<path d="M-10 -97 h20 v-10 a10 10 0 0 0 -20 0 z" fill="#DFE2E7" stroke="#9AA0A8" stroke-width="1"/>'
    return svg(P(s, col) + top, -22, -118, 44, 120, 6, 1)
def runner_frame():
    s = Sh(0, 0); rect(s, -132, 0, 132, 217); h = Sh(0, 0); rect(h, -124, 8, 124, 209)
    return svg(f'<path d="{s.path()} {h.path()}" fill="#F3F4F6" fill-rule="evenodd" {ST}/>', -132, -217, 264, 217, 8, 2.4)
def tray_part():
    paths, labs, folds = tray(lambda: Sh(0, 0))
    body = f'<path d="{" ".join(p.path() for p in paths)}" fill="{KIT}" fill-rule="evenodd" {ST}/>'
    tt = 'WELCOME · HOME · RUMO'; a0, a1 = -PI * .86, -PI * .14
    for k, ch in enumerate(tt):
        aa = a0 + (a1 - a0) * k / (len(tt) - 1); x, y = math.cos(aa) * 60, -130 + math.sin(aa) * 60
        body += f'<text transform="translate({x:.1f},{y:.1f}) rotate({math.degrees(aa + PI / 2):.0f})" font-family="{FONT}" font-size="10" font-weight="700" fill="{DARK}" text-anchor="middle" dominant-baseline="middle">{ch}</text>'
    body += ''.join(f'<rect x="{-66+k*10.15:.1f}" y="-8" width="10.2" height="8" fill="{"#FFFFFF" if k%2 else (GREEN if k==4 else (BLUE if k==8 else GRAY))}"/>' for k in range(13))
    return svg(body, -132, -236, 264, 316, 8, 2.4)
def plinth():
    b = f'<rect x="-73" y="-76" width="146" height="152" fill="#FFFFFF" {ST}/>'
    for x, z, w_, d_ in [(-32, -58, 34, 42), (32, -58, 34, 42), (-32, 55, 34, 40), (32, 55, 34, 40)]:
        b += f'<rect x="{x-w_/2}" y="{-z-d_/2}" width="{w_}" height="{d_}" fill="#EEF0F3" {ST}/>'
    b += f'<text x="0" y="4" font-family="{FONT}" font-size="11" font-weight="800" fill="#4A4F57" text-anchor="middle">RUMO</text>'
    return svg(b, -73, -76, 146, 152, 8, 2)
def mat():
    b = ''
    for i in range(10):
        for j in range(8):
            f = '#FFFFFF' if (i + j) % 2 else GRAY
            if (i + j) % 2 == 0:
                k = (i * 7 + j * 13) % 11
                if k == 3: f = GREEN
                if k == 8: f = BLUE
            b += f'<rect x="{i*26.2:.1f}" y="{j*26.5:.1f}" width="26.3" height="26.6" fill="{f}"/>'
    return svg(b + f'<rect x="0" y="0" width="262" height="212" fill="none" {ST}/>', 0, 0, 262, 212, 8, 2)
def window_frame():
    o = Sh(0, 0); r = 35; o.M(-35, 0).L(35, 0).L(35, 82 - r); o.A(0, 82 - r, r, 0, PI, False); o.L(-35, 0)
    i = Sh(0, 0); r2 = 28; i.M(-28, 6).L(28, 6).L(28, 78 - r2); i.A(0, 78 - r2, r2, 0, PI, False); i.L(-28, 6)
    b = f'<path d="{o.path()} {i.path()}" fill="{KIT}" fill-rule="evenodd" {ST}/><path d="{i.path()}" fill="#FFF0B8" opacity=".8"/>'
    b += f'<rect x="-1.5" y="-78" width="3" height="72" fill="{KIT}" {ST}/><rect x="-28" y="-43" width="56" height="3" fill="{KIT}" {ST}/>'
    return svg(b, -35, -82, 70, 82, 6, 1)

PARTS = [  # (그룹, 코드, 이름, 수량, 크기, 언제, 완성 후, svg)
    ('바로 쓰는 것', '—', '하우스 박스', 1, '270 × 220 × 220 · 판지 3T · 풀칠 탭 4 · 고정 홈 16', '받기 · 열기', '루모의 집 (지붕·벽·양문)', kit_icons.house()),
    ('바로 쓰는 것', '—', '받침 블록', 1, '146 × 152 × 16 · 폼보드 겹 + 바닥 4T', '받기 · 9단계', '아치 안 루모 침대', plinth()),
    ('바로 쓰는 것', '—', '동네 트레이', 1, '264 × 236 + 바닥판 132 × 90 · 5T · 리브 홈 4', '1 · 3단계', '리모컨 받침대 · 고리로 오른쪽 벽에 고정', tray_part()),
    ('바로 쓰는 것', '—', '바닥 매트', 1, '262 × 212 · 인쇄 시트', '4단계', '집 바닥 체크 무늬', mat()),
    ('런너에서 떼는 부품', 'A1', '아치 패널', 1, '210 × 195 · 5T · 바닥 탭 2', '7단계', '정면 아치 대문 · 바닥 홈에 끼움', runner_part(0, 'A1', sw=2)),
    ('런너에서 떼는 부품', 'C1', '칸막이', 1, '197 × 190 · 5T · 탭 2 · 홈 4', '6단계', '선반칸 세로 벽 · 바닥 홈에 끼움', runner_part(2, 'C1', sw=2)),
    ('런너에서 떼는 부품', 'D1 · D2', '선반', 2, '40 × 197 · 5T · 양쪽 탭 2', '6단계', '칸막이 홈 ↔ 오른쪽 벽 홈', runner_part(3, 'D1', sw=2)),
    ('런너에서 떼는 부품', 'D3', '문패', 1, '90 × 40 · 5T', '11단계', '왼쪽 벽 표시 자리에 붙임', sign()),
    ('런너에서 떼는 부품', 'D4–D7', '굴뚝 벽', 4, '앞뒤 30 × 45 / 63 · 옆 20 × 60 · 5T · 탭 1', '10단계', '지붕 경사에 맞춰 잘림 · 지붕 홈에 끼움', runner_part(3, 'D4', sw=1.2, pad=6)),
    ('런너에서 떼는 부품', 'D8', '굴뚝 캡', 1, '40 × 40 · 5T · 리본 홈 3', '10단계', '굴뚝 뚜껑 · 리본 3개 꽂는 자리', runner_part(3, 'D8', sw=1.2, pad=6)),
    ('런너에서 떼는 부품', 'B1', '물결 리본 · 네잎', 1, '약 18 × 115', '10단계', '굴뚝 위 연기', rib('clover', '#D9E9B0', 9)),
    ('런너에서 떼는 부품', 'B2', '물결 리본 · 동그라미', 1, '약 14 × 115', '10단계', '굴뚝 위 연기', rib('dot', '#C9D6F5', 7)),
    ('런너에서 떼는 부품', 'C2', '물결 리본 · 아치', 1, '약 16 × 115', '10단계', '굴뚝 위 연기', rib('arch', '#E6E8EC', 8)),
    ('런너에서 떼는 부품', 'E1 · E2', '고정 고리', 2, '48 × 15 · 5T · 양끝 탭', '3단계', '받침대 대문 ↔ 집 오른쪽 벽', runner_part(1, 'E1', sw=1.2, pad=6)),
    ('런너에서 떼는 부품', 'F1 · F2', '리모컨 리브', 2, '86 × 53 · 5T · 바닥 탭 2', '11단계', '바닥판 홈에 꽂아 리모컨을 20°로 받침', runner_part(1, 'F1', sw=1.2, pad=6)),
    ('런너에서 떼는 부품', 'A~D', '런너 틀', 4, '264 × 217 · 5T', '4 · 12단계', '겹쳐서 집 받침대', runner_frame()),
    ('문 포켓 · 굿즈', '—', '창틀', 1, '70 × 82 · 5T', '8단계', '왼문 아치 창', window_frame()),
    ('문 포켓 · 굿즈', '—', '네잎 코스터', 2, '약 36 × 36 · 4T', '1단계', '컵 받침 · 동네 둥근 창', kit_icons.coaster()),
    ('문 포켓 · 굿즈', '—', '뼈 네임태그', 1, '약 60 × 22 · 5T', '1단계', '손잡이 이름표', kit_icons.bone()),
    ('문 포켓 · 굿즈', '—', '리모컨', 1, '50 × 110 × 22', '1 · 11단계', '리브 F1·F2에 기대 두기', kit_icons.remote()),
]

def html():
    groups = []
    for g, *rest in PARTS:
        if not groups or groups[-1][0] != g: groups.append((g, []))
        groups[-1][1].append(rest)
    total = sum(p[3] for p in PARTS)
    body = ''
    for g, items in groups:
        body += f'<h2>{g}<span>{sum(i[2] for i in items)}개</span></h2><div class="grid">'
        for code, name, n, size, when, after, s in items:
            body += (f'<article class="part"><div class="fig">{s}</div><div class="meta"><div class="row"><b>{name}</b><span class="n">× {n}</span></div>'
                     + (f'<span class="code">{code}</span>' if code != '—' else '') +
                     f'<span class="size">{size}</span><span class="when">{when}</span><span class="after">→ {after}</span></div></article>')
        body += '</div>'
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>RUMO 조립 세트</title>
<meta name="description" content="RUMO 올인원 패키지 v8 — 부품 하나하나 보기">
<style>
@font-face{{font-family:"Pretendard";src:url("../fonts/PretendardVariable.woff2") format("woff2");font-weight:45 920;font-display:swap}}
*{{box-sizing:border-box}}
body{{margin:0;background:#000;color:#fff;font-family:Pretendard,-apple-system,system-ui,sans-serif;-webkit-font-smoothing:antialiased}}
header{{position:sticky;top:0;z-index:2;display:flex;align-items:center;justify-content:space-between;gap:12px;height:56px;padding:0 max(16px,env(safe-area-inset-right,0px)) 0 max(16px,env(safe-area-inset-left,0px));background:rgba(0,0,0,.82);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);border-bottom:1px solid #1c1c1e}}
header a{{color:#fff;text-decoration:none;font-size:14px;font-weight:600}}
.pill{{display:inline-flex;align-items:center;height:36px;padding:0 16px;border-radius:999px;background:#fff;color:#111!important}}
main{{max-width:1280px;margin:0 auto;padding:40px max(16px,env(safe-area-inset-right,0px)) 72px max(16px,env(safe-area-inset-left,0px));display:flex;flex-direction:column;gap:20px}}
h1{{margin:0;font-size:clamp(30px,4.4vw,48px);line-height:1.15;font-weight:700;letter-spacing:-.02em}}
.lead{{margin:0;color:#a3a3a3;font-size:16px;line-height:1.6;max-width:640px}}
.sum{{display:flex;gap:8px;flex-wrap:wrap}}
.sum span{{height:32px;display:inline-flex;align-items:center;padding:0 14px;border-radius:999px;background:#141416;color:#d4d4d4;font-size:14px}}
.sum b{{color:#d5ff44;margin-right:6px}}
h2{{margin:28px 0 0;display:flex;align-items:baseline;gap:10px;font-size:22px;font-weight:600}}
h2 span{{font-size:14px;color:#8a8a90;font-weight:500}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}}
.part{{border-radius:22px;background:#111113;padding:14px;display:flex;flex-direction:column;gap:12px;min-width:0}}
.fig{{height:180px;border-radius:16px;background:#1c1c1e;padding:14px}}
.meta{{display:flex;flex-direction:column;gap:4px;padding:0 4px 4px}}
.row{{display:flex;justify-content:space-between;align-items:baseline;gap:8px}}
.row b{{font-size:18px;font-weight:600}}
.n{{font-size:14px;color:#8a8a90;font-variant-numeric:tabular-nums}}
.code{{align-self:flex-start;height:22px;display:inline-flex;align-items:center;padding:0 8px;border-radius:6px;background:#26262a;color:#d4d4d4;font-size:12px;font-weight:700;letter-spacing:.02em}}
.size{{font-size:13px;color:#8a8a90;font-variant-numeric:tabular-nums}}
.when{{font-size:13px;color:#a3a3a3}}
.after{{font-size:14px;color:#d5ff44}}
@media (max-width:560px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}}.fig{{height:128px;padding:10px}}.row b{{font-size:15px}}.part{{padding:10px;border-radius:18px}}}}
</style>
</head>
<body>
<header><a href="../index.html#package">← 사용 방법으로</a><a class="pill" href="./">3D로 보기</a></header>
<main>
  <h1>조립 세트, 하나하나</h1>
  <p class="lead">상자에 들어 있는 부품을 낱개로 펼쳐 봤어요. 단계 번호는 사용 방법의 조립 순서예요. 크기는 mm, v8 3D 모형 기준이에요.</p>
  <div class="sum"><span><b>{len(PARTS)}</b>종류</span><span><b>{total}</b>조각</span><span>런너 4장에서 <b>17</b>부품을 떼고, 빈 틀 4장도 다시 써요</span></div>
  {body}
</main>
</body>
</html>
'''
open(os.path.join(REPO, 'docs', 'package', 'kit.html'), 'w', encoding='utf-8').write(html())
print('parts', len(PARTS), sum(p[3] for p in PARTS))
