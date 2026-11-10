class_name Sheet_ex_robo_tiros
const SHOOT_ZONES: =[
	["ad1", "robo_a", "bala_r1d", "m_bala"],
	["ed1", "robo_a", "bala_r1d2", "m_bala"],
	["ad2", "robo_a2", "bala_r2d1", "m2_bala"],
	["ed2", "robo_a2", "bala_r2d2", "m2_bala"],
	["ad3", "robo_a3", "bala_r3d1", "m3_bala"],
	["ed3", "robo_a3", "bala_r3d2", "m3_bala"],
]
const SHOT_FORCES: =[
	["bala_r1d", -500.0],["bala_r1d2", 500.0],["bala_r2d1", -500.0],
	["bala_r2d2", 500.0],["bala_r3d2", 500.0],["bala_r3d1", -500.0],
]
const PLAYER_HIT_SHOTS: =["bala_r1d", "bala_r1d2", "bala_r2d1", "bala_r2d2", "bala_r3d1", "bala_r3d2"]
const TURRET_HITS: =[
	["bala1", "robo_a", "barv1", "bazu"],
	["bala2", "robo_a", "barv1", "bazu"],
	["bala1", "robo_a2", "barv2", "bazu2"],
	["bala2", "robo_a2", "barv2", "bazu2"],
	["bala2", "robo_a3", "barv3", "bazu3"],
	["bala1", "robo_a3", "barv3", "bazu3"],
]
static func run(layout: GDLayout, _delta: float) -> void:
	if layout.scene_just_begins:
		_begin()
	for f in SHOT_FORCES:
		for b in GD.pick(f[0]):
			b.add_force_xy(f[1], 0.0)
	_turrets_shoot()
	_turrets_take_damage()
	_turrets_states()
	_shots_hit_player()
	_cull_far_shots()
static func _cull_far_shots() -> void:
	var p = GD.first("Player2")
	if p == null:
		return
	for name in PLAYER_HIT_SHOTS:
		for b in GD.pick(name):
			if absf(b.position.x - p.position.x) > 2500.0:
				b.gd_delete()
static func _begin() -> void:
	for n in["ad1", "ad2", "ad3", "ed1", "ed2", "ed3"]:
		for z in GD.pick(n):
			if z is CanvasItem:
				z.visible = false
	for n in["barv1", "barv2", "barv3"]:
		for b in GD.pick(n):
			b.set_value("=", b.value())
	for n in["robo_a", "robo_a2", "robo_a3"]:
		for r in GD.pick(n):
			r.set_anim_index(1)
static func _turrets_shoot() -> void:
	for s in SHOOT_ZONES:
		for p in GD.pick("Player2"):
			for z in GD.pick(s[0]):
				if GD.once(GD.pair_key("ex_tiros_zone_" + s[0], p, z), GD.collide_np(p, z)):
					for r in GD.pick(s[1]):
						r.set_anim_index(2)
					var pt: = GD.point_of(s[1], s[3])
					GD.create(s[2], pt.x, pt.y)
					for b in GD.pick(s[2]):
						b.set_size(64.0, 64.0)
static func _turrets_take_damage() -> void:
	var dmg: = GD.per_mult(12.0, "mult_hp")
	for h in TURRET_HITS:
		for b in GD.pick(h[0]):
			for r in GD.pick(h[1]):
				if GD.once(GD.pair_key("ex_tiros_hit_" + h[0] + h[1], b, r), GD.collide_np(b, r)):
					var c: Vector2 = r.bbox_center()
					GD.create(h[3], c.x, c.y)
					GD.bar_set(h[2], "-", dmg)
					b.gd_delete()
					GD.delete_after(h[3], 1.5)
					break
static func _turrets_states() -> void:
	if GD.once("ex_tiros_dies_1", GD.bar_any_empty("barv1")):
		_turret_one_dies()
	if GD.once("ex_tiros_dies_2", GD.bar_any_empty("barv2")):
		_turret_two_dies()
	if GD.once("ex_tiros_dies_3", GD.bar_any_empty("barv3")):
		_turret_three_dies()
static func _turret_one_dies() -> void:
	for r in GD.pick("robo_a"):
		r.set_anim_index(3)
	GD.delete_all("ad1")
	GD.delete_all("ed1")
	if not await GD.wait(1.5):
		return
	GD.delete_all("robo_a")
static func _turret_two_dies() -> void:
	for r in GD.pick("robo_a2"):
		r.set_anim_index(3)
		var c: Vector2 = r.bbox_center()
		var up = GD.create("upvida", c.x - 22.0, c.y - 45.0)
		up.set_size(45.0, 91.0)
	GD.delete_all("ad2")
	GD.delete_all("ed2")
	if not await GD.wait(1.5):
		return
	GD.delete_all("robo_a2")
static func _turret_three_dies() -> void:
	for r in GD.pick("robo_a3"):
		r.set_anim_index(3)
	GD.delete_all("ad3")
	GD.delete_all("ed3")
	if not await GD.wait(1.5):
		return
	GD.delete_all("robo_a3")
static func _shots_hit_player() -> void:
	for name in PLAYER_HIT_SHOTS:
		for b in GD.pick(name):
			for p in GD.pick("Player2"):
				if GD.once(GD.pair_key("ex_tiros_player_" + name, b, p), GD.collide_np(p, b)):
					GD.bar_set("bar_vida_play", "-", 15.0 * GD.get_num("mult_dano"))
					var c: Vector2 = p.bbox_center()
					GD.create("RedExplosion2", c.x, c.y)
					b.gd_delete()
					if name == "bala_r2d2":
						GD.delete_all("RedExplosion2")
					else:
						GD.delete_after("RedExplosion2", 1.5)
					break
