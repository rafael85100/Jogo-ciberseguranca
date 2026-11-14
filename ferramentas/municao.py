"""Sistema de munição do Cyber Sentinel (13/11/2026).

- Pente de 12 balas; recarga de 1,2 s (tecla R ou automática quando o pente esvazia).
- Reserva inicial: Normal 36, Difícil 24. Caixa de munição: Normal +24, Difícil +30 (máx. 96).
- Caixas (objeto global `Municao`) ficam em pontos fixos de cada cena; no início da cena
  sobra só um sorteio delas: Normal mais, Difícil menos.
- Insano: balas infinitas, sem caixas e sem contador.
- Rede de segurança: com pente e reserva zerados, o robô gera 6 balas a cada 5 s (Normal)
  ou 8 s (Difícil), para a fase nunca travar.

Uso: python3 ferramentas/municao.py game.json
"""
import json, sys, uuid

PENTE = 12
GJ = sys.argv[1]
g = json.load(open(GJ))
if any(o['name'] == 'Municao' for o in g['objects']):
    sys.exit('o sistema de munição já foi aplicado neste game.json')

# ---------------------------------------------------------------- recursos
FRAMES = [f'assets/image/municao/municao{i}.png' for i in range(1, 10)]
names = {r['name'] for r in g['resources']['resources']}
for f in FRAMES:
    if f not in names:
        g['resources']['resources'].append({"file": f, "kind": "image", "metadata": "{\"extension\":\".png\"}",
                                            "name": f, "smoothed": False, "userAdded": True})

# ---------------------------------------------------------------- variáveis globais
gv = {v['name'] for v in g['variables']}
for n, v in [('dificuldade', 0), ('pente', PENTE), ('reserva', 36), ('recarga', 0),
             ('emergencia', 0), ('n_recarga', 0), ('alvo_municao', 0)]:
    if n not in gv:
        g['variables'].append({"name": n, "type": "number", "value": v})

# ---------------------------------------------------------------- objetos globais
def U(): return str(uuid.uuid4())
glob = {o['name']: o for o in g['objects']}
seq = list(range(9)) + list(range(7, 0, -1))  # vai e volta: brilho pulsa sem salto
if 'Municao' not in glob:
    g['objects'].append({
        "adaptCollisionMaskAutomatically": True, "assetStoreId": "", "name": "Municao",
        "persistentUuid": U(), "type": "Sprite", "updateIfNotVisible": False,
        "variables": [], "effects": [], "behaviors": [],
        "animations": [{"name": "brilho", "useMultipleDirections": False, "directions": [{
            "looping": True, "timeBetweenFrames": 0.07,
            "sprites": [{"hasCustomCollisionMask": False, "image": FRAMES[i], "points": [],
                         "originPoint": {"name": "origine", "x": 0, "y": 0},
                         "centerPoint": {"automatic": True, "name": "centre", "x": 0, "y": 0},
                         "customCollisionMask": []} for i in seq]}]}]})
if 'txt_municao' not in glob:
    g['objects'].append({
        "assetStoreId": "", "bold": False, "italic": False, "name": "txt_municao", "persistentUuid": U(),
        "smoothed": True, "type": "TextObject::Text", "underlined": False, "variables": [],
        "effects": [{"effectType": "Outline", "name": "Effect", "doubleParameters": {"padding": 0, "thickness": 2},
                     "stringParameters": {"color": "0;0;0"}, "booleanParameters": {}}],
        "behaviors": [], "string": "12 / 36", "font": "STAR7.ttf", "textAlignment": "left",
        "characterSize": 16, "color": {"b": 35, "g": 196, "r": 255},
        "content": {"bold": False, "isOutlineEnabled": False, "isShadowEnabled": False, "italic": False,
                    "outlineColor": "255;255;255", "outlineThickness": 2, "shadowAngle": 90,
                    "shadowBlurRadius": 2, "shadowColor": "0;0;0", "shadowDistance": 4, "shadowOpacity": 127,
                    "smoothed": True, "underlined": False, "text": "12 / 36", "font": "STAR7.ttf",
                    "textAlignment": "left", "verticalTextAlignment": "top", "characterSize": 16,
                    "lineHeight": 0, "color": "255;196;35"}})
    # pasta de objetos (só para aparecer organizado no editor)
    fs = g.get('objectsFolderStructure', {}).get('children')
    if isinstance(fs, list):
        for n in ('Municao', 'txt_municao'):
            if not any(c.get('objectName') == n for c in fs):
                fs.append({"objectName": n})

# ---------------------------------------------------------------- pontos das caixas por cena
# (x, y) = canto superior esquerdo da caixa (64x66), apoiada no chão ou no topo de um bloco.
CAIXA_H = 66
def chao(x, top): return (x, top - CAIXA_H)
def bloco(bx, by, bw, bh):  # topo da colisão do bloco = 73/500 da altura
    return (round(bx + bw / 2 - 32), round(by + bh * 73 / 500) - CAIXA_H)

