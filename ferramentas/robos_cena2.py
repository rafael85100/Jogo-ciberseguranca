#!/usr/bin/env python3
"""Corrige bugs dos robôs da fase 2 que vieram do projeto original (23/11/2026).

O APK já tinha essas correções desde a v7 (ver mobile/LEIAME.md); aqui elas chegam ao PC.
- barZ4 (HP do robo_z4) pegava o Y do robo_z2: quando o robo_z2 morria, a barra ia para y 0,
  fora da tela, e o HP do robo_z4 sumia.
- robo_z5, robo_z6 e robo_z7 não tinham o ponto da barra (z5/z6/z7). O GDevelop usa a origem,
  então a barra ficava solta no canto de cima do quadro (do lado direito quando o robô vira).
  Os pontos novos usam as coordenadas do ponto z4 do robo_z4 (mesmas imagens).
- Quando o HP do robo_z7 acabava, o evento apagava o robo_z (o primeiro robô) em vez do robo_z7.
- A morte do robo_a3 tocava a animação no robo_a.
Roda uma vez só. Uso (na pasta do projeto): python3 ferramentas/robos_cena2.py game.json
"""
import copy, json, sys

PATH = sys.argv[1]
g = json.load(open(PATH, encoding='utf-8'))
L = {l['name']: l for l in g['layouts']}
X = {x['name']: x for x in g['externalEvents']}
feito = []

# 1) barZ4 usa o proprio robo_z4
for e in X['ex_robo']['events']:
    for a in e.get('actions', []):
        if a['type']['value'] == 'SetXY' and a['parameters'][0] == 'barZ4' and 'robo_z2.PointY("z4")' in a['parameters'][4]:
            a['parameters'][4] = 'robo_z4.PointY("z4")'
            feito.append('barZ4 -> robo_z4')

# 2) pontos z5/z6/z7 (cena2 e cena3, que tambem declara esses objetos)
for cena in ['cena2', 'cena3']:
    O = {o['name']: o for o in L[cena]['objects']}
    if 'robo_z4' not in O:
        continue
    ref = O['robo_z4']['animations']
    for n, pt in [('robo_z5', 'z5'), ('robo_z6', 'z6'), ('robo_z7', 'z7')]:
        if n not in O:
            continue
        for anim, anim_ref in zip(O[n]['animations'], ref):
            for s, s_ref in zip(anim['directions'][0]['sprites'], anim_ref['directions'][0]['sprites']):
                if any(p['name'] == pt for p in s['points']):
                    continue
                z4 = next((p for p in s_ref['points'] if p['name'] == 'z4'), None)
                if z4 is None:
                    continue
                novo = copy.deepcopy(z4)
                novo['name'] = pt
                s['points'].append(novo)
        if any(p['name'] == pt for a in O[n]['animations'] for s in a['directions'][0]['sprites'] for p in s['points']):
            feito.append('%s: ponto %s (%s)' % (n, pt, cena))

# 3) morte do robo_z7 apaga o robo_z7
for e in X['ex_robo']['events']:
    cs = e.get('conditions', [])
    if cs and cs[0]['type']['value'].endswith('IsEmpty') and cs[0]['parameters'][0] == 'barZ7':
        for a in e['actions']:
            if a['type']['value'] == 'Delete' and a['parameters'][0] == 'robo_z':
                a['parameters'][0] = 'robo_z7'
                feito.append('morte do robo_z7 apaga o robo_z7')

# 4) morte do robo_a3 anima o robo_a3
for e in X['ex_robo_tiros']['events']:
    cs = e.get('conditions', [])
    if cs and cs[0]['type']['value'].endswith('IsEmpty') and cs[0]['parameters'][0] == 'barv3':
        for a in e['actions']:
            if a['type']['value'].endswith('SetIndex') and a['parameters'][0] == 'robo_a':
                a['parameters'][0] = 'robo_a3'
                feito.append('morte do robo_a3 anima o robo_a3')

assert len(feito) >= 6, feito
json.dump(g, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('\n'.join(feito))
