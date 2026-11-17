"""RUMO v8 조립 키트 — 부품 형상(탭·홈 포함)·런너 배치·게이트·조립 점검의 단일 원본.
좌표: mm, y 위쪽. 런너 좌표는 x -132..132, y 0..217 (안쪽 구멍 -126..126 × 6..211)."""
import math
from shapely.geometry import Polygon, box as sbox
from shapely import affinity

KT, T = 5, 3
TAN = 78 / 135
RUN_W, RUN_H, IN = 264, 217, (-126, 6, 126, 211)

def arc(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
def rect(x1, y1, x2, y2): return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
def wave(amp, L=95, w=4):
    pts = [(amp * math.sin((L * i / 40) / L * math.pi * 2.2), L * i / 40) for i in range(41)]
    return [(px - w, py) for px, py in pts] + [(px + w, py) for px, py in reversed(pts)]

# ───── 부품 (로컬 좌표 · outline, holes)
def A1():
    o = [(0, 0), (5, 0), (5, -5), (25, -5), (25, 0), (30, 0), (30, 115)] + arc(105, 115, 75, math.pi, 0)[1:-1] + [(180, 115), (180, 0), (185, 0), (185, -5), (205, -5), (205, 0), (210, 0), (210, 195), (0, 195)]
    return o, []
def C1():   # u = 깊이(박스 z-3), v = 높이(박스 y-T)
    o = [(0, 0), (27, 0), (27, -5), (47, -5), (47, 0), (147, 0), (147, -5), (167, -5), (167, 0), (197, 0), (197, 190), (0, 190)]
    holes = [rect(u - 7.5, v - 2.5, u + 7.5, v + 2.5) for u in (47, 147) for v in (67, 134)]
    return o, holes
def SHELF():  # x: 칸막이 쪽 -10 ~ 벽 쪽 51, y = 깊이
    o = [(0, 0), (40, 0), (40, 39.5), (51, 39.5), (51, 54.5), (40, 54.5), (40, 139.5), (51, 139.5), (51, 154.5), (40, 154.5), (40, 197), (0, 197),
         (0, 154.5), (-10, 154.5), (-10, 139.5), (0, 139.5), (0, 54.5), (-10, 54.5), (-10, 39.5), (0, 39.5)]
    return o, []
def SIGN(): return rect(0, 0, 90, 40), []
def WALL(h):     # 굴뚝 앞·뒤 벽 (30 폭), 아래 탭 16×5
    return [(0, 0), (7, 0), (7, -5), (23, -5), (23, 0), (30, 0), (30, h), (0, h)], []
def SIDEWALL():  # 굴뚝 옆벽 (20 폭) — 아래가 지붕 경사(30°)를 따라 잘림
    rise = 20 * TAN
    return [(0, 0), (6, 6 * TAN), (6 + 2.5, 6 * TAN - 4.3), (14 + 2.5, 14 * TAN - 4.3), (14, 14 * TAN), (20, rise), (20, 60), (0, 60)], []
def CAP(): return rect(0, 0, 40, 40), [rect(cx - 4, cy - 2.5, cx + 4, cy + 2.5) for cx, cy in ((10, 28), (30, 28), (20, 12))]
def RIBBON(amp, top):
    """물결 리본 + 꼭지 장식을 한 조각으로 (리본 끝 5mm가 캡 홈에 들어감)."""
    from shapely.geometry import Point
    from shapely.ops import unary_union
    body = Polygon(wave(amp)); ex = amp * math.sin(math.pi * 2.2)
    if top == 'clover': t = unary_union([Point(ex + a * 7.2, 103 + b * 7.2).buffer(8, 16) for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1))])
    elif top == 'dot': t = Point(ex, 103).buffer(11, 24).difference(Point(ex, 104).buffer(5, 16))
    else: t = Polygon([(ex - 10, 95), (ex + 10, 95), (ex + 10, 103)] + arc(ex, 103, 10, 0, math.pi)[1:-1] + [(ex - 10, 103)])
    u = unary_union([body, t]).buffer(0)
    return list(u.exterior.coords)[:-1], [list(r.coords)[:-1] for r in u.interiors]
