"""RUMO 올인원 패키지 v8 — 전개도 SVG (mm, Illustrator에서 바로 열림, 공개 폴더에 안 올림) + 조립 세트 한눈에 보기 SVG (docs/package).
Geometry mirrors the v8 3D model (탭·슬릿·풀칠면은 v8처럼 생략). Run: python3 tools/sync/dieline.py"""
import math, os
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(REPO, 'docs', 'package')
W, D, H, R, FIN = 270, 220, 220, 78, 70
S = math.hypot(135, 78)
CUT, FOLD, INK, MUTE = '#EC008C', '#00A0E9', '#111111', '#8A8F98'
PI = math.pi

class Sh:
    """Tiny THREE.Shape → SVG path (y-up input, flipped on output)."""
    def __init__(s, ox=0, oy=0, flip=True): s.d = []; s.cur = None; s.st = None; s.ox, s.oy, s.fl = ox, oy, flip
    def P(s, x, y): return f'{s.ox + x:.2f} {(-y if s.fl else y) + s.oy:.2f}'
    def M(s, x, y): s.d.append('M' + s.P(x, y)); s.cur = s.st = (x, y); return s
    def L(s, x, y): s.d.append('L' + s.P(x, y)); s.cur = (x, y); return s
    def Q(s, cx, cy, x, y): s.d.append('Q' + s.P(cx, cy) + ' ' + s.P(x, y)); s.cur = (x, y); return s
    def A(s, cx, cy, r, a0, a1, cw=False):
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        if s.cur is None: s.M(x0, y0)
        elif abs(s.cur[0] - x0) > 1e-6 or abs(s.cur[1] - y0) > 1e-6: s.L(x0, y0)
        raw = (a1 - a0) if not cw else (a0 - a1)
        if abs(abs(raw) - 2 * PI) < 1e-9: da = 2 * PI
        else:
            da = raw
            while da < 0: da += 2 * PI
        sweep = 1 if cw else 0
        if not s.fl: sweep = 1 - sweep
        segs = 2 if da > PI + 1e-9 else 1
        for k in range(1, segs + 1):
            a = a0 + (da * k / segs) * (1 if not cw else -1)
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            s.d.append(f'A{r:.2f} {r:.2f} 0 0 {sweep} ' + s.P(x, y)); s.cur = (x, y)
        return s
    def Z(s): s.d.append('Z'); s.cur = s.st; return s
    def path(s): return ' '.join(s.d)

def rect(sh, x1, y1, x2, y2): return sh.M(x1, y1).L(x2, y1).L(x2, y2).L(x1, y2).Z()
def cut(d, w=0.35): return f'<path d="{d}" fill="none" stroke="{CUT}" stroke-width="{w}" stroke-linejoin="round"/>'
def fold(x1, y1, x2, y2): return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{FOLD}" stroke-width="0.35" stroke-dasharray="4 2"/>'
def label(x, y, t, size=7, c=INK, w=600, anchor='middle'):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{t}</text>'

def arch(sh, cx, yb, w, h):
    r = w / 2; sh.M(cx - r, yb).L(cx + r, yb).L(cx + r, yb + h - r); sh.A(cx, yb + h - r, r, 0, PI, False); sh.L(cx - r, yb); return sh
def slot(sh, cx, cy, w, h):
    r = h / 2; sh.M(cx - w / 2 + r, cy - r).L(cx + w / 2 - r, cy - r); sh.A(cx + w / 2 - r, cy, r, -PI / 2, PI / 2, False)
    sh.L(cx - w / 2 + r, cy + r); sh.A(cx - w / 2 + r, cy, r, PI / 2, PI * 1.5, False); sh.Z(); return sh

