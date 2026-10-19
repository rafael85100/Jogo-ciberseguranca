import json, os, sys, collections
from PIL import Image
root = sys.argv[1]
d = json.load(open(os.path.join(root, 'game.json')))
res = {r['name']: r for r in d['resources']['resources']}
use = collections.defaultdict(set)   # resource name -> set of (scope, objname, type)
objs = []  # (scope, obj)
for o in d.get('objects', []): objs.append(('GLOBAL', o))
for l in d['layouts']:
    for o in l['objects']: objs.append((l['name'], o))
def walk(x, cb):
    if isinstance(x, dict):
        for k, v in x.items():
            if isinstance(v, str) and v in res: cb(k, v)
            walk(v, cb)
    elif isinstance(x, list):
        for v in x: walk(v, cb)
for scope, o in objs:
    walk(o, lambda k, v: use[v].add((o['type'], o['name'])))
# instance sizes per object
inst = collections.defaultdict(list)
for l in d['layouts']:
    for i in l['instances']:
        inst[i['name']].append((l['name'], i.get('customSize'), round(i.get('width',0)), round(i.get('height',0)), i.get('layer')))
rows = []
for name, r in res.items():
    if r['kind'] != 'image': continue
    f = os.path.join(root, r['file'])
    try:
        w, h = Image.open(f).size
    except Exception as e:
        w = h = None
    u = sorted(use.get(name, []))
    rows.append((r['file'], w, h, os.path.getsize(f) if os.path.exists(f) else -1, u))
for f, w, h, s, u in sorted(rows, key=lambda r: r[0]):
    objsz = []
    for t, n in u[:3]:
        ins = [x for x in inst.get(n, []) if x[1]]
        objsz.append(f"{n}[{t.split('::')[-1]}]" + (f"{ins[0][2]}x{ins[0][3]}" if ins else ''))
    print(f"{f}\t{w}x{h}\t{s//1024}K\t{len(u)}\t{' '.join(objsz)}")
