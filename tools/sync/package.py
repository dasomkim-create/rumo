"""Copies the RUMO 올인원 패키지 v8 page into docs/package/index.html and adds an ?embed mode
used by the landing's manual section. usage: python3 tools/sync/package.py <saved v8 index.html>
(v8: https://claude.ai/artifact/VYuXUBv8A7ntd73bgiQDoH — read it with path "index.html")"""
import sys, os
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
s = open(sys.argv[1], encoding='utf-8').read()
EMBED = '''<style>
html.embed,html.embed body{height:100%;background:var(--stage)}
html.embed body{padding:0!important}
html.embed .wrap{display:block;height:100%;max-width:none}
html.embed aside,html.embed .hint{display:none}
html.embed #view{height:100%;min-height:0;border-radius:0}
</style>
<script>if(/[?&]embed\\b/.test(location.search))document.documentElement.classList.add('embed');</script>
'''
i = s.find('<script src=')
assert i > 0
s = s[:i] + EMBED + s[i:]
CAM = 'new THREE.PerspectiveCamera(32,'
if CAM in s:  # embed: wider lens so a narrow frame still shows the whole set
    s = s.replace(CAM, "new THREE.PerspectiveCamera(/[?&]embed\\b/.test(location.search)?(innerWidth/innerHeight<1.1?42:innerWidth/innerHeight<1.6?31:22):32,", 1)
Z = 'ctrl.enableDamping=true;'
if Z in s:  # embed: wheel scrolls the landing instead of zooming the model
    s = s.replace(Z, Z + "if(/[?&]embed\\b/.test(location.search))ctrl.enableZoom=false;", 1)
out = os.path.join(REPO, 'docs', 'package', 'index.html')
open(out, 'w', encoding='utf-8').write(s)
print('wrote', out, len(s))
