extends Node
const VIEW_CENTER: = Vector2(640, 360)
const PROJECT_JSON: = "res://data/gd_project.json"
const OBJECTS_JSON: = "res://data/gd_objects.json"
const BEHAVIOR_SCRIPTS: = {
	"PlatformBehavior::PlatformBehavior": "res://scripts/behaviors/platform.gd",
	"PlatformBehavior::PlatformerObjectBehavior": "res://scripts/behaviors/platformer_object.gd",
	"TimedBackAndForthMovement::TimedBackAndForthMirroredMovement": "res://scripts/behaviors/timed_back_and_forth.gd",
	"AnimatedBackAndForthMovement::AnimatedBackAndForthMirroredMovement": "res://scripts/behaviors/animated_back_and_forth.gd",
	"Tween::TweenBehavior": "res://scripts/behaviors/tween.gd",
	"TweenIntoView::TweenIntoView": "res://scripts/behaviors/tween_into_view.gd",
	"Parallax::HorizontalTiledSpriteParallax": "res://scripts/behaviors/parallax.gd",
	"Parallax::VerticalTiledSpriteParallax": "res://scripts/behaviors/parallax.gd",
	"AnchorBehavior::AnchorBehavior": "res://scripts/behaviors/anchor.gd",
	"PanelSpriteContinuousBar::ResourceBar": "res://scripts/behaviors/resource_bar.gd",
	"TiledUnitsBar::ResourceBar": "res://scripts/behaviors/resource_bar.gd",
	"PanelSpriteButton::ButtonFSM": "res://scripts/behaviors/button_fsm.gd",
	"PanelSpriteButton::TextStyleState": "res://scripts/behaviors/text_style_state.gd",
	"PanelSpriteButton::BitmapTextStyleState": "res://scripts/behaviors/text_style_state.gd",
	"SmoothCamera::SmoothCamera": "res://scripts/behaviors/smooth_camera.gd",
	"SmoothCamera::SmoothPlatformerCamera": "res://scripts/behaviors/smooth_camera.gd",
}
const KEY_MAP: = {
	"Left": KEY_LEFT, "Right": KEY_RIGHT, "Up": KEY_UP, "Down": KEY_DOWN,
	"Space": KEY_SPACE, "Escape": KEY_ESCAPE, "Enter": KEY_ENTER, "Return": KEY_ENTER,
}
var project: Dictionary = { }
var defs: Dictionary = { }
var vars: Dictionary = { }
var layout: Node = null
var layout_name: = ""
var layout_serial: = 0
var layer_centers: Dictionary = { }
var once_state: Dictionary = { }
var _tex_cache: Dictionary = { }
var _stream_cache: Dictionary = { }
var _music: AudioStreamPlayer
var _sfx: Array[AudioStreamPlayer] =[]
var _sfx_next: = 0
var _tracked: Dictionary = { }
var _last_state: Dictionary = { }
var _released: Dictionary = { }
var _mouse_down: = false
var _mouse_started: = false
var _mouse_ended: = false
const GAMEPLAY_SCENES: =["cena1", "cena2", "cena3", "final"]
const SUB_MENUS: =["dificuldade", "historia", "equipe", "cenademo"]
var touch: GDTouch = null
func _ready() -> void:
	project = _read_json(PROJECT_JSON)
	defs = _read_json(OBJECTS_JSON)
	reset_globals()
	_music = AudioStreamPlayer.new()
	_music.bus = &"Master"
	add_child(_music)
	for i in 8:
		var p: = AudioStreamPlayer.new()
		add_child(p)
		_sfx.append(p)
	get_tree().set_quit_on_go_back(false)
	if OS.has_feature("android") or DisplayServer.is_touchscreen_available():
		var touch_layer: = CanvasLayer.new()
		touch_layer.layer = 120
		touch_layer.process_mode = Node.PROCESS_MODE_ALWAYS
		add_child(touch_layer)
		touch = GDTouch.new()
		touch_layer.add_child(touch)
func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_GO_BACK_REQUEST:
		_on_back()
	elif what == NOTIFICATION_APPLICATION_PAUSED or what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		if touch != null and is_gameplay() and not get_tree().paused:
			set_paused(true)
func is_gameplay() -> bool:
	return GAMEPLAY_SCENES.has(layout_name)
func is_paused() -> bool:
	return get_tree().paused
func set_paused(on: bool) -> void:
	get_tree().paused = on and is_gameplay()
	if touch != null:
		touch.on_pause_changed()
func _on_back() -> void:
	if is_gameplay():
		set_paused(not get_tree().paused)
	elif layout_name == "menu":
		quit_game()
	elif SUB_MENUS.has(layout_name):
		change_scene("menu")
func _read_json(path: String) -> Dictionary:
	var f: = FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("GD: cannot open " + path)
		return { }
	var parsed = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else { }