# ───────── 1) 하우스 박스 전개도
def box_svg():
    pad = 30; top = H + S + FIN; left = 135 + D + 135
    ox, oy = left + pad, top + pad + 18          # world (y-up) → svg
    Wd, Hd = 2 * left + 2 * pad, top + D + 2 * pad + 18 + 60
    g_cut, g_fold, g_lab = [], [], []
    def sx(x): return ox + x
    def sy(y): return oy - y
    # 외곽 칼선 (한 장): 바닥 아래 → 오른쪽 날개 → 꼭대기 → 왼쪽 날개
    o = Sh(ox, oy)
    o.M(-135, -D).L(135, -D).L(135, 0)
    o.L(135 + D, 0).L(135 + D + 135, 0).L(135 + D + 135, H + R).L(135 + D, H)       # 오른쪽: 측벽 바닥 → 오른문
    o.L(135 + D, H + S + FIN).L(135, H + S + FIN).L(135, H)                          # 지붕 + 핀 (오른쪽)
    o.L(0, H + R).L(-135, H)                                                         # 뒷벽 박공
    o.L(-135, H + S + FIN).L(-135 - D, H + S + FIN).L(-135 - D, H)                   # 지붕 + 핀 (왼쪽)
    o.L(-135 - D - 135, H + R).L(-135 - D - 135, 0).L(-135 - D, 0).L(-135, 0).Z()    # 왼문 → 측벽 바닥
    g_cut.append(cut(o.path(), 0.5))
    # 핀 슬롯 (손잡이 구멍)
    for c in (-135 - D / 2, 135 + D / 2):
        g_cut.append(cut(slot(Sh(ox, oy), c, H + S + 37, 100, 24).path()))
    # 왼문 아치 창: 오른쪽 세로변은 접는 선(덧창 경첩)
    cx = -135 - D - 67.5
    a = Sh(ox, oy); r = 28; a.M(cx + r, 95).L(cx - r, 95).L(cx - r, 95 + 72 - r); a.A(cx, 95 + 72 - r, r, PI, 0, True)
    g_cut.append(cut(a.path())); g_fold.append(fold(sx(cx + r), sy(95), sx(cx + r), sy(95 + 72 - r)))
    # 접는 선
    for x1, y1, x2, y2 in [(-135, 0, 135, 0), (-135, 0, -135, H), (135, 0, 135, H), (-135 - D, H, -135, H), (135, H, 135 + D, H),
                           (-135 - D, H + S, -135, H + S), (135, H + S, 135 + D, H + S), (-135 - D, 0, -135 - D, H), (135 + D, 0, 135 + D, H)]:
        g_fold.append(fold(sx(x1), sy(y1), sx(x2), sy(y2)))
    # 이름
    for x, y, t in [(0, H / 2, '뒷벽'), (0, -D / 2, '바닥'), (-135 - D / 2, H / 2, '측벽 1'), (135 + D / 2, H / 2, '측벽 2'),
                    (-135 - D / 2, H + S / 2, '지붕 1'), (135 + D / 2, H + S / 2, '지붕 2'), (-135 - D / 2, H + S + 12, '손잡이 핀 1'),
                    (135 + D / 2, H + S + 12, '손잡이 핀 2'), (-135 - D - 67.5, 40, '왼문 (아치 창)'), (135 + D + 67.5, 40, '오른문')]:
        g_lab.append(label(sx(x), sy(y), t, 8))
    for x, y, t in [(0, -D - 8, '270'), (-135 - D / 2, -8, '220'), (-135 - D - 67.5, -8, '135')]:
        g_lab.append(label(sx(x), sy(y) + 6, t + ' mm', 6, MUTE, 500))
    g_lab.append(label(pad, 22, 'RUMO 올인원 패키지 v8 — 하우스 박스 전개도', 11, INK, 700, 'start'))
    g_lab.append(label(pad, 34, f'판지 3T · 펼친 크기 {2*left:.0f} × {top + D:.0f} mm · 접으면 270 × 220 × 220 (지붕 끝 298) · 탭·풀칠면은 v8 모형처럼 생략', 6.5, MUTE, 500, 'start'))
    ly = Hd - 22
    g_lab.append(f'<line x1="{pad}" y1="{ly}" x2="{pad+18}" y2="{ly}" stroke="{CUT}" stroke-width="0.6"/>' + label(pad + 22, ly + 2.2, '칼선 (자르기)', 6.5, INK, 500, 'start'))
    g_lab.append(f'<line x1="{pad+90}" y1="{ly}" x2="{pad+108}" y2="{ly}" stroke="{FOLD}" stroke-width="0.6" stroke-dasharray="4 2"/>' + label(pad + 112, ly + 2.2, '접는 선', 6.5, INK, 500, 'start'))
    return Wd, Hd, g_cut, g_fold, g_lab

