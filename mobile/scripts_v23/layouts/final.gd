extends GDLayout
const MYS_X: = 770.0
const MYS_Y: = 512.0
const TIRO_DIST: = 650.0
const TBF: =[0.08, 0.06, 0.1]
const TIRO_EM: = 0.72
const SOCO_EM: = 0.42
const BALAS: =[["bala_r1d", -500.0],["bala_r1d2", 500.0]]
const BOSS_X_MIN: = 520.0
const BOSS_X_MAX: = 1450.0
const BOSS_PULO_CD: = 2.2
const TIRO_CD: = 1.4
const TIRO_DUR: = 1.28
# v23 (igual ao PC, ferramentas/plataformas_final.py e boss_final.py):
# plataformas neon atravessaveis na arena, mira do chefe reta ou diagonal (45 graus), sorteio de
# tiro 50 + 10 * dificuldade (%), balas que somem longe e portal no fim da arena.
const PLATAFORMAS: =[Vector2(480, 555), Vector2(760, 445), Vector2(1040, 555), Vector2(1320, 445)]
const BALA_VEL: = 500.0
const BALA_DIAG: = 353.553
const TIRO_RETRY: = 0.7
const PORTAL_X: = 2830.0
var dialogo: = 0
var luta: = 0
var atirando: = false
var atira_t: = 0.0
var cd_tiro: = 1.0
var cd_pulo: = 2.0
var pulo_hold: = 0.0
var preso_t: = 0.0
func _events(delta: float) -> void:
	if scene_just_begins:
		_begin()
	if GD.once("final_shield", GD.key_held("d")):
		_shield_pickup()
	_escudo_bloqueia_drones()
	Sheet_Player.run(self, delta)
	Sheet_ex_inimigos.drone_shots()
	Sheet_ex_inimigos.run(self, delta)
	if touching("Player2", "portalF"):
		for ptl in GD.pick("portal"):
			ptl.set_anim_index(1)
		GD.set_var("tela_load", 5)
		go_scene_after(0.4, "load")
	_dialogo(delta)
	if Sheet_Player.todos_mortos():
		GD.set_var("tela_dead", 4)
		go_scene("dead")
	_boss(delta)
	Sheet_ex_boos.run(self, delta)
func _begin() -> void:
	hide_objects(["acao_tiros", "acao_tiros2"])
	GD.set_fullscreen(true)
	GD.delete_all("boss_x")
	for pos in PLATAFORMAS:
		var pl = GD.create("plataforma_neon", pos.x, pos.y)
		if pl != null:
			pl.z_index = 8
	var m = GD.create("Mysterious", MYS_X, MYS_Y)
	m.z_index = 62
	m.set_flip_x(true)
	var beh = m.behavior("PlatformerObject")
	if beh != null:
		beh.ai_control = true
	GD.play_sound("Midnight_Asphalt_Pursuit.mp3", true)
	hide_objects(["ativa_dialogo_box", "Plataforma2", "Plataforma", "box_d", "txt_dialogo_final"])
	GDDialogue.load_from_json("dialogofinal")
	for t in GD.pick("txt_dialogo_final"):
		t.label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		t.label.custom_minimum_size = Vector2(770, 0)
		t.label.size = Vector2(770, 120)
	_after_intro()
func _after_intro() -> void:
	if not await GD.wait(2.0):
		return
	GD.delete_all("BasicExplosionEnergy")
	GD.set_var("tela_dead", 0)
	GD.set_var("tela_load", 0)
func _show(names: Array, on: bool) -> void:
	for n in names:
		for o in GD.pick(str(n)):
			if o is CanvasItem:
				o.visible = on
func _dialogo(delta: float) -> void:
	var p = GD.first("Player2")
	var wall = GD.first("ativa_dialogo_box")
	if dialogo == 0 and p != null and wall != null and wall.position.x - p.bbox_center().x < 60.0:
		GDDialogue.start_from_branch("Start")
		dialogo = 1
		_show(["box_d", "txt_dialogo_final"], true)
	if dialogo != 1:
		return
	if GDDialogue.is_text_line():
		GDDialogue.scroll(delta)
		GD.set_text("txt_dialogo_final", GDDialogue.clipped_text())
		if GD.key_released("q"):
			if GDDialogue.scrolling_completed():
				GDDialogue.go_to_next_line()
			else:
				GDDialogue._visible = float(GDDialogue._current().length())
				GD.set_text("txt_dialogo_final", GDDialogue.clipped_text())
	if not GDDialogue.is_text_line():
		GD.delete_all("ativa_dialogo_box")
		_show(["box_d", "txt_dialogo_final"], false)
		luta = 1
		dialogo = 2
