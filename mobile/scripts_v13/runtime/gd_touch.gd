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
		{ "key": KEY_LEFT, "label": "", "icon": "left", "pos": Vector2(90, 630), "r": 58.0, "w": 1.15 },
		{ "key": KEY_RIGHT, "label": "", "icon": "right", "pos": Vector2(220, 630), "r": 58.0, "w": 1.15 },
		{ "key": KEY_UP, "label": "PULO", "icon": "jump", "pos": Vector2(1080, 630), "r": 62.0, "w": 1.0 },
		{ "key": KEY_F, "label": "TIRO", "icon": "fire", "pos": Vector2(1205, 630), "r": 62.0, "w": 1.0 },
		{ "key": KEY_E, "label": "E", "icon": "", "pos": Vector2(1080, 500), "r": 46.0, "w": 1.0 },
		{ "key": KEY_Q, "label": "Q", "icon": "", "pos": Vector2(1205, 500), "r": 46.0, "w": 1.0 },
		{ "key": KEY_D, "label": "ESCUDO", "icon": "shield", "pos": Vector2(1205, 380), "r": 50.0, "w": 1.0 },
		{ "key": KEY_X, "label": "", "icon": "x", "pos": Vector2(1080, 380), "r": 46.0, "w": 1.0 },
		{ "key": KEY_R, "label": "R", "icon": "", "pos": Vector2(955, 640), "r": 46.0, "w": 1.0 },
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
# ---- estilo neon (octogono azul-escuro, borda ciano + roxa, icone claro) ----
const C_FILL: = Color(0.05, 0.07, 0.22, 0.78)
const C_FILL_ON: = Color(0.16, 0.36, 0.78, 0.9)
const C_GLOW: = Color(0.25, 0.55, 1.0, 0.22)
const C_EDGE: = Color(0.35, 0.72, 1.0, 1.0)
const C_INNER: = Color(0.55, 0.38, 1.0, 0.95)
const C_ICON: = Color(0.72, 0.9, 1.0, 1.0)
const C_TEXT: = Color(0.95, 0.98, 1.0, 1.0)
const C_SHADOW: = Color(0.02, 0.02, 0.1, 0.9)
func _octo(c: Vector2, hw: float, hh: float, k: float) -> PackedVector2Array:
	return PackedVector2Array([
		Vector2(c.x - hw + k, c.y - hh), Vector2(c.x + hw - k, c.y - hh),
		Vector2(c.x + hw, c.y - hh + k), Vector2(c.x + hw, c.y + hh - k),
		Vector2(c.x + hw - k, c.y + hh), Vector2(c.x - hw + k, c.y + hh),
		Vector2(c.x - hw, c.y + hh - k), Vector2(c.x - hw, c.y - hh + k),
	])
func _closed(p: PackedVector2Array) -> PackedVector2Array:
	var q: = PackedVector2Array(p)
	q.append(p[0])
	q.append(p[1])
	return q
func _panel(c: Vector2, hw: float, hh: float, pressed: bool) -> void:
	var k: = minf(hw, hh) * 0.36
	draw_polyline(_closed(_octo(c, hw + 4.0, hh + 4.0, k + 1.6)), C_GLOW, 9.0, true)
	draw_colored_polygon(_octo(c, hw, hh, k), C_FILL_ON if pressed else C_FILL)
	draw_polyline(_closed(_octo(c, hw, hh, k)), C_EDGE, 4.0, true)
	draw_polyline(_closed(_octo(c, hw - 7.0, hh - 7.0, k - 2.8)), C_INNER, 2.0, true)
	# brilho no topo
	draw_line(Vector2(c.x - hw + k + 4.0, c.y - hh + 3.5), Vector2(c.x + hw - k - 4.0, c.y - hh + 3.5), Color(0.8, 0.95, 1.0, 0.55), 2.0, true)
func _text(font: Font, center: Vector2, w: float, t: String, fs: int, col: Color) -> void:
	var y: = center.y + fs * 0.36
	draw_string_outline(font, Vector2(center.x - w * 0.5, y), t, HORIZONTAL_ALIGNMENT_CENTER, w, fs, 6, C_SHADOW)
	draw_string(font, Vector2(center.x - w * 0.5, y), t, HORIZONTAL_ALIGNMENT_CENTER, w, fs, col)
