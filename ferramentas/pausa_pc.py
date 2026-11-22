#!/usr/bin/env python3
"""Pausa nas fases e botao para voltar ao menu, como no APK v21 (depois de ferramentas/v21_pc.py).

- Desenha assets/image/pausa_botao.png (botao II neon, 72x72) e assets/image/pausa_tela.png
  (1280x720: fundo escurecido, PAUSADO, CONTINUAR e MENU PRINCIPAL), no estilo dos botoes do APK.
- Cria os objetos globais pausa_botao e pausa_tela.
- Troca o codigo dos eventos JavaScript do controle por ferramentas/controle_pausa.js.
Pode rodar de novo (so atualiza imagens e o JS). Uso (na pasta do projeto): python3 ferramentas/pausa_pc.py game.json
"""
import json, os, sys, uuid
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PATH = sys.argv[1]
FONTE = 'assets/Roboto-Regular.ttf'
C_FILL = (13, 18, 56, 199)
C_GLOW = (64, 140, 255, 90)
C_EDGE = (89, 184, 255, 255)
C_INNER = (140, 97, 255, 242)
C_ICON = (184, 230, 255, 255)
C_TEXT = (242, 250, 255, 255)
C_SHADOW = (5, 5, 26, 230)


def octo(cx, cy, hw, hh, k):
    return [(cx - hw + k, cy - hh), (cx + hw - k, cy - hh), (cx + hw, cy - hh + k), (cx + hw, cy + hh - k),
            (cx + hw - k, cy + hh), (cx - hw + k, cy + hh), (cx - hw, cy + hh - k), (cx - hw, cy - hh + k)]


def painel(im, cx, cy, hw, hh):
    k = min(hw, hh) * 0.36
    glow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).line(octo(cx, cy, hw + 4, hh + 4, k + 1.6) + [octo(cx, cy, hw + 4, hh + 4, k + 1.6)[0]],
                              fill=C_GLOW, width=9, joint='curve')
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(2)))
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon(octo(cx, cy, hw, hh, k), fill=C_FILL)
    p = octo(cx, cy, hw, hh, k)
    d.line(p + [p[0]], fill=C_EDGE, width=4, joint='curve')
    q = octo(cx, cy, hw - 7, hh - 7, k - 2.8)
    d.line(q + [q[0]], fill=C_INNER, width=2, joint='curve')
    d.line((cx - hw + k + 4, cy - hh + 3.5, cx + hw - k - 4, cy - hh + 3.5), fill=(204, 242, 255, 140), width=2)
    im.alpha_composite(lay)


def texto(im, cx, cy, t, tam, cor):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONTE, tam)
    d.text((cx, cy), t, font=f, fill=cor, anchor='mm', stroke_width=3, stroke_fill=C_SHADOW)


# botao II (centro em 36,36; raio do APK 34 * 0.85)
b = Image.new('RGBA', (72, 72), (0, 0, 0, 0))
r = 34 * 0.85
painel(b, 36, 36, r, r)
s = r * 2
bw, bh = s * 0.14, s * 0.5
d = ImageDraw.Draw(b)
d.rectangle((36 - bw * 1.7, 36 - bh * 0.5, 36 - bw * 0.7, 36 + bh * 0.5), fill=C_ICON)
d.rectangle((36 + bw * 0.7, 36 - bh * 0.5, 36 + bw * 1.7, 36 + bh * 0.5), fill=C_ICON)
b.save('assets/image/pausa_botao.png')

# tela de pausa
t = Image.new('RGBA', (1280, 720), (3, 0, 20, 179))
texto(t, 640, 240, 'PAUSADO', 52, C_EDGE)
for (x, y, w, h), rot in [((490, 300, 300, 70), 'CONTINUAR'), ((490, 400, 300, 70), 'MENU PRINCIPAL')]:
    painel(t, x + w / 2, y + h / 2, w / 2, h / 2)
    texto(t, x + w / 2, y + h / 2, rot, 26, C_TEXT)
ImageDraw.Draw(t).text((640, 520), '↑ ↓ escolhe   ·   Enter ou Espaço confirma   ·   Esc ou P continua   ·   M vai ao menu',
                       font=ImageFont.truetype(FONTE, 16), fill=(184, 189, 204, 255), anchor='mm')
t.save('assets/image/pausa_tela.png')

# destaque da opcao escolhida (por cima do botao de 300x70, com 20 px de margem)
sel = Image.new('RGBA', (340, 110), (0, 0, 0, 0))
k = 35 * 0.36
glow = Image.new('RGBA', sel.size, (0, 0, 0, 0))
o = octo(170, 55, 156, 41, k + 3)
ImageDraw.Draw(glow).line(o + [o[0]], fill=(255, 200, 80, 200), width=10, joint='curve')
sel.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4)))
ImageDraw.Draw(sel).line(o + [o[0]], fill=(255, 214, 102, 255), width=3, joint='curve')
sel.save('assets/image/pausa_sel.png')

# ---------- game.json ----------
g = json.load(open(PATH, encoding='utf-8'))
JS = open(os.path.join(os.path.dirname(__file__), 'controle_pausa.js'), encoding='utf-8').read()
JA = {o['name'] for o in g['objects']}
RES = {r['name'] for r in g['resources']['resources']}


def sprite(name, image, w, h, mask):
    return {'adaptCollisionMaskAutomatically': False, 'assetStoreId': '', 'name': name,
            'persistentUuid': str(uuid.uuid4()), 'type': 'Sprite', 'updateIfNotVisible': False,
            'variables': [], 'effects': [], 'behaviors': [],
            'animations': [{'name': '', 'useMultipleDirections': False, 'directions': [{
                'looping': False, 'timeBetweenFrames': 0.08, 'sprites': [{
                    'hasCustomCollisionMask': True, 'image': image, 'points': [],
                    'originPoint': {'name': 'origine', 'x': 0, 'y': 0},
                    'centerPoint': {'automatic': True, 'name': 'centre', 'x': 0, 'y': 0},
                    'customCollisionMask': [[{'x': 0, 'y': 0}, {'x': mask, 'y': 0},
                                             {'x': mask, 'y': mask}, {'x': 0, 'y': mask}]]}]}]}]}


for f in ['assets/image/pausa_botao.png', 'assets/image/pausa_tela.png', 'assets/image/pausa_sel.png']:
    if f in RES:
        continue
    g['resources']['resources'].append({'file': f, 'kind': 'image', 'metadata': '', 'name': f,
                                        'smoothed': True, 'userAdded': True})
for n, w, h in [('pausa_botao', 72, 72), ('pausa_tela', 1280, 720), ('pausa_sel', 340, 110)]:
    if n in JA:
        continue
    g['objects'].append(sprite(n, 'assets/image/%s.png' % n, w, h, 1))
    g['objectsFolderStructure']['children'].append({'objectName': n})

trocados = 0


def troca(evs):
    global trocados
    for e in evs:
        if e['type'] == 'BuiltinCommonInstructions::JsCode' and '_cyberSentinelPad' in e['inlineCode']:
            e['inlineCode'] = JS
            trocados += 1
        troca(e.get('events', []))


for l in g['layouts']:
    troca(l['events'])
for x in g['externalEvents']:
    troca(x['events'])
assert trocados == 3, trocados
json.dump(g, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok, eventos JS trocados:', trocados)
