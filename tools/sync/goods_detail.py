"""④ 굿즈 끼움 · 루모 실사이즈 점검 — 종합 도면용 상세 (1:1, mm). 모든 숫자는 kitgeo 원본에서."""
import math
import kitgeo as K
from shapely.geometry import Point, box as sbox
from shapely import affinity
CUT, INK, MUTE, GREEN, BLUE, DARK = '#EC008C', '#2B2E33', '#8A9099', '#A8D14B', '#8EA8EA', '#2B2E33'
FOAM, BACK, ITEM, RED = '#E9ECF0', '#AEB4BD', '#F1F2F4', '#E5484D'
F = 'Pretendard, Apple SD Gothic Neo, sans-serif'
def t(x, y, s, size=5.5, w=600, c=INK, a='middle'): return f'<text x="{x:.2f}" y="{y:.2f}" font-family="{F}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{a}">{s}</text>'
def path(g, ox, oy):                       # shapely (y 위) → svg (y 아래), 기준점 (ox, oy)
    gs = getattr(g, 'geoms', [g]); d = ''
    for p in gs:
        for ring in [p.exterior] + list(p.interiors):
            c = list(ring.coords); d += 'M' + 'L'.join(f'{ox + x:.2f},{oy - y:.2f}' for x, y in c) + 'Z'
    return d
def shape(g, ox, oy, fill='none', stroke=CUT, sw=0.4, extra=''):
    return f'<path d="{path(g, ox, oy)}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{sw}"{extra}/>'
def dim(x1, y1, x2, y2, s, off=0, size=4.6, side=1):  # 치수선
    if abs(y1 - y2) < 1e-6:
        y = y1 + off; return (f'<path d="M{x1:.2f},{y:.2f}H{x2:.2f}M{x1:.2f},{y-1.6:.2f}V{y+1.6:.2f}M{x2:.2f},{y-1.6:.2f}V{y+1.6:.2f}" stroke="{MUTE}" stroke-width="0.25" fill="none"/>'
                              + t((x1 + x2) / 2, y - 1.2 if side > 0 else y + 4.6, s, size, 500, MUTE))
    x = x1 + off; return (f'<path d="M{x:.2f},{y1:.2f}V{y2:.2f}M{x-1.6:.2f},{y1:.2f}H{x+1.6:.2f}M{x-1.6:.2f},{y2:.2f}H{x+1.6:.2f}" stroke="{MUTE}" stroke-width="0.25" fill="none"/>'
                          + f'<text x="0" y="0" transform="translate({x-1.2 if side>0 else x+4.2:.2f},{(y1+y2)/2:.2f}) rotate(-90)" font-family="{F}" font-size="{size}" font-weight="500" fill="{MUTE}" text-anchor="middle">{s}</text>')
def card(x, y, w, h, title, sub=''):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#FFFFFF" stroke="#D5D9DF" stroke-width="0.4"/>'
            + t(x + 8, y + 12, title, 7.5, 700, INK, 'start') + (t(x + w - 8, y + 12, sub, 5, 500, MUTE, 'end') if sub else ''))
