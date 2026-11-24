#!/usr/bin/env python3
"""Monta a pasta de patch dos dados da v23 para o build_assets.py.

- textura .ctex + .import de assets/image/plataforma_neon.png (copiada do projeto de PC) e a
  entrada no resourceMap de assets/data/gd_project.json;
- assets/data/gd_objects.json:
  - final: objeto plataforma_neon (copiado do game.json do PC; Platform do tipo Jumpthru);
  - cena2: robo_z3 ganha a patrulha (cópia da do robo_z2, velocidade 105), como no PC;
  - cena2: robo_z5/z6/z7 ganham o ponto da barra (z5/z6/z7, copiado do z4 do robo_z4).

Uso: v23_apk.py base.apk game.json pasta_do_projeto_pc patch/
"""
import copy, hashlib, json, os, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ctex  # noqa: E402
from PIL import Image  # noqa: E402

base_apk, game_json, pc_dir, patch = sys.argv[1:5]
z = zipfile.ZipFile(base_apk)
modelo = z.read('assets/.godot/imported/municao1.png-966b01800c84a06f41fd166211fcad67.ctex')
proj = json.loads(z.read('assets/data/gd_project.json'))
objs = json.loads(z.read('assets/data/gd_objects.json'))
g = json.load(open(game_json, encoding='utf-8'))
L = {l['name']: l for l in g['layouts']}

# ---- textura da plataforma ----
img = 'assets/image/plataforma_neon.png'
res = 'res://' + img
nome = os.path.basename(img) + '-' + hashlib.md5(res.encode()).hexdigest() + '.ctex'
destino = os.path.join(patch, 'assets/.godot/imported', nome)
os.makedirs(os.path.dirname(destino), exist_ok=True)
open(destino, 'wb').write(ctex.build(modelo, Image.open(os.path.join(pc_dir, img)).convert('RGBA')))
imp = os.path.join(patch, 'assets', img + '.import')
os.makedirs(os.path.dirname(imp), exist_ok=True)
open(imp, 'w').write('[remap]\n\nimporter="texture"\ntype="CompressedTexture2D"\npath="res://.godot/imported/%s"\n'
                     'metadata={\n"vram_texture": false\n}\n' % nome)
proj['resourceMap'][img] = res

# ---- final: plataforma_neon ----
pl = copy.deepcopy(next(o for o in L['final']['objects'] if o['name'] == 'plataforma_neon'))
assert pl['behaviors'][0]['platformType'] == 'Jumpthru'
pl['_default_size'] = [216, 36]
pl['_godot_script'] = 'gd_sprite.gd'
objs['final']['plataforma_neon'] = pl

# ---- cena2: patrulha do robo_z3 ----
c2 = objs['cena2']
PATRULHA = 'TimedBackAndForthMovement::TimedBackAndForthMirroredMovement'
if not any(b['type'] == PATRULHA for b in c2['robo_z3']['behaviors']):
    b = copy.deepcopy(next(b for b in c2['robo_z2']['behaviors'] if b['type'] == PATRULHA))
    b['Speed'] = 105
    c2['robo_z3']['behaviors'].insert(0, b)

# ---- cena2: pontos das barras z5/z6/z7 ----
ref = c2['robo_z4']['animations']
for n, pt in [('robo_z5', 'z5'), ('robo_z6', 'z6'), ('robo_z7', 'z7')]:
    for anim, anim_ref in zip(c2[n]['animations'], ref):
        for s, s_ref in zip(anim['directions'][0]['sprites'], anim_ref['directions'][0]['sprites']):
            z4 = next((p for p in s_ref['points'] if p['name'] == 'z4'), None)
            if z4 is None or any(p['name'] == pt for p in s['points']):
                continue
            novo = copy.deepcopy(z4)
            novo['name'] = pt
            s['points'].append(novo)
    assert any(p['name'] == pt for a in c2[n]['animations'] for s in a['directions'][0]['sprites']
               for p in s['points']), n

os.makedirs(os.path.join(patch, 'assets/data'), exist_ok=True)
json.dump(proj, open(os.path.join(patch, 'assets/data/gd_project.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(objs, open(os.path.join(patch, 'assets/data/gd_objects.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('ok: plataforma_neon, patrulha do robo_z3, pontos z5/z6/z7')
