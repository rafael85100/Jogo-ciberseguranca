extends GDLayout
# Cena final (v11): conversa com o boss Mysterious e luta. Espelha os eventos da cena "final" do
# game.json de 11/11/2026. O Mysterious nao esta no final.scn: ele e criado no inicio da cena.
const MYS_X: = 770.0
const MYS_Y: = 512.0
const TIRO_DIST: = 650.0
const TBF: =[0.08, 0.06, 0.1]
const TIRO_EM: = 0.72
const SOCO_EM: = 0.42
const BALAS: =[["bala_r1d", -500.0],["bala_r1d2", 500.0]]
var dialogo: = 0
var luta: = 0
func _events(delta: float) -> void:
	if scene_just_begins:
		_begin()
	Sheet_Player.run(self, delta)
	Sheet_ex_inimigos.homing_bullets()
	Sheet_ex_inimigos.run(self, delta)
	if touching("Player2", "portalF"):
		for ptl in GD.pick("portal"):
			ptl.set_anim_index(1)
		GD.set_var("tela_load", 5)
		go_scene_after(0.4, "load")
	_dialogo(delta)
	if GD.bar_any_empty("bar_vida_play"):
		GD.set_var("tela_dead", 4)
		go_scene("dead")
	_boss()
	Sheet_ex_boos.run(self, delta)
func _begin() -> void:
	hide_objects(["acao_tiros", "acao_tiros2"])
	GD.set_fullscreen(true)
	GD.delete_all("boss_x")
	var m = GD.create("Mysterious", MYS_X, MYS_Y)
	m.z_index = 62
	m.set_flip_x(true)
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
# conversa: comeca uma vez so, quando o robo chega perto da parede; Q completa a fala ou passa
# para a proxima; quando acaba, a parede some e a luta comeca
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
	return (float(m.anim.frame) + m.anim.frame_progress) * float(TBF[i])
func _anim(m, i: int, playing: bool) -> void:
	m.set_anim_index(i)
	if playing and not m.anim.is_playing():
		m.anim.play()
	elif not playing and m.anim.is_playing():
		m.anim.pause()
func _boss() -> void:
	for f in BALAS:
		for b in GD.pick(f[0]):
			b.add_force_xy(f[1], 0.0)
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
	var dx: = absf(pc.x - mc.x)
	var dy: = absf(pc.y - mc.y)
	var modo: = 3
	if luta == 1:
		modo = 0
		if dx <= TIRO_DIST:
			modo = 1
		if dx <= m.get_width() * 0.445 + 25.0 and dy < m.get_height() * 0.6:
			modo = 2
	if modo == 3:
		_anim(m, 2, true)
	elif modo == 0:
		_anim(m, 0, false)
	elif modo == 1:
		_anim(m, 0, true)
		if GD.once("mys_tiro", _elapsed(m) >= TIRO_EM):
			var pt: Vector2 = m.point_pos("arma")
			var nome: = "bala_r1d" if m.is_flipped_x() else "bala_r1d2"
			var b = GD.create(nome, pt.x - 32.0, pt.y - 32.0)
			b.set_size(64.0, 64.0)
			GD.play_music("weaponfire1.wav", false)
	elif modo == 2:
		_anim(m, 1, true)
		if GD.once("mys_soco", _elapsed(m) >= SOCO_EM):
			GD.bar_set("bar_vida_play", "-", 25.0 * GD.get_num("mult_dano"))
			GD.create("RedExplosion2", pc.x, pc.y)
			GD.play_music("bzzzt.wav", false)
			GD.delete_after("RedExplosion2", 0.5)
	if luta == 1:
		_dano_no_boss(m)
		if GD.once("mys_morte", GD.bar_any_empty("bar_monstro_life")):
			GD.create("Holy_Explosion3", mc.x - 48.0, mc.y - 48.0)
			GD.create("portalF", mc.x - 175.0, 662.0 - 272.0)
			m.gd_delete()
			GD.delete_all("bar_monstro_life")
			GD.delete_after("Holy_Explosion3", 1.5)
func _balas_do_boss(p) -> void:
	for f in BALAS:
		for b in GD.pick(f[0]):
			if p != null and GD.once(GD.pair_key("mys_bala_" + str(f[0]), p, b), GD.collide_np(p, b)):
				var c: Vector2 = p.bbox_center()
				GD.bar_set("bar_vida_play", "-", 15.0 * GD.get_num("mult_dano"))
				GD.create("RedExplosion2", c.x, c.y)
				b.gd_delete()
				GD.delete_after("RedExplosion2", 1.5)
				continue
			var some: = false
			for w in["Plataforma", "Plataforma2", "bloco"]:
				for o in GD.pick(w):
					if GD.collide_np(b, o):
						some = true
			if some or (p != null and absf(b.position.x - p.position.x) > 2500.0):
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
