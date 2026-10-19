"""Para cada arquivo de imagem: escala (sx, sy) com que aparece na tela."""
import json, os, re, sys, collections, statistics
from PIL import Image
root = sys.argv[1]
d = json.load(open(os.path.join(root, 'game.json')))
res = {r['name']: r for r in d['resources']['resources'] if r['kind'] == 'image'}
s_all = json.dumps(d)
setsize = collections.defaultdict(list)
for o, w, h in re.findall(r'SetSize"\}, "parameters": \["([^"]+)", "[^"]+", "(\d+)", "(\d+)"\]', s_all):
    setsize[o].append((int(w), int(h)))
def frames(o):
    out = []
    if o['type'] == 'Sprite':
        for a in o.get('animations', []):
            for dr in a['directions']:
                for sp in dr['sprites']: out.append(sp['image'])
    elif 'TiledSprite' in o['type'] or 'PanelSprite' in o['type']:
        out.append(o.get('texture') or o.get('content', {}).get('texture'))
    return [f for f in out if f in res]
scopes = [('*', d.get('objects', []))] + [(l['name'], l['objects']) for l in d['layouts']]
inst = collections.defaultdict(list)
for l in d['layouts']:
    for i in l['instances']:
        inst[(l['name'], i['name'])].append(i)
fscale = collections.defaultdict(list)
for scope, objs in scopes:
    for o in objs:
        fr = frames(o)
        if not fr: continue
        try: w0, h0 = Image.open(os.path.join(root, res[fr[0]]["file"])).size
        except OSError: continue
        tiled = o['type'] != 'Sprite'
        sc = []
        if not tiled:
            for (ls, n), L in inst.items():
                if n != o['name'] or (scope != '*' and ls != scope): continue
                for i in L:
                    if i.get('customSize'): sc.append((i['width'] / w0, i['height'] / h0))
            for w, h in setsize.get(o['name'], []): sc.append((w / w0, h / h0))
        if not sc: sc = [(1.0, 1.0)]
        sx = statistics.median(a for a, b in sc); sy = statistics.median(b for a, b in sc)
        for f in fr: fscale[res[f]['file']].append((sx, sy, o['name']))
json.dump({f: v for f, v in fscale.items()}, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
