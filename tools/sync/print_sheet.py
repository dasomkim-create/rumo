"""RUMO 올인원 패키지 v8 — 디자인 입힌 전개도 한 장 (박스 바깥면 · 안쪽 · 조립 부품 · 트레이 · 받침 블록 · 굿즈).
mm 단위 SVG, Illustrator에서 바로 열려요. 공개 폴더에 올리지 않아요 → PRINT_OUT(기본: 현재 폴더)에 저장.
그래픽은 v8 3D 모형의 텍스처를 벡터로 옮긴 것이에요."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dieline import Sh, rect, slot, label, fold, cut, runner_parts, ribbon, tray, GATES, CUT, FOLD, INK, MUTE, W, D, H, R, FIN, S, PI

GREEN, BLUE, GRAY, DARK, BOARD, KIT = '#A8D14B', '#8EA8EA', '#C9CDD3', '#2B2E33', '#EEF0F3', '#FBFBFC'
FONT = 'Pretendard, Apple SD Gothic Neo, sans-serif'
def txt(x, y, t, size, w=700, c=DARK, anchor='middle', extra=''):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{size:.2f}" font-weight="{w}" fill="{c}" text-anchor="{anchor}"{extra}>{t}</text>'
def box(x, y, w, h, c): return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{c}"/>'

def door_chk(X0, Y0, n, m, s, out):           # v8 chk(): 짝수 칸만 칠함, 일부 초록
    for i in range(n):
        for j in range(m):
            if (i + j) % 2 == 0: out.append(box(X0 + i * s, Y0 + j * s, s, s, GREEN if (i * 5 + j * 3) % 7 == 2 else GRAY))
def roof_chk(X0, Y0, w, h, cols, rows, out):  # v8 checker(): 흰/회색 + 포인트 초록·파랑
    cw, ch = w / cols, h / rows
    for i in range(cols):
        for j in range(rows):
            f = '#FFFFFF' if (i + j) % 2 else GRAY
            if (i + j) % 2 == 0:
                k = (i * 7 + j * 13) % 11
                if k == 3: f = GREEN
                if k == 8: f = BLUE
            out.append(box(X0 + i * cw, Y0 + j * ch, cw + .05, ch + .05, f))
def clover(cx, cy, r, c=GREEN): return ''.join(f'<circle cx="{cx + a * r * .9:.2f}" cy="{cy + b * r * .9:.2f}" r="{r:.2f}" fill="{c}"/>' for a, b in [(-1, 0), (1, 0), (0, -1), (0, 1)])

def outline(mirror):
    """박스 외곽 칼선 path (world 좌표) — mirror면 바깥면에서 본 모습."""
    o = Sh(0, 0, False)
    pts = [(-135, -D), (135, -D), (135, 0), (135 + D, 0), (490, 0), (490, H + R), (135 + D, H), (135 + D, H + S + FIN), (135, H + S + FIN), (135, H),
           (0, H + R), (-135, H), (-135, H + S + FIN), (-135 - D, H + S + FIN), (-135 - D, H), (-490, H + R), (-490, 0), (-135 - D, 0), (-135, 0)]
    m = -1 if mirror else 1
    for k, (x, y) in enumerate(pts): (o.M if k == 0 else o.L)(m * x, y)
    return o.Z().path()

def box_sheet(OX, OY, mirror):
    """mirror=True → 바깥면(인쇄면), False → 안쪽면. OX,OY = 뒷벽 아래 가운데의 출력 좌표."""
    m = -1 if mirror else 1
    X = lambda x: OX + m * x
    Y = lambda y: OY - y
    out = []
    g = []
    # 판지 바탕
    out.append(f'<path d="{outline(mirror)}" transform="translate({OX:.2f},{OY:.2f}) scale(1,-1)" fill="{BOARD if mirror else "#F7F8FA"}"/>')
    if mirror:
        for xw in (-135 - D, 135):                                   # 지붕 체크 (지붕 1·2)
            x0 = min(X(xw), X(xw + D)); roof_chk(x0, Y(H + S), D, S, 7, 5, out)
        # 왼문 바깥 (힌지 = world -355 → 출력 OX+355)
        hx = OX + 355; top = Y(H)
        door_chk(hx, top + 202, 17, 2, 8, out)
        # 오른문 바깥 (출력 OX-490 ~ OX-355)
        rx = OX - 490
        out.append(txt(rx + 67.5, top + 75, 'RUMO', 27, 800))
        out.append(txt(rx + 67.5, top + 87.5, 'A little care, every day.', 7.5, 500, '#6B7079'))
        out.append(clover(rx + 67.5, top + 130, 6))
        out.append(f'<path d="M{rx+100:.2f} {top+210:.2f} L{rx+100:.2f} {top+192.5:.2f} A10 10 0 0 1 {rx+120:.2f} {top+192.5:.2f} L{rx+120:.2f} {top+210:.2f} Z" fill="{BLUE}"/>')
    else:
        top = Y(H)
        lx = OX - 490                                                 # 왼문 안쪽 (u=0 → 먼 쪽 끝)
        door_chk(lx, top + 202, 17, 2, 8, out)
        rx = OX + 355                                                 # 오른문 안쪽 (u=0 → 힌지)
        out.append(txt(rx + 17.5, top + 62.5, 'Welcome', 11.5, 600, DARK, 'start'))
        out.append(txt(rx + 17.5, top + 76.5, 'Home.', 11.5, 600, DARK, 'start'))
        st = f'stroke="#3A3D42" stroke-width="1" fill="none" stroke-linecap="round"'
        out.append(f'<path d="M{rx+75} {top+155} L{rx+75} {top+117.5}" {st}/><circle cx="{rx+75}" cy="{top+107.5}" r="12" {st}/>'
                   f'<path d="M{rx+63} {top+110} Q{rx+50} {top+130} {rx+37.5} {top+120}" {st}/><circle cx="{rx+37.5}" cy="{top+120}" r="2" fill="#3A3D42"/>')
        door_chk(rx + 85, top + 175, 6, 5, 8, out)
        # 바닥 매트 (별도 인쇄 · 262×212) — 바닥 위에 겹쳐 표시
        mx, my = OX - 131, Y(0) + 4
        roof_chk(mx, my, 262, 212, 10, 8, out)
        out.append(f'<rect x="{mx:.2f}" y="{my:.2f}" width="262" height="212" fill="none" stroke="{MUTE}" stroke-width="0.4" stroke-dasharray="1.5 1.5"/>')
        out.append(txt(OX, my + 110, '바닥 매트 · 별도 인쇄 262 × 212', 7, 700, INK) )
    # 칼선 · 접는 선 (world → 출력)
    out.append(f'<path d="{outline(mirror)}" transform="translate({OX:.2f},{OY:.2f}) scale(1,-1)" fill="none" stroke="{CUT}" stroke-width="0.5"/>')
    for c in (-135 - D / 2, 135 + D / 2):
        out.append(f'<g transform="translate({OX:.2f},{OY:.2f}) scale({m},-1)">{cut(slot(Sh(0, 0, False), c, H + S + 37, 100, 24).path())}</g>')
    cx = -135 - D - 67.5; r = 28
    a = Sh(0, 0, False); a.M(cx + r, 95).L(cx - r, 95).L(cx - r, 95 + 72 - r); a.A(cx, 95 + 72 - r, r, PI, 0, True)
    out.append(f'<g transform="translate({OX:.2f},{OY:.2f}) scale({m},-1)"><path d="{a.path()}" fill="#FFFFFF" stroke="{CUT}" stroke-width="0.4"/></g>')
    out.append(fold(X(cx + r), Y(95), X(cx + r), Y(95 + 72 - r)))
    for x1, y1, x2, y2 in [(-135, 0, 135, 0), (-135, 0, -135, H), (135, 0, 135, H), (-135 - D, H, -135, H), (135, H, 135 + D, H),
                           (-135 - D, H + S, -135, H + S), (135, H + S, 135 + D, H + S), (-135 - D, 0, -135 - D, H), (135 + D, 0, 135 + D, H)]:
        out.append(fold(X(x1), Y(y1), X(x2), Y(y2)))
    for x, y, t in [(0, H / 2, '뒷벽'), (0, -D / 2 - (24 if not mirror else 0), '바닥'), (-135 - D / 2, H / 2, '측벽 1'), (135 + D / 2, H / 2, '측벽 2'),
                    (-135 - D / 2, H + S + 12, '손잡이 핀 1'), (135 + D / 2, H + S + 12, '손잡이 핀 2'), (-135 - D - 67.5, 40, '왼문'), (135 + D + 67.5, 40, '오른문')]:
        out.append(label(X(x), Y(y), t, 7, MUTE, 600))
    return out

def kit_sheet(X0, Y0):
    out = []; cw, ch, gap = 264, 217, 26
    names = ['런너 A', '런너 B', '런너 C', '런너 D']
    for i, (c, r) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)]):
        ox = X0 + c * (cw + gap) + 132; oy = Y0 + 16 + r * (ch + gap + 16) + ch
        f = Sh(ox, oy); rect(f, -132, 0, 132, 217); hh = Sh(ox, oy); rect(hh, -124, 8, 124, 209)
        out.append(f'<path d="{f.path()} {hh.path()}" fill="#F3F4F6" fill-rule="evenodd" stroke="{CUT}" stroke-width="0.5"/>')
        out.append(box(ox - 132 + 3, oy - 7 + 0.5, 14, 7, '#E9ECF0') + txt(ox - 125, oy - 1.6, 'ABCD'[i], 5, 800, '#4A4F57'))
        for x, y in GATES[i]: out.append(box(ox + x - 2, oy - y - 2, 4, 4, '#D5D9DF'))
        for fn, lab, (lx, ly) in runner_parts(i):
            sh = fn(Sh(ox, oy)); fill = KIT
            if 'B1' in lab: fill = '#D9E9B0'
            if 'B2' in lab: fill = '#C9D6F5'
            if 'C2' in lab: fill = '#E6E8EC'
            if 'D8' in lab: fill = '#DFE2E7'
            out.append(f'<path d="{sh.path()}" fill="{fill}" fill-rule="evenodd" stroke="{CUT}" stroke-width="0.5"/>')
            if lab.startswith('D3'):
                out.append(txt(ox + 11, oy - 160 + 6.5, 'RUMO', 19.5, 800) + f'<circle cx="{ox + 11 + 35.5:.2f}" cy="{oy - 160 - 11.7:.2f}" r="2.5" fill="{GREEN}"/>')
            elif lab[:2] in ('D4', 'D5', 'D6', 'D7'):
                for rr_ in range(10):
                    if rr_ % 2 == 0: out.append(box(ox + lx - 15, oy - ly + 35 - (rr_ + 1) * 7, 30, 7, DARK))
                out.append(f'<rect x="{ox+lx-15:.2f}" y="{oy-ly-35:.2f}" width="30" height="70" fill="none" stroke="{CUT}" stroke-width="0.5"/>')
            if lab.startswith('D3'): out.append(label(ox + lx, oy - ly + 30, lab, 5.5, INK, 600)); continue
            out.append(label(ox + lx, oy - ly + (14 if lab[:2] in ('D4', 'D5', 'D6', 'D7') else 2) + (0 if lab[:2] not in ('D4','D5','D6','D7') else 31), lab.split(' ')[0] if lab[:2] in ('D4','D5','D6','D7') else lab, 5.5, INK, 600))
        # 리본 꼭지 장식
        if i == 1:
            out.append(clover(ox - 75 + 113, oy - 190, 6))
            out.append(f'<circle cx="{ox+35+113:.2f}" cy="{oy-150:.2f}" r="9" fill="none" stroke="{BLUE}" stroke-width="5"/>'.replace(f'cx="{ox+35+113:.2f}"', f'cx="{min(ox+35+111, ox+120):.2f}"'))
        if i == 2:
            out.append(f'<path d="M{ox+92:.2f} {oy-40-113:.2f} h16 v-8 a8 8 0 0 0 -16 0 z" fill="#DFE2E7" stroke="{CUT}" stroke-width="0.4"/>')
        out.append(txt(ox - 132, oy - ch - 5, names[i], 8, 700, INK, 'start') + txt(ox + 132, oy - ch - 5, '폼보드 5T · 264 × 217', 5.5, 500, MUTE, 'end'))
    # 트레이 (가운데 대문 인쇄)
    tx = X0 + 2 * (cw + gap) + 132 + 10; ty = Y0 + 16 + 260
    paths, labs, folds = tray(lambda: Sh(tx, ty))
    out.append(f'<path d="{" ".join(p.path() for p in paths)}" fill="{KIT}" fill-rule="evenodd" stroke="{CUT}" stroke-width="0.5"/>')
    # 대문 아치 둘레 글자 + 바닥 체크 띠
    tt = 'WELCOME · HOME · RUMO'; a0, a1 = -PI * .86, -PI * .14; cxg, cyg, rg = tx, ty - 130, 60
    for k, chh in enumerate(tt):
        aa = a0 + (a1 - a0) * k / (len(tt) - 1)
        x, y = cxg + math.cos(aa) * rg, cyg + math.sin(aa) * rg
        out.append(f'<text x="0" y="0" transform="translate({x:.2f},{y:.2f}) rotate({math.degrees(aa + PI / 2):.1f})" font-family="{FONT}" font-size="10" font-weight="700" fill="{DARK}" text-anchor="middle" dominant-baseline="middle">{chh}</text>')
    for k in range(13):
        out.append(box(tx - 66 + k * 10.17, ty - 8, 10.3, 8, '#FFFFFF' if k % 2 else (GREEN if k == 4 else (BLUE if k == 8 else GRAY))))
    for x1, y1, x2, y2 in folds: out.append(fold(tx + x1, ty - y1, tx + x2, ty - y2))
    for x, y, t in labs: out.append(label(tx + x, ty - y + 2, t, 5.5, MUTE, 600))
    out.append(txt(tx - 132, Y0 + 11, '동네 트레이', 8, 700, INK, 'start') + txt(tx + 132, Y0 + 11, '폼보드 5T · 병풍 3폭 + 바닥판', 5.5, 500, MUTE, 'end'))
    # 받침 블록 (위에서 본 모습) + 굿즈
    by = ty + 110
    px, py = tx - 132 + 73, by + 76
    out.append(f'<rect x="{px-73:.2f}" y="{py-76:.2f}" width="146" height="152" fill="#FFFFFF" stroke="{CUT}" stroke-width="0.5"/>')
    for x, z, w_, d_ in [(-32, -58, 34, 42), (32, -58, 34, 42), (-32, 55, 34, 40), (32, 55, 34, 40)]:
        out.append(f'<rect x="{px+x-w_/2:.2f}" y="{py-z-d_/2:.2f}" width="{w_}" height="{d_}" fill="#F3F4F6" stroke="{CUT}" stroke-width="0.4"/>')
    out.append(txt(px, py + 4, 'RUMO', 9, 800, '#4A4F57'))
    out.append(txt(px - 73, by - 5, '받침 블록', 8, 700, INK, 'start') + txt(px + 73, by - 5, '146 × 152 × 20 · 네 발 홈', 5.5, 500, MUTE, 'end'))
    gx = tx + 40; gy = by + 20
    out.append(clover(gx, gy, 9.5) + clover(gx + 40, gy, 9.5) + label(gx + 20, gy + 26, '네잎 코스터 ×2', 5.5, INK, 600))
    out.append(f'<rect x="{gx-8:.2f}" y="{gy+46:.2f}" width="56" height="12" rx="6" fill="{BLUE}"/>' + label(gx + 20, gy + 72, '뼈 네임태그', 5.5, INK, 600))
    out.append(f'<rect x="{gx+60:.2f}" y="{gy-10:.2f}" width="22" height="50" rx="4" fill="#F1F2F4" stroke="{MUTE}" stroke-width="0.4"/>' + label(gx + 71, gy + 52, '리모컨', 5.5, INK, 600))
    return out

def main():
    pad = 30; WD = 1040
    secs = []
    y = pad
    secs.append(txt(pad, y + 10, 'RUMO 올인원 패키지 v8 — 인쇄 전개도 · 조립 부품', 16, 800, INK, 'start'))
    secs.append(txt(pad, y + 22, '바깥면(인쇄면) · 안쪽면 · 조립 키트를 한 장에. 판지 3T / 폼보드 5T, 단위 mm. 탭·풀칠면은 v8 모형처럼 생략 — 인쇄 전에 탭 추가 필요.', 6.5, 500, MUTE, 'start'))
    y += 48
    secs.append(txt(pad, y, '① 하우스 박스 — 바깥면 (인쇄면에서 본 모습)', 10, 700, INK, 'start')); y += 10
    OY = y + H + S + FIN; secs += box_sheet(pad + 490 + 5, OY, True); y = OY + D + 26
    secs.append(txt(pad, y, '② 하우스 박스 — 안쪽면 (문 안쪽 인쇄 · 바닥 매트)', 10, 700, INK, 'start')); y += 10
    OY = y + H + S + FIN; secs += box_sheet(pad + 490 + 5, OY, False); y = OY + D + 26
    secs.append(txt(pad, y, '③ 조립 키트 — 런너 A~D · 동네 트레이 · 받침 블록 · 굿즈', 10, 700, INK, 'start')); y += 8
    secs += kit_sheet(pad, y); y += 16 * 2 + 217 * 2 + 26 + 24 + 130
    ly = y + 6
    secs.append(f'<line x1="{pad}" y1="{ly}" x2="{pad+18}" y2="{ly}" stroke="{CUT}" stroke-width="0.8"/>' + label(pad + 22, ly + 2.2, '칼선', 6.5, INK, 500, 'start'))
    secs.append(f'<line x1="{pad+60}" y1="{ly}" x2="{pad+78}" y2="{ly}" stroke="{FOLD}" stroke-width="0.8" stroke-dasharray="4 2"/>' + label(pad + 82, ly + 2.2, '접는 선', 6.5, INK, 500, 'start'))
    HD = ly + 20
    svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{WD}mm" height="{HD:.0f}mm" viewBox="0 0 {WD} {HD:.2f}">\n'
           f'<rect width="{WD}" height="{HD:.2f}" fill="#FFFFFF"/>\n' + '\n'.join(secs) + '\n</svg>\n')
    out = os.path.join(os.environ.get('PRINT_OUT', os.getcwd()), 'rumo-v8-print-dieline.svg')
    open(out, 'w', encoding='utf-8').write(svg); print(out, f'{WD}x{HD:.0f}mm')
main()
