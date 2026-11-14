class_name Sheet_Player
# v12: sistema de municao igual ao do PC (ferramentas/municao.py, 13/11/2026).
# Pente de 12, recarga de 1,2 s (R ou automatica), caixas "Municao" sorteadas entre pontos fixos.
# Insano (dificuldade 2): balas infinitas, sem caixas e sem contador.
const PENTE: = 12
const RECARGA: = 1.2
const CAIXAS: = {
	"cena1": { "n": 2, "d": 1, "pts":[[2008, 330],[2500, 462],[3260, 462],[3758, 332],[4700, 462]] },
	"cena2": { "n": 7, "d": 6, "pts":[[700, 468],[1330, 468],[1950, 468],[2722, 335],[3300, 468],[4128, 347],[4760, 468],[5560, 468],[6420, 468],[7600, 338]] },
	"cena3": { "n": 4, "d": 3, "pts":[[1300, 461],[2018, 342],[3000, 461],[4338, 331],[5304, 331],[6650, 461],[8300, 461]] },
	"final": { "n": 2, "d": 1, "pts":[[1300, 596],[2000, 596],[2700, 596]] },
}
static func run(layout: GDLayout, _delta: float) -> void:
	if layout.scene_just_begins:
		for b in GD.pick("bar_vida_play"):
			b.set_value("=", b.value())
		_ammo_begin()
	if GD.key_held("Left"):
		for p in GD.pick("Player2"):
			p.set_anim_index(1)
			p.set_flip_x(true)
	if GD.key_held("Right"):
		for p in GD.pick("Player2"):
			p.set_anim_index(1)
			p.set_flip_x(false)
	if GD.key_released("Left"):
		for p in GD.pick("Player2"):
			p.set_flip_x(true)
			p.set_anim_index(0)
	if GD.key_released("Right"):
		for p in GD.pick("Player2"):
			p.set_flip_x(false)
			p.set_anim_index(0)
	for b in GD.pick("bala1"):
		b.add_force_xy(450, 0)
	for b in GD.pick("bala2"):
		b.add_force_xy(-450, 0)
	for p in GD.pick("Player2"):
		GD.center_camera(p)
		GD.center_camera(p,["bg"])
		GD.center_camera(p,["predios"])
	for p in GD.pick("Player2"):
		if GD.once("player_fire1_%d" % p.get_instance_id(), GD.key_held("f") and not p.is_flipped_x() and _can_fire()):
			p.set_anim_index(2)
			GD.create("bala1", p.point_x("disparo"), p.point_y("disparo"))
			GD.set_var("pente", GD.get_num("pente") - 1)
			GD.play_music("weaponfire1.wav", false)
	if GD.key_released("f"):
		for p in GD.pick("Player2"):
			p.set_anim_index(0)
	for p in GD.pick("Player2"):
		if GD.once("player_fire2_%d" % p.get_instance_id(), GD.key_held("f") and p.is_flipped_x() and _can_fire()):
			p.set_anim_index(2)
			GD.create("bala2", p.point_x("disparo"), p.point_y("disparo"))
			GD.set_var("pente", GD.get_num("pente") - 1)
			GD.play_music("weaponfire1.wav", false)
	_cull_far_shots()
	_hit_by_bullet(layout, "B2", "BlueExplosion")
	_hit_by_bullet(layout, "B3", "BlueExplosion2")
	_hit_by_bullet(layout, "B4", "BlueExplosion3")
	for p in GD.pick("Player2"):
		for u in GD.pick("upvida"):
			if GD.collide_np(p, u):
				for b in GD.pick("bar_vida_play"):
					b.set_value("=", 200)
				u.gd_delete()
		for r in GD.pick("Rocket_Pickup"):
			if GD.collide_np(p, r):
				_add_reserve()
				r.gd_delete()
	_ammo(_delta)
static func _dif() -> float:
	return GD.get_num("dificuldade")
static func _insano() -> bool:
	return _dif() >= 2.0
static func _can_fire() -> bool:
	return GD.get_num("pente") > 0.0 and GD.get_num("recarga") <= 0.0
static func _add_reserve() -> void:
	GD.set_var("reserva", minf(GD.get_num("reserva") + 24.0 + 6.0 * _dif(), 96.0))