func _icon(kind: String, c: Vector2, s: float) -> void:
	match kind:
		"left", "right":
			var d: float = -1.0 if kind == "left" else 1.0
			var tri: = PackedVector2Array([
				Vector2(c.x + d * s * 0.42, c.y),
				Vector2(c.x - d * s * 0.26, c.y - s * 0.42),
				Vector2(c.x - d * s * 0.26, c.y + s * 0.42),
			])
			draw_colored_polygon(tri, C_ICON)
			draw_polyline(_closed(tri), C_EDGE, 2.0, true)
		"jump":
			for i in 2:
				var yy: = c.y - s * 0.12 + i * s * 0.26
				draw_polyline(PackedVector2Array([Vector2(c.x - s * 0.34, yy + s * 0.2), Vector2(c.x, yy - s * 0.12), Vector2(c.x + s * 0.34, yy + s * 0.2)]), C_ICON, 5.0, true)
		"fire":
			var rr: = s * 0.3
			draw_arc(c, rr, 0.0, TAU, 32, C_ICON, 3.0, true)
			for v in[Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)]:
				draw_line(c + v * rr * 0.45, c + v * rr * 1.45, C_ICON, 3.0, true)
			draw_circle(c, 3.0, C_ICON)
		"shield":
			var w: = s * 0.34
			var sh: = PackedVector2Array([
				Vector2(c.x, c.y - s * 0.42), Vector2(c.x + w, c.y - s * 0.28),
				Vector2(c.x + w * 0.92, c.y + s * 0.05), Vector2(c.x, c.y + s * 0.42),
				Vector2(c.x - w * 0.92, c.y + s * 0.05), Vector2(c.x - w, c.y - s * 0.28),
			])
			draw_polyline(_closed(sh), C_ICON, 3.0, true)
			var inner: = PackedVector2Array()
			for p in sh:
				inner.append(c + (p - c) * 0.55)
			draw_colored_polygon(inner, Color(C_ICON, 0.75))
		"x":
			var a: = s * 0.3
			draw_line(c + Vector2(-a, -a), c + Vector2(a, a), C_TEXT, 7.0, true)
			draw_line(c + Vector2(a, -a), c + Vector2(-a, a), C_TEXT, 7.0, true)
		"pause":
			var bw: = s * 0.14
			var bh: = s * 0.5
			draw_rect(Rect2(c.x - bw * 1.7, c.y - bh * 0.5, bw, bh), C_ICON)
			draw_rect(Rect2(c.x + bw * 0.7, c.y - bh * 0.5, bw, bh), C_ICON)
func _draw() -> void:
	var font: = ThemeDB.fallback_font
	if GD.is_paused():
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.01, 0.0, 0.08, 0.7))
		_text(font, Vector2(size.x * 0.5, 240.0), size.x, "PAUSADO", 52, C_EDGE)
		for r in[[RESUME_RECT, "CONTINUAR"],[MENU_RECT, "MENU PRINCIPAL"]]:
			var rect: Rect2 = r[0]
			_panel(rect.get_center(), rect.size.x * 0.5, rect.size.y * 0.5, false)
			_text(font, rect.get_center(), rect.size.x, str(r[1]), 26, C_TEXT)
		return
	if GD.is_gameplay():
		var pc: Vector2 = PAUSE_BTN["pos"]
		var pr: = float(PAUSE_BTN["r"]) * 0.85
		_panel(pc, pr, pr, false)
		_icon("pause", pc, pr * 2.0)
	for b in _buttons:
		var c: Vector2 = b["pos"]
		var r: = float(b["r"])
		var pressed: = _held.has(int(b["key"]))
		var sc: float = 0.94 if pressed else 1.0
		var hh: = r * 0.86 * sc
		var hw: = hh * float(b["w"])
		_panel(c, hw, hh, pressed)
		var icon: = str(b["icon"])
		var label: = str(b["label"])
		if icon != "" and label != "":
			_icon(icon, c + Vector2(0, -hh * 0.22), hh * 1.15)
			_text(font, c + Vector2(0, hh * 0.5), hw * 2.0, label, 15 if label.length() > 4 else 17, C_TEXT)
		elif icon != "":
			_icon(icon, c, hh * 1.5)
		else:
			_text(font, c, hw * 2.0, label, 30, C_TEXT)
