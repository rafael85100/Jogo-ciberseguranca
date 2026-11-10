class_name Sheet_ex_robo
const ROBOTS: =["robo_z", "robo_z2", "robo_z3", "robo_z4", "robo_z5", "robo_z6", "robo_z7"]
const ZONES: =["pz", "pz2", "pz3", "pz4", "pz5", "pz6", "pz7"]
const BARS: =["barZ", "barZ2", "barZ3", "barZ4", "barZ5", "barZ6", "barZ7"]
const BAZUS: =["bazu", "bazu2", "bazu3", "bazu4", "bazu5", "bazu6", "bazu7"]
const BAR_POINTS: =["zbarra", "z2", "z3", "z4", "z5", "z6", "z7"]
static func run(layout: GDLayout, _delta: float) -> void:
	if layout.scene_just_begins:
		_begin()
	_zones_start_attack()
	_robots_touch_player()
	_bars_follow()
	_bullets_hit_robots()
	for i in ROBOTS.size():
		if GD.once("ex_robo_vanish_%d" % i, GD.bar_any_empty(BARS[i])):
			_robot_vanishes(i)
	_destroy_robots()
static func _begin() -> void:
	for n in ZONES:
		for z in GD.pick(n):
			if z is CanvasItem:
				z.visible = false
	for n in BARS:
		for b in GD.pick(n):
			b.set_value("=", b.value())
static func _zones_start_attack() -> void:
	for i in ZONES.size():
		for p in GD.pick("Player2"):
			for z in GD.pick(ZONES[i]):
				if GD.once(GD.pair_key("ex_robo_zone_%d" % i, p, z), GD.collide_np(p, z)):
					_charge(i, z)
static func _charge(i: int, zone) -> void:
	for r in GD.pick(ROBOTS[i]):
		r.add_force_toward_object(GD.first("Player2"), 350.0)
		r.set_anim_index(1)
	if not await GD.wait(5.0):
		return
	for r in GD.pick(ROBOTS[i]):
		if is_instance_valid(zone) and not zone.gd_deleted:
			r.add_force_toward_object(zone, 350.0)
static func _robots_touch_player() -> void:
	for i in ROBOTS.size():
		for r in GD.pick(ROBOTS[i]):
			for p in GD.pick("Player2"):
				if GD.once(GD.pair_key("ex_robo_touch_%d" % i, r, p), GD.collide_np(r, p)):
					GD.bar_set("bar_vida_play", "-", 30.0 * GD.get_num("mult_dano"))
					GD.play_music("bzzzt.wav", false)
static func _bars_follow() -> void:
	var c: = GD.point_of("robo_z", "zbarra")
	for b in GD.pick("barZ"):
		b.set_center(c.x, c.y)
	for i in range(1, ROBOTS.size()):
		var p: = GD.point_of(ROBOTS[i], BAR_POINTS[i])
		for b in GD.pick(BARS[i]):
			b.set_xy(p.x, p.y)
	for pair in[["barv1", "robo_a", "bar_v1"],["barv2", "robo_a2", "bar_v2"],["barv3", "robo_a3", "bar_v3"]]:
		var q: = GD.point_of(pair[1], pair[2])
		for b in GD.pick(pair[0]):
			b.set_xy(q.x, q.y)
static func _bullets_hit_robots() -> void:
	var dmg: = GD.per_mult(10.0, "mult_hp")
	for i in ROBOTS.size():
		for bullet in["bala1", "bala2"]:
			for b in GD.pick(bullet):
				for r in GD.pick(ROBOTS[i]):
					if GD.once(GD.pair_key("ex_robo_hit_%d" % i, b, r), GD.collide_np(b, r)):
						for bar in GD.pick(BARS[i]):
							bar.set_value("-", dmg)
						var c: Vector2 = r.bbox_center()
						GD.create(BAZUS[i], c.x, c.y)
						b.gd_delete()
						break
static func _robot_vanishes(i: int) -> void:
	for r in GD.pick(ROBOTS[i]):
		r.set_anim_index(4)
	if not await GD.wait(1.0):
		return
	GD.delete_all(ROBOTS[i])
static func _destroy_robots() -> void:
	for i in ROBOTS.size():
		if GD.once("ex_robo_destroy_%d" % i, GD.bar_any_empty(BARS[i])):
			_destroy(i, i == 3)
static func _destroy(i: int, with_pickup: bool) -> void:
	for r in GD.pick(ROBOTS[i]):
		r.set_anim_index(4)
		if with_pickup:
			var c: Vector2 = r.bbox_center()
			var up = GD.create("upvida", c.x - 22.0, c.y - 45.0)
			up.set_size(45.0, 91.0)
	if not await GD.wait(1.5):
		return
	GD.delete_all(ROBOTS[i])
	GD.delete_all(ZONES[i])
