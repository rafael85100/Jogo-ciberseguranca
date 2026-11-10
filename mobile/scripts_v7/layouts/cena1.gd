extends GDLayout
func _events(delta: float) -> void:
	if scene_just_begins:
		_begin()
	Sheet_Player.run(self, delta)
	Sheet_ex_inimigos.homing_bullets()
	Sheet_ex_inimigos.trigger_zone("acao_tiros")
	Sheet_ex_inimigos.run(self, delta)
	Sheet_ex_inimigos.trigger_zone("acao_tiros2")
	for p in GD.pick("Player2"):
		for a in GD.pick("paniel_arma"):
			if GD.once("cena1_arma", GD.collide_np(p, a)):
				_weapon_pickup()
	if touching("Player2", "portal"):
		for ptl in GD.pick("portal"):
			ptl.set_anim_index(1)
		GD.set_var("tela_load", 2)
		go_scene_after(1.0, "load")
	if GD.bar_any_empty("bar_vida_play"):
		GD.set_var("tela_dead", 1)
		go_scene("dead")
func _begin() -> void:
	hide_objects(["acao_tiros", "acao_tiros2"])
	GD.set_fullscreen(true)
	GD.play_sound("Midnight_Asphalt_Pursuit.mp3", true)
	hide_objects(["Plataforma2", "Plataforma"])
	_intro_wait()
func _intro_wait() -> void:
	if not await GD.wait(10.0):
		return
	GD.delete_all("ct")
	GD.delete_all("NewLight")
	GD.set_var("tela_dead", 0)
func _weapon_pickup() -> void:
	if not await GD.wait(0.3):
		return
	GD.play_sound("laserthing.wav")
	GD.delete_all("paniel_arma")
	GD.delete_all("txto_arma")