# ───────── 2) 조립 세트 한눈에 (런너 A~D + 동네 트레이)
KT = 5
def runner_parts(i):
    """parts on runner i in runner coords (x -132..132, y 0..217, y-up). returns list of (Sh-callable, label, labelpos)."""
    out = []
    def R_(cx, cy, w, h, lab):
        out.append((lambda sh, cx=cx, cy=cy, w=w, h=h: rect(sh, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), lab, (cx, cy)))
    if i == 0:
        def archp(sh, dx=10, dy=8.5):
            sh.M(-132 + dx, dy).L(-102 + dx, dy).L(-102 + dx, 115 + dy); sh.A(-27 + dx, 115 + dy, 75, PI, 0, True)
            sh.L(48 + dx, dy).L(78 + dx, dy).L(78 + dx, 200 + dy).L(-132 + dx, 200 + dy).Z(); return sh
        out.append((archp, 'A1 아치 패널', (-27 + 10, 200)))
    if i == 1:
        out.append((lambda sh: ribbon(sh, -75, 190, True, 9), 'B1 물결 리본 · 네잎', (-20, 176)))
        out.append((lambda sh: ribbon(sh, 35, 150, True, 7), 'B2 물결 리본 · 동그라미', (85, 136)))
    if i == 2:
        R_(-23.5, 108.5, 197, 200, 'C1 칸막이')
        out.append((lambda sh: ribbon(sh, 100, 40, False, 8), 'C2 리본 · 아치', (100, 20)))
    if i == 3:
        R_(-102, 108.5, 40, 197, 'D1 선반'); R_(-58, 108.5, 40, 197, 'D2 선반'); R_(11, 160, 90, 40, 'D3 문패 RUMO')
        for k, x in enumerate([-19, 13, 45, 77]): R_(x, 45, 30, 70, f'D{4+k}')
        R_(107, 45, 40, 40, 'D8 캡')
    return out

def ribbon(sh, x0, y0, horiz, amp):
    L_, w = 95, 4
    pts = [(amp * math.sin((L_ * i / 40) / L_ * PI * 2.2), L_ * i / 40) for i in range(41)]
    def T(px, py): return (x0 + py, y0 - px) if horiz else (x0 + px, y0 + py)
    first = True
    for px, py in pts + [(px, py) for px, py in reversed(pts)]:
        pass
    seq = [(px - w, py) for px, py in pts] + [(px + w, py) for px, py in reversed(pts)]
    for k, (px, py) in enumerate(seq):
        x, y = T(px, py); (sh.M if k == 0 else sh.L)(x, y)
    sh.Z(); return sh

GATES = [[(-122, 90), (0, 10), (100, 172)], [(-122, 90), (0, 10), (122, 90)], [(-122, 91), (-23, 10), (75, 207)],
         [(-102, 10), (-58, 207), (-34, 140), (-34, 110), (-19, 10), (13, 10), (45, 10), (77, 10), (122, 45)]]

