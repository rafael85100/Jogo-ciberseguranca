#!/usr/bin/env python3
"""Leva para o game.json (PC) as mudancas do APK v21 (21/11/2026).

- Menu: botao CONTROLES e cena nova "controles" (tabela de teclas e controle).
- Robo: soco (G), mira para cima / diagonal (segurar seta para cima + F), animacoes novas
  AtirarCima, AtirarDiag e Soco (imagens tiro_cima.png, tiro_diag.png, soco_player.png).
- Tiros do jogador e dos drones param nas caixas roxas (bloco*) e somem a 2000 px do robo.
- Tiro dos drones (cena1 e final) vai reto na direcao em que saiu, nao persegue mais.
- Final: Mysterious anda e pula atras do robo (PlatformerObject), atira com intervalo,
  e o escudo (D) funciona na fase final, bloqueando tiros e o soco do chefe.
- Fase 1: o painel de controles (ct) saiu, porque os controles agora ficam no menu.
- Controle (gamepad) para 1 jogador, via evento JavaScript (navigator.getGamepads).

Roda uma vez so: python3 ferramentas/v21_pc.py game.json
"""
import copy, json, sys, uuid

PATH = sys.argv[1]
g = json.load(open(PATH, encoding='utf-8'))
L = {l['name']: l for l in g['layouts']}
EXT = {x['name']: x for x in g['externalEvents']}
GLOBAL_OBJS = {o['name']: o for o in g['objects']}
CENAS = ['cena1', 'cena2', 'cena3', 'final']
v21 = json.load(open(sys.argv[2], encoding='utf-8'))  # gd_objects.json do APK v21

assert not any(o['name'] == 'soco_hitbox' for o in g['objects']), 'script ja foi aplicado'


# ---------- helpers de eventos ----------
def I(t, *params, inv=False, sub=None):
    d = {'type': {'value': t}, 'parameters': [str(p) for p in params]}
    if inv:
        d['type']['inverted'] = True
    if sub is not None:
        d['subInstructions'] = sub
    return d


def E(conds=(), acts=(), events=()):
    return {'type': 'BuiltinCommonInstructions::Standard', 'conditions': list(conds),
            'actions': list(acts), 'events': list(events)}


def C(text):
    return {'type': 'BuiltinCommonInstructions::Comment', 'color': {'b': 109, 'g': 230, 'r': 255,
            'textB': 0, 'textG': 0, 'textR': 0}, 'comment': text, 'comment2': ''}


def JS(code):
    return {'type': 'BuiltinCommonInstructions::JsCode', 'inlineCode': code,
            'parameterObjects': '', 'useStrict': True, 'eventsSheetExpanded': False}


key = lambda k: I('KeyFromTextPressed', '', '"%s"' % k)
nkey = lambda k: I('KeyFromTextPressed', '', '"%s"' % k, inv=True)
nv = lambda v, op, x: I('NumberVariable', v, op, x)
setv = lambda v, op, x: I('SetNumberVariable', v, op, x)
nov = lambda o, v, op, x: I('NumberObjectVariable', o, v, op, x)
setov = lambda o, v, op, x: I('SetNumberObjectVariable', o, v, op, x)
cmp = lambda a, op, b: I('BuiltinCommonInstructions::CompareNumbers', a, op, b)
once = lambda: I('BuiltinCommonInstructions::Once')
anim = lambda o, i: I('AnimatableCapability::AnimatableBehavior::SetIndex', o, 'Animation', '=', i)
create = lambda o, x, y: I('Create', '', o, x, y, '')
delete = lambda o: I('Delete', o, '')
wait = lambda s: I('Wait', s)
coll = lambda a, b: I('CollisionNP', a, b, '', '', '')
count = lambda o, op, n: I('SceneInstancesCount', '', o, op, n)
OR = lambda *c: I('BuiltinCommonInstructions::Or', sub=list(c))
AND = lambda *c: I('BuiltinCommonInstructions::And', sub=list(c))
plat = lambda what, o: I('PlatformBehavior::' + what, o, 'PlatformerObject')


def objs_of(scene):
    return {o['name']: o for o in L[scene]['objects']}


def has(scene, name):
    return name in objs_of(scene) or name in GLOBAL_OBJS


