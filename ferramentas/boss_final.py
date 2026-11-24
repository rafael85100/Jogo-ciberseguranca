#!/usr/bin/env python3
"""Mysterious (cena final): mira na diagonal, nem sempre atira, e o portal nasce no fim da arena (23/11/2026).

- Mira: no ataque de tiro, a direção é recalculada a cada quadro a partir do ponto "arma" até o
  centro do robô e encaixada em 3 opções para o lado em que o chefe está virado: reto, diagonal
  para cima ou diagonal para baixo (45°, quando o robô está a mais de 22,5° da horizontal).
  A bala guarda vx/vy (500 px/s) e gira para apontar para onde vai.
- Nem sempre atira: quando a recarga acaba, sorteia 1..100; atira se cair até
  50 + 10 * dificuldade (Normal 50%, Difícil 60%, Insano 70%). Senão, tenta de novo em 0,7 s.
  Ele continua andando atrás do robô e virado para ele o tempo todo.
- Balas do chefe que passam de 2000 px do robô ou sobem acima de y -400 são apagadas.
- Portal: quando o chefe morre, o portalF nasce no fim da arena, encostado na torre de caixas
  (x 2830; a torre começa em ~3177), e não mais no lugar do chefe.
Roda uma vez só. Uso (na pasta do projeto): python3 ferramentas/boss_final.py game.json
"""
import json, sys

PATH = sys.argv[1]
PORTAL_X = '2830'
g = json.load(open(PATH, encoding='utf-8'))
F = {l['name']: l for l in g['layouts']}['final']
O = {o['name']: o for o in F['objects']}
ev = F['events']


def I(t, *p, inv=False, sub=None):
    d = {'type': {'value': t}, 'parameters': list(p)}
    if inv:
        d['type']['inverted'] = True
    if sub is not None:
        d['subInstructions'] = sub
    return d


def E(conds=(), acts=(), events=()):
    return {'type': 'BuiltinCommonInstructions::Standard', 'conditions': list(conds), 'actions': list(acts),
            'events': list(events)}


def C(t):
    return {'type': 'BuiltinCommonInstructions::Comment', 'color': {'b': 109, 'g': 230, 'r': 255, 'textB': 0,
            'textG': 0, 'textR': 0}, 'comment': t, 'comment2': ''}


setv = lambda v, op, x: I('SetNumberVariable', v, op, x)
cmp = lambda a, op, b: I('BuiltinCommonInstructions::CompareNumbers', a, op, b)
setov = lambda o, v, op, x: I('SetNumberObjectVariable', o, v, op, x)
sig = lambda e: [(c['type']['value'], c['parameters']) for c in e.get('conditions', [])]
acts = lambda e: [(a['type']['value'], a['parameters']) for a in e.get('actions', [])]

assert not any(v['name'] == 'boss_vx' for v in F['variables']), 'script ja foi aplicado'
for n in ['boss_vx', 'boss_vy', 'sorteio_tiro']:
    F['variables'].append({'name': n, 'type': 'number', 'value': 0})
for b in ['bala_r1d', 'bala_r1d2']:
    vs = O[b].setdefault('variables', [])
    for n in ['vx', 'vy']:
        vs.append({'name': n, 'type': 'number', 'value': 0})

# 1) forca das balas vem de vx/vy
k33 = next(i for i, e in enumerate(ev) if ('AddForceXY', ['bala_r1d', '-500', '0', '']) in acts(e))
for a in ev[k33]['actions']:
    if a['type']['value'] == 'AddForceXY' and a['parameters'][0] in ('bala_r1d', 'bala_r1d2'):
        b = a['parameters'][0]
        a['parameters'] = [b, b + '.Variable(vx)', b + '.Variable(vy)', '']