def tray(sh_factory):
    """동네 트레이: 가운데 대문 + 왼쪽(계단 박공) + 오른쪽(종 지붕) 한 장 · 바닥판."""
    paths, labs, folds = [], [], []
    s = sh_factory(); s.M(-66, 0).L(66, 0).L(66, 196).L(0, 236).L(-66, 196).Z(); paths.append(s)   # 가운데
    g = sh_factory(); g.M(46, 10).L(46, 130); g.A(0, 130, 46, 0, PI, False); g.L(-46, 10).L(46, 10); paths.append(g)
    c = sh_factory(); c.A(0, 206, 9, 0, 2 * PI, True); paths.append(c)
    l = sh_factory(); l.M(-132, 0).L(-66, 0).L(-66, 182)
    for x, y in [(-74, 182), (-74, 192), (-84, 192), (-84, 203), (-94, 203), (-94, 213), (-104, 213), (-104, 203), (-114, 203), (-114, 192), (-124, 192), (-124, 182), (-132, 182)]: l.L(x, y)
    l.Z(); paths.append(l)
    for y in (150, 102): h = sh_factory(); h.A(-98, y, 20, 0, 2 * PI, True); paths.append(h)
    v = sh_factory(); cx, cy, w_, h_ = -98, 45, 22, 56; r = w_ / 2
    v.M(cx + r, cy - h_ / 2 + r).L(cx + r, cy + h_ / 2 - r); v.A(cx, cy + h_ / 2 - r, r, 0, PI, False); v.L(cx - r, cy - h_ / 2 + r); v.A(cx, cy - h_ / 2 + r, r, PI, 2 * PI, False); paths.append(v)
    rr_ = sh_factory(); rr_.M(66, 0).L(132, 0).L(132, 178).Q(132, 196, 116, 198).Q(99, 216, 82, 198).Q(66, 196, 66, 178).Z(); paths.append(rr_)
    def rrect(x1, y1, x2, y2, r):
        q = sh_factory(); q.M(x1 + r, y1).L(x2 - r, y1); q.A(x2 - r, y1 + r, r, -PI / 2, 0); q.L(x2, y2 - r); q.A(x2 - r, y2 - r, r, 0, PI / 2); q.L(x1 + r, y2)
        q.A(x1 + r, y2 - r, r, PI / 2, PI); q.L(x1, y1 + r); q.A(x1 + r, y1 + r, r, PI, PI * 1.5); paths.append(q)
    rrect(71, 40, 125, 154, 8); rrect(78, 162, 90, 174, 2); rrect(108, 162, 120, 174, 2)
    b = sh_factory(); rect(b, -66, -70, 66, 0); paths.append(b)
    rrect(-27, -34, 27, -10, 8)                     # 리모컨 홈 52 × 24
    folds += [(-66, 0, -66, 182), (66, 0, 66, 178), (-66, 0, 66, 0)]
    labs += [(0, 60, '대문 · 루모 창'), (-99, 125, '코스터'), (-99, 82, '네임태그'), (99, 100, '리모컨'), (0, -52, '바닥판 · 리모컨 홈')]
    return paths, labs, folds

