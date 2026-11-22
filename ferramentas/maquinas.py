#!/usr/bin/env python3
"""Maquinas geradoras de inimigos nas fases 1 e 2 (pedido de 21/11/2026).

Mesma quantidade de inimigos, mas eles saem de uma maquina (uma por area). Quando o robo chega
perto (a maquina entra na tela), ela solta o grupo todo de uma vez e cada inimigo vai para o seu
ponto de sempre (a posicao da instancia na cena); la ele volta a patrulhar normalmente.

- Fase 1: 1 maquina com os 3 drones.
- Fase 2: 3 maquinas, com 3 + 3 + 4 robos.

Como funciona (eventos gerados por este script, no inicio de cada cena):
- no comeco, cada inimigo guarda o ponto dele (home_x, home_y), desliga a patrulha
  (TimedBackAndForthMirroredMovement) e fica guardado longe da fase (y = -20000);
- quando Player2.X() > maquina.X() - 650 (e depois de 1 s de fase), a maquina toca a animacao
  "gerando" e solta o grupo: drones saem do nucleo, robos saem da maquina no nivel do chao;
- cada inimigo vai ate o ponto dele com tween ("saida", easeOutQuad, 550 px/s, no minimo 0,7 s);
  ao chegar, a patrulha volta e o espelhamento volta ao original;
- 1,3 s depois a maquina fica "desligada".

Imagens: ferramentas/maquina_geradora.py. Roda uma vez so: python3 ferramentas/maquinas.py game.json
"""
import json, sys, uuid

PATH = sys.argv[1]
g = json.load(open(PATH, encoding='utf-8'))
L = {l['name']: l for l in g['layouts']}
assert not any(o['name'] == 'maquina_geradora' for o in g['objects']), 'script ja foi aplicado'

PATRULHA = 'TimedBackAndForthMirroredMovement'
NUCLEO = (60, 78)          # centro do nucleo na imagem (120x150)
VEL, MIN_T = 550, 0.7      # velocidade de saida (px/s) e duracao minima do tween
GATILHO = 650              # a maquina solta quando o robo esta a menos disso (entra na tela)

# (cena, centro x da maquina, base y, inimigos, voam?)
MAQUINAS = [
    ('cena1', 2650, 532, ['drone2', 'drone3', 'drone4'], True),
    ('cena2', 560, 538, ['robo_z', 'robo_z2', 'robo_z3'], False),
    ('cena2', 2100, 538, ['robo_z4', 'robo_z5', 'robo_z6'], False),
    ('cena2', 4330, 538, ['robo_z7', 'robo_a', 'robo_a2', 'robo_a3'], False),
]


def I(t, *params, inv=False):
    d = {'type': {'value': t}, 'parameters': [str(p) for p in params]}
    if inv:
        d['type']['inverted'] = True
    return d


def E(conds=(), acts=(), events=()):
    return {'type': 'BuiltinCommonInstructions::Standard', 'conditions': list(conds),
            'actions': list(acts), 'events': list(events)}


def C(text):
    return {'type': 'BuiltinCommonInstructions::Comment', 'color': {'b': 109, 'g': 230, 'r': 255,
            'textB': 0, 'textG': 0, 'textR': 0}, 'comment': text, 'comment2': ''}


nov = lambda o, v, op, x: I('NumberObjectVariable', o, v, op, x)
setov = lambda o, v, op, x: I('SetNumberObjectVariable', o, v, op, x)
cmp = lambda a, op, b: I('BuiltinCommonInstructions::CompareNumbers', a, op, b)
anim = lambda o, i: I('AnimatableCapability::AnimatableBehavior::SetIndex', o, 'Animation', '=', i)
flip = lambda o, yes: I('FlippableCapability::FlippableBehavior::FlipX', o, 'Flippable', 'yes' if yes else 'no')
flipped = lambda o, inv=False: I('FlippableCapability::FlippableBehavior::FlippedX', o, 'Flippable', inv=inv)
setxy = lambda o, x, y: I('SetXY', o, '=', x, '=', y)
ativa = lambda o, yes: I('ActivateBehavior', o, PATRULHA, 'yes' if yes else 'no')


def declare(o, name, value=0):
    vs = o.setdefault('variables', [])
    if not any(v['name'] == name for v in vs):
        vs.append({'name': name, 'type': 'number', 'value': value})


# ---------- objeto global: maquina_geradora ----------
def quadro(img):
    return {'hasCustomCollisionMask': True, 'image': img, 'points': [
                {'name': 'nucleo', 'x': NUCLEO[0], 'y': NUCLEO[1]}],
            'originPoint': {'name': 'origine', 'x': 0, 'y': 0},
            'centerPoint': {'automatic': True, 'name': 'centre', 'x': 0, 'y': 0},
            'customCollisionMask': [[{'x': 6, 'y': 12}, {'x': 114, 'y': 12}, {'x': 114, 'y': 147}, {'x': 6, 'y': 147}]]}


anims = []
for nome, n, tbf, loop in [('ligada', 4, 0.18, True), ('gerando', 6, 0.07, True), ('desligada', 1, 0.1, False)]:
    imgs = ['assets/image/maquina/%s%d.png' % (nome, i) for i in range(n)] if n > 1 else ['assets/image/maquina/%s.png' % nome]
    for f in imgs:
        g['resources']['resources'].append({'file': f, 'kind': 'image', 'metadata': '', 'name': f,
                                            'smoothed': False, 'userAdded': True})
    anims.append({'name': nome, 'useMultipleDirections': False, 'directions': [{
        'looping': loop, 'timeBetweenFrames': tbf, 'sprites': [quadro(f) for f in imgs]}]})