SPOTS = {
    'cena1': dict(n=2, d=1, pts=[bloco(1944, 368, 193, 192), chao(2500, 528), chao(3260, 528),
                                 bloco(3693, 370, 193, 192), chao(4700, 528)]),
    'cena2': dict(n=7, d=6, pts=[chao(700, 534), chao(1330, 534), chao(1950, 534), bloco(2657, 373, 193, 192),
                                 chao(3300, 534), bloco(4064, 385, 193, 192), chao(4760, 534), chao(5560, 534),
                                 chao(6420, 534), (7600, 404 - CAIXA_H)]),
    'cena3': dict(n=4, d=3, pts=[chao(1300, 527), bloco(1950, 379, 200, 200), chao(3000, 527),
                                 bloco(4274, 369, 193, 193), bloco(5240, 369, 193, 193), chao(6650, 527),
                                 chao(8300, 527)]),
    'final': dict(n=2, d=1, pts=[chao(1300, 662), chao(2000, 662), chao(2700, 662)]),
}

def inst(name, x, y, layer, z):
    return {"angle": 0, "customSize": False, "height": 0, "keepRatio": True, "layer": layer, "name": name,
            "persistentUuid": U(), "width": 0, "x": x, "y": y, "zOrder": z,
            "numberProperties": [], "stringProperties": [], "initialVariables": []}

def C(v, *p, inv=False):
    t = {"value": v}
    if inv: t["inverted"] = True
    return {"type": t, "parameters": list(p)}
A = C
def ev(conds=(), acts=(), subs=()):
    e = {"type": "BuiltinCommonInstructions::Standard", "conditions": list(conds), "actions": list(acts)}
    if subs: e["events"] = list(subs)
    return e
def comment(txt):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0,
            "textG": 0, "textR": 0}, "comment": txt, "comment2": ""}
def setvar(n, op, val): return A('SetNumberVariable', n, op, val)
def var(n, op, val): return C('NumberVariable', n, op, val)

for l in g['layouts']:
    if l['name'] not in SPOTS: continue
    s = SPOTS[l['name']]
    l['instances'] = [i for i in l['instances'] if i['name'] not in ('Municao', 'txt_municao', 'Rocket_Pickup')]
    for x, y in s['pts']:
        l['instances'].append(inst('Municao', x, y, '', 8))
    l['instances'].append(inst('txt_municao', 70, 46, 'GUI', 17))
    for o in l['objects']:
        if o['name'] == 'balas':
            o['content']['InitialValue'] = PENTE; o['content']['MaxValue'] = PENTE
    marker = 'Munição: quantas caixas'
    l['events'] = [e for e in l['events'] if marker not in e.get('comment', '')
                   and not e.get('_municao')]
    head = [comment(f'{marker} ficam nesta cena (sorteadas entre os {len(s["pts"])} pontos). '
                    f'Normal {s["n"]}, Difícil {s["d"]}, Insano 0 (balas infinitas).'),
            ev([C('SceneJustBegins', '')], [], [
                ev([var('dificuldade', '=', '0')], [setvar('alvo_municao', '=', str(s['n']))]),
                ev([var('dificuldade', '=', '1')], [setvar('alvo_municao', '=', str(s['d']))]),
                ev([var('dificuldade', '>=', '2')], [setvar('alvo_municao', '=', '0')]),
            ])]
    head[1]['_municao'] = True
    l['events'] = head + l['events']

# ---------------------------------------------------------------- tela de dificuldade
for l in g['layouts']:
    if l['name'] != 'dificuldade': continue
    for e in l['events']:
        for c in e.get('conditions', []):
            if c['type']['value'].endswith('IsClicked'):
                nivel = {'bt_normal': '0', 'bt_dificil': '1', 'bt_insano': '2'}.get(c['parameters'][0])
                if nivel is None: continue
                e['actions'] = [a for a in e['actions'] if not (a['type']['value'] == 'SetNumberVariable'
                                                                and a['parameters'][0] == 'dificuldade')]
                e['actions'].insert(0, setvar('dificuldade', '=', nivel))

# ---------------------------------------------------------------- eventos do Player
P = [e for e in g['externalEvents'] if e['name'] == 'Player'][0]['events']
assert P[0]['conditions'][0]['type']['value'] == 'SceneJustBegins'
INSANO = var('dificuldade', '>=', '2')
NAO_INSANO = var('dificuldade', '<', '2')

# [0] início da cena: pente cheio, reserva por dificuldade, sorteio das caixas
P[0]['actions'] = [a for a in P[0]['actions'] if not (a['parameters'] and a['parameters'][0] == 'balas')]
P[0]['actions'] += [setvar('pente', '=', str(PENTE)), setvar('recarga', '=', '0'), setvar('emergencia', '=', '0')]
P[0]['events'] = [
    ev([var('dificuldade', '=', '0')], [setvar('reserva', '=', '36')]),
    ev([var('dificuldade', '>=', '1')], [setvar('reserva', '=', '24')]),
    {"type": "BuiltinCommonInstructions::While", "infiniteLoopWarning": True,
     "whileConditions": [C('SceneInstancesCount', '', 'Municao', '>', 'alvo_municao')],
     "conditions": [C('AjoutHasard', '', 'Municao')], "actions": [A('Delete', 'Municao', '')]},
    ev([INSANO], [A('Hide', 'txt_municao')]),
]

