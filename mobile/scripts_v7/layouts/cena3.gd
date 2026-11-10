extends GDLayout
func _events(delta: float) -> void:
	if scene_just_begins:
		_begin()
	follow_point("MetalRedBar", "lagarto_boss4", "barrav")
	follow_point("Medium_Star", "virus", "efeito")
	follow_point("luzazul", "virus", "luzcentro")
	Sheet_Player.run(self, delta)
	Sheet_ex_inimigos.run(self, delta)
	if touching("Player2", "portal3"):
		for ptl in GD.pick("portal3"):
			ptl.set_anim_index(1)
		GD.set_var("tela_load", 4)
		go_scene("load")
	if GD.bar_any_empty("bar_vida_play"):
		GD.set_var("tela_dead", 3)
		go_scene("dead")
	Sheet_ex_robo.run(self, delta)
	for m in["mina", "mina2", "mina3", "mina4"]:
		_mine(m)
	Sheet_ex_inimigos.trigger_zone("acao_tiros2")
	Sheet_ex_inimigos.trigger_zone("acao_tiros")
	if not _barriers_done and not Sheet_ex_serpente.boss_defeated and touching("Player2", "c6"):
		_barriers_done = true
		_spawn_barriers()
	Sheet_ex_serpente.run(self, delta)
	if GD.once("cena3_shield", GD.key_held("d")):
		_shield_pickup()
	Sheet_ex_virus.run(self, delta)
var _barriers_done: = false
func _begin() -> void:
	GD.set_fullscreen(true)
	GD.play_sound("Midnight_Asphalt_Pursuit.mp3", true)
	hide_objects(["Plataforma2", "Plataforma", "acao_tiros", "acao_tiros2"])
	GD.set_var("tela_load", 0)
	GD.set_var("tela_dead", 0)
	_begin_wait()
func _begin_wait() -> void:
	if not await GD.wait(7.0):
		return
	GD.delete_all("box_lagarto2")
	GD.delete_all("txt_escudo")
	GD.delete_all("barrreirainicio")
func _mine(mine_name: String) -> void:
	for p in GD.pick("Player2"):
		for mine in GD.pick(mine_name):
			if GD.once(GD.pair_key("cena3_" + mine_name, p, mine), GD.collide_np(p, mine)):
				var c: Vector2 = mine.bbox_center()
				GD.create("RedExplosion", c.x, c.y)
				GD.bar_set("bar_vida_play", "-", 15.0 * GD.get_num("mult_dano"))
				GD.play_music("crash.wav", false)
				mine.gd_delete()
				GD.delete_after("RedExplosion", 1.5)
func _spawn_barriers() -> void:
	var b1: = GD.pos_of("b1")
	var r1 = GD.create("barreira1", b1.x, b1.y)
	r1.set_size(280.0, 280.0)
	var b2: = GD.pos_of("b2")
	var r2 = GD.create("barreira2", b2.x, b2.y)
	r2.set_size(280.0, 280.0)
func _shield_pickup() -> void:
	var pt: = GD.point_of("Player2", "escudo")
	var s = GD.create("Front_Shield_Pickup", pt.x, pt.y)
	s.set_size(150.0, 150.0)
	if not await GD.wait(3.0):
		return
	GD.delete_all("Front_Shield_Pickup")
	GD.delete_all("barrreirainicio")
