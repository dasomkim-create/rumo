"""다솜님이 일러스트에서 고친 인쇄 전개도(art/rumo-print-dieline.svg)를 면마다 잘라 v8 3D 박스 텍스처로 구워요.
칼선 · 접는 선 · 회색 안내 글자 · 홈 표시는 빼고, 인쇄되는 그림만 남겨요.
  python3 tools/sync/box_tex.py <v8 index.html>   → 같은 파일의 /*BOXTEX*/ 자리를 갈아 끼워요
좌표: 전개도 world(mm) — 뒷벽 아래 가운데 = (0,0), 위가 +y. 바깥면 시트는 좌우가 뒤집혀 있어요."""
import sys, os, re, io, json, base64, math, subprocess, tempfile
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'art', 'rumo-print-dieline.svg')
W, D, H, R, FIN = 270, 220, 220, 78, 70
S = math.hypot(135, 78)
OX = 525.0
OY_OUT = 30 + 48 + 10 + H + S + FIN                 # ① 바깥면: 뒷벽 아래 가운데 (print_sheet.py와 같은 배치)
OY_IN = OY_OUT + D + 26 + 10 + H + S + FIN          # ② 안쪽면
PXMM = float(os.environ.get('PXMM', 8))             # 텍스처 해상도 (px/mm)

FACES_OUT = {   # 이름: world 사각형 (x0, y0, x1, y1)
    'back': (-135, 0, 135, H + R), 'floor': (-135, -D, 135, 0),
    'side1': (-135 - D, 0, -135, H), 'side2': (135, 0, 135 + D, H),
    'roof1': (-135 - D, H, -135, H + S), 'roof2': (135, H, 135 + D, H + S),
    'fin1': (-135 - D, H + S, -135, H + S + FIN), 'fin2': (135, H + S, 135 + D, H + S + FIN),
    'doorL': (-490, 0, -355, H + R), 'doorR': (355, 0, 490, H + R),
}
FACES_IN = {'doorL_in': (-490, 0, -355, H + R), 'doorR_in': (355, 0, 490, H + R), 'mat': (-131, -216, 131, -4)}

def clean_svg():
    s = open(SRC, encoding='latin-1').read()
    # 칼선/접는 선(선만), 안내 글자(회색), 홈 표시(흰 칸) 숨김
    s = s.replace('</style>', '*{stroke:none!important}.st2,.st26,.st62,.st23,.st49{display:none}\n</style>', 1)
    return s

def render(svg, sheet_box, px):
    pt = 2948.031 / 1040
    x0, y0, x1, y1 = sheet_box
    vb = f'{x0*pt:.3f} {y0*pt:.3f} {(x1-x0)*pt:.3f} {(y1-y0)*pt:.3f}'
    s = re.sub(r'viewBox="[^"]*"', f'viewBox="{vb}"', svg, count=1)
    s = re.sub(r'<svg ', f'<svg width="{px[0]}" height="{px[1]}" ', s, count=1)
    with tempfile.TemporaryDirectory() as d:
        open(d + '/a.svg', 'w', encoding='latin-1').write(s)
        subprocess.run(['rsvg-convert', d + '/a.svg', '-o', d + '/a.png'], check=True)
        im = Image.open(d + '/a.png').convert('RGBA'); bg = Image.new('RGBA', im.size, '#FBFBFC'); bg.alpha_composite(im); return bg.convert('RGB')

def bake():
    svg = clean_svg(); out = {}
    for faces, outside in ((FACES_OUT, True), (FACES_IN, False)):
        for name, (x0, y0, x1, y1) in faces.items():
            oy = OY_OUT if outside else OY_IN
            if outside: box = (OX - x1, oy - y1, OX - x0, oy - y0)
            else: box = (OX + x0, oy - y1, OX + x1, oy - y0)
            px = (round((x1 - x0) * PXMM), round((y1 - y0) * PXMM))
            im = render(svg, box, px)
            if outside: im = im.transpose(Image.FLIP_LEFT_RIGHT)      # world 방향으로 되돌림
            b = io.BytesIO(); im.save(b, 'WEBP', quality=92, method=6)
            out[name] = {'r': [x0, y0, x1, y1], 'u': 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()}
            if os.environ.get('DUMP'): im.save(os.path.join(os.environ['DUMP'], name + '.png'))
    return out

if __name__ == '__main__':
    tx = bake()
    js = '/*BOXTEX*/const BOXTEX=' + json.dumps(tx, separators=(',', ':')) + ';/*/BOXTEX*/'
    p = sys.argv[1]; s = open(p, encoding='utf-8').read()
    s = re.sub(r'/\*BOXTEX\*/.*?/\*/BOXTEX\*/', lambda m: js, s, flags=re.S)
    open(p, 'w', encoding='utf-8').write(s)
    print('baked', len(tx), 'faces', len(js) // 1024, 'KB')