def obj(scene, name):
    return objs_of(scene).get(name) or GLOBAL_OBJS[name]


def declare_obj_var(o, name, value=0):
    vs = o.setdefault('variables', [])
    if not any(v['name'] == name for v in vs):
        vs.append({'name': name, 'type': 'number', 'value': value})


def declare(varlist, name, value=0):
    if not any(v['name'] == name for v in varlist):
        varlist.append({'name': name, 'type': 'number', 'value': value})


def find_event(evs, pred):
    for i, e in enumerate(evs):
        if pred(e):
            return i
    raise KeyError('evento nao achado')


def acts_of(e):
    return [a['type']['value'] + str(a['parameters']) for a in e.get('actions', [])]


def conds_of(e):
    return [c['type']['value'] + str(c['parameters']) for c in e.get('conditions', [])]


def new_instance(name, x, y, z, w=0, h=0, layer=''):
    return {'angle': 0, 'customSize': bool(w), 'depth': 0, 'height': h, 'keepRatio': True,
            'layer': layer, 'name': name, 'persistentUuid': str(uuid.uuid4()), 'width': w,
            'x': x, 'y': y, 'zOrder': z, 'numberProperties': [], 'stringProperties': [],
            'initialVariables': []}


def add_image_resource(file, smoothed=False):
    rs = g['resources']['resources']
    if not any(r['name'] == file for r in rs):
        rs.append({'file': file, 'kind': 'image', 'metadata': '', 'name': file,
                   'smoothed': smoothed, 'userAdded': True})


def sprite_object(name, image, w, h, points=()):
    return {'adaptCollisionMaskAutomatically': False, 'assetStoreId': '', 'name': name,
            'persistentUuid': str(uuid.uuid4()), 'type': 'Sprite', 'updateIfNotVisible': False,
            'variables': [], 'effects': [], 'behaviors': [],
            'animations': [{'name': '', 'useMultipleDirections': False, 'directions': [{
                'looping': False, 'timeBetweenFrames': 0.08, 'sprites': [{
                    'hasCustomCollisionMask': True, 'image': image, 'points': list(points),
                    'originPoint': {'name': 'origine', 'x': 0, 'y': 0},
                    'centerPoint': {'automatic': True, 'name': 'centre', 'x': 0, 'y': 0},
                    'customCollisionMask': [[{'x': 0, 'y': 0}, {'x': w, 'y': 0},
                                             {'x': w, 'y': h}, {'x': 0, 'y': h}]]}]}]}]}


# ---------- recursos novos ----------
for f in ['tiro_cima.png', 'tiro_diag.png', 'soco_player.png']:
    add_image_resource(f)
add_image_resource('assets/image/soco_hitbox.png')
add_image_resource('assets/image/cursor_pad.png')
add_image_resource('assets/image/tabela_controles.png', smoothed=True)

# objetos globais: hitbox do soco (invisivel) e cursor do controle nos menus
g['objects'].append(sprite_object('soco_hitbox', 'assets/image/soco_hitbox.png', 68, 60))
g['objects'].append(sprite_object('cursor_pad', 'assets/image/cursor_pad.png', 32, 32))
GLOBAL_OBJS = {o['name']: o for o in g['objects']}

# variaveis globais novas
for n in ['mira', 'mira_x', 'mira_pose', 'mira_prev', 'soco_t', 'soco_cd', 'soco_n',
          'pad_mira_cima', 'pad_mira_esq', 'pad_mira_dir']:
    declare(g['variables'], n)

# ---------- Player2: 3 animacoes novas em todas as fases ----------
for cena in CENAS:
    p = objs_of(cena)['Player2']
    assert len(p['animations']) == 3, cena
    p['animations'].extend(copy.deepcopy(v21[cena]['Player2']['animations'][3:6]))
    for n in ['bala1', 'bala2']:
        for vn in ['aim', 'vx', 'vy']:
            declare_obj_var(obj(cena, n), vn)

# final: o Player2 nao tinha o ponto "escudo" (so a cena3 tinha); copia da cena3
p3 = objs_of('cena3')['Player2']['animations'][0]['directions'][0]['sprites']
pf = objs_of('final')['Player2']['animations'][0]['directions'][0]['sprites']
for s3, sf in zip(p3, pf):
    for pt in s3['points']:
        if pt['name'] == 'escudo' and not any(q['name'] == 'escudo' for q in sf['points']):
            sf['points'].append(copy.deepcopy(pt))