func _process(_delta: float) -> void:
	_released.clear()
	for k in _tracked.keys():
		var now: = _is_key_down(k)
		if _last_state.get(k, false) and not now:
			_released[k] = true
		_last_state[k] = now
	var down: = Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)
	_mouse_started = down and not _mouse_down
	_mouse_ended = _mouse_down and not down
	_mouse_down = down
func mouse_started() -> bool:
	return _mouse_started
func mouse_ended() -> bool:
	return _mouse_ended
func mouse_world() -> Vector2:
	var vp: = get_viewport()
	return vp.get_canvas_transform().affine_inverse() * vp.get_mouse_position()
func first(obj_name: String) -> Node:
	var a: = pick(obj_name)
	return a[0] if not a.is_empty() else null
func pair_key(ev: String, a: Node, b: Node) -> String:
	var ia: = a.get_instance_id() if a != null else 0
	var ib: = b.get_instance_id() if b != null else 0
	return "%s|%d|%d" %[ev, ia, ib]
func pos_of(obj_name: String) -> Vector2:
	var o = first(obj_name)
	if o is Node2D:
		return(o as Node2D).position
	return Vector2.ZERO
func bar_set(bar_name: String, op: String, v: float) -> void:
	for b in pick(bar_name):
		b.set_value(op, v)
func bar_any_empty(bar_name: String) -> bool:
	for b in pick(bar_name):
		if b.is_empty():
			return true
	return false
func per_mult(v: float, mult_name: String) -> float:
	return v / maxf(get_num(mult_name), 0.0001)
func delete_after(obj_name: String, seconds: float) -> void:
	if not await wait(seconds):
		return
	delete_all(obj_name)
func set_text(obj_name: String, value: String) -> void:
	for o in pick(obj_name):
		o.set_text(value)
func center_of(obj_name: String) -> Vector2:
	var o: = first(obj_name)
	return o.bbox_center() if o != null else Vector2.ZERO
func point_of(obj_name: String, point_name: String) -> Vector2:
	var o: = first(obj_name)
	return o.point_pos(point_name) if o != null else Vector2.ZERO
func delete_all(obj_name: String) -> void:
	for o in pick(obj_name):
		o.gd_delete()
func font(res_name: String) -> Font:
	var key: = "font|" + res_name
	if _tex_cache.has(key):
		return _tex_cache[key]
	var path = project.get("resourceMap", { }).get(res_name)
	var f: Font = null
	if path != null and ResourceLoader.exists(str(path)):
		f = load(str(path)) as Font
	_tex_cache[key] = f
	return f
func reset_globals() -> void:
	vars = project.get("globals", { }).duplicate(true)
func get_var(var_name: String) -> Variant:
	return vars.get(var_name, 0.0)
func set_var(var_name: String, value: Variant) -> void:
	vars[var_name] = value
func get_num(var_name: String) -> float:
	return float(vars.get(var_name, 0.0))
func enter_layout(l: Node) -> void:
	layout = l
	layout_name = str(l.get("gd_layout_name"))
	layout_serial += 1
	layer_centers.clear()
	once_state.clear()
func exit_layout_state() -> void:
	layout_serial += 1
func change_scene(scene_name: String) -> void:
	layout_serial += 1
	if get_tree().paused:
		get_tree().paused = false
		if touch != null:
			touch.on_pause_changed()
	get_tree().change_scene_to_file("res://scenes/%s.tscn" % scene_name)
func quit_game() -> void:
	get_tree().quit()
func layout_meta(name: String = "") -> Dictionary:
	var n: = name if name != "" else layout_name
	return project.get("layouts", { }).get(n, { })
func center_camera(obj: Node, layers: Array =[]) -> void:
	var targets: Array = layers if not layers.is_empty() else[""]
	var c: Vector2 = obj.camera_center() if obj.has_method("camera_center") else(obj as Node2D).position
	for l in targets:
		layer_centers[str(l)] = c
func camera_center(layer: String = "") -> Vector2:
	return layer_centers.get(layer, VIEW_CENTER)
func _keycode(key_name: String) -> int:
	if KEY_MAP.has(key_name):
		return KEY_MAP[key_name]
	if key_name.length() == 1:
		return key_name.to_upper().unicode_at(0)
	return 0
func _is_key_down(key_name: String) -> bool:
	var code: = _keycode(key_name)
	return code != 0 and Input.is_key_pressed(code)
func key_held(key_name: String) -> bool:
	_tracked[key_name] = true
	return _is_key_down(key_name)
func key_released(key_name: String) -> bool:
	_tracked[key_name] = true
	return _released.get(key_name, false)
func _stream(res_name: String, loop: bool) -> AudioStream:
	var key: = "%s|%s" %[res_name, loop]
	if _stream_cache.has(key):
		return _stream_cache[key]
	var s = load_audio(res_name)
	if s == null:
		return null
	s = s.duplicate()
	if s is AudioStreamMP3:
		s.loop = loop
	elif s is AudioStreamWAV:
		s.loop_mode = AudioStreamWAV.LOOP_FORWARD if loop else AudioStreamWAV.LOOP_DISABLED
	_stream_cache[key] = s
	return s
