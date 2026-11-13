"""Copy fetched canvas files into the repo and build a local render folder.
usage: python3 tools/sync/prepare.py <folder with fetched project/*.dc.html>
"""
import sys, os, re, glob, shutil
SRC = sys.argv[1]; REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src = glob.glob(os.path.join(SRC, '**', '*.dc.html'), recursive=True) + glob.glob(os.path.join(SRC, '**', 'canvas.json'), recursive=True)
changed = []
for f in src:
    name = os.path.basename(f); dst = os.path.join(REPO, 'project', name)
    new = open(f, 'rb').read()
    if not os.path.exists(dst) or open(dst, 'rb').read() != new:
        changed.append(name); open(dst, 'wb').write(new)
    if name.endswith('.dc.html') and not name.startswith('Brand'):
        shutil.copy(f, os.path.join(REPO, 'docs', 'app', 'screens', name))
R = os.path.join(REPO, 'tools', 'sync', '.render'); os.makedirs(R, exist_ok=True)
for f in glob.glob(os.path.join(REPO, 'project', '*.dc.html')): shutil.copy(f, R)
for line in open(os.path.join(os.path.dirname(__file__), 'slides.txt')):
    n = line.split('\t')[0].strip()
    if not n: continue
    open(os.path.join(R, 'E_' + n + '.dc.html'), 'w').write(
        '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>' + n + '</title><script src="./support.js"></script></head><body><x-dc>'
        '<div style="width: 1920px; height: 1080px;"><dc-import name="' + n + '" embed="{{yes}}" hint-size="1920px,1080px"></dc-import></div></x-dc>'
        '<script type="text/x-dc" data-dc-script data-props=\'{"$preview":{"width":1920,"height":1080}}\'>class Component extends DCLogic { renderVals() { return { yes: true }; } }</script></body></html>')
ids = set()
for f in glob.glob(os.path.join(REPO, 'project', '*.dc.html')):
    ids |= set(re.findall(r'/_blob/([0-9a-f]{32})', open(f).read()))
have = {os.path.splitext(x)[0] for x in os.listdir(os.path.join(REPO, 'docs', 'blobs'))}
print('CHANGED:', ' '.join(changed) or '(none)')
print('MISSING_BLOBS:', ' '.join(sorted(ids - have)) or '(none)')
print('support.js present:', os.path.exists(os.path.join(R, 'support.js')))