# ---------- controle (gamepad) via JavaScript ----------
PAD_JS = r"""// Controle (gamepad) para o jogador 1. Registra uma vez so e roda antes dos eventos de toda cena.
// Na fase, os botoes viram teclas (as mesmas do teclado). Nos menus, o analogico move um cursor
// e o A clica. Mapa igual ao do APK v21.
if (!gdjs._cyberSentinelPad) {
  gdjs._cyberSentinelPad = true;
  const KEYS = { Left: 37, Up: 38, Right: 39, Space: 32, f: 70, g: 71, d: 68, r: 82, q: 81, e: 69, x: 88 };
  const FASES = ['cena1', 'cena2', 'cena3', 'final'];
  const DEAD = 0.5, STICK = 0.25;
  const st = { keys: {}, click: false, cx: 640, cy: 360, ct: 99, scene: null, cursor: null };
  gdjs.registerRuntimeScenePreEventsCallback(function (scene) {
    const game = scene.getGame();
    const im = game.getInputManager();
    let pad = null;
    try {
      const list = navigator.getGamepads ? navigator.getGamepads() : [];
      for (const p of list) { if (p && p.connected) { pad = p; break; } }
    } catch (e) { pad = null; }
    const bt = (i) => !!(pad && pad.buttons[i] && pad.buttons[i].pressed);
    const ax = (i) => (pad && pad.axes[i] !== undefined ? pad.axes[i] : 0);
    const trig = (i) => !!(pad && pad.buttons[i] && pad.buttons[i].value > DEAD);
    const fase = FASES.indexOf(scene.getName()) >= 0;
    const want = {};
    if (pad && fase) {
      want.Left = bt(14) || ax(0) < -DEAD;
      want.Right = bt(15) || ax(0) > DEAD;
      want.Up = bt(12) || ax(1) < -DEAD;
      want.Space = bt(0);
      want.f = bt(2);
      want.g = bt(1);
      want.d = bt(3);
      want.r = bt(4);
      want.q = bt(5);
      want.e = trig(6);
      want.x = bt(8);
    }
    for (const k in KEYS) {
      const w = !!want[k];
      if (w && !st.keys[k]) im.onKeyPressed(KEYS[k]);
      else if (!w && st.keys[k]) im.onKeyReleased(KEYS[k]);
      st.keys[k] = w;
    }
    const vars = game.getVariables();
    vars.get('pad_mira_cima').setNumber(pad && fase && ax(3) < -DEAD ? 1 : 0);
    vars.get('pad_mira_esq').setNumber(pad && fase && ax(2) < -DEAD ? 1 : 0);
    vars.get('pad_mira_dir').setNumber(pad && fase && ax(2) > DEAD ? 1 : 0);

    // cursor nos menus
    if (st.scene !== scene) { st.scene = scene; st.cursor = null; st.ct = 99; }
    let vx = 0, vy = 0;
    if (pad && !fase) {
      const sx = ax(0), sy = ax(1);
      if (Math.hypot(sx, sy) > STICK) { vx += sx; vy += sy; }
      if (bt(14)) vx -= 1;
      if (bt(15)) vx += 1;
      if (bt(12)) vy -= 1;
      if (bt(13)) vy += 1;
    }
    const dt = scene.getTimeManager().getElapsedTime() / 1000;
    if (vx !== 0 || vy !== 0) {
      const len = Math.hypot(vx, vy), k = len > 1 ? 1 / len : 1;
      st.cx = Math.min(1280, Math.max(0, st.cx + vx * k * 650 * dt));
      st.cy = Math.min(720, Math.max(0, st.cy + vy * k * 650 * dt));
      st.ct = 0;
      im.onMouseMove(st.cx, st.cy);
    } else {
      st.ct += dt;
    }
    const click = !!pad && !fase && bt(0);
    if (click && !st.click) { im.onMouseMove(st.cx, st.cy); im.onMouseButtonPressed(0); st.ct = 0; }
    else if (!click && st.click) im.onMouseButtonReleased(0);
    st.click = click;
    const show = !!pad && !fase && st.ct < 3;
    if (show && !st.cursor) {
      st.cursor = scene.createObject('cursor_pad');
      if (st.cursor) st.cursor.setZOrder(100000);
    }
    if (st.cursor) {
      st.cursor.setPosition(st.cx - 16, st.cy - 16);
      st.cursor.hide(!show);
    }
  });
}"""

