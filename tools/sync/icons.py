"""앱 아이콘 · 파비콘 링크를 docs 안 모든 페이지에 넣어요 (여러 번 돌려도 한 번만 들어감).
다른 생성 스크립트(package.py, parts.py, deck.py …)를 돌린 뒤 마지막에 실행하세요."""
import os, re, glob
DOCS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs'))
for f in glob.glob(os.path.join(DOCS, '**', '*.html'), recursive=True):
    s = open(f, encoding='utf-8').read()
    if '<title' not in s or os.sep + 'screens' + os.sep in f: continue
    rel = os.path.relpath(DOCS, os.path.dirname(f)).replace(os.sep, '/'); rel = '' if rel == '.' else rel + '/'
    tag = (f'<!--rumo-icons--><link rel="icon" href="{rel}icon.svg" type="image/svg+xml"><link rel="icon" href="{rel}favicon-32.png" sizes="32x32">'
           f'<link rel="apple-touch-icon" href="{rel}apple-touch-icon.png"><!--/rumo-icons-->')
    s2 = re.sub(r'<!--rumo-icons-->.*?<!--/rumo-icons-->', '', s)
    s2 = re.sub(r'(<title[^>]*>.*?</title>)', lambda m: m.group(1) + tag, s2, count=1, flags=re.S)
    if s2 != s: open(f, 'w', encoding='utf-8').write(s2); print('icons →', os.path.relpath(f, DOCS))