func _elapsed(m) -> float:
	var i: int = clampi(m.anim_index, 0, TBF.size() - 1)
	return(float(m.anim.frame) + m.anim.frame_progress) * float(TBF[i])
func _anim(m, i: int, playing: bool) -> void:
	m.set_anim_index(i)
	if playing and not m.anim.is_playing():
		m.anim.play()
	elif not playing and m.anim.is_playing():
		m.anim.pause()
func _boss(delta: float) -> void:
	for f in BALAS:
		for b in GD.pick(f[0]):
			b.add_force_xy(float(b.ovar("vx")), float(b.ovar("vy")))
	var p = GD.first("Player2")
	_balas_do_boss(p)
	var m = GD.first("Mysterious")
	if m == null or p == null:
		return
	var mc: Vector2 = m.bbox_center()
	var pc: Vector2 = p.bbox_center()
	for bar in GD.pick("bar_monstro_life"):
		bar.set_xy(mc.x - bar.get_width() / 2.0, m.position.y - 10.0)
	m.set_flip_x(pc.x < mc.x)
	if luta != 1:
		_anim(m, 2, true)
		return
	_boss_ia(m, p, mc, pc, delta)
	_dano_no_boss(m)
	if GD.once("mys_morte", GD.bar_any_empty("bar_monstro_life")):
		GD.create("Holy_Explosion3", mc.x - 48.0, mc.y - 48.0)
		GD.create("portalF", PORTAL_X, 662.0 - 272.0)
		m.gd_delete()
		GD.delete_all("bar_monstro_life")
		GD.delete_after("Holy_Explosion3", 1.5)
func _boss_ia(m, p, mc: Vector2, pc: Vector2, delta: float) -> void:
	var beh = m.behavior("PlatformerObject")
	if beh == null:
		return
	var dx: = absf(pc.x - mc.x)
	var dy: = pc.y - mc.y
	if dx <= m.get_width() * 0.445 + 25.0 and absf(dy) < m.get_height() * 0.6:
		_parar_boss(beh)
		_anim(m, 1, true)
		if GD.once("mys_soco", _elapsed(m) >= SOCO_EM):
			if _escudo_ativo():
				GD.create("RedExplosion", pc.x, pc.y)
				GD.delete_after("RedExplosion", 0.5)
			else:
				Sheet_Player.dano(p, 25.0 * GD.get_num("mult_dano"))
				GD.create("RedExplosion2", pc.x, pc.y)
				GD.play_music("bzzzt.wav", false)
				GD.delete_after("RedExplosion2", 0.5)
		return
	if atirando:
		_parar_boss(beh)
		_anim(m, 0, true)
		atira_t += delta
		if GD.once("mys_tiro", _elapsed(m) >= TIRO_EM):
			var pt: Vector2 = m.point_pos("arma")
			var nome: = "bala_r1d" if m.is_flipped_x() else "bala_r1d2"
			var b = GD.create(nome, pt.x - 32.0, pt.y - 32.0)
			b.set_size(64.0, 64.0)
			_mira(b, nome == "bala_r1d", pc - pt, m.is_flipped_x())
			GD.play_music("weaponfire1.wav", false)
		if atira_t >= TIRO_DUR:
			atirando = false
			atira_t = 0.0
			cd_tiro = TIRO_CD
		return
	var quer_esq: = pc.x < mc.x - 20.0 and mc.x > BOSS_X_MIN
	var quer_dir: = pc.x > mc.x + 20.0 and mc.x < BOSS_X_MAX
	beh.ai_left = quer_esq
	beh.ai_right = quer_dir
	_anim(m, 2, true)
	cd_tiro -= delta
	cd_pulo -= delta
	if(quer_esq or quer_dir) and absf(beh.speed.x) < 10.0:
		preso_t += delta
	else:
		preso_t = 0.0
	if cd_tiro <= 0.0 and dx <= TIRO_DIST and beh.on_floor:
		if randi_range(1, 100) <= 50 + 10 * int(GD.get_num("dificuldade")):
			atirando = true
			atira_t = 0.0
			_parar_boss(beh)
			return
		cd_tiro = TIRO_RETRY
	if beh.on_floor and(cd_pulo <= 0.0 or preso_t > 0.15 or(dy < -80.0 and dx < 450.0)):
		pulo_hold = 0.25
		cd_pulo = BOSS_PULO_CD
	if pulo_hold > 0.0:
		pulo_hold -= delta
	beh.ai_jump = pulo_hold > 0.0