# ---------- Player (eventos externos) ----------
pe = EXT['Player']['events']
pe.insert(0, JS(PAD_JS))

# forca das balas: reta (450) ou na direcao da mira (vx, vy)
i = find_event(pe, lambda e: 'AddForceXY[\'bala1\', \'450\', \'0\', \'\']' in acts_of(e))
pe[i:i + 1] = [
    E([nov('bala1', 'aim', '=', '0')], [I('AddForceXY', 'bala1', '450', '0', '')]),
    E([nov('bala1', 'aim', '=', '1')], [I('AddForceXY', 'bala1', 'bala1.Variable(vx)', 'bala1.Variable(vy)', '')]),
    E([nov('bala2', 'aim', '=', '0')], [I('AddForceXY', 'bala2', '-450', '0', '')]),
    E([nov('bala2', 'aim', '=', '1')], [I('AddForceXY', 'bala2', 'bala2.Variable(vx)', 'bala2.Variable(vy)', '')]),
]

# mira: seta para cima (ou analogico direito do controle) + lado
i = find_event(pe, lambda e: any('KeyFromTextReleased' in c and '"Right"' in c for c in conds_of(e)))
mira_evs = [
    C('Mira (APK v21): segure a seta para cima e aperte F para atirar para cima; com ← ou → junto, na diagonal. '
      'No controle, o analógico direito mira.'),
    E([], [setv('mira', '=', '0'), setv('mira_x', '=', '0'), setv('mira_pose', '=', '0')]),
    E([OR(key('Up'), nv('pad_mira_cima', '=', '1'))], [setv('mira', '=', '1')]),
    E([OR(key('Right'), nv('pad_mira_dir', '=', '1'))], [setv('mira_x', '+', '1')]),
    E([OR(key('Left'), nv('pad_mira_esq', '=', '1'))], [setv('mira_x', '-', '1')]),
    E([nv('pad_mira_cima', '=', '1')], [setv('mira_pose', '=', '1')]),
    E([nv('mira', '=', '1'), key('f')], [setv('mira_pose', '=', '1')]),
    E([nv('pad_mira_esq', '=', '1'), nkey('Right'), nv('pad_mira_dir', '=', '0')],
      [I('FlippableCapability::FlippableBehavior::FlipX', 'Player2', 'Flippable', 'yes')]),
    E([nv('pad_mira_dir', '=', '1'), nkey('Left'), nv('pad_mira_esq', '=', '0')],
      [I('FlippableCapability::FlippableBehavior::FlipX', 'Player2', 'Flippable', 'no')]),
]
pe[i + 1:i + 1] = mira_evs

# tiros retos so sem mira
fire_idx = [k for k, e in enumerate(pe) if any(c.startswith('KeyFromTextPressed') and '"f"' in c for c in conds_of(e))
            and any(a.startswith('Create') for a in acts_of(e))]
assert len(fire_idx) == 2, fire_idx
for k in fire_idx:
    cs = pe[k]['conditions']
    cs.insert(len(cs) - 1, nv('mira', '=', '0'))  # antes do Trigger once


def tiro_mirado(mx, idx, nome, vx, vy, ang):
    return E([nv('mira_x', '=', mx)], [
        anim('Player2', idx),
        create(nome, 'Player2.PointX("disparo")', 'Player2.PointY("disparo")'),
        setov(nome, 'aim', '=', '1'), setov(nome, 'vx', '=', vx), setov(nome, 'vy', '=', vy),
        I('SetAngle', nome, '=', ang)])


