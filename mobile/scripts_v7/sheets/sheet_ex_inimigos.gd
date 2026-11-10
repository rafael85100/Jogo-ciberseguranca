class_name Sheet_ex_inimigos
static func run(layout: GDLayout, _delta: float) -> void:
	for bar in GD.pick("GreenFlatBar2"):
		var pt: = GD.point_of("drone2", "barravida")
		bar.set_center(pt.x, pt.y)
	for bar in GD.pick("GreenFlatBar3"):
		var pt: = GD.point_of("drone3", "bvida3")
		bar.set_center(pt.x, pt.y)
	for bar in GD.pick("GreenFlatBar4"):
		var pt: = GD.point_of("drone4", "bvida4")
		bar.set_center(pt.x, pt.y)
	if layout.scene_just_begins:
		for n in["GreenFlatBar2", "GreenFlatBar3", "GreenFlatBar4"]:
			for b in GD.pick(n):
				b.set_value("=", b.value())
	var dmg: = 10.0 / maxf(GD.get_num("mult_hp"), 0.0001)
	_bullet_hit("bala1", "drone2", "GreenFlatBar2", dmg, "RedExplosion", "RedExplosion", true)
	_bullet_hit("bala1", "drone3", "GreenFlatBar3", dmg, "RedExplosion2", "RedExplosion2", false)
	_bullet_hit("bala1", "drone4", "GreenFlatBar4", dmg, "RedExplosion3", "RedExplosion3", false)
	_bullet_hit("bala2", "drone2", "GreenFlatBar2", dmg, "RedExplosion", "RedExplosion2", false)
	_bullet_hit("bala2", "drone3", "GreenFlatBar3", dmg, "RedExplosion2", "RedExplosion3", false)
	_bullet_hit("bala2", "drone4", "GreenFlatBar4", dmg, "RedExplosion3", "RedExplosion3", true)
	if GD.once("ex_drone2_dies", _any_empty("GreenFlatBar2")):
		_drone_dies_with_pickup(GD.first("drone2"), "drone2", "Holy_Explosion", "B2")
	if GD.once("ex_drone3_dies", _any_empty("GreenFlatBar3")):
		_drone_dies_plain("drone3", "Holy_Explosion2", "B3")
	if GD.once("ex_drone4_dies", _any_empty("GreenFlatBar4")):
		_drone_dies_with_pickup(GD.first("drone4"), "drone4", "Holy_Explosion4", "B4")
		GD.delete_all("acao_tiros")
		GD.delete_all("acao_tiros2")
static func homing_bullets() -> void:
	var p = GD.first("Player2")
	if p == null:
		return
	for n in["B2", "B3", "B4"]:
		for b in GD.pick(n):
			b.add_force_toward_object(p, 400.0)
static func trigger_zone(zone: String) -> void:
	for p in GD.pick("Player2"):
		for z in GD.pick(zone):
			if GD.once(GD.pair_key("drones_" + zone, p, z), GD.collide_np(p, z)):
				drones_fire()
static func drones_fire() -> void:
	var p2: = GD.point_of("drone2", "olho")
	GD.create("B2", p2.x, p2.y)
	if not await GD.wait(2.0):
		return
	var p3: = GD.point_of("drone3", "olho")
	GD.create("B3", p3.x, p3.y)
	if not await GD.wait(1.0):
		return
	var p4: = GD.point_of("drone4", "olho")
	GD.create("B4", p4.x, p4.y)
	GD.play_music("burst fire.mp3", false)
static func _any_empty(bar_name: String) -> bool:
	for bar in GD.pick(bar_name):
		if bar.is_empty():
			return true
	return false
static func _bullet_hit(bullet: String, drone: String, bar_name: String, dmg: float, fx_name: String, fx_delete: String, play_burst: bool) -> void:
	for b in GD.pick(bullet):
		for d in GD.pick(drone):
			if GD.once(GD.pair_key("ex_hit_%s_%s" %[bullet, drone], b, d), GD.collide_np(b, d)):
				for bar in GD.pick(bar_name):
					bar.set_value("-", dmg)
				var c: Vector2 = d.bbox_center()
				GD.create(fx_name, c.x, c.y)
				if play_burst:
					GD.play_music("burst fire.mp3", false)
				b.gd_delete()
				_remove_after(fx_delete, 0.5)
				break
static func _remove_after(fx_name: String, seconds: float) -> void:
	if not await GD.wait(seconds):
		return
	GD.delete_all(fx_name)
static func _drone_dies_with_pickup(_d, drone: String, holy: String, bullets: String) -> void:
	var c: = GD.center_of(drone)
	GD.create(holy, c.x - 48, c.y - 48)
	var up = GD.create("upvida", c.x - 22, c.y - 45)
	GD.delete_all(bullets)
	up.set_size(45, 91)
	_finish_drone(drone, holy)
static func _drone_dies_plain(drone: String, holy: String, bullets: String) -> void:
	var c: = GD.center_of(drone)
	GD.create(holy, c.x - 48, c.y - 48)
	GD.delete_all(bullets)
	_finish_drone(drone, holy)
static func _finish_drone(drone: String, holy: String) -> void:
	if not await GD.wait(0.3):
		return
	GD.delete_all(drone)
	GD.delete_all(holy)
