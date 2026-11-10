class_name Sheet_ex_serpente
const BOSS_LEGS: =[
	["c1", "ir_para_c2", "c2"],
	["c2", "ir_para_c3", "c3"],
	["c3", "ir_para_c4", "c4"],
	["c4", "ir_para_c5", "c5"],
	["c5", "ir_para_c1", "c1"],
]
const MONSTER_LEGS: =[
	["n1", "monstro_alado", "ir_n2", "n2",["vortex", "vortex2"]],
	["n2", "monstro_alado", "ir_n3", "n3",["vortex", "vortex2"]],
	["n3", "monstro_alado", "ir_n1", "n1",["vortex", "vortex2"]],
	["n4", "monstro_alado2", "ir_n5", "n5",["vortex3", "vortex4"]],
	["n5", "monstro_alado2", "ir_n6", "n6",["vortex3", "vortex4"]],
	["n6", "monstro_alado2", "ir_n4", "n4",["vortex3", "vortex4"]],
]
const VORTEXES: =["vortex", "vortex2", "vortex3", "vortex4"]
const STARS: =["Starry_Background_Big_Star_1", "Starry_Background_Big_Star_2"]
const SHOTS: =["bala1", "bala2"]
static func run(layout: GDLayout, _delta: float) -> void:
	if layout.scene_just_begins:
		_begin()
	var player = GD.first("Player2")
	for s in GD.pick("Starry_Background_Big_Star_1"):
		s.add_force_toward_object(player, 200.0)
	for s in GD.pick("Starry_Background_Big_Star_2"):
		s.add_force_toward_object(player, -200.0)
	_boss_start()
	_boss_legs()
	_stars_hit_player()
	for shot in SHOTS:
		_shot_hits("lagarto_boss4", shot, "MetalRedBar", "Holy_Explosion2", GD.per_mult(10.0, "mult_hp"))
	var lights: =["red_luz", "red_luz2", "red_luz3", "red_luz4"]
	for i in lights.size():
		_set_xy(lights[i], "lagarto_boss4", "luz%d" %(i + 1))
	_set_xy("w_bar", "monstro_alado", "barra")
	_set_xy("w_bar2", "monstro_alado2", "barra")
	for v in VORTEXES:
		for vv in GD.pick(v):
			vv.add_force_toward_object(player, 480.0)
	_monsters_patrol()
	_vortexes_hit_player()
	_shield_stops_vortexes()
	for shot in SHOTS:
		_shot_hits("monstro_alado", shot, "w_bar", "Holy_Explosion4", GD.per_mult(12.0, "mult_hp"))
	_monster_one_dies()
	_monster_two_dies()
	_barrier_stops_vortexes()
	_monster_two_appears()
	for shot in SHOTS:
		_shot_hits("monstro_alado2", shot, "w_bar2", "Holy_Explosion3", GD.per_mult(12.0, "mult_hp"))
	_monster_two_vanishes()
	_shield_hits_stars()
	_boss_low()
	_boss_defeated_check()
static func _begin() -> void:
	boss_defeated = false
	for n in["c1", "c2", "c3", "c4", "c5", "c6", "b1", "b2", "n1", "n2", "n3", "n4", "n5", "n6", "barrreirainicio", "acao_tiros3"]:
		for o in GD.pick(n):
			if o is CanvasItem:
				o.visible = false
	for n in["MetalRedBar", "w_bar", "w_bar2"]:
		for b in GD.pick(n):
			b.set_value("=", b.value())
	for m in GD.pick("monstro_alado"):
		m.set_flip_x(true)
static func _set_xy(obj_name: String, src: String, point: String) -> void:
	var p: = GD.point_of(src, point)
	for o in GD.pick(obj_name):
		o.set_xy(p.x, p.y)
static func _tween_to(obj, tween_name: String, zone: String, seconds: float) -> void:
	var p: = GD.pos_of(zone)
	var t = obj.behavior("Tween")
	if t != null:
		t.add_object_position_tween2(tween_name, p.x, p.y, "linear", seconds)
static func _boss_start() -> void:
	var cond: bool = not GD.pick("lagarto_boss3").is_empty() and GD.key_released("x")
	if not GD.once("ex_serp_boss_start", cond):
		return
	GD.delete_all("lagarto_boss3")
	var boss = GD.create("lagarto_boss4", 7805.0, 54.0)
	boss.set_size(200.0, 236.0)
	boss.set_flip_x(true)
	GD.play_sound("thunk2.wav")
	_tween_to(boss, "ir_para_c1", "c1", 3.0)
	GD.delete_all("box_lagarto")
	GD.delete_all("NewText")
static func _boss_legs() -> void:
	for leg in BOSS_LEGS:
		for z in GD.pick(leg[0]):
			for boss in GD.pick("lagarto_boss4"):
				if GD.once(GD.pair_key("ex_serp_leg_" + leg[1], z, boss), GD.collide_np(boss, z)):
					_tween_to(boss, leg[1], leg[2], 3.0)
					var pt: = GD.point_of("lagarto_boss4", "disparol")
					var star = GD.create("Starry_Background_Big_Star_1", pt.x - 80.0, pt.y - 80.0)
					star.set_size(160.0, 160.0)
					GD.play_sound("thunk2.wav")
					GD.delete_after("Starry_Background_Big_Star_1", 4.0)
