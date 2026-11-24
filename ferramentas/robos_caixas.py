#!/usr/bin/env python3
"""Robôs da fase 2 não atravessam mais as caixas (bloco) (23/11/2026).

Os robôs andam com a patrulha TimedBackAndForthMirroredMovement, que só move em X e vira quando
chega à distância configurada; ela não tem colisão. Para cada robô com patrulha na cena2:
- se encostar numa caixa depois de sair da máquina geradora (estado 2), é separado dela
  (SeparateFromObjects, a caixa não se mexe);
- e passa a andar para o lado oposto ao da caixa (a direção da patrulha é o espelhamento:
  espelhado = anda para a esquerda).
Durante a saída da máquina (tween "saida", estado 1) nada muda, para não brigar com o tween.
Roda uma vez só. Uso (na pasta do projeto): python3 ferramentas/robos_caixas.py game.json
"""
import json, sys

PATH = sys.argv[1]
PATRULHA = 'TimedBackAndForthMirroredMovement'
g = json.load(open(PATH, encoding='utf-8'))
C = {l['name']: l for l in g['layouts']}['cena2']
O = {o['name']: o for o in C['objects']}
MARCA = 'Robôs não atravessam as caixas'
assert not any(e.get('comment', '').startswith(MARCA) for e in C['events']), 'script ja foi aplicado'


def I(t, *p):
    return {'type': {'value': t}, 'parameters': list(p)}


def E(conds, acts, events=()):
    return {'type': 'BuiltinCommonInstructions::Standard', 'conditions': conds, 'actions': acts,
            'events': list(events)}


robos = [n for n, o in O.items() if n.startswith('robo_') and any(b['name'] == PATRULHA for b in o['behaviors'])]
robos.sort()
novos = [{'type': 'BuiltinCommonInstructions::Comment', 'color': {'b': 109, 'g': 230, 'r': 255, 'textB': 0,
          'textG': 0, 'textR': 0}, 'comment': MARCA + ': encostou numa caixa (bloco) depois de sair da máquina, '
          'é separado dela e passa a patrulhar para o lado oposto (espelhado = anda para a esquerda).',
          'comment2': ''}]
for n in robos:
    flip = lambda yes: I('FlippableCapability::FlippableBehavior::FlipX', n, 'Flippable', 'yes' if yes else 'no')
    cx = n + '.BoundingBoxCenterX()'
    novos.append(E([I('CollisionNP', n, 'bloco', '', '', ''), I('NumberObjectVariable', n, 'estado', '=', '2')],
                   [I('SeparateFromObjects', n, 'bloco', 'no')], [
        E([I('BuiltinCommonInstructions::CompareNumbers', cx, '<', 'bloco.BoundingBoxCenterX()')], [flip(True)]),
        E([I('BuiltinCommonInstructions::CompareNumbers', cx, '>=', 'bloco.BoundingBoxCenterX()')], [flip(False)]),
    ]))
C['events'].extend(novos)
json.dump(g, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok: %d robos com colisao nas caixas: %s' % (len(robos), ', '.join(robos)))
