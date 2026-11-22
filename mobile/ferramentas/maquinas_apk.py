#!/usr/bin/env python3
"""Monta a pasta de patch das maquinas geradoras (v22) para o build_assets.py.

- texturas .ctex + .import das 11 imagens de assets/image/maquina/ (copiadas do projeto de PC);
- entradas no resourceMap de assets/data/gd_project.json;
- objeto global maquina_geradora em assets/data/gd_objects.json (copiado do game.json do PC).

Uso: maquinas_apk.py base.apk game.json pasta_do_projeto_pc patch/
"""
import hashlib, io, json, os, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ctex  # noqa: E402

base_apk, game_json, pc_dir, patch = sys.argv[1:5]
z = zipfile.ZipFile(base_apk)
modelo = z.read('assets/.godot/imported/municao1.png-966b01800c84a06f41fd166211fcad67.ctex')
proj = json.loads(z.read('assets/data/gd_project.json'))
objs = json.loads(z.read('assets/data/gd_objects.json'))
g = json.load(open(game_json, encoding='utf-8'))

maq = [o for o in g['objects'] if o['name'] == 'maquina_geradora'][0]
imagens = [s['image'] for a in maq['animations'] for d in a['directions'] for s in d['sprites']]

for img in imagens:
    res = 'res://' + img
    nome = os.path.basename(img) + '-' + hashlib.md5(res.encode()).hexdigest() + '.ctex'
    destino = os.path.join(patch, 'assets/.godot/imported', nome)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    from PIL import Image
    open(destino, 'wb').write(ctex.build(modelo, Image.open(os.path.join(pc_dir, img)).convert('RGBA')))
    imp = os.path.join(patch, 'assets', img + '.import')
    os.makedirs(os.path.dirname(imp), exist_ok=True)
    open(imp, 'w').write('[remap]\n\nimporter="texture"\ntype="CompressedTexture2D"\npath="res://.godot/imported/%s"\n'
                         'metadata={\n"vram_texture": false\n}\n' % nome)
    proj['resourceMap'][img] = res

d = json.loads(json.dumps(maq))
d['_default_size'] = [120, 150]
d['_godot_script'] = 'gd_sprite.gd'
objs['_global']['maquina_geradora'] = d

os.makedirs(os.path.join(patch, 'assets/data'), exist_ok=True)
json.dump(proj, open(os.path.join(patch, 'assets/data/gd_project.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(objs, open(os.path.join(patch, 'assets/data/gd_objects.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('imagens:', len(imagens))