func _parar_boss(beh) -> void:
	beh.ai_left = false
	beh.ai_right = false
	beh.ai_jump = false
	pulo_hold = 0.0
func _balas_do_boss(p) -> void:
	for f in BALAS:
		for b in GD.pick(f[0]):
			if _escudo_bloqueia(b):
				_explode_bloqueado(b)
				continue
			if p != null and GD.once(GD.pair_key("mys_bala_" + str(f[0]), p, b), GD.collide_np(p, b)):
				var c: Vector2 = p.bbox_center()
				Sheet_Player.dano(p, 15.0 * GD.get_num("mult_dano"))
				GD.create("RedExplosion2", c.x, c.y)
				b.gd_delete()
				GD.delete_after("RedExplosion2", 1.5)
				continue
			var some: = false
			for w in["Plataforma", "Plataforma2", "bloco"]:
				for o in GD.pick(w):
					if GD.collide_np(b, o):
						some = true
			if some or b.position.y < -400.0 or(p != null and absf(b.position.x - p.position.x) > 2000.0):
				b.gd_delete()
# reto ou diagonal (45 graus) para o lado em que o chefe esta virado; gira a bala no centro
func _mira(b, para_esquerda: bool, d: Vector2, virado_esq: bool) -> void:
	var vx: = BALA_VEL
	var vy: = 0.0
	if d.y < - absf(d.x) * 0.414:
		vx = BALA_DIAG
		vy = - BALA_DIAG
	elif d.y > absf(d.x) * 0.414:
		vx = BALA_DIAG
		vy = BALA_DIAG
	if virado_esq:
		vx = - vx
	b.set_ovar("vx", vx)
	b.set_ovar("vy", vy)
	var ang: = rad_to_deg(atan2(vy, vx)) -(180.0 if para_esquerda else 0.0)
	var c: = Vector2(32.0, 32.0)
	b.set_angle(ang)
	b.position += c - c.rotated(deg_to_rad(ang))
func _shield_pickup() -> void:
	var pt: = GD.point_of("Player2", "escudo")
	var s = GD.create("Front_Shield_Pickup", pt.x, pt.y)
	s.set_size(150.0, 150.0)
	if not await GD.wait(3.0):
		return
	GD.delete_all("Front_Shield_Pickup")
func _escudo_ativo() -> bool:
	return not GD.pick("Front_Shield_Pickup").is_empty()
func _escudo_bloqueia(b) -> bool:
	for sh in GD.pick("Front_Shield_Pickup"):
		if GD.collide_np(b, sh):
			return true
	return false
func _escudo_bloqueia_drones() -> void:
	for n in["B2", "B3", "B4"]:
		for b in GD.pick(n):
			if _escudo_bloqueia(b):
				_explode_bloqueado(b)
func _explode_bloqueado(b) -> void:
	var c: Vector2 = b.bbox_center()
	GD.create("RedExplosion", c.x, c.y)
	GD.delete_after("RedExplosion", 1.5)
	b.gd_delete()
func _dano_no_boss(m) -> void:
	for bn in["bala1", "bala2"]:
		for b in GD.pick(bn):
			if GD.once(GD.pair_key("mys_dano_" + bn, b, m), GD.collide_np(b, m)):
				var c: Vector2 = m.bbox_center()
				GD.bar_set("bar_monstro_life", "-", GD.per_mult(10.0, "mult_hp"))
				GD.create("Holy_Explosion3", c.x - 48.0, c.y - 48.0)
				b.gd_delete()
				GD.delete_after("Holy_Explosion3", 1.5)
