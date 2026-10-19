import json, sys, os
path, converted = sys.argv[1], set(json.load(open(sys.argv[2])))
raw = open(path, encoding='utf-8').read()
d = json.loads(raw)
SOFT = ('Glow', 'LightGlow', 'ExplosionTexture', 'ExplosionFog', 'Lightning', 'DarkMagicSmoke')
changed = []
for r in d['resources']['resources']:
    if r['kind'] != 'image': continue
    f = r['file']
    pixel = f in converted or (f.startswith('assets/') and not f.startswith('assets/image/')
                                 and not any(s in f for s in SOFT)) \
        or f in ('assets/image/d801cff8-420f-4641-8aa4-a37c5214efb7-removebg-preview.png',
                 'assets/image/ChatGPT_Image_1_de_jul._de_2026__11_41_37-removebg-preview.png',
                 'passarela_1-removebg-preview.png', 'passarela_2-removebg-preview.png',
                 'passarela_2-removebg-preview2.png')
    if pixel and r.get('smoothed', True):
        r['smoothed'] = False; changed.append(f)
d['properties']['pixelsRounding'] = True
out = json.dumps(d, indent=2, ensure_ascii='\\u00' in raw) + '\n'
open(path, 'w', encoding='utf-8').write(out)
print(len(changed), 'recursos com suavizacao desligada')