D = '318.198'  # 450 * cos(45)
soco_evs = [
    C('Tiro mirado: sai do ponto "disparo" das animações AtirarCima (3) e AtirarDiag (4).'),
    E([key('f'), nv('mira', '=', '1'), nv('pente', '>', '0'), nv('recarga', '<=', '0'), once()],
      [setv('pente', '-', '1'), I('PlayMusic', '', 'weaponfire1.wav', '', '', '')], [
        tiro_mirado('0', '3', 'bala1', '0', '-450', '-90'),
        tiro_mirado('1', '4', 'bala1', D, '-' + D, '-45'),
        tiro_mirado('-1', '4', 'bala2', '-' + D, '-' + D, '45'),
    ]),
    E([nv('mira_pose', '=', '1'), nv('mira_x', '=', '0')], [anim('Player2', '3')]),
    E([nv('mira_pose', '=', '1'), nv('mira_x', '!=', '0')], [anim('Player2', '4')]),
    E([nv('mira_pose', '=', '0'), nv('mira_prev', '=', '1')], [anim('Player2', '0')]),
    E([], [setv('mira_prev', '=', 'mira_pose')]),
    C('Soco (APK v21): G. Dura 0,3 s, recarga 0,4 s, 15 de dano (dividido por mult_hp). A área do soco '
      '(soco_hitbox, 68x60, invisível) fica no ponto "soco" da animação Soco (5). Cada inimigo leva um golpe por soco '
      '(variável soco_id = soco_n). Os acertos ficam nos eventos de cada fase.'),
    E([], [setv('soco_cd', '-', 'TimeDelta()'), setv('soco_t', '-', 'TimeDelta()')]),
    E([key('g'), once()], [], [
        E([nv('soco_cd', '<=', '0')], [setv('soco_t', '=', '0.3'), setv('soco_cd', '=', '0.4'),
                                      setv('soco_n', '+', '1'), I('PlaySound', '', 'thunk.wav', '', '60', '1.8')])]),
    E([nv('soco_t', '>', '0')], [anim('Player2', '5')], [
        E([count('soco_hitbox', '=', '0')],
          [create('soco_hitbox', 'Player2.PointX("soco") - 34', 'Player2.PointY("soco") - 30')]),
        E([], [I('SetXY', 'soco_hitbox', '=', 'Player2.PointX("soco") - 34', '=', 'Player2.PointY("soco") - 30')]),
    ]),
    E([nv('soco_t', '<=', '0'), I('AnimatableCapability::AnimatableBehavior::Index', 'Player2', 'Animation', '=', '5')],
      [anim('Player2', '0')]),
    E([nv('soco_t', '<=', '0')], [delete('soco_hitbox')]),
    C('Tiros param nas caixas roxas e somem a mais de 2000 px do robô.'),
]
for b in ['bala1', 'bala2', 'B2', 'B3', 'B4']:
    soco_evs.append(E([coll(b, 'bloco')], [delete(b)]))
    soco_evs.append(E([OR(I('PosX', b, '>', 'Player2.X() + 2000'), I('PosX', b, '<', 'Player2.X() - 2000'),
                          I('PosY', b, '>', 'Player2.Y() + 2000'), I('PosY', b, '<', 'Player2.Y() - 2000'))],
                      [delete(b)]))
last_fire = max(k for k, e in enumerate(pe) if any(c.startswith('KeyFromTextPressed') and '"f"' in c
                                                    for c in conds_of(e)) and any(a.startswith('Create') for a in acts_of(e)))
pe[last_fire + 1:last_fire + 1] = soco_evs

# cena3 tem bloco2..bloco4 tambem
c3 = L['cena3']['events']
i = find_event(c3, lambda e: e['type'].endswith('Link') and e.get('target') == 'Player')
c3[i + 1:i + 1] = [E([coll(b, c)], [delete(b)]) for c in ['bloco2', 'bloco3', 'bloco4']
                   for b in ['bala1', 'bala2', 'B2', 'B3', 'B4']]

# ---------- acertos do soco em cada fase ----------
ALVOS = [('drone2', 'GreenFlatBar2', 'RedExplosion'), ('drone3', 'GreenFlatBar3', 'RedExplosion2'),
         ('drone4', 'GreenFlatBar4', 'RedExplosion3'), ('virus', 'bar_v1', 'Holy_Explosion'),
         ('virus2', 'bar_v2', 'Holy_Explosion'), ('monstro_alado', 'w_bar', 'Holy_Explosion4'),
         ('monstro_alado2', 'w_bar2', 'Holy_Explosion3'), ('lagarto_boss4', 'MetalRedBar', 'Holy_Explosion2'),
         ('Mysterious', 'bar_monstro_life', 'Holy_Explosion3')]