g['objects'].append({'adaptCollisionMaskAutomatically': False, 'assetStoreId': '', 'name': 'maquina_geradora',
                     'persistentUuid': str(uuid.uuid4()), 'type': 'Sprite', 'updateIfNotVisible': False,
                     'variables': [{'name': 'grupo', 'type': 'number', 'value': 0},
                                   {'name': 'estado', 'type': 'number', 'value': 0}],
                     'effects': [], 'behaviors': [], 'animations': anims})
g['objectsFolderStructure']['children'].append({'objectName': 'maquina_geradora'})

# ---------- por cena ----------
por_cena = {}
for k, (cena, cx, base, inimigos, voa) in enumerate(MAQUINAS):
    por_cena.setdefault(cena, []).append((k + 1, cx, base, inimigos, voa))

for cena, maqs in por_cena.items():
    lay = L[cena]
    objs = {o['name']: o for o in lay['objects']}
    inicio, gatilhos, chegada = [], [], []
    for grupo, cx, base, inimigos, voa in maqs:
        lay['instances'].append({
            'angle': 0, 'customSize': False, 'depth': 0, 'height': 0, 'keepRatio': True, 'layer': '',
            'name': 'maquina_geradora', 'persistentUuid': str(uuid.uuid4()), 'width': 0,
            'x': cx - 60, 'y': base - 150, 'zOrder': 8, 'numberProperties': [], 'stringProperties': [],
            'initialVariables': [{'name': 'grupo', 'type': 'number', 'value': grupo}]})
        saida = []
        for n in inimigos:
            o = objs[n]
            for v in ['home_x', 'home_y', 'estado', 'flip0']:
                declare(o, v)
            if not any(b['type'] == 'Tween::TweenBehavior' for b in o['behaviors']):
                o['behaviors'].append({'name': 'Tween', 'type': 'Tween::TweenBehavior'})
            patrulha = any(b['name'] == PATRULHA for b in o['behaviors'])
            inicio.append(E([], [setov(n, 'home_x', '=', n + '.X()'), setov(n, 'home_y', '=', n + '.Y()'),
                                 setov(n, 'estado', '=', '0')] +
                            ([ativa(n, False)] if patrulha else []) +
                            [setxy(n, n + '.X()', '-20000')],
                            [E([flipped(n)], [setov(n, 'flip0', '=', '1')])]))
            # saida: drones do nucleo, robos do pe da maquina no nivel do chao deles
            x0 = 'maquina_geradora.PointX("nucleo") - %s.Width() / 2' % n
            y0 = ('maquina_geradora.PointY("nucleo") - %s.Height() / 2' % n) if voa else (n + '.Variable(home_y)')
            dur = 'max(%s, abs(%s.Variable(home_x) - %s.X()) / %d)' % (MIN_T, n, n, VEL)
            saida.append(E([], [setxy(n, x0, y0), setov(n, 'estado', '=', '1'),
                                I('Tween::TweenBehavior::AddObjectPositionTween2', n, 'Tween', '"saida"',
                                  n + '.Variable(home_x)', n + '.Variable(home_y)', '"easeOutQuad"', dur, '')], [
                E([cmp(n + '.Variable(home_x)', '<', n + '.X()')], [flip(n, True)]),
                E([cmp(n + '.Variable(home_x)', '>=', n + '.X()')], [flip(n, False)]),
            ]))
            chegada.append(E([nov(n, 'estado', '=', '1'), I('Tween::HasFinished', n, 'Tween', '"saida"')],
                             [setov(n, 'estado', '=', '2')] + ([ativa(n, True)] if patrulha else []), [
                E([nov(n, 'flip0', '=', '1')], [flip(n, True)]),
                E([nov(n, 'flip0', '=', '0')], [flip(n, False)]),
            ]))
        gatilhos.append(E([nov('maquina_geradora', 'grupo', '=', str(grupo)),
                           nov('maquina_geradora', 'estado', '=', '0'),
                           cmp('TimeFromStart()', '>', '1'),
                           cmp('Player2.X()', '>', 'maquina_geradora.X() - %d' % GATILHO)],
                          [setov('maquina_geradora', 'estado', '=', '1'), anim('maquina_geradora', '1'),
                           I('PlaySound', '', 'bzzzt.wav', '', '80', '0.6'),
                           I('Create', '', 'RedExplosion', 'maquina_geradora.PointX("nucleo")',
                             'maquina_geradora.PointY("nucleo")', '')],
                          saida + [E([], [I('Wait', '1.3'), anim('maquina_geradora', '2'),
                                          setov('maquina_geradora', 'estado', '=', '2'),
                                          I('Delete', 'RedExplosion', '')])]))
    eventos = [C('Máquinas geradoras (ferramentas/maquinas.py): os inimigos começam guardados e saem da máquina '
                 'do grupo deles quando o robô chega perto; depois vão para o ponto de sempre e voltam a patrulhar.'),
               E([I('SceneJustBegins', '')], [anim('maquina_geradora', '0')], inicio)] + gatilhos + chegada
    lay['events'][0:0] = eventos
    print(cena, 'maquinas:', len(maqs), 'inimigos:', sum(len(m[3]) for m in maqs))

json.dump(g, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok')
