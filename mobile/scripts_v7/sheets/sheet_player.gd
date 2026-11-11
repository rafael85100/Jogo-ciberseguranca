class_name Sheet_Player
static func run(layout: GDLayout, _delta: float) -> void:
	if layout.scene_just_begins:
		for b in GD.pick("bar_vida_play"):
			b.set_value("=", b.value())
		for b in GD.pick("balas"):
			b.set_value("=", b.value())
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
		if GD.once("player_fire1_%d" % p.get_instance_id(), GD.key_held("f") and not p.is_flipped_x()):
			p.set_anim_index(2)
			GD.create("bala1", p.point_x("disparo"), p.point_y("disparo"))
			_bars_add("balas", "-", 1)
			GD.play_music("weaponfire1.wav", false)
	if GD.key_released("f"):
		for p in GD.pick("Player2"):
			p.set_anim_index(0)
	for p in GD.pick("Player2"):
		if GD.once("player_fire2_%d" % p.get_instance_id(), GD.key_held("f") and p.is_flipped_x()):
			p.set_anim_index(2)
			GD.create("bala2", p.point_x("disparo"), p.point_y("disparo"))
			_bars_add("balas", "-", 1)
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
				for b in GD.pick("balas"):
					b.set_value("=", 50)
				r.gd_delete()
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