# 2) mira no ataque de tiro (modo 1)
k41 = next(i for i, e in enumerate(ev) if sig(e) == [('NumberVariable', ['modo_boss', '=', '1'])])
DX = '(Player2.BoundingBoxCenterX() - Mysterious.PointX("arma"))'
DY = '(Player2.BoundingBoxCenterY() - Mysterious.PointY("arma"))'
D45 = '353.553'
mira = [
    C('Mira do chefe: reto, diagonal para cima ou para baixo (45°), para o lado em que está virado.'),
    E([], [setv('boss_vx', '=', '500'), setv('boss_vy', '=', '0')]),
    E([cmp(DY, '<', '-abs(%s) * 0.414' % DX)], [setv('boss_vx', '=', D45), setv('boss_vy', '=', '-' + D45)]),
    E([cmp(DY, '>', 'abs(%s) * 0.414' % DX)], [setv('boss_vx', '=', D45), setv('boss_vy', '=', D45)]),
    E([I('FlippableCapability::FlippableBehavior::FlippedX', 'Mysterious', 'Flippable')],
      [setv('boss_vx', '*', '-1')]),
]
subs = ev[k41]['events']
criou = 0
for e in subs:
    for a in list(e.get('actions', [])):
        if a['type']['value'] == 'Create' and a['parameters'][1] in ('bala_r1d', 'bala_r1d2'):
            b = a['parameters'][1]
            ang = 'ToDeg(atan2(boss_vy, boss_vx))' + (' - 180' if b == 'bala_r1d' else '')
            i = e['actions'].index(a)
            e['actions'][i + 1:i + 1] = [setov(b, 'vx', '=', 'boss_vx'), setov(b, 'vy', '=', 'boss_vy'),
                                         I('SetAngle', b, '=', ang)]
            criou += 1
assert criou == 2, criou
ev[k41]['events'] = mira + subs

# 3) nem sempre atira
k45 = next(i for i, e in enumerate(ev) if sig(e) == [('NumberVariable', ['modo_boss', '=', '4'])])
j = next(i for i, e in enumerate(ev[k45]['events'])
         if ('SetNumberVariable', ['atirando', '=', '1']) in acts(e))
e = ev[k45]['events'][j]
CHANCE = '50 + 10 * dificuldade'
ev[k45]['events'][j] = E(e['conditions'], [setv('sorteio_tiro', '=', 'RandomInRange(1, 100)')], [
    E([cmp('sorteio_tiro', '<=', CHANCE)], e['actions']),
    E([cmp('sorteio_tiro', '>', CHANCE)], [setv('cd_tiro', '=', '0.7')]),
])
ev[k45 - 1]['comment'] += ('. Quando a recarga acaba, só atira se o sorteio (1..100) cair até 50 + 10 * dificuldade; '
                           'senão tenta de novo em 0,7 s')

# 4) balas do chefe somem longe
k47 = next(i for i, e in enumerate(ev) if e['type'].endswith('Comment') and 'balas do Mysterious' in e['comment'])
limpa = []
for b in ['bala_r1d', 'bala_r1d2']:
    limpa.append(E([I('BuiltinCommonInstructions::Or', sub=[
        I('PosY', b, '<', '-400'), I('PosX', b, '>', 'Player2.X() + 2000'), I('PosX', b, '<', 'Player2.X() - 2000')])],
        [I('Delete', b, '')]))
ev[k47 + 1:k47 + 1] = limpa

# 5) portal no fim da arena
k59 = next(i for i, e in enumerate(ev) if ('PanelSpriteContinuousBar::PanelSpriteContinuousBar::IsEmpty',
                                          ['bar_monstro_life', '']) in sig(e))
n = 0
for a in ev[k59]['actions']:
    if a['type']['value'] == 'Create' and a['parameters'][1] == 'portalF':
        a['parameters'][2] = PORTAL_X
        n += 1
assert n == 1
ev[k59:k59] = [C('Chefe morreu: o portal aparece no fim da arena, encostado na torre de caixas (x %s).' % PORTAL_X)]

json.dump(g, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok: mira diagonal, chance de tiro 50+10*dificuldade, portal em x', PORTAL_X)
