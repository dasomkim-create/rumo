"""구성품 2D 도식 아이콘 (v8 기준). 장표와 랜딩이 같이 써요.
ICONS: [(key, 이름, 수량, 배송 때, 완성 후, svg)]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dieline import Sh, tray, rect, PI

ST = 'stroke="#9AA0A8" stroke-width="1.6" stroke-linejoin="round"'
BOARD, KIT, GREEN, BLUE, GRAY, DARK = '#EEF0F3', '#FFFFFF', '#A8D14B', '#8EA8EA', '#C9CDD3', '#2B2E33'
def svg(body, vb='0 0 160 120'): return f'<svg viewBox="{vb}" width="100%" height="100%" aria-hidden="true" style="display:block">{body}</svg>'

def house():
    b = f'<path d="M30 112 V52 L80 22 L130 52 V112 Z" fill="{BOARD}" {ST}/>'
    for k in range(6):                                   # 지붕 끝 체크 띠
        b += f'<rect x="{38+k*14}" y="{(52 - 30*(1-abs((38+k*14+7)-80)/50))+2:.1f}" width="7" height="7" fill="{[GRAY,GREEN,GRAY,BLUE,GRAY,GREEN][k]}"/>'
    b += f'<rect x="64" y="6" width="32" height="14" rx="3" fill="{BOARD}" {ST}/><rect x="72" y="10" width="16" height="5" rx="2.5" fill="#050505"/>'
    b += f'<line x1="80" y1="58" x2="80" y2="112" stroke="#9AA0A8" stroke-width="1.6"/>'
    b += f'<path d="M48 96 V82 a9 9 0 0 1 18 0 V96 Z" fill="#FFF0B8" {ST}/>'
    b += f'<text x="105" y="86" font-family="Pretendard,sans-serif" font-size="10" font-weight="800" fill="{DARK}" text-anchor="middle">RUMO</text>'
    return svg(b)

def tray_icon():
    paths, labs, folds = tray(lambda: Sh(0, 0))
    d = ' '.join(p.path() for p in paths)
    return svg(f'<g transform="translate(80 92) scale(0.3)"><path d="{d}" fill="{KIT}" fill-rule="evenodd" stroke="#9AA0A8" stroke-width="3.6" stroke-linejoin="round"/></g>')

def runners():
    b = ''
    for k, l in enumerate('DCBA'):
        x, y = 28 + k * 8, 30 - k * 6 + 18
        b += f'<path d="M{x} {y} h88 v66 h-88 Z M{x+5} {y+5} v56 h78 v-56 Z" fill="#F3F4F6" fill-rule="evenodd" {ST}/>'
        b += f'<text x="{x+6}" y="{y+64}" font-family="Pretendard,sans-serif" font-size="7" font-weight="800" fill="#6B7079">{l}</text>'
    b += f'<path d="M64 38 h20 v32 h-20 Z" fill="#FFFFFF" stroke="#EC008C" stroke-width="1.2"/><path d="M90 52 h14 v18 h-14 Z" fill="#FFFFFF" stroke="#EC008C" stroke-width="1.2"/>'
    return svg(b)

def plinth():
    b = f'<path d="M34 50 L80 32 L126 50 L80 68 Z" fill="#FFFFFF" {ST}/><path d="M34 50 V64 L80 82 V68 Z" fill="#E3E6EA" {ST}/><path d="M126 50 V64 L80 82 V68 Z" fill="#D5D9DF" {ST}/>'
    for cx, cy in [(62, 46), (80, 39), (80, 54), (98, 47)]:
        b += f'<path d="M{cx-7} {cy} L{cx} {cy-3} L{cx+7} {cy} L{cx} {cy+3} Z" fill="#E3E6EA" stroke="#9AA0A8" stroke-width="1"/>'
    b += '<text x="80" y="104" font-family="Pretendard,sans-serif" font-size="9" font-weight="600" fill="#9AA0A8" text-anchor="middle">네 발 홈</text>'
    return svg(b)

def mat():
    b = ''
    for i in range(8):
        for j in range(6):
            f = '#FFFFFF' if (i + j) % 2 else GRAY
            if (i + j) % 2 == 0 and (i * 7 + j * 13) % 11 == 3: f = GREEN
            if (i + j) % 2 == 0 and (i * 7 + j * 13) % 11 == 8: f = BLUE
            b += f'<rect x="{32+i*12}" y="{24+j*12}" width="12" height="12" fill="{f}"/>'
    return svg(b + f'<rect x="32" y="24" width="96" height="72" fill="none" {ST}/>')

def coaster():
    c = lambda cx, cy, r: ''.join(f'<circle cx="{cx+a*r*.9}" cy="{cy+bb*r*.9}" r="{r}" fill="{GREEN}"/>' for a, bb in [(-1, 0), (1, 0), (0, -1), (0, 1)])
    return svg(c(54, 60, 11) + c(106, 60, 11))

def bone():
    return svg(f'<g transform="translate(80 60) rotate(-18)"><rect x="-38" y="-9" width="76" height="18" rx="4" fill="{BLUE}"/>'
               + ''.join(f'<circle cx="{sx*40}" cy="{sy*8}" r="10" fill="{BLUE}"/>' for sx in (-1, 1) for sy in (-1, 1)) + '</g>')

def remote():
    b = f'<rect x="66" y="16" width="28" height="88" rx="10" fill="#F1F2F4" {ST}/>'
    b += ''.join(f'<circle cx="{x}" cy="{y}" r="5" fill="#8EC8EC"/>' for x, y in [(80, 36), (72, 56), (88, 56), (80, 72)])
    return svg(b)

def robot():
    b = f'<ellipse cx="80" cy="96" rx="34" ry="14" fill="#F7F7F6" {ST}/>'
    b += f'<circle cx="80" cy="56" r="34" fill="#F7F7F6" {ST}/><rect x="56" y="48" width="48" height="20" rx="10" fill="#1C1D20"/>'
    b += '<circle cx="70" cy="58" r="4" fill="#8FE6FF"/><circle cx="90" cy="58" r="4" fill="#8FE6FF"/>'
    b += f'<ellipse cx="42" cy="54" rx="7" ry="20" fill="#1C1D20"/><ellipse cx="118" cy="54" rx="7" ry="20" fill="#1C1D20"/>'
    return svg(b)

ICONS = [
    ('house', '하우스 박스', '1', '양문형 선물 상자', '루모의 집 지붕·벽', house()),
    ('robot', '루모', '1', '받침 블록 위에 고정', '집 안에서 생활', robot()),
    ('plinth', '받침 블록', '1', '네 발을 홈에 끼워 고정', '아치 안 루모 침대', plinth()),
    ('tray', '동네 트레이', '1', '대문 창 · 굿즈 홈', '병풍형 루모 동네', tray_icon()),
    ('runners', '런너 A~D', '4', '바닥 완충 4겹', '부품 13개 → 틀은 받침대', runners()),
    ('mat', '바닥 매트', '1', '런너 위 덮개', '집 바닥 체크 무늬', mat()),
    ('coaster', '네잎 코스터', '2', '트레이 둥근 창', '컵 받침', coaster()),
    ('bone', '뼈 네임태그', '1', '트레이 세로 창', '손잡이 이름표', bone()),
    ('remote', '리모컨', '1', '트레이 긴 창', '루모 조작', remote()),
]