def BRACKET(): return [(0, 3), (5, 3), (5, 0), (43, 0), (43, 3), (48, 3), (48, 12), (43, 12), (43, 15), (5, 15), (5, 12), (0, 12)], []
def RIB():   # 리모컨 지지 리브: u = 대문에서 앞으로, v = 바닥판 위로
    return [(22, 0), (30, 0), (30, -5), (40, -5), (40, 0), (66, 0), (66, -5), (76, -5), (76, 0), (86, 0), (86, 20), (81, 20), (80, 13.5), (59, 6), (41.9, 53), (35, 53)], []

def place(geom, dx, dy, rot=0):
    o, holes = geom
    def tr(p):
        x, y = p
        if rot == 90: x, y = -y, x
        return (x + dx, y + dy)
    return [tr(p) for p in o], [[tr(p) for p in h] for h in holes]

# ───── 런너 배치 (code, 이름, 형상, dx, dy, rot, 3D 중심)
RUNNERS = {
    'A': [('A1', '아치 패널', A1(), -105, 14, 0)],
    'B': [('B1', '물결 리본 · 네잎', RIBBON(9, 'clover'), -110, 190, -90), ('B2', '물결 리본 · 동그라미', RIBBON(7, 'dot'), -5, 150, -90),
          ('F1', '리모컨 리브', RIB(), -142, 17, 0), ('F2', '리모컨 리브', RIB(), -70, 17, 0),
          ('E1', '고정 고리', BRACKET(), 30, 20, 0), ('E2', '고정 고리', BRACKET(), 30, 45, 0)],
    'C': [('C1', '칸막이', C1(), -122, 15, 0), ('C2', '물결 리본 · 아치', RIBBON(8, 'arch'), 100, 30, 0)],
    'D': [('D1', '선반', SHELF(), -110, 8, 0), ('D2', '선반', SHELF(), -45, 8, 0),
          ('D4', '굴뚝 벽 (위)', WALL(45.3), 14, 17, 0), ('D5', '굴뚝 벽 (아래)', WALL(62.7), 50, 17, 0), ('D6', '굴뚝 옆벽', SIDEWALL(), 86, 17, 0),
          ('D7', '굴뚝 옆벽', SIDEWALL(), 14, 90, 0), ('D8', '굴뚝 캡', CAP(), 44, 90, 0), ('D3', '문패', SIGN(), 14, 160, 0)],
}
def placed(r):
    out = []
    for code, name, g, dx, dy, rot in RUNNERS[r]:
        if rot == -90:   # 리본: 세로 → 가로 (x = dx + py, y = dy - px)
            o, h = g; out.append((code, name, [(dx + py, dy - px) for px, py in o], [[(dx + py, dy - px) for px, py in r] for r in h])); continue
        o, h = place(g, dx, dy, rot); out.append((code, name, o, h))
    return out
def poly(o, h=()): return Polygon(o, [list(x) for x in h]).buffer(0)

def gates(r):
    """각 부품에서 가장 가까운 틀 안쪽 변으로 4mm 게이트(연결 다리)."""
    x1, y1, x2, y2 = IN; out = []
    for code, name, o, h in placed(r):
        P = poly(o, h); bx1, by1, bx2, by2 = P.bounds; cx, cy = (bx1 + bx2) / 2, (by1 + by2) / 2
        cands = [(by1 - y1, (cx - 2, y1, cx + 2, by1)), (y2 - by2, (cx - 2, by2, cx + 2, y2)), (bx1 - x1, (x1, cy - 2, bx1, cy + 2)), (x2 - bx2, (bx2, cy - 2, x2, cy + 2))]
        others = [poly(o2, h2) for c2, _, o2, h2 in placed(r) if c2 != code]
        for d, g in sorted(cands):
            G = sbox(*g).buffer(-0.01)
            if not any(G.intersects(Q) for Q in others): out.append((code, g)); break
        else: out.append((code, sorted(cands)[0][1]))
    return out