# inicio da cena: pente cheio, reserva pela dificuldade, caixas sorteadas e contador no GUI
static func _ammo_begin() -> void:
	GD.set_var("pente", PENTE)
	GD.set_var("recarga", 0.0)
	GD.set_var("emergencia", 0.0)
	GD.set_var("reserva", 36.0 if _dif() < 1.0 else 24.0)
	GD.delete_all("Rocket_Pickup")
	if not CAIXAS.has(GD.layout_name):
		return
	var cfg: Dictionary = CAIXAS[GD.layout_name]
	var alvo: = 0
	if _dif() < 1.0:
		alvo = int(cfg["n"])
	elif not _insano():
		alvo = int(cfg["d"])
	GD.set_var("alvo_municao", alvo)
	var pts: Array = (cfg["pts"] as Array).duplicate()
	pts.shuffle()
	for i in mini(alvo, pts.size()):
		var c = GD.create("Municao", float(pts[i][0]), float(pts[i][1]))
		c.z_index = 8
	var t = GD.create("txt_municao", 70.0, 46.0, "GUI")
	t.z_index = 17
	if _insano():
		t.visible = false
static func _ammo(delta: float) -> void:
	var nao_insano: = not _insano()
	if not nao_insano:
		GD.set_var("pente", PENTE)
		GD.set_var("recarga", 0.0)
	# gatilho sem bala
	if GD.once("ammo_dry", GD.key_held("f") and GD.get_num("pente") <= 0.0 and nao_insano):
		GD.play_sound("thunk.wav", false, 60.0, 1.6)
	# recarga automatica (pente vazio) ou manual (R)
	if GD.get_num("pente") <= 0.0 and GD.get_num("reserva") > 0.0 and GD.get_num("recarga") <= 0.0 and nao_insano:
		GD.set_var("recarga", RECARGA)
		GD.play_sound("thunk2.wav", false, 80.0, 1.0)
	if GD.key_held("r") and GD.get_num("pente") < PENTE and GD.get_num("reserva") > 0.0 and GD.get_num("recarga") <= 0.0 and nao_insano:
		GD.set_var("recarga", RECARGA)
		GD.play_sound("thunk2.wav", false, 80.0, 1.0)
	if GD.get_num("recarga") > 0.0:
		GD.set_var("recarga", GD.get_num("recarga") - delta)
		if GD.get_num("recarga") <= 0.0:
			var n: = minf(PENTE - GD.get_num("pente"), GD.get_num("reserva"))
			GD.set_var("n_recarga", n)
			GD.set_var("pente", GD.get_num("pente") + n)
			GD.set_var("reserva", GD.get_num("reserva") - n)
			GD.set_var("recarga", 0.0)
			GD.play_sound("thunk.wav", false, 70.0, 1.0)
	# rede de seguranca: sem nenhuma bala, ganha 6 depois de 5 s (Normal) ou 8 s (Dificil)
	if GD.get_num("pente") <= 0.0 and GD.get_num("reserva") <= 0.0 and GD.get_num("recarga") <= 0.0 and nao_insano:
		GD.set_var("emergencia", GD.get_num("emergencia") + delta)
		if GD.get_num("emergencia") >= 5.0 + 3.0 * _dif():
			GD.set_var("reserva", 6.0)
			GD.set_var("emergencia", 0.0)
	# pegar caixa
	if nao_insano:
		var got: = false
		for p in GD.pick("Player2"):
			for c in GD.pick("Municao"):
				if GD.collide_np(p, c):
					got = true
					c.gd_delete()
		if got:
			_add_reserve()
			GD.set_var("emergencia", 0.0)
			GD.play_sound("laserthing.wav", false, 70.0, 1.4)
	# HUD
	for b in GD.pick("balas"):
		b.set_value("=", GD.get_num("pente"))
	if nao_insano:
		var pente: = GD.get_num("pente")
		var reserva: = GD.get_num("reserva")
		if GD.get_num("recarga") > 0.0:
			GD.set_text("txt_municao", "RECARREGANDO...")
		elif pente <= 0.0 and reserva <= 0.0:
			GD.set_text("txt_municao", "SEM BALAS!")
		else:
			GD.set_text("txt_municao", "%d / %d" %[int(pente), int(reserva)])
static func _cull_far_shots() -> void:
	var p = GD.first("Player2")
	if p == null:
		return
	for n in["bala1", "bala2"]:
		for b in GD.pick(n):
			if absf(b.position.x - p.position.x) > 2000.0:
				b.gd_delete()
static func _bars_add(bar_name: String, op: String, v: float) -> void:
	for b in GD.pick(bar_name):
		b.set_value(op, v)
static func _hit_by_bullet(_layout: GDLayout, bullet_name: String, fx_name: String) -> void:
	for p in GD.pick("Player2"):
		for b in GD.pick(bullet_name):
			if GD.once("player_hit_%s_%d" %[bullet_name, b.get_instance_id()], GD.collide_np(p, b)):
				b.gd_delete()
				var c: Vector2 = p.bbox_center()
				GD.create(fx_name, c.x, c.y)
				_damage_after_explosion(fx_name)
static func _damage_after_explosion(fx_name: String) -> void:
	if not await GD.wait(0.3):
		return
	GD.delete_all(fx_name)
	_bars_add("bar_vida_play", "-", 10 * GD.get_num("mult_dano"))