def section(x, y, gap_w, item_w, item_t, extra_w=26, protrude_band=False, k=3):
    """단면 A-A: 위 = 앞(문 쪽). 폼 5T · 뒷판 1T · 물건."""
    o = []; gap_w, item_w, item_t, extra_w = gap_w * k, item_w * k, item_t * k, extra_w * k; W_ = gap_w + extra_w * 2; x0 = x - W_ / 2; KT, BT = K.KT * k, K.BACK_T * k
    o.append(f'<rect x="{x0:.2f}" y="{y:.2f}" width="{extra_w:.2f}" height="{KT}" fill="{FOAM}" stroke="{INK}" stroke-width="0.25"/>')
    o.append(f'<rect x="{x + gap_w/2:.2f}" y="{y:.2f}" width="{extra_w:.2f}" height="{KT}" fill="{FOAM}" stroke="{INK}" stroke-width="0.25"/>')
    o.append(f'<rect x="{x0:.2f}" y="{y + KT:.2f}" width="{W_:.2f}" height="{BT}" fill="{BACK}"/>')
    o.append(f'<rect x="{x - item_w/2:.2f}" y="{y + KT - item_t:.2f}" width="{item_w:.2f}" height="{item_t:.2f}" fill="{ITEM}" stroke="{INK}" stroke-width="0.3"/>')
    if protrude_band:
        top = y + KT - item_t - 0.6; ys = y + KT / 2
        o.append(f'<path d="M{x - gap_w/2 - 9:.2f},{y + KT + BT + 0.8:.2f}L{x - gap_w/2 - 9:.2f},{ys:.2f}L{x - item_w/2:.2f},{top:.2f}L{x + item_w/2:.2f},{top:.2f}L{x + gap_w/2 + 9:.2f},{ys:.2f}L{x + gap_w/2 + 9:.2f},{y + KT + BT + 0.8:.2f}Z" fill="none" stroke="{BLUE}" stroke-width="1.1" stroke-linejoin="round"/>')
    o.append(t(x0 - 2, y + 2, '앞 ↑', 4.2, 600, MUTE, 'end') + t(x0 - 2, y + KT + BT, '뒤', 4.2, 600, MUTE, 'end') + t(x + W_ / 2, y - 3, f'{k}배 확대', 4, 500, MUTE, 'end'))
    return ''.join(o)

def robot_front(cx, base):                 # 루모 정면 실루엣 (3D 모형 가정값 · 폭 105 × 높이 180)
    o = []; W = '#FFFFFF'
    for s in (-1, 1):
        o.append(f'<rect x="{cx + s*32 - 14:.2f}" y="{base - 72:.2f}" width="28" height="72" rx="6" fill="{W}" stroke="{INK}" stroke-width="0.35"/>')
        o.append(f'<rect x="{cx + s*32 - 15:.2f}" y="{base - 16:.2f}" width="30" height="16" rx="2" fill="{DARK}"/>')
    o.append(f'<ellipse cx="{cx}" cy="{base - 92}" rx="44" ry="36" fill="{W}" stroke="{INK}" stroke-width="0.35"/>')
    o.append(f'<ellipse cx="{cx}" cy="{base - 108}" rx="30" ry="9" fill="#BFE0F4"/>')
    for s in (-1, 1): o.append(f'<ellipse cx="{cx + s*47}" cy="{base - 126}" rx="7" ry="30" transform="rotate({-s*12.6} {cx + s*47} {base - 126})" fill="{DARK}"/>')
    o.append(f'<ellipse cx="{cx}" cy="{base - 134}" rx="50" ry="44" fill="{W}" stroke="{INK}" stroke-width="0.35"/>')
    o.append(f'<rect x="{cx - 38}" y="{base - 158}" width="76" height="32" rx="14" fill="{DARK}"/>')
    for s in (-1, 1): o.append(f'<ellipse cx="{cx + s*15}" cy="{base - 143}" rx="8" ry="7" fill="#8FE6FF"/>')
    return ''.join(o)
def robot_side(z0, base):                  # 옆 실루엣, z0 = 몸 중심 (오른쪽 = 앞)
    o = []; W = '#FFFFFF'
    for z in (58, -55):
        o.append(f'<rect x="{z0 + z - 14:.2f}" y="{base - 72:.2f}" width="28" height="72" rx="6" fill="{W}" stroke="{INK}" stroke-width="0.35"/>')
        o.append(f'<rect x="{z0 + z - 20:.2f}" y="{base - 16:.2f}" width="40" height="16" rx="2" fill="{DARK}"/>')
    o.append(f'<ellipse cx="{z0 - 4}" cy="{base - 92}" rx="72" ry="36" fill="{W}" stroke="{INK}" stroke-width="0.35"/>')
    o.append(f'<ellipse cx="{z0 + 38}" cy="{base - 134}" rx="44" ry="44" fill="{W}" stroke="{INK}" stroke-width="0.35"/>')
    o.append(f'<ellipse cx="{z0 + 62}" cy="{base - 142}" rx="18" ry="16" fill="{DARK}"/>')
    o.append(f'<circle cx="{z0 + 80}" cy="{base - 122}" r="7" fill="{DARK}"/>')
    o.append(f'<ellipse cx="{z0 + 30}" cy="{base - 126}" rx="17" ry="30" fill="{DARK}" opacity=".85"/>')
    return ''.join(o)