ALVOS += [('robo_z' + s, 'barZ' + s, 'bazu' + s) for s in ['', '2', '3', '4', '5', '6', '7']]
for cena in CENAS:
    evs = [C('Soco do robô (APK v21): cada inimigo leva 15 de dano por soco.')]
    for alvo, barra, fx in ALVOS:
        if not (has(cena, alvo) and has(cena, barra) and has(cena, fx)):
            continue
        declare_obj_var(obj(cena, alvo), 'soco_id')
        evs.append(E([coll('soco_hitbox', alvo), nov(alvo, 'soco_id', '!=', 'soco_n')], [
            setov(alvo, 'soco_id', '=', 'soco_n'),
            I('PanelSpriteContinuousBar::PanelSpriteContinuousBar::SetValue', barra, '-', '15 / mult_hp', ''),
            create(fx, alvo + '.BoundingBoxCenterX() - 48', alvo + '.BoundingBoxCenterY() - 48'),
            wait('1.5'), delete(fx)]))
    ev = L[cena]['events']
    i = find_event(ev, lambda e: e['type'].endswith('Link') and e.get('target') == 'Player')
    ev[i + 1:i + 1] = evs
    print(cena, 'alvos do soco:', len(evs) - 1)

# ---------- tiro dos drones reto (cena1 e final) ----------
for cena in ['cena1', 'final']:
    ev = L[cena]['events']
    i = find_event(ev, lambda e: any(a.startswith('AddForceTowardObject[\'B2\'') for a in acts_of(e)))
    novo = [C('Tiro dos drones (APK v21): segue reto na direção em que o robô estava quando saiu.')]
    for b in ['B2', 'B3', 'B4']:
        for vn in ['dir_ok', 'vx', 'vy']:
            declare_obj_var(obj(cena, b), vn)
        novo.append(E([nov(b, 'dir_ok', '=', '0')], [
            setov(b, 'vx', '=', '400 * cos(ToRad(%s.AngleToObject(Player2)))' % b),
            setov(b, 'vy', '=', '400 * sin(ToRad(%s.AngleToObject(Player2)))' % b),
            setov(b, 'dir_ok', '=', '1')]))
        novo.append(E([], [I('AddForceXY', b, b + '.Variable(vx)', b + '.Variable(vy)', '')]))
    ev[i:i + 1] = novo

# ---------- cena1: painel de controles saiu ----------
L['cena1']['instances'] = [x for x in L['cena1']['instances'] if x['name'] != 'ct']

# ---------- final: Mysterious anda/pula, escudo ----------
F = L['final']
fo = objs_of('final')
fo['Mysterious']['behaviors'] = copy.deepcopy(v21['final']['Mysterious']['behaviors'])
for n, v in [('atirando', 0), ('atira_t', 0), ('cd_tiro', 1), ('cd_pulo', 2), ('pulo_hold', 0),
             ('preso_t', 0), ('mys_last_x', 0), ('quer_andar', 0)]:
    declare(F['variables'], n, v)
fe = F['events']

# escudo D (igual a cena3) e bloqueio dos tiros pelo escudo
i = find_event(fe, lambda e: e['type'].endswith('Link') and e.get('target') == 'Player')
bloq = [C('Escudo na fase final (APK v21): D cria o escudo por 3 s; ele bloqueia tiros do chefe, dos drones e o soco.'),
        E([key('d'), once()], [
            create('Front_Shield_Pickup', 'Player2.PointX("escudo")', 'Player2.PointY("escudo")'),
            I('ResizableCapability::ResizableBehavior::SetSize', 'Front_Shield_Pickup', 'Resizable', '150', '150'),
            wait('3'), delete('Front_Shield_Pickup')])]
for b in ['bala_r1d', 'bala_r1d2', 'B2', 'B3', 'B4']:
    bloq.append(E([coll(b, 'Front_Shield_Pickup')], [
        create('RedExplosion', b + '.BoundingBoxCenterX()', b + '.BoundingBoxCenterY()'),
        delete(b), wait('1.5'), delete('RedExplosion')]))
fe[i:i] = bloq