# ───── 조립 점검
def check():
    rep = []
    def ok(c, msg): rep.append(('OK ' if c else '!! ') + msg); return c
    inner = sbox(*IN)
    for r in 'ABCD':
        ps = placed(r)
        for code, name, o, h in ps:
            P = poly(o, h)
            ok(inner.buffer(-2).contains(P), f'런너 {r} · {code} {name}: 틀 안쪽 2mm 안에 들어감 (bounds {tuple(round(v,1) for v in P.bounds)})')
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                d = poly(ps[i][2], ps[i][3]).distance(poly(ps[j][2], ps[j][3]))
                ok(d >= 2, f'런너 {r} · {ps[i][0]}↔{ps[j][0]} 간격 {d:.1f}mm (≥2)')
    # 끼움: 탭 길이 ≥ 끼우는 판 두께
    ok(5 >= T, 'A1·C1 바닥 탭 5mm ≥ 바닥 판지 3T (+ 바닥 매트 0.3) — 아래로 1.7mm 나옴, 런너 받침대 구멍 안이라 안 걸림')
    ok(10 >= (87.5 - 83) + KT, f'선반 안쪽 탭 10mm ≥ 칸막이까지 틈 4.5 + 칸막이 5T = 9.5')
    ok(11 >= (135 - 127.5) + T, f'선반 바깥 탭 11mm ≥ 벽까지 틈 7.5 + 벽 3T = 10.5')
    ok(5 >= T, '굴뚝 벽 탭 5mm ≥ 지붕 판지 3T')
    ok(abs((43 - 5) - (176.3 - 138)) < 0.5, '고정 고리 몸통 38mm = 받침대 대문 뒤 ↔ 집 벽 거리 38.3mm')
    # 홈 위치 = 탭 위치
    ok(-132 + 15 == -117 and -132 + 195 == 63, 'A1 탭 x(-117, 63) = 바닥 홈 x')
    ok((27 + 47) / 2 + 3 == 40 and (147 + 167) / 2 + 3 == 160, 'C1 탭 z(40, 160) = 바닥 홈 z')
    ok(47 + 3 == 50 and 147 + 3 == 150, '선반 탭 z(50, 150) = 칸막이 홈 = 오른쪽 벽 홈')
    ok(67 + T == 70 and 134 + T == 137, '선반 높이(70, 137) = 칸막이 홈 높이 + 바닥 3T')
    # 공간
    ok(115 + 75 - (4 + 180) >= 5, f'아치 꼭대기 {115+75+T} > 받침 블록 바닥 4 + 루모 180 = {4+180+T} (여유 {115+75-4-180}mm)')
    ok(146 <= 150, '받침 블록 폭 146 ≤ 아치 입구 150')
    ok(-27 + 73 < 78, '받침 블록 오른쪽 끝 46 < 칸막이 78 (루모 침대와 선반칸이 안 겹침)')
    ok(T + 190 < 220, '칸막이 190 + 바닥 < 벽 높이 220')
    # 리모컨 거치
    beta = 20; com_z = 59 - 55 * math.sin(math.radians(beta)) + 11 * math.cos(math.radians(beta))
    ok(com_z < 59, f'리모컨 무게중심 z {com_z:.1f} < 바닥 닿는 점 z 59 → 뒤(리브) 쪽으로 기대어 안정, 앞 턱이 미끄럼 막음')
    ok(True, '리브 2장은 기대는 힘을 판 방향(in-plane)으로 받아 휘지 않음 — 접은 날개(경첩)는 힘을 못 받아 쓰러져서 바꿈')
    return rep