static func _stars_hit_player() -> void:
	for star in STARS:
		for s in GD.pick(star):
			for p in GD.pick("Player2"):
				if GD.collide_np(s, p):
					var c: Vector2 = s.bbox_center()
					GD.create("RedExplosion2", c.x, c.y)
					GD.bar_set("bar_vida_play", "-", 8.0 * GD.get_num("mult_dano"))
					s.gd_delete()
					break
static func _shot_hits(target: String, shot: String, bar: String, fx: String, dmg: float) -> void:
	for b in GD.pick(shot):
		for t in GD.pick(target):
			if GD.once(GD.pair_key("ex_serp_hit_" + target + shot, b, t), GD.collide_np(b, t)):
				GD.bar_set(bar, "-", dmg)
				var c: Vector2 = t.bbox_center()
				GD.create(fx, c.x - 48.0, c.y - 48.0)
				b.gd_delete()
				GD.delete_after(fx, 1.5)
				break
static func _monsters_patrol() -> void:
	for leg in MONSTER_LEGS:
		for z in GD.pick(leg[0]):
			for m in GD.pick(leg[1]):
				if GD.once(GD.pair_key("ex_serp_patrol_" + leg[2], z, m), GD.collide_np(z, m)):
					_tween_to(m, leg[2], leg[3], 3.0)
					var pt: = GD.point_of(leg[1], "tiro")
					for v in leg[4]:
						GD.create(v, pt.x, pt.y)
static func _vortexes_hit_player() -> void:
	for v in VORTEXES:
		for vv in GD.pick(v):
			for p in GD.pick("Player2"):
				if GD.once(GD.pair_key("ex_serp_vortex_player_" + v, vv, p), GD.collide_np(p, vv)):
					GD.bar_set("bar_vida_play", "-", 10.0 * GD.get_num("mult_dano"))
					vv.gd_delete()
static func _shield_stops_vortexes() -> void:
	for v in VORTEXES:
		for vv in GD.pick(v):
			for sh in GD.pick("Front_Shield_Pickup"):
				if GD.collide_np(sh, vv):
					vv.gd_delete()
					break
static func _barrier_stops_vortexes() -> void:
	for bar in GD.pick("barrreirainicio"):
		for vv in GD.pick("vortex"):
			if GD.collide_np(bar, vv):
				GD.delete_all("vortex")
				GD.delete_all("vortex2")
static func _monster_one_dies() -> void:
	if not GD.once("ex_serp_m1_dead", GD.bar_any_empty("w_bar")):
		return
	GD.delete_all("monstro_alado")
	var n1: = GD.pos_of("n1")
	var n2: = GD.pos_of("n2")
	var up = GD.create("upvida", n1.x, n2.y)
	up.set_size(45.0, 91.0)
static func _monster_two_appears() -> void:
	for z in GD.pick("acao_tiros3"):
		for p in GD.pick("Player2"):
			if GD.once(GD.pair_key("ex_serp_spawn_m2", z, p), GD.collide_np(p, z)):
				var m = GD.create("monstro_alado2", 2485.0, 208.0)
				m.set_size(215.0, 215.0)
				m.set_flip_x(true)
				GD.delete_all("acao_tiros3")
static func _monster_two_dies() -> void:
	if not GD.once("ex_serp_m2_dead", GD.bar_any_empty("w_bar2")):
		return
	GD.delete_all("monstro_alado2")
	var n4: = GD.pos_of("n4")
	var up = GD.create("upvida", n4.x, n4.y)
	up.set_size(45.0, 91.0)
static func _monster_two_vanishes() -> void:
	if GD.once("ex_serp_m2_vanish", GD.bar_any_empty("w_bar2")):
		GD.delete_after("monstro_alado2", 3.0)
static func _shield_hits_stars() -> void:
	for star in STARS:
		for s in GD.pick(star):
			for sh in GD.pick("Front_Shield_Pickup"):
				if GD.collide_np(sh, s):
					var c: Vector2 = sh.bbox_center()
					GD.create("RedExplosion", c.x, c.y)
					s.gd_delete()
					GD.delete_after("RedExplosion", 1.5)
					break
static func _boss_low() -> void:
	var low: = false
	for b in GD.pick("MetalRedBar"):
		if b.value() <= 100.0:
			low = true
	if not GD.once("ex_serp_boss_low", low):
		return
	var c: = GD.center_of("lagarto_boss4")
	var up = GD.create("upvida", c.x - 22.0, c.y - 45.0)
	up.set_size(45.0, 95.0)
static var boss_defeated: = false
static func _boss_defeated_check() -> void:
	if GD.once("ex_serp_boss_dead", GD.bar_any_empty("MetalRedBar") and not GD.pick("lagarto_boss4").is_empty()):
		boss_defeated = true
		_defeat_boss()
static func _defeat_boss() -> void:
	for n in["c1", "c2", "c3", "c4", "c5"]:
		GD.delete_all(n)
	var c: = GD.center_of("lagarto_boss4")
	GD.create("BlueExplosion3", c.x, c.y)
	if not await GD.wait(1.5):
		return
	GD.delete_all("lagarto_boss4")
	GD.delete_all("barreira1")
	GD.delete_all("barreira2")
	GD.delete_all("BlueExplosion3")
