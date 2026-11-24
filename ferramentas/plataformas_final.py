#!/usr/bin/env python3
"""Plataformas na arena do chefe (cena final) e escudo na tecla C (23/11/2026).

- Desenha assets/image/plataforma_neon.png (pixel art, 72x12 px ampliado 3x = 216x36, contorno (18,14,28)).
- Cria o objeto plataforma_neon na cena final, com comportamento Platform do tipo Jumpthru
  (atravessa por baixo e segura por cima), e 4 instancias alternando baixa (topo y 555) e alta (topo y 445).
  O chao fica em y ~665 e o pulo do robo chega a 140 px, entao cada degrau tem 110 px.
  O Mysterious (PlatformerObject, pula 650) tambem sobe nelas quando o robo esta acima.
- Escudo: a tecla D passa a ser "andar para a direita" (WASD), entao o escudo vai para C (cena3 e final).
Roda uma vez so. Uso (na pasta do projeto): python3 ferramentas/plataformas_final.py game.json
"""
import json, sys, uuid
from PIL import Image

PATH = sys.argv[1]
IMG = 'assets/image/plataforma_neon.png'
W, H, K = 72, 12, 3
POS = [(480, 555), (760, 445), (1040, 555), (1320, 445)]

# ---------- imagem ----------
OUT = (18, 14, 28, 255)
NEON1, NEON2 = (130, 240, 255, 255), (60, 165, 235, 255)
METAL, METAL_ESC, JUNTA = (46, 40, 70, 255), (30, 26, 48, 255), (24, 20, 38, 255)
BRILHO = (72, 64, 104, 255)
ROSA, ROSA_ESC = (255, 70, 200, 255), (150, 40, 130, 255)
ROXO = (140, 80, 255, 255)

im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
px = im.load()
for x in range(W):
    for y in range(H):
        if (x in (0, W - 1)) and y in (0, H - 1):
            continue  # cantos arredondados
        if x in (0, W - 1) or y in (0, H - 1):
            c = OUT
        elif y == 1:
            c = NEON1
        elif y == 2:
            c = NEON2
        elif y == 3:
            c = BRILHO
        elif y <= 8:
            c = METAL
        elif y == 9:
            c = METAL_ESC
        else:
            c = ROXO if 2 <= x <= W - 3 and x % 4 != 0 else METAL_ESC
        px[x, y] = c
for x in range(12, W - 1, 12):  # juntas das placas
    for y in range(3, 10):
        px[x, y] = JUNTA
for i, x in enumerate(range(6, W - 1, 12)):  # luzes do painel
    c = ROSA if i % 2 == 0 else NEON2
    px[x, 5] = px[x + 1, 5] = c
    px[x, 6] = px[x + 1, 6] = ROSA_ESC if i % 2 == 0 else (30, 90, 150, 255)
for x in (3, W - 4):  # rebites
    px[x, 4] = px[x, 8] = BRILHO
im.resize((W * K, H * K), Image.NEAREST).save(IMG)

# ---------- game.json ----------
g = json.load(open(PATH, encoding='utf-8'))
L = {l['name']: l for l in g['layouts']}
F = L['final']
assert not any(o['name'] == 'plataforma_neon' for o in F['objects']), 'script ja foi aplicado'

rs = g['resources']['resources']
if not any(r['name'] == IMG for r in rs):
    rs.append({'file': IMG, 'kind': 'image', 'metadata': '', 'name': IMG, 'smoothed': False, 'userAdded': True})

w, h = W * K, H * K
F['objects'].append({
    'adaptCollisionMaskAutomatically': False, 'assetStoreId': '', 'name': 'plataforma_neon',
    'persistentUuid': str(uuid.uuid4()), 'type': 'Sprite', 'updateIfNotVisible': False,
    'variables': [], 'effects': [],
    'behaviors': [{'name': 'Platform', 'type': 'PlatformBehavior::PlatformBehavior', 'canBeGrabbed': False,
                   'platformType': 'Jumpthru', 'yGrabOffset': 0}],
    'animations': [{'name': '', 'useMultipleDirections': False, 'directions': [{
        'looping': False, 'timeBetweenFrames': 0.08, 'sprites': [{
            'hasCustomCollisionMask': True, 'image': IMG, 'points': [],
            'originPoint': {'name': 'origine', 'x': 0, 'y': 0},
            'centerPoint': {'automatic': True, 'name': 'centre', 'x': 0, 'y': 0},
            'customCollisionMask': [[{'x': 0, 'y': 0}, {'x': w, 'y': 0}, {'x': w, 'y': h}, {'x': 0, 'y': h}]]}]}]}]})
F['objectsFolderStructure']['children'].append({'objectName': 'plataforma_neon'})
for x, y in POS:
    F['instances'].append({'angle': 0, 'customSize': False, 'depth': 0, 'height': 0, 'keepRatio': True,
                           'layer': '', 'name': 'plataforma_neon', 'persistentUuid': str(uuid.uuid4()),
                           'width': 0, 'x': x, 'y': y, 'zOrder': 8, 'numberProperties': [],
                           'stringProperties': [], 'initialVariables': []})


# ---------- escudo: D -> C ----------
def walk(evs):
    for e in evs:
        yield e
        yield from walk(e.get('events', []))


trocas = 0
for cena in ['cena3', 'final']:
    for e in walk(L[cena]['events']):
        for c in e.get('conditions', []):
            if c['type']['value'] == 'KeyFromTextPressed' and c['parameters'][1] == '"d"':
                c['parameters'][1] = '"c"'
                trocas += 1
        if e['type'].endswith('Comment') and 'D cria o escudo' in e.get('comment', ''):
            e['comment'] = e['comment'].replace('D cria o escudo', 'C cria o escudo')
assert trocas == 2, trocas

json.dump(g, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok: 4 plataformas na final, escudo em C (%d eventos)' % trocas)