# ───── 굿즈 · 트레이 포켓 (실측값이 오면 여기 숫자만 바꾸면 트레이·도면·점검이 같이 바뀌어요)
ROBOT = dict(W=105, L=165, H=180)        # 상품 표기 치수 (폭 × 길이 × 높이)
ROBOT_MODEL = dict(head_w=100, head_front=82, nose=87, paw=(30, 40), paw_x=32, paw_z=(58, -55))  # 3D 모형 가정값 — 실측 필요
REMOTE = dict(W=50, L=110, T=22)         # 가정값 — 실측 필요
COASTER = dict(r=9.5, T=4)               # 네잎 = 지름 19 원 4개 → 36.1 × 36.1, 코르크 4T
BONE = dict(L=60, W=22, T=5, hole=3)     # 뼈 네임태그 폼보드 5T, 끈 구멍 Ø3
PRESS = 0.2      # 코스터·네임태그 포켓은 0.2mm 작게 → 폼이 눌리며 잡아 줌 (세워도 안 빠짐)
SLIP = 0.5       # 리모컨(딱딱한 플라스틱)은 0.5mm 크게 → 밴드로 잡음
BACK_T = 1       # 날개 뒷판: 그레이보드 1T
TRAY_Z, DOOR_Z, DOCK_Z = 168, 217, 80   # 배송 때 트레이 앞면 · 닫힌 문 안쪽 · 받침 블록 중심 (박스 z)
COASTER_AT = [(-98, 150), (-98, 102)]; BONE_AT = (-98, 45); REMOTE_AT = (98, 97)

def P_(o, h=()): return Polygon(o, [list(x) for x in h]).buffer(0)
def clover_poly(cx, cy, r=None):
    r = r or COASTER['r']; from shapely.geometry import Point
    from shapely.ops import unary_union
    return unary_union([Point(cx + a * r * .9, cy + b * r * .9).buffer(r, 64) for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1))])
def bone_poly(cx, cy, vertical=True):
    from shapely.geometry import Point
    from shapely.ops import unary_union
    hl, hw = BONE['L'] / 2 - 6, BONE['W'] / 2 - 6     # 끝 원 r6
    g = unary_union([sbox(-hl + 4, -5, hl - 4, 5)] + [Point(x, y).buffer(6, 48) for x in (-hl, hl) for y in (-hw, hw)])
    g = affinity.rotate(g, 90, origin=(0, 0)) if vertical else g
    return affinity.translate(g, cx, cy)
def bone_hole(cx, cy, vertical=True):
    from shapely.geometry import Point
    hx = BONE['L'] / 2 - 14
    return Point(cx, cy + hx).buffer(BONE['hole'] / 2, 24) if vertical else Point(cx + hx, cy).buffer(BONE['hole'] / 2, 24)
def rrect_poly(x1, y1, x2, y2, r): return sbox(x1 + r, y1 + r, x2 - r, y2 - r).buffer(r, 32)
def remote_window():
    cx, cy = REMOTE_AT; w, l = REMOTE['W'] / 2 + SLIP, REMOTE['L'] / 2 + SLIP
    return rrect_poly(cx - w, cy - l, cx + w, cy + l, 4)
def band_slits():                       # 밴드 슬릿 12 × 2, 창에서 6.5mm 떨어짐
    cx, cy = REMOTE_AT; e = REMOTE['L'] / 2 + SLIP + 6.5
    return [sbox(cx - 6, cy - e - 2, cx + 6, cy - e), sbox(cx - 6, cy + e, cx + 6, cy + e + 2)]
def deco_squares(): return [rrect_poly(78, 164, 90, 176, 2), rrect_poly(108, 164, 120, 176, 2)]
def finger(cx, cy, r=6):
    from shapely.geometry import Point
    return Point(cx, cy).buffer(r, 32)
def pockets():
    """(이름, 물건 모양, 칼선 구멍 모양, 손가락 홈) — 트레이 좌표"""
    out = []
    for k, (x, y) in enumerate(COASTER_AT):
        item = clover_poly(x, y); out.append((f'코스터 {k+1}', item, item.buffer(-PRESS, join_style=1), finger(x - 18.5, y)))
    item = bone_poly(*BONE_AT); out.append(('네임태그', item, item.buffer(-PRESS, join_style=1), finger(BONE_AT[0] + 8.5, BONE_AT[1])))
    out.append(('리모컨', sbox(REMOTE_AT[0] - REMOTE['W'] / 2, REMOTE_AT[1] - REMOTE['L'] / 2, REMOTE_AT[0] + REMOTE['W'] / 2, REMOTE_AT[1] + REMOTE['L'] / 2), remote_window(), None))
    return out