# modos do chefe: 4 = anda atras do robo, 1 = atirando (rajada de 1,28 s), 2 = soco, 3 = conversa
k1 = find_event(fe, lambda e: any("SetNumberVariable['modo_boss', '=', '1']" in a for a in acts_of(e)))
k2 = find_event(fe, lambda e: any("SetNumberVariable['modo_boss', '=', '2']" in a for a in acts_of(e)))
assert k2 == k1 + 1
DX = 'abs(Player2.BoundingBoxCenterX() - Mysterious.BoundingBoxCenterX())'
DY = 'Player2.BoundingBoxCenterY() - Mysterious.BoundingBoxCenterY()'
fe[k1:k2 + 1] = [
    E([nv('luta', '=', '1'), count('Mysterious', '>', '0')], [setv('modo_boss', '=', '4')], [
        E([nv('atirando', '=', '1')], [setv('modo_boss', '=', '1')]),
        E([cmp(DX, '<=', 'Mysterious.Width() * 0.445 + 25'), cmp('abs(%s)' % DY, '<', 'Mysterious.Height() * 0.6')],
          [setv('modo_boss', '=', '2')]),
    ])]

# modo 0 (parado longe) nao existe mais
k0 = find_event(fe, lambda e: conds_of(e) == ["NumberVariable['modo_boss', '=', '0']"])
del fe[k0]
if fe[k0 - 1]['type'].endswith('Comment') and 'longe' in fe[k0 - 1]['comment']:
    del fe[k0 - 1]

# modo 1: conta a rajada
k = find_event(fe, lambda e: conds_of(e) == ["NumberVariable['modo_boss', '=', '1']"])
fe[k]['actions'].append(setv('atira_t', '+', 'TimeDelta()'))
fe[k]['events'].append(E([nv('atira_t', '>=', '1.28')],
                         [setv('atirando', '=', '0'), setv('atira_t', '=', '0'), setv('cd_tiro', '=', '1.4')]))
fe[k - 1]['comment'] = 'tiro: rajada de 1,28 s (uma bala no quadro 9), depois espera 1,4 s'

# modo 2: soco nao machuca com escudo
k = find_event(fe, lambda e: conds_of(e) == ["NumberVariable['modo_boss', '=', '2']"])
sub = fe[k]['events'][0]
dano = sub['actions']
sub['actions'] = []
sub['events'] = [
    E([count('Front_Shield_Pickup', '=', '0')], dano),
    E([count('Front_Shield_Pickup', '>', '0')], [
        create('RedExplosion', 'Player2.BoundingBoxCenterX()', 'Player2.BoundingBoxCenterY()'),
        wait('0.5'), delete('RedExplosion')]),
]

# modo 4: anda e pula (entre x 520 e 1450)
MX = 'Mysterious.BoundingBoxCenterX()'
PX = 'Player2.BoundingBoxCenterX()'
modo4 = [
    C('anda atrás do robô (APK v21): fica entre x 520 e 1450, pula a cada 2,2 s, quando trava ou quando o robô está '
      'acima; atira quando está perto (650 px), no chão e sem recarga'),
    E([nv('modo_boss', '=', '4')], [
        anim('Mysterious', '2'), I('AnimatableCapability::AnimatableBehavior::PlayAnimation', 'Mysterious', 'Animation'),
        setv('cd_tiro', '-', 'TimeDelta()'), setv('cd_pulo', '-', 'TimeDelta()'), setv('quer_andar', '=', '0')], [
        E([cmp(PX, '<', MX + ' - 20'), cmp(MX, '>', '520')],
          [plat('SimulateLeftKey', 'Mysterious'), setv('quer_andar', '=', '1')]),
        E([cmp(PX, '>', MX + ' + 20'), cmp(MX, '<', '1450')],
          [plat('SimulateRightKey', 'Mysterious'), setv('quer_andar', '=', '1')]),
        E([nv('quer_andar', '=', '1'), cmp('abs(Mysterious.X() - mys_last_x)', '<', '10 * TimeDelta()')],
          [setv('preso_t', '+', 'TimeDelta()')]),
        E([OR(nv('quer_andar', '=', '0'), cmp('abs(Mysterious.X() - mys_last_x)', '>=', '10 * TimeDelta()'))],
          [setv('preso_t', '=', '0')]),
        E([nv('cd_tiro', '<=', '0'), cmp(DX, '<=', '650'), plat('IsOnFloor', 'Mysterious')],
          [setv('atirando', '=', '1'), setv('atira_t', '=', '0')]),
        E([nv('atirando', '=', '0'), plat('IsOnFloor', 'Mysterious'),
           OR(nv('cd_pulo', '<=', '0'), nv('preso_t', '>', '0.15'), AND(cmp(DY, '<', '-80'), cmp(DX, '<', '450')))],
          [setv('pulo_hold', '=', '0.25'), setv('cd_pulo', '=', '2.2')]),
        E([nv('atirando', '=', '0'), nv('pulo_hold', '>', '0')],
          [setv('pulo_hold', '-', 'TimeDelta()'), plat('SimulateJumpKey', 'Mysterious')]),
    ]),
    E([count('Mysterious', '>', '0')], [setv('mys_last_x', '=', 'Mysterious.X()')]),
]
k = find_event(fe, lambda e: conds_of(e) == ["NumberVariable['modo_boss', '=', '2']"])
fe[k + 1:k + 1] = modo4