def build(X0, Y0, WD):
    o = []; y = Y0
    o.append(t(X0, y, '④ 굿즈 끼움 상세 · 루모 실사이즈 점검 (1:1)', 10, 700, INK, 'start')); y += 8
    o.append(t(X0, y + 4, f'코스터·네임태그는 폼보드 포켓을 {K.PRESS}mm 작게 따서 눌러 끼우고, 뒤에 그레이보드 {K.BACK_T}T 뒷판을 붙여 바닥을 막아요. 리모컨은 두께가 {K.REMOTE["T"]}mm라 포켓에 다 안 들어가서, 창은 {K.SLIP}mm 크게 따고 고무 리본 밴드로 앞에서 잡아요.', 5.5, 500, MUTE, 'start')); y += 14
    cw, chh, g = (WD - 2 * X0 - 2 * 14) / 3, 210, 14
    # ── 카드 1: 코스터
    cx0 = X0; o.append(card(cx0, y, cw, chh, '네잎 코스터 포켓 ×2', f'코르크 {K.COASTER["T"]}T · 36.1 × 36.1'))
    name, item, cutp, notch = K.pockets()[0]; c = item.centroid; ox, oy = cx0 + cw / 2 - c.x, y + 72 + c.y
    o.append(shape(item, ox, oy, GREEN, 'none') + shape(cutp.union(notch), ox, oy, 'none', CUT, 0.5))
    for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        pass
    bx = item.bounds; hb = cutp.bounds
    o.append(dim(ox + bx[0], oy - bx[3], ox + bx[2], oy - bx[3], '36.1 (코스터)', -6))
    o.append(dim(ox + hb[0], oy - hb[1], ox + hb[2], oy - hb[1], f'{hb[2]-hb[0]:.1f} (칼선 · −{K.PRESS} 눌러 끼움)', 6, side=-1))
    o.append(t(ox + c.x - 30, oy - c.y - 14, '손가락 홈 R6', 4.6, 600, CUT, 'end'))
    o.append(t(ox + c.x, oy - c.y + 1.6, '원 Ø19 × 4', 4.4, 600, '#3E5A12'))
    sy = y + 132; o.append(t(cx0 + 8, sy - 8, '단면 A-A', 5.5, 700, INK, 'start'))
    o.append(section(cx0 + cw / 2, sy, 35.7, 35.7, K.COASTER['T']))
    o.append(t(cx0 + cw / 2, sy + 30, f'폼 5T 포켓 · 코스터 4T → 1mm 안으로 앉음 · 회색 = 뒷판 1T가 바닥', 4.8, 500, MUTE))
    o.append(t(cx0 + 8, y + chh - 28, '끼우는 법: 손가락 홈 쪽을 먼저 넣고 반대쪽을 눌러요.', 5, 600, INK, 'start'))
    o.append(t(cx0 + 8, y + chh - 19, '빼는 법: 손가락 홈에 손톱을 넣어 들어 올려요.', 5, 600, INK, 'start'))
    o.append(t(cx0 + 8, y + chh - 10, '폼이 0.1mm씩 눌리며 잡아서 트레이를 세워도 안 빠져요.', 5, 500, MUTE, 'start'))
    # ── 카드 2: 네임태그
    cx0 = X0 + cw + g; o.append(card(cx0, y, cw, chh, '뼈 네임태그 포켓', f'폼보드 {K.BONE["T"]}T · {K.BONE["W"]} × {K.BONE["L"]} · 끈 Ø{K.BONE["hole"]}'))
    name, item, cutp, notch = K.pockets()[2]; c = item.centroid; ox, oy = cx0 + cw / 2 - c.x - 20, y + 78 + c.y
    o.append(shape(item, ox, oy, BLUE, 'none') + shape(K.bone_hole(*K.BONE_AT), ox, oy, '#FFFFFF', INK, 0.3) + shape(cutp.union(notch), ox, oy, 'none', CUT, 0.5))
    bx = item.bounds
    o.append(dim(ox + bx[0], oy - bx[3], ox + bx[2], oy - bx[3], f'{K.BONE["W"]}', -5))
    o.append(dim(ox + bx[0], oy - bx[1], ox + bx[0], oy - bx[3], f'{K.BONE["L"]}', -6))
    o.append(t(ox + c.x + 18, oy - c.y + 1.6, '손가락 홈 R6', 4.6, 600, CUT, 'start'))
    o.append(t(ox + c.x + 18, oy - c.y - 18, f'끈 구멍 Ø{K.BONE["hole"]}', 4.6, 600, INK, 'start'))
    o.append(t(ox + c.x + 18, oy - c.y - 11, '왁스 끈 200mm로 손잡이에 묶음', 4.4, 500, MUTE, 'start'))
    sy = y + 132; o.append(t(cx0 + 8, sy - 8, '단면 B-B', 5.5, 700, INK, 'start'))
    o.append(section(cx0 + cw / 2, sy, 21.6, 21.6, K.BONE['T']))
    o.append(t(cx0 + cw / 2, sy + 30, '포켓 깊이 5 = 네임태그 5T → 표면과 같은 높이', 4.8, 500, MUTE))
    o.append(t(cx0 + 8, y + chh - 28, '배송: 끈은 미리 꿰어 두고 태그 뒤로 접어 함께 끼워요.', 5, 600, INK, 'start'))
    o.append(t(cx0 + 8, y + chh - 19, '완성: 끈을 손잡이 구멍에 둘러 묶어 이름표로 달아요.', 5, 600, INK, 'start'))
    o.append(t(cx0 + 8, y + chh - 10, '그냥 올려 두는 게 아니라 끈으로 매달아야 해요.', 5, 500, MUTE, 'start'))
    # ── 카드 3: 리모컨
    cx0 = X0 + 2 * (cw + g); o.append(card(cx0, y, cw, chh, '리모컨 창 + 고정 밴드', f'가정 {K.REMOTE["W"]} × {K.REMOTE["L"]} × {K.REMOTE["T"]} · 실측 필요'))
    win = K.remote_window(); sl = K.band_slits(); rx, ry = K.REMOTE_AT
    sc = 0.62; ox, oy = cx0 + 22, y + 44
    def S(g_): return affinity.scale(affinity.translate(g_, -rx, -ry), sc, sc, origin=(0, 0))
    o.append(shape(S(K.wing_R()), ox + 30, oy + 60 + 97 * sc - 0, FOAM, INK, 0.25).replace(f'{0:.2f}', f'{0:.2f}'))
    # 날개 전체를 0.8배로: 기준점을 창 중심으로
    base_x, base_y = ox + 30, oy + 60
    o[-1] = shape(S(K.wing_R()), base_x, base_y, FOAM, INK, 0.25)
    o.append(f'<rect x="{base_x - K.REMOTE["W"]/2*sc:.2f}" y="{base_y - K.REMOTE["L"]/2*sc:.2f}" width="{K.REMOTE["W"]*sc:.2f}" height="{K.REMOTE["L"]*sc:.2f}" rx="3" fill="{ITEM}" stroke="{INK}" stroke-width="0.3"/>')
    for bx_, by_ in ((0, 30), (-12, -5), (12, -5), (0, -20)): o.append(f'<circle cx="{base_x + bx_*sc:.2f}" cy="{base_y - by_*sc:.2f}" r="{6*sc:.2f}" fill="#BFE0F4"/>')
    o.append(shape(S(win), base_x, base_y, 'none', CUT, 0.5) + ''.join(shape(S(s_), base_x, base_y, 'none', CUT, 0.5) for s_ in sl))
    sb = [S(s_).bounds for s_ in sl]
    o.append(f'<rect x="{base_x - 4.8:.2f}" y="{base_y - sb[1][3]:.2f}" width="9.6" height="{sb[1][3]-sb[0][1]:.2f}" fill="{BLUE}" opacity=".55"/>')
    wb = S(win).bounds
    o.append(dim(base_x + wb[0], base_y - wb[3], base_x + wb[2], base_y - wb[3], f'{K.REMOTE["W"]+2*K.SLIP:.0f} 창', -5))
    o.append(dim(base_x + wb[2], base_y - wb[1], base_x + wb[2], base_y - wb[3], f'{K.REMOTE["L"]+2*K.SLIP:.0f} 창', 14, side=-1))
    o.append(t(base_x + 36, base_y - sb[1][1] + 2, '슬릿 12 × 2', 4.4, 600, CUT, 'start') + t(base_x + 36, base_y - sb[0][1] + 2, '슬릿 12 × 2', 4.4, 600, CUT, 'start'))
    o.append(t(base_x + 36, base_y - 4, '고무 리본 8mm', 4.4, 600, '#3D5BB8', 'start') + t(base_x + 36, base_y + 2.5, '둘레 260 고리', 4.4, 500, MUTE, 'start'))
    o.append(t(base_x, base_y + 58 * sc + 12, '0.62배 축소', 4, 500, MUTE))
    sy = y + 112; sx = cx0 + cw * 0.70; o.append(t(sx - 70, sy - 52, '단면 C-C', 5.5, 700, INK, 'start'))
    o.append(section(sx, sy, 51, 50, K.REMOTE['T'], 9, True, 2))
    o.append(dim(sx + 62, sy + 2 * K.KT, sx + 62, sy + 2 * (K.KT - K.REMOTE['T']), f'{K.REMOTE["T"]}', 0, 4.2, -1))
    o.append(t(sx, sy + 24, f'앞으로 {K.REMOTE["T"]-K.KT}mm 나옴 · 문까지 {K.DOOR_Z-K.TRAY_Z-(K.REMOTE["T"]-K.KT)}mm 여유', 4.6, 500, MUTE) + t(sx, sy + 32, '파란 선 = 고무 리본', 4.6, 600, '#3D5BB8'))
    o.append(t(cx0 + 8, y + chh - 28, '두께 22는 5T 포켓에 다 안 들어가요 → 마찰만으론 앞으로 쏟아짐.', 5, 600, INK, 'start'))
    o.append(t(cx0 + 8, y + chh - 19, '그래서 위·아래 슬릿에 고무 리본을 걸어 앞에서 눌러 줘요.', 5, 600, INK, 'start'))
    o.append(t(cx0 + 8, y + chh - 10, '리본을 빼면 리모컨이 나오는 ‘선물 리본’ 연출도 돼요.', 5, 500, MUTE, 'start'))
    y += chh + 14
    # ── 뒷판 부품 + 루모 실사이즈
    o.append(card(X0, y, 210, 252, '날개 뒷판 L · R', f'그레이보드 {K.BACK_T}T · 2장 · 풀칠'))
    L, R = K.backings(); bxL, bxR = L.bounds, R.bounds
    o.append(shape(L, X0 + 14 - bxL[0], y + 28 + bxL[3], '#D9DDE3', CUT, 0.5) + t(X0 + 14 + (bxL[2]-bxL[0])/2, y + 28 + (bxL[3]-bxL[1])/2, '뒷판 L', 5.5, 700))
    o.append(shape(R, X0 + 110 - bxR[0], y + 28 + bxR[3] + 6, '#D9DDE3', CUT, 0.5) + t(X0 + 110 + (bxR[2]-bxR[0])/2, y + 28 + 6 + (bxR[3]-bxR[1])/2 + 20, '뒷판 R', 5.5, 700))
    o.append(t(X0 + 8, y + 244, '접는 선에서 2mm 띄워 붙여야 날개가 꺾여요 · 슬릿·장식 창은 같이 뚫음', 4.6, 500, MUTE, 'start'))
    # 루모 정면 · 아치
    fx = X0 + 224; fw = 300
    o.append(card(fx, y, fw, 252, '루모 × 아치 (정면)', f'상품 표기 {K.ROBOT["W"]} × {K.ROBOT["L"]} × {K.ROBOT["H"]}'))
    floor = y + 240; ax = fx + fw / 2
    A = K.P_(K.A1()[0]) if isinstance(K.A1(), tuple) else None
    arch_o, arch_h = K.A1()
    o.append(shape(K.P_(arch_o, arch_h), ax - 105, floor, '#F6F7F9', CUT, 0.5))
    o.append(f'<rect x="{ax - 73:.2f}" y="{floor - 4:.2f}" width="146" height="4" fill="#D9DDE3" stroke="{INK}" stroke-width="0.25"/>')
    o.append(robot_front(ax, floor - 4))
    top_gap = 115 + 75 - 4 - K.ROBOT['H']
    o.append(dim(ax + 70, floor, ax + 70, floor - 190, '아치 190', 0, 4.4, -1) + dim(ax - 70, floor - 4, ax - 70, floor - 4 - K.ROBOT['H'], f'루모 {K.ROBOT["H"]}', 0, 4.4))
    o.append(dim(ax - 52.5, floor - 4 - K.ROBOT['H'] - 8, ax + 52.5, floor - 4 - K.ROBOT['H'] - 8, f'{K.ROBOT["W"]}', 0, 4.2))
    o.append(t(ax, floor - 202, f'위 여유 {top_gap}mm · 옆 여유 각 {(150 - K.ROBOT["W"]) / 2:.1f}mm', 5, 700, '#2E7D32'))
    # 배송 단면 (옆)
    sx0 = fx + fw + 14; sw_ = WD - X0 - sx0
    o.append(card(sx0, y, sw_, 252, '배송 단면 (옆에서) — 앞뒤 여유', '뒷벽 ↔ 트레이 ↔ 문'))
    fl = y + 222; zx = lambda z: sx0 + 16 + z * 1.0
    o.append(f'<rect x="{zx(0):.2f}" y="{fl - 223:.2f}" width="3" height="223" fill="{BACK}"/>' + t(zx(1.5), fl - 226, '뒷벽', 4.4, 600, MUTE))
    o.append(f'<rect x="{zx(0):.2f}" y="{fl:.2f}" width="220" height="3" fill="{BACK}"/>')
    o.append(f'<rect x="{zx(3):.2f}" y="{fl - 23:.2f}" width="217" height="20" fill="#EEF0F3" stroke="{MUTE}" stroke-width="0.25"/>' + t(zx(112), fl - 10, '런너 4장 (받침)', 4.4, 600, MUTE))
    o.append(f'<rect x="{zx(K.DOCK_Z - 76):.2f}" y="{fl - 27:.2f}" width="152" height="4" fill="#D9DDE3" stroke="{INK}" stroke-width="0.25"/>')
    o.append(robot_side(zx(K.DOCK_Z), fl - 27))
    o.append(f'<rect x="{zx(K.TRAY_Z - K.KT):.2f}" y="{fl - 23 - 190:.2f}" width="{K.KT}" height="190" fill="{FOAM}" stroke="{INK}" stroke-width="0.3"/>')
    o.append(f'<rect x="{zx(K.TRAY_Z - K.KT):.2f}" y="{fl - 23 - 176 - 10:.2f}" width="{K.KT}" height="166" fill="#FFFFFF" stroke="{CUT}" stroke-width="0.3" stroke-dasharray="1.2 1"/>')
    o.append(t(zx(K.TRAY_Z - 2.5), fl - 23 - 194, '트레이', 4.4, 600, INK))
    o.append(f'<rect x="{zx(K.DOOR_Z):.2f}" y="{fl - 223:.2f}" width="3" height="223" fill="{BACK}"/>' + t(zx(K.DOOR_Z + 1.5), fl - 226, '문', 4.4, 600, MUTE))
    o.append(f'<rect x="{zx(K.TRAY_Z):.2f}" y="{fl - 23 - 97 - 55:.2f}" width="{K.REMOTE["T"] - K.KT}" height="110" fill="{ITEM}" stroke="{INK}" stroke-width="0.3"/>' + t(zx(K.TRAY_Z + 9), fl - 23 - 97 + 60, '리모컨', 4.2, 600, INK))
    hf = K.DOCK_Z + K.ROBOT_MODEL['head_front']
    o.append(dim(zx(3), fl - 172, zx(K.DOCK_Z - 76), fl - 172, f'{K.DOCK_Z - 76 - 3}', 0, 4))
    o.append(dim(zx(hf), fl - 150, zx(K.TRAY_Z - K.KT), fl - 150, '', 0, 4))
    o.append(t(zx(250), fl - 150, f'← 얼굴 ↔ 트레이 {K.TRAY_Z - K.KT - hf}mm', 5, 700, '#2E7D32', 'start'))
    o.append(t(zx(250), fl - 138, '코끝만 대문 창(폭 92) 안으로 · 머리(폭 100)가 창에 걸려 안 빠짐', 4.4, 500, MUTE, 'start') + t(zx(250), fl - 60, '← 리모컨 앞 ↔ 문 여유', 5, 700, '#2E7D32', 'start') + t(zx(250), fl - 180, f'← 뒷벽 ↔ 꼬리 {K.DOCK_Z - 76 - 3}mm', 5, 700, '#2E7D32', 'start'))
    o.append(dim(zx(K.TRAY_Z + K.REMOTE['T'] - K.KT), fl - 60, zx(K.DOOR_Z), fl - 60, f'{K.DOOR_Z - K.TRAY_Z - K.REMOTE["T"] + K.KT}', 0, 4))
    y += 252 + 14
    # ── 실측 체크리스트
    rows = [('리모컨 폭 × 길이 × 두께', f'{K.REMOTE["W"]} × {K.REMOTE["L"]} × {K.REMOTE["T"]} (가정)', '창 = +1mm · 폭 ≤ 53 · 길이 ≤ 113 · 두께 ≠ 22면 리브 F 앉는 자리 다시'),
            ('발 4개 위치 · 크기', '좌우 ±32 · 앞뒤 +58 / −55 · 30 × 40', '받침 블록 홈 = 발 +4mm (34 × 42)'),
            ('머리 가장 넓은 폭', f'{K.ROBOT_MODEL["head_w"]}', '대문 창 92보다 넓어야 앞으로 안 빠짐'),
            ('꼬리 끝 ↔ 머리 폭이 92가 되는 지점', '약 131', '≤ 160 (뒷벽 3 ~ 트레이 뒷면 163) · 넘으면 받침 블록 홈을 앞으로'),
            ('전체 높이 (받침 위에 섰을 때)', f'{K.ROBOT["H"]}', f'≤ 186 (아치 190 − 받침 4) → 지금 여유 {top_gap}mm'),
            ('코스터 · 네임태그 실제 두께', f'{K.COASTER["T"]} / {K.BONE["T"]}', '≤ 5 (포켓 깊이) · 다르면 PRESS 값 조정')]
    o.append(card(X0, y, WD - 2 * X0, 30 + 11 * len(rows), '로봇 받으면 잴 것 — 숫자만 바꾸면 도면이 다시 맞춰져요 (tools/sync/kitgeo.py)'))
    cols = [X0 + 10, X0 + 260, X0 + 470]
    for k, hdr in enumerate(['항목', '지금 도면 값', '허용 범위 · 바뀌는 것']): o.append(t(cols[k], y + 24, hdr, 5, 700, MUTE, 'start'))
    for i, r in enumerate(rows):
        for k, v in enumerate(r): o.append(t(cols[k], y + 35 + i * 11, v, 5.4, 600 if k == 0 else 500, INK, 'start'))
    y += 30 + 11 * len(rows) + 14
    return o, y