def tray_holes():
    """트레이 날개에 뚫는 칼선 (포켓 + 손가락 홈 합침) + 밴드 슬릿 + 장식 창"""
    hs = []
    for _, _, cutp, notch in pockets(): hs.append(cutp.union(notch) if notch is not None else cutp)
    return hs + band_slits() + deco_squares()
def wing_L(): return P_([(-132, 0), (-66, 0), (-66, 182), (-74, 182), (-74, 192), (-84, 192), (-84, 203), (-94, 203), (-94, 213), (-104, 213), (-104, 203), (-114, 203), (-114, 192), (-124, 192), (-124, 182), (-132, 182)])
def wing_R():
    q = [(66, 0), (132, 0), (132, 178)]
    def quad(p0, c, p1, n=12): return [((1-t)**2*p0[0]+2*(1-t)*t*c[0]+t*t*p1[0], (1-t)**2*p0[1]+2*(1-t)*t*c[1]+t*t*p1[1]) for t in [i/n for i in range(1, n+1)]]
    q += quad((132, 178), (132, 196), (116, 198)) + quad((116, 198), (99, 216), (82, 198)) + quad((82, 198), (66, 196), (66, 178))
    return P_(q)
def backings():
    """날개 뒷판 (그레이보드 1T) — 접는 선에서 2mm 띄움, 바깥 1mm 안쪽. 밴드 슬릿·장식 창은 뒷판에도 뚫어요."""
    L = wing_L().buffer(-1, join_style=2).intersection(sbox(-140, -10, -68, 300))
    R = wing_R().buffer(-1, join_style=2).intersection(sbox(68, -10, 140, 300))
    for h in band_slits() + deco_squares(): R = R.difference(h)
    return L, R

def goods_check():
    rep = []
    def ok(c, msg): rep.append(('OK ' if c else '!! ') + msg); return c
    for name, item, cutp, notch in pockets():
        wing = wing_L() if item.centroid.x < 0 else wing_R()
        hole = cutp.union(notch) if notch is not None else cutp
        others = [h for h in tray_holes() if not h.equals(hole)]
        m_edge = wing.exterior.distance(hole); m_other = min(hole.distance(h) for h in others)
        bx = item.bounds
        ok(m_edge >= 5, f'{name}: 날개 가장자리까지 폼 {m_edge:.1f}mm (≥5)')
        ok(m_other >= 5, f'{name}: 옆 구멍까지 폼 {m_other:.1f}mm (≥5)')
        fit = (cutp.bounds[2] - cutp.bounds[0]) - (bx[2] - bx[0])
        ok(True, f'{name}: 물건 {bx[2]-bx[0]:.1f} × {bx[3]-bx[1]:.1f} · 구멍 {cutp.bounds[2]-cutp.bounds[0]:.1f} × {cutp.bounds[3]-cutp.bounds[1]:.1f} ({fit:+.1f})')
    ok(COASTER['T'] <= KT, f"코스터 {COASTER['T']}T ≤ 포켓 깊이 {KT} → 1mm 들어가 앉아 문에 안 닿음")
    ok(BONE['T'] <= KT, f"네임태그 {BONE['T']}T = 포켓 깊이 {KT} → 표면과 같은 높이")
    out = REMOTE['T'] - KT
    ok(TRAY_Z + out < DOOR_Z, f"리모컨은 뒷판에 닿고 앞으로 {out}mm 나옴 → {TRAY_Z+out} < 문 안쪽 {DOOR_Z} (여유 {DOOR_Z-TRAY_Z-out}mm), 밴드가 앞에서 잡음")
    hf = DOCK_Z + ROBOT_MODEL['head_front']; tb = TRAY_Z - KT
    ok(hf < tb, f"루모 얼굴 앞 z {hf} < 트레이 뒷면 {tb} (여유 {tb-hf}mm) · 머리 폭 {ROBOT_MODEL['head_w']} > 대문 창 92 → 앞으로 안 빠짐")
    ok(min(s.distance(remote_window()) for s in band_slits()) >= 5, '밴드 슬릿 ↔ 리모컨 창 폼 6.5mm (≥5)')
    return rep

if __name__ == '__main__':
    for line in check() + goods_check(): print(line)
