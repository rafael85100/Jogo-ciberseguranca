extends GDLayout
func _events(delta: float) -> void:
	if scene_just_begins:
		_begin()
	Sheet_Player.run(self, delta)
	Sheet_ex_inimigos.run(self, delta)
	if touching("Player2", "portal3"):
		for ptl in GD.pick("portal3"):
			ptl.set_anim_index(1)
		GD.set_var("tela_load", 3)
		go_scene("load")
	Sheet_ex_robo.run(self, delta)
	if GD.bar_any_empty("bar_vida_play"):
		GD.set_var("tela_dead", 2)
		go_scene("dead")
	Sheet_ex_robo_tiros.run(self, delta)
func _begin() -> void:
	GD.set_fullscreen(true)
	GD.play_sound("Midnight_Asphalt_Pursuit.mp3", true)
	hide_objects(["Plataforma2", "Plataforma"])
	GD.set_var("tela_dead", 0)
	GD.set_var("tela_load", 0)
