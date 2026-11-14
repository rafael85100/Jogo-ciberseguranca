extends GDLayout
func _events(_delta: float) -> void:
	if scene_just_begins:
		GD.set_fullscreen(true)
	for b in GD.pick("bt_normal"):
		if b.is_clicked():
			GD.set_var("mult_hp", 1.0)
			GD.set_var("mult_dano", 1.0)
			GD.set_var("dificuldade", 0)
			GD.change_scene("cena1")
	for b in GD.pick("bt_dificil"):
		if b.is_clicked():
			GD.set_var("mult_hp", 1.3)
			GD.set_var("mult_dano", 1.25)
			GD.set_var("dificuldade", 1)
			GD.change_scene("cena1")
	for b in GD.pick("bt_insano"):
		if b.is_clicked():
			GD.set_var("mult_hp", 2.0)
			GD.set_var("mult_dano", 1.75)
			GD.set_var("dificuldade", 2)
			GD.change_scene("cena1")
	for b in GD.pick("bt_voltar"):
		if b.is_clicked():
			GD.change_scene("menu")
