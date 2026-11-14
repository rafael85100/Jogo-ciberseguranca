class_name GDTouch
extends Control
const MENU_SCENES: =["menu", "dificuldade", "equipe", "historia", "load", "dead", ""]
var _buttons: Array =[]
var _touches: Dictionary = { }
var _held: Dictionary = { }
var _was_gameplay: = false
const PAUSE_BTN: = { "label": "II", "pos": Vector2(1230, 50), "r": 34.0 }
const RESUME_RECT: = Rect2(490, 300, 300, 70)
const MENU_RECT: = Rect2(490, 400, 300, 70)
func _ready() -> void:
	_buttons =[
		{ "key": KEY_LEFT, "label": "<", "pos": Vector2(90, 630), "r": 58.0 },
		{ "key": KEY_RIGHT, "label": ">", "pos": Vector2(220, 630), "r": 58.0 },
		{ "key": KEY_UP, "label": "PULO", "pos": Vector2(1080, 630), "r": 62.0 },
		{ "key": KEY_F, "label": "TIRO", "pos": Vector2(1205, 630), "r": 62.0 },
		{ "key": KEY_E, "label": "E", "pos": Vector2(1080, 500), "r": 46.0 },
		{ "key": KEY_Q, "label": "Q", "pos": Vector2(1205, 500), "r": 46.0 },
		{ "key": KEY_D, "label": "ESCUDO", "pos": Vector2(1205, 380), "r": 50.0 },
		{ "key": KEY_X, "label": "X", "pos": Vector2(1080, 380), "r": 46.0 },
		{ "key": KEY_R, "label": "R", "pos": Vector2(955, 640), "r": 46.0 },
	]
	size = Vector2(1280, 720)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
func _process(_delta: float) -> void:
	var show: = not MENU_SCENES.has(GD.layout_name)
	var gp: = GD.is_gameplay()
	if gp != _was_gameplay:
		_was_gameplay = gp
		queue_redraw()
	if show != visible:
		if not show:
			_release_all()
		visible = show
		queue_redraw()
func on_pause_changed() -> void:
	_release_all()
	queue_redraw()
func _pause_tap(pos: Vector2) -> void:
	if GD.is_paused():
		if RESUME_RECT.has_point(pos):
			GD.set_paused(false)
		elif MENU_RECT.has_point(pos):
			GD.change_scene("menu")
	elif pos.distance_to(PAUSE_BTN["pos"]) <= float(PAUSE_BTN["r"]):
		GD.set_paused(true)
func _input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventScreenTouch:
		if event.pressed and GD.is_gameplay():
			var tp: Vector2 = event.position
			if GD.is_paused() or tp.distance_to(PAUSE_BTN["pos"]) <= float(PAUSE_BTN["r"]):
				_pause_tap(tp)
				get_viewport().set_input_as_handled()
				return
	if GD.is_paused():
		return
	if event is InputEventScreenTouch:
		if event.pressed:
			_touch(event.index, event.position)
		else:
			_untouch(event.index)
	elif event is InputEventScreenDrag:
		_touch(event.index, event.position)
func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT or what == NOTIFICATION_WM_WINDOW_FOCUS_OUT:
		_release_all()
		queue_redraw()
func _touch(index: int, pos: Vector2) -> void:
	var keys: Array =[]
	for b in _buttons:
		if pos.distance_to(b["pos"]) <= float(b["r"]):
			keys.append(int(b["key"]))
	var old: Array = _touches.get(index,[])
	for k in old:
		if not keys.has(k):
			_release(k)
	for k in keys:
		if not old.has(k):
			_hold(k)
	_touches[index] = keys
	queue_redraw()
func _untouch(index: int) -> void:
	for k in _touches.get(index,[]):
		_release(int(k))
	_touches.erase(index)
	queue_redraw()
func _hold(k: int) -> void:
	_held[k] = int(_held.get(k, 0)) + 1
	if _held[k] == 1:
		_send(k, true)
func _release(k: int) -> void:
	if not _held.has(k):
		return
	_held[k] = int(_held[k]) - 1
	if _held[k] <= 0:
		_held.erase(k)
		_send(k, false)
func _release_all() -> void:
	for k in _held.keys():
		_send(int(k), false)
	_held.clear()
	_touches.clear()
func _send(k: int, down: bool) -> void:
	var ev: = InputEventKey.new()
	ev.keycode = k
	ev.physical_keycode = k
	ev.pressed = down
	Input.parse_input_event(ev)
func _draw() -> void:
	var font: = ThemeDB.fallback_font
	if GD.is_paused():
		draw_rect(Rect2(Vector2.ZERO, size), Color(0, 0, 0, 0.65))
		draw_string(font, Vector2(0, 250), "PAUSADO", HORIZONTAL_ALIGNMENT_CENTER, size.x, 48, Color(1, 1, 1))
		for r in[[RESUME_RECT, "CONTINUAR"],[MENU_RECT, "MENU PRINCIPAL"]]:
			var rect: Rect2 = r[0]
			draw_rect(rect, Color(1, 1, 1, 0.15))
			draw_rect(rect, Color(1, 0.35, 0.35, 0.9), false, 3.0)
			draw_string(font, Vector2(rect.position.x, rect.position.y + 45.0), str(r[1]), HORIZONTAL_ALIGNMENT_CENTER, rect.size.x, 26, Color(1, 1, 1))
		return
	if GD.is_gameplay():
		var pc: Vector2 = PAUSE_BTN["pos"]
		var pr: = float(PAUSE_BTN["r"])
		draw_circle(pc, pr, Color(1, 1, 1, 0.2))
		draw_arc(pc, pr, 0.0, TAU, 40, Color(1, 0.35, 0.35, 0.9), 3.0)
		draw_string(font, Vector2(pc.x - pr, pc.y + 7.0), str(PAUSE_BTN["label"]), HORIZONTAL_ALIGNMENT_CENTER, pr * 2.0, 20, Color(1, 1, 1, 0.95))
	for b in _buttons:
		var c: Vector2 = b["pos"]
		var r: = float(b["r"])
		var pressed: = _held.has(int(b["key"]))
		draw_circle(c, r, Color(1, 1, 1, 0.55 if pressed else 0.2))
		draw_arc(c, r, 0.0, TAU, 48, Color(1, 0.35, 0.35, 0.9), 3.0)
		draw_string(font, Vector2(c.x - r, c.y + 6.0), str(b["label"]), HORIZONTAL_ALIGNMENT_CENTER, r * 2.0, 18, Color(1, 1, 1, 0.95))