# [7] e [9] tiro: só com bala no pente e fora da recarga
for k in (7, 9):
    e = P[k]
    assert e['conditions'][0]['parameters'][1] == '"f"'
    e['conditions'] = [c for c in e['conditions'] if c['type']['value'] not in ('NumberVariable',)]
    once = e['conditions'].pop()  # Once fica por último
    e['conditions'] += [var('pente', '>', '0'), var('recarga', '<=', '0'), once]
    e['actions'] = [a for a in e['actions'] if not (a['parameters'] and a['parameters'][0] in ('balas', 'pente'))]
    e['actions'].insert(2, setvar('pente', '-', '1'))

# [16] Rocket_Pickup (não tem mais instâncias): vale como uma caixa de munição
P[16]['actions'] = [setvar('reserva', '=', 'min(reserva + 24 + 6 * dificuldade, 96)'), A('Delete', 'Rocket_Pickup', '')]

P[:] = [e for e in P if not e.get('_municao') and 'Munição (pente' not in e.get('comment', '')]
bloco_ev = ev([], [], [
    ev([INSANO], [setvar('pente', '=', str(PENTE)), setvar('recarga', '=', '0')]),
    # gatilho sem bala
    ev([C('KeyFromTextPressed', '', '"f"'), var('pente', '<=', '0'), NAO_INSANO, C('BuiltinCommonInstructions::Once')],
       [A('PlaySound', '', 'thunk.wav', '', '60', '1.6')]),
    # recarga automática (pente vazio) ou manual (R)
    ev([var('pente', '<=', '0'), var('reserva', '>', '0'), var('recarga', '<=', '0'), NAO_INSANO],
       [setvar('recarga', '=', '1.2'), A('PlaySound', '', 'thunk2.wav', '', '80', '1')]),
    ev([C('KeyFromTextPressed', '', '"r"'), var('pente', '<', str(PENTE)), var('reserva', '>', '0'),
        var('recarga', '<=', '0'), NAO_INSANO],
       [setvar('recarga', '=', '1.2'), A('PlaySound', '', 'thunk2.wav', '', '80', '1')]),
    ev([var('recarga', '>', '0')], [setvar('recarga', '-', 'TimeDelta()')], [
        ev([var('recarga', '<=', '0')], [
            setvar('n_recarga', '=', f'min({PENTE} - pente, reserva)'),
            setvar('pente', '+', 'n_recarga'), setvar('reserva', '-', 'n_recarga'), setvar('recarga', '=', '0'),
            A('PlaySound', '', 'thunk.wav', '', '70', '1')]),
    ]),
    # rede de segurança: sem nenhuma bala, gera 6 depois de alguns segundos
    ev([var('pente', '<=', '0'), var('reserva', '<=', '0'), var('recarga', '<=', '0'), NAO_INSANO],
       [setvar('emergencia', '+', 'TimeDelta()')], [
        ev([var('emergencia', '>=', '5 + 3 * dificuldade')],
           [setvar('reserva', '=', '6'), setvar('emergencia', '=', '0')]),
    ]),
    # pegar caixa
    ev([C('CollisionNP', 'Player2', 'Municao', '', '', ''), NAO_INSANO],
       [setvar('reserva', '=', 'min(reserva + 24 + 6 * dificuldade, 96)'), setvar('emergencia', '=', '0'),
        A('Delete', 'Municao', ''), A('PlaySound', '', 'laserthing.wav', '', '70', '1.4')]),
    # HUD
    ev([], [A('PanelSpriteContinuousBar::PanelSpriteContinuousBar::SetValue', 'balas', '=', 'pente', '')]),
    ev([NAO_INSANO, var('recarga', '>', '0')],
       [A('TextContainerCapability::TextContainerBehavior::SetValue', 'txt_municao', 'Text', '=', '"RECARREGANDO..."')]),
    ev([NAO_INSANO, var('recarga', '<=', '0'), var('pente', '<=', '0'), var('reserva', '<=', '0')],
       [A('TextContainerCapability::TextContainerBehavior::SetValue', 'txt_municao', 'Text', '=', '"SEM BALAS!"')]),
    ev([NAO_INSANO, var('recarga', '<=', '0'), C('BuiltinCommonInstructions::CompareNumbers', 'pente + reserva', '>', '0')],
       [A('TextContainerCapability::TextContainerBehavior::SetValue', 'txt_municao', 'Text', '=',
          'ToString(pente) + " / " + ToString(reserva)')]),
])
bloco_ev['_municao'] = True
P.append(comment(f'Munição (pente {PENTE}, recarga 1,2 s com R ou automática). '
                 'Insano = infinita. Caixas: objeto Municao. Ver ferramentas/municao.py'))
P.append(bloco_ev)

# remove marcadores internos
def strip(evs):
    for e in evs:
        e.pop('_municao', None); strip(e.get('events', []))
for l in g['layouts']: strip(l['events'])
strip(P)

json.dump(g, open(GJ, 'w'), indent=2, ensure_ascii=False)
print('ok')
