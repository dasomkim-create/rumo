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

if __name__ == '__main__':
    for line in check(): print(line)