def kit_svg():
    pad, gap, cw, ch = 24, 26, 264, 217
    cols = [(0, 0), (1, 0), (0, 1), (1, 1)]
    Wd = pad * 2 + cw * 3 + gap * 2; Hd = pad * 2 + 40 + ch * 2 + gap + 40
    body = []
    names = ['런너 A', '런너 B', '런너 C', '런너 D']
    for i, (c, r) in enumerate(cols):
        ox = pad + c * (cw + gap) + 132; oy = pad + 40 + r * (ch + gap) + ch   # runner origin (bottom-center)
        f = Sh(ox, oy); rect(f, -132, 0, 132, 217); body.append(f'<path d="{f.path()}" fill="#F3F4F6" stroke="{INK}" stroke-width="0.5"/>')
        h = Sh(ox, oy); rect(h, -124, 8, 124, 209); body.append(f'<path d="{h.path()}" fill="#FFFFFF" stroke="{MUTE}" stroke-width="0.35"/>')
        for x, y in GATES[i]: body.append(f'<rect x="{ox + x - 2:.2f}" y="{oy - y - 2:.2f}" width="4" height="4" fill="#D5D9DF"/>')
        for fn, lab, (lx, ly) in runner_parts(i):
            sh = fn(Sh(ox, oy)); body.append(f'<path d="{sh.path()}" fill="#FFFFFF" fill-rule="evenodd" stroke="{CUT}" stroke-width="0.6"/>')
            body.append(label(ox + lx, oy - ly + 2, lab, 6.5, INK, 600))
        body.append(label(ox - 132, oy - ch - 6, names[i], 9, INK, 700, 'start'))
        body.append(label(ox + 132, oy - ch - 6, '5T 폼보드 · 264 × 217', 6, MUTE, 500, 'end'))
    # 트레이 (오른쪽 세로 칸)
    tx = pad + 2 * (cw + gap) + 132; ty = pad + 40 + ch + 100
    paths, labs, folds = tray(lambda: Sh(tx, ty))
    d = ' '.join(p.path() for p in paths)
    body.append(f'<path d="{d}" fill="#FFFFFF" fill-rule="evenodd" stroke="{CUT}" stroke-width="0.6"/>')
    for x1, y1, x2, y2 in folds: body.append(fold(tx + x1, ty - y1, tx + x2, ty - y2))
    for x, y, t in labs: body.append(label(tx + x, ty - y + 2, t, 6, INK, 600))
    body.append(label(tx - 132, pad + 40 - 6 + 0, '동네 트레이', 9, INK, 700, 'start'))
    body.append(label(tx + 132, pad + 40 - 6, '3폭 + 바닥판 · 펴면 리모컨 받침대', 6, MUTE, 500, 'end'))
    # 굿즈 (트레이 아래)
    gy = ty + 70 + 40
    def clover(cx, cy, r):
        return ''.join(f'<circle cx="{cx + a * r * .9:.2f}" cy="{cy + b * r * .9:.2f}" r="{r}" fill="#A8D14B"/>' for a, b in [(-1, 0), (1, 0), (0, -1), (0, 1)])
    body.append(clover(tx - 100, gy, 9.5) + clover(tx - 60, gy, 9.5) + label(tx - 80, gy + 30, '네잎 코스터 ×2', 6, INK, 600))
    body.append(f'<rect x="{tx - 28}" y="{gy - 6}" width="56" height="12" rx="6" fill="#8EA8EA"/>' + label(tx, gy + 30, '뼈 네임태그', 6, INK, 600))
    body.append(f'<rect x="{tx + 52}" y="{gy - 24}" width="22" height="50" rx="4" fill="#F1F2F4" stroke="{MUTE}" stroke-width="0.4"/>' + label(tx + 63, gy + 38, '리모컨', 6, INK, 600))
    head = [label(pad, pad + 6, 'RUMO 올인원 패키지 v8 — 조립 세트 한눈에', 12, INK, 700, 'start'),
            label(pad, pad + 20, '런너 4장(A~D)에서 13개 부품을 떼어 루모의 집을 만들어요. 빈 런너 틀 4장은 받침대가 돼요. 회색 점은 게이트(연결점).', 6.5, MUTE, 500, 'start')]
    ly = Hd - pad + 4
    leg = [f'<line x1="{pad}" y1="{ly}" x2="{pad+18}" y2="{ly}" stroke="{CUT}" stroke-width="0.8"/>', label(pad + 22, ly + 2.2, '부품 칼선', 6.5, INK, 500, 'start'),
           f'<line x1="{pad+80}" y1="{ly}" x2="{pad+98}" y2="{ly}" stroke="{FOLD}" stroke-width="0.8" stroke-dasharray="4 2"/>', label(pad + 102, ly + 2.2, '접는 선', 6.5, INK, 500, 'start')]
    return Wd, Hd, head + body + leg

def write(name, Wd, Hd, groups, out=None):
    svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{Wd:.0f}mm" height="{Hd:.0f}mm" viewBox="0 0 {Wd:.2f} {Hd:.2f}">\n'
           + ''.join(f'<g id="{gid}">{"".join(items)}</g>\n' for gid, items in groups) + '</svg>\n')
    path = os.path.join(out or OUT, name); open(path, 'w', encoding='utf-8').write(svg); print(path, f'{Wd:.0f}x{Hd:.0f}mm')

if __name__ == '__main__':
    Wd, Hd, c, f, l = box_svg()
    # 전개도는 공개 사이트에 올리지 않아요 — 실행한 폴더(또는 DIELINE_OUT)에 저장
    write('rumo-v8-dieline-box.svg', Wd, Hd, [('cut', c), ('fold', f), ('labels', l)], os.environ.get('DIELINE_OUT', os.getcwd()))
    Wd, Hd, items = kit_svg()
    write('rumo-v8-kit-overview.svg', Wd, Hd, [('kit', items)])
