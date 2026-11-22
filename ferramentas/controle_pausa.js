// Controle (gamepad) do jogador 1 e pausa, como no APK v21. Registra uma vez so e roda antes dos
// eventos de toda cena. Este arquivo e copiado para os eventos JavaScript do game.json por
// ferramentas/pausa_pc.py (menu, controles e eventos externos "Player").
//
// Fases (cena1, cena2, cena3, final):
//   - botao II (pausa_botao) no canto superior direito, Esc ou P, ou Start do controle: pausa/continua;
//   - pausado: tempo da cena parado, teclas ignoradas, tela pausa_tela com CONTINUAR e MENU PRINCIPAL.
//     Funciona sem mouse: setas cima/baixo escolhem (destaque pausa_sel), Enter ou Espaco confirmam,
//     Esc ou P continuam, M vai ao menu. Controle: direcional escolhe, A confirma, B vai ao menu.
//     O clique do mouse tambem funciona;
//   - botoes do controle viram as teclas do teclado.
// Submenus (dificuldade, historia, equipe, controles, cenademo): Esc volta ao menu.
// Menus: o analogico esquerdo move um cursor (cursor_pad) e o A clica.
if (!gdjs._cyberSentinelPad2) {
  gdjs._cyberSentinelPad2 = true;
  gdjs._cyberSentinelPad = true; // a versao antiga (sem pausa) nao registra de novo
  const KEYS = { Left: 37, Up: 38, Right: 39, Space: 32, f: 70, g: 71, d: 68, r: 82, q: 81, e: 69, x: 88 };
  const FASES = ['cena1', 'cena2', 'cena3', 'final'];
  const SUBMENUS = ['dificuldade', 'historia', 'equipe', 'controles', 'cenademo'];
  const DEAD = 0.5, STICK = 0.25;
  const BOTAO_PAUSA = { x: 1230, y: 50, r: 34 };
  const CONTINUAR = { x: 490, y: 300, w: 300, h: 70 };
  const MENU = { x: 490, y: 400, w: 300, h: 70 };
  const st = {
    keys: {}, click: false, cx: 640, cy: 360, ct: 99, scene: null, cursor: null,
    pausado: false, botao: null, tela: null, sel: null, opcao: 0, esc: false, prev: {}, tec: {},
  };
  window.addEventListener('keydown', function (e) {
    if (e.repeat) return;
    if (e.key === 'Escape' || e.key === 'p' || e.key === 'P') st.esc = true;
    else if (e.key === 'ArrowUp') st.tec.cima = true;
    else if (e.key === 'ArrowDown') st.tec.baixo = true;
    else if (e.key === 'Enter' || e.key === ' ') st.tec.ok = true;
    else if (e.key === 'm' || e.key === 'M') st.tec.menu = true;
  });
  const dentro = (x, y, r) => x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h;

  gdjs.registerRuntimeScenePreEventsCallback(function (scene) {
    const game = scene.getGame();
    const im = game.getInputManager();
    const nome = scene.getName();
    const fase = FASES.indexOf(nome) >= 0;
    let pad = null;
    try {
      const list = navigator.getGamepads ? navigator.getGamepads() : [];
      for (const p of list) { if (p && p.connected) { pad = p; break; } }
    } catch (e) { pad = null; }
    const bt = (i) => !!(pad && pad.buttons[i] && pad.buttons[i].pressed);
    const ax = (i) => (pad && pad.axes[i] !== undefined ? pad.axes[i] : 0);
    const trig = (i) => !!(pad && pad.buttons[i] && pad.buttons[i].value > DEAD);
    const aperta = (i) => { const now = bt(i), was = !!st.prev[i]; st.prev[i] = now; return now && !was; };
    const startJ = aperta(9), aJ = aperta(0), bJ = aperta(1), cimaJ = aperta(12), baixoJ = aperta(13);
    const esc = st.esc, tec = st.tec;
    st.esc = false;
    st.tec = {};

    if (st.scene !== scene) {
      st.scene = scene; st.cursor = null; st.ct = 99;
      st.pausado = false; st.botao = null; st.tela = null; st.sel = null;
    }

    // ---- submenus: Esc volta ao menu ----
    if (esc && SUBMENUS.indexOf(nome) >= 0) {
      scene.requestChange(gdjs.SceneChangeRequest.REPLACE_SCENE, 'menu');
      return;
    }

    // ---- pausa nas fases ----
    if (fase) {
      if (!st.botao) {
        st.botao = scene.createObject('pausa_botao');
        if (st.botao) {
          st.botao.setLayer('GUI');
          st.botao.setPosition(BOTAO_PAUSA.x - 36, BOTAO_PAUSA.y - 36);
          st.botao.setZOrder(100000);
        }
      }
      const soltou = im.isMouseButtonReleased(0);
      const mx = im.getCursorX(), my = im.getCursorY();
      let alterna = esc || startJ;
      if (!st.pausado && soltou &&
          Math.hypot(mx - BOTAO_PAUSA.x, my - BOTAO_PAUSA.y) <= BOTAO_PAUSA.r) alterna = true;
      if (st.pausado) {
        if (tec.cima || cimaJ) st.opcao = 0;
        if (tec.baixo || baixoJ) st.opcao = 1;
        const ok = tec.ok || aJ;
        if ((ok && st.opcao === 0) || (soltou && dentro(mx, my, CONTINUAR))) alterna = true;
        if (tec.menu || bJ || (ok && st.opcao === 1) || (soltou && dentro(mx, my, MENU))) {
          scene.getTimeManager().setTimeScale(1);
          scene.requestChange(gdjs.SceneChangeRequest.REPLACE_SCENE, 'menu');
          return;
        }
      }
      if (alterna) {
        st.pausado = !st.pausado;
        scene.getTimeManager().setTimeScale(st.pausado ? 0 : 1);
        if (st.pausado && !st.tela) {
          st.tela = scene.createObject('pausa_tela');
          if (st.tela) { st.tela.setLayer('GUI'); st.tela.setPosition(0, 0); st.tela.setZOrder(100001); }
        }
        if (st.pausado && !st.sel) {
          st.sel = scene.createObject('pausa_sel');
          if (st.sel) { st.sel.setLayer('GUI'); st.sel.setZOrder(100002); }
        }
        st.opcao = 0;
        if (st.tela) st.tela.hide(!st.pausado);
        if (st.sel) st.sel.hide(!st.pausado);
        if (st.botao) st.botao.hide(st.pausado);
      }
      if (st.pausado) {
        if (st.sel) {
          const r = st.opcao === 0 ? CONTINUAR : MENU;
          st.sel.setPosition(r.x - 20, r.y - 20);
        }
        // solta as teclas simuladas pelo controle e ignora o teclado enquanto pausado
        for (const k in KEYS) st.keys[k] = false;
        im._pressedKeys.clear();
        im._justPressedKeys.clear();
        im._releasedKeys.clear();
        return;
      }
    }

    // ---- controle: botoes viram teclas nas fases ----
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

    // ---- cursor do controle nos menus ----
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
}
