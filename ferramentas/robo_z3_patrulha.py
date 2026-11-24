#!/usr/bin/env python3
"""O robo_z3 da fase 2 ficava parado: no projeto original ele nunca teve o comportamento de
patrulha (TimedBackAndForthMirroredMovement), que todos os outros robo_z têm (23/11/2026).

- Copia a patrulha do robo_z2 (distância 350) com velocidade 105 (entre os 100 e 110 dos vizinhos).
- Como os outros robôs das máquinas geradoras, a patrulha fica desligada enquanto ele está guardado
  (evento do início) e liga quando o tween "saida" termina (evento de chegada).
Roda uma vez só. Uso (na pasta do projeto): python3 ferramentas/robo_z3_patrulha.py game.json
"""
import copy, json, sys

PATH = sys.argv[1]
PATRULHA = 'TimedBackAndForthMirroredMovement'
g = json.load(open(PATH, encoding='utf-8'))
C = {l['name']: l for l in g['layouts']}['cena2']
O = {o['name']: o for o in C['objects']}
z3 = O['robo_z3']
assert not any(b['name'] == PATRULHA for b in z3['behaviors']), 'script ja foi aplicado'

b = copy.deepcopy(next(b for b in O['robo_z2']['behaviors'] if b['name'] == PATRULHA))
b['Speed'] = 105
z3['behaviors'].insert(0, b)


def ativa(yes):
    return {'type': {'value': 'ActivateBehavior'}, 'parameters': ['robo_z3', PATRULHA, 'yes' if yes else 'no']}


def walk(evs):
    for e in evs:
        yield e
        yield from walk(e.get('events', []))


ini = che = 0
for e in walk(C['events']):
    acts = e.get('actions', [])
    conds = e.get('conditions', [])
    tipos = [(a['type']['value'], a['parameters'][:2]) for a in acts]
    # inicio: guarda home_x/home_y/estado e manda para y -20000
    if ('SetNumberObjectVariable', ['robo_z3', 'home_x']) in tipos and not conds:
        k = next(i for i, a in enumerate(acts) if a['type']['value'] == 'SetXY')
        acts.insert(k, ativa(False))
        ini += 1
    # chegada: estado 1 + tween "saida" terminou
    if any(c['type']['value'] == 'Tween::HasFinished' and c['parameters'][0] == 'robo_z3' for c in conds):
        acts.append(ativa(True))
        che += 1
assert ini == 1 and che == 1, (ini, che)

json.dump(g, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok: robo_z3 com patrulha (velocidade 105, distancia %s)' % b.get('Distance'))
