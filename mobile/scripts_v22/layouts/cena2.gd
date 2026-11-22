extends GDLayout
# Fase (v22): codigo da v21 + maquinas geradoras de inimigos.
const MAQUINAS: =[
	{ "x": 560, "base": 538, "inimigos":["robo_z", "robo_z2", "robo_z3"], "voa": false },
	{ "x": 2100, "base": 538, "inimigos":["robo_z4", "robo_z5", "robo_z6"], "voa": false },
	{ "x": 4330, "base": 538, "inimigos":["robo_z7", "robo_a", "robo_a2", "robo_a3"], "voa": false },
]
func _events(delta: float) -> void:
	if scene_just_begins:
		_begin()
		_maquinas_begin()
	_maquinas(delta)
	Sheet_Player.run(self, delta)
	Sheet_ex_inimigos.run(self, delta)
	if touching("Player2", "portal3"):
		for ptl in GD.pick("portal3"):
			ptl.set_anim_index(1)
		GD.set_var("tela_load", 3)
		go_scene("load")
	Sheet_ex_robo.run(self, delta)
	if Sheet_Player.todos_mortos():
		GD.set_var("tela_dead", 2)
		go_scene("dead")
	Sheet_ex_robo_tiros.run(self, delta)
func _begin() -> void:
	GD.set_fullscreen(true)
	GD.play_sound("Midnight_Asphalt_Pursuit.mp3", true)
	hide_objects(["Plataforma2", "Plataforma"])
	GD.set_var("tela_dead", 0)
	GD.set_var("tela_load", 0)

# ---- Maquinas geradoras (v22): mesma logica do PC (ferramentas/maquinas.py) ----
# Os inimigos de cada grupo comecam guardados (y -20000, patrulha parada). Quando o robo chega
# perto (a maquina entra na tela) e a fase ja tem 1 s, a maquina solta o grupo todo de uma vez e
# cada inimigo vai ate o ponto dele (easeOutQuad, 550 px/s, minimo 0,7 s). La a patrulha volta.
const MAQ_NUCLEO: = Vector2(60, 78)
const MAQ_VEL: = 550.0
const MAQ_MIN_T: = 0.7
const MAQ_GATILHO: = 650.0
const MAQ_PATRULHA: = "TimedBackAndForthMirroredMovement"
var _maq: Array =[]
var _maq_tempo: = 0.0
func _maquinas_begin() -> void:
	_maq.clear()
	_maq_tempo = 0.0
	for cfg in MAQUINAS:
		var m = GD.create("maquina_geradora", float(cfg["x"]) - 60.0, float(cfg["base"]) - 150.0)
		m.z_index = 8
		m.set_anim_index(0)
		var lista: Array =[]
		for n in cfg["inimigos"]:
			for e in GD.pick(str(n)):
				var beh = e.behavior(MAQ_PATRULHA)
				if beh != null:
					beh.set_process(false)
				lista.append({ "o": e, "home": e.position, "flip": e.is_flipped_x(), "beh": beh,
					"de": Vector2.ZERO, "dur": 1.0, "chegou": false })
				e.position = Vector2(e.position.x, -20000.0)
		_maq.append({ "m": m, "lista": lista, "estado": 0, "t": 0.0, "voa": bool(cfg["voa"]) })
func _maquinas(delta: float) -> void:
	_maq_tempo += delta
	var p = GD.first("Player2")
	for mq in _maq:
		var m = mq["m"]
		if m == null or not is_instance_valid(m):
			continue
		if mq["estado"] == 0 and _maq_tempo > 1.0 and p != null and p.position.x > m.position.x - MAQ_GATILHO:
			mq["estado"] = 1
			mq["t"] = 0.0
			m.set_anim_index(1)
			GD.play_sound("bzzzt.wav", false, 80.0, 0.6)
			var nucleo: Vector2 = m.position + MAQ_NUCLEO
			var fx = GD.create("RedExplosion", nucleo.x, nucleo.y)
			if fx != null:
				fx.z_index = 9
			for it in mq["lista"]:
				var e = it["o"]
				if e == null or not is_instance_valid(e) or e.gd_deleted:
					continue
				var home: Vector2 = it["home"]
				var de: = Vector2(nucleo.x - e.get_width() / 2.0, nucleo.y - e.get_height() / 2.0)
				if not mq["voa"]:
					de.y = home.y
				e.position = de
				e.set_flip_x(home.x < de.x)
				it["de"] = de
				it["dur"] = maxf(MAQ_MIN_T, absf(home.x - de.x) / MAQ_VEL)
		if mq["estado"] != 1:
			continue
		mq["t"] = float(mq["t"]) + delta
		var todos: = true
		for it in mq["lista"]:
			if it["chegou"]:
				continue
			var e = it["o"]
			if e == null or not is_instance_valid(e) or e.gd_deleted:
				it["chegou"] = true
				continue
			var k: = clampf(float(mq["t"]) / float(it["dur"]), 0.0, 1.0)
			var suave: = 1.0 -(1.0 - k) *(1.0 - k)
			e.position =(it["de"] as Vector2).lerp(it["home"], suave)
			if k >= 1.0:
				it["chegou"] = true
				e.set_flip_x(bool(it["flip"]))
				if it["beh"] != null and is_instance_valid(it["beh"]):
					it["beh"].set_process(true)
			else:
				todos = false
		if float(mq["t"]) >= 1.3 and m.anim_index != 2:
			m.set_anim_index(2)
			GD.delete_all("RedExplosion")
		if todos and float(mq["t"]) >= 1.3:
			mq["estado"] = 2