func _loop_of(p: AudioStreamPlayer) -> String:
	return str(p.get_meta("gd_loop", "")) if p.playing else ""
func _is_looping(res_name: String) -> bool:
	if _loop_of(_music) == res_name:
		return true
	for p in _sfx:
		if _loop_of(p) == res_name:
			return true
	return false
func _stop_loops() -> void:
	var all: Array =[_music]
	all.append_array(_sfx)
	for p in all:
		if str(p.get_meta("gd_loop", "")) != "":
			p.stop()
			p.set_meta("gd_loop", "")
func _next_sfx() -> AudioStreamPlayer:
	for i in _sfx.size():
		var p: AudioStreamPlayer = _sfx[_sfx_next]
		_sfx_next =(_sfx_next + 1) % _sfx.size()
		if _loop_of(p) == "":
			return p
	var q: AudioStreamPlayer = _sfx[_sfx_next]
	_sfx_next =(_sfx_next + 1) % _sfx.size()
	return q
func play_sound(res_name: String, loop: = false, volume: = 100.0, pitch: = 1.0) -> void:
	if loop and _is_looping(res_name):
		return
	var s: = _stream(res_name, loop)
	if s == null:
		return
	if loop:
		_stop_loops()
	var p: = _next_sfx()
	p.set_meta("gd_loop", res_name if loop else "")
	p.stream = s
	p.volume_db = linear_to_db(clampf(volume / 100.0, 0.0001, 1.0))
	p.pitch_scale = pitch
	p.play()
func play_music(res_name: String, loop: = true, volume: = 100.0) -> void:
	if loop and _is_looping(res_name):
		return
	var s: = _stream(res_name, loop)
	if s == null:
		return
	if loop:
		_stop_loops()
	_music.set_meta("gd_loop", res_name if loop else "")
	_music.stream = s
	_music.volume_db = linear_to_db(clampf(volume / 100.0, 0.0001, 1.0))
	_music.play()
func stop_music() -> void:
	_music.stop()
func load_audio(res_name: String):
	var path = project.get("resourceMap", { }).get(res_name)
	if path == null or not ResourceLoader.exists(str(path)):
		return null
	return load(str(path))
func restore_gd_props(n: Node) -> void:
	for k in n.get_meta_list():
		var key: = str(k)
		if key.begins_with("gd_"):
			n.set(key, n.get_meta(key))
func set_fullscreen(on: bool) -> void:
	if OS.has_feature("android"):
		return
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if on else DisplayServer.WINDOW_MODE_WINDOWED)
func texture(res_name: String) -> Texture2D:
	if _tex_cache.has(res_name):
		return _tex_cache[res_name]
	var path = project.get("resourceMap", { }).get(res_name)
	var t: Texture2D = null
	if path != null and ResourceLoader.exists(str(path)):
		t = load(str(path)) as Texture2D
	_tex_cache[res_name] = t
	return t
func get_def(def_key: String, obj_name: String) -> Dictionary:
	var by_layout: Dictionary = defs.get(def_key, { })
	if by_layout.has(obj_name):
		return by_layout[obj_name]
	var by_global: Dictionary = defs.get("_global", { })
	if by_global.has(obj_name):
		return by_global[obj_name]
	push_warning("GD: no object definition for '%s' in '%s'" %[obj_name, def_key])
	return { }
func pick(obj_name: String) -> Array:
	var out: Array =[]
	for n in get_tree().get_nodes_in_group("gd:" + obj_name):
		if is_instance_valid(n) and not n.gd_deleted:
			out.append(n)
	return out
func create(obj_name: String, x: float, y: float, layer_name: = "") -> Node:
	var def: = get_def(layout_name, obj_name)
	var script_file: String = def.get("_godot_script", "gd_object.gd")
	var node: = Node2D.new()
	node.set_script(load("res://scripts/objects/" + script_file))
	node.gd_name = obj_name
	node.gd_def_key = layout_name if defs.get(layout_name, { }).has(obj_name) else "_global"
	node.gd_layer_name = layer_name
	node.gd_created = true
	node.position = Vector2(x, y)
	var parent: Node = layout.get_layer(layer_name) if layout and layout.has_method("get_layer") else layout
	parent.add_child(node)
	return node
func collide_np(a: Node, b: Node) -> bool:
	if a == null or b == null or a == b:
		return false
	return GDGeom.polys_overlap(a.scene_polygons(), b.scene_polygons())
func collide_point(obj: Node, p: Vector2) -> bool:
	return GDGeom.point_in_polys(obj.world_polygons(), p)
func once(id: String, cond: bool) -> bool:
	if cond:
		if once_state.get(id, false):
			return false
		once_state[id] = true
		return true
	once_state[id] = false
	return false
func wait(seconds: float) -> bool:
	var serial: = layout_serial
	await get_tree().create_timer(seconds, false).timeout
	return serial == layout_serial