# ---------- menu: botao CONTROLES ----------
M = L['menu']
mo = {o['name']: o for o in M['objects']}
bt = copy.deepcopy(mo['bt_historia']); bt['name'] = 'bt_controles'; bt['persistentUuid'] = str(uuid.uuid4())
tx = copy.deepcopy(mo['txt_historio']); tx['name'] = 'txt_controles'; tx['persistentUuid'] = str(uuid.uuid4())
tx['string'] = tx['content']['text'] = 'Controles'
M['objects'] += [bt, tx]
POS = {'bt_jogar': [(705, 20)], 'arme': [(698, 0)], 'bt_historia': [(705, 160)], 'bt_equipe': [(705, 300)],
       'bt_sair': [(705, 580)], 'arme2': [(697, 139), (697, 279), (697, 559)], 'txt_jogar': [(809, 52)],
       'txt_historio': [(793, 192)], 'txt_equipe': [(807, 332)], 'txt_sair': [(826, 612)]}
seen = {}
for ins in M['instances']:
    lst = POS.get(ins['name'])
    if lst:
        j = seen.get(ins['name'], 0); seen[ins['name']] = j + 1
        ins['x'], ins['y'] = lst[j]
M['instances'] += [new_instance('bt_controles', 705, 440, 13, 315, 97),
                   new_instance('arme2', 697, 419, 14, 330, 127),
                   new_instance('txt_controles', 782, 472, 15)]
M['events'].insert(0, JS(PAD_JS))
M['events'].append(E([I('PanelSpriteButton::PanelSpriteButton::IsClicked', 'bt_controles', '')],
                     [I('Scene', '', '"controles"', '')]))

# ---------- cena nova "controles" (copia da historia) ----------
H = copy.deepcopy(L['historia'])
H['name'] = 'controles'
H['mangledName'] = 'controles'
H['instances'] = [x for x in H['instances'] if x['name'] not in ('NewText', 'historia')]
for x in H['instances']:
    x['persistentUuid'] = str(uuid.uuid4())
H['objects'] = [o for o in H['objects'] if o['name'] not in ('NewText', 'historia')]
H['objects'].append(sprite_object('tabela_controles', 'assets/image/tabela_controles.png', 1280, 720))
H['instances'].append(new_instance('tabela_controles', 0, 0, 2))
H['events'].insert(0, JS(PAD_JS))
g['layouts'].insert(g['layouts'].index(L['historia']) + 1, H)

# pastas de objetos do editor
def fs_add(fs, names):
    for n in names:
        if not any(c.get('objectName') == n for c in fs['children']):
            fs['children'].append({'objectName': n})
fs_add(g['objectsFolderStructure'], ['soco_hitbox', 'cursor_pad'])
fs_add(M['objectsFolderStructure'], ['bt_controles', 'txt_controles'])
H['objectsFolderStructure']['children'] = [c for c in H['objectsFolderStructure']['children']
                                           if c.get('objectName') not in ('NewText', 'historia')]
fs_add(H['objectsFolderStructure'], ['tabela_controles'])

json.dump(g, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ok')
