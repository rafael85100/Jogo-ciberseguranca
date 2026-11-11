class_name GDSprite
extends GDObject
var anim: AnimatedSprite2D
var anim_index: = 0
var flip_x_on: = false
var frame_data: Array =[]
func _build() -> void:
	anim = AnimatedSprite2D.new()
	anim.centered = false
	add_child(anim)
	var frames: = SpriteFrames.new()
	frames.remove_animation("default")
	var animations: Array = gd_def.get("animations",[])
	for i in animations.size():
		var a: Dictionary = animations[i]
		var dirs: Array = a.get("directions",[])
		var aname: = str(i)
		frames.add_animation(aname)
		frames.set_animation_speed(aname, 1.0)
		var fdata: Array =[]
		if dirs.is_empty():
			frame_data.append(fdata)
			continue
		var dir: Dictionary = dirs[0]
		frames.set_animation_loop(aname, bool(dir.get("looping", true)))
		for s in dir.get("sprites",[]):
			var tex: = GD.texture(str(s.get("image", "")))
			if tex == null:
				continue
			var origin: = _pt(s.get("originPoint", { }))
			var size: = tex.get_size()
			frames.add_frame(aname, tex, float(dir.get("timeBetweenFrames", 0.1)))
			var cp = s.get("centerPoint", { })
			var center: = size * 0.5
			if cp is Dictionary and not bool(cp.get("automatic", true)):
				center = _pt(cp)
			fdata.append({
				"origin": origin,
				"center": center,
				"size": size,
				"mask": _masks(s, size),
				"points": s.get("points",[]),
			})
		frame_data.append(fdata)
	anim.sprite_frames = frames
	if frames.has_animation("0"):
		anim.play("0")
	_refresh()
func _pt(d) -> Vector2:
	if d is Dictionary:
		return Vector2(float(d.get("x", 0.0)), float(d.get("y", 0.0)))
	return Vector2.ZERO
func _masks(s: Dictionary, size: Vector2) -> Array:
	var out: Array =[]
	var polys: Array =[]
	if s.get("hasCustomCollisionMask", false) and s.has("customCollisionMask"):
		for poly in s.get("customCollisionMask",[]):
			var pa: = PackedVector2Array()
			for p in poly:
				pa.append(_pt(p))
			polys.append(pa)
	else:
		polys.append(PackedVector2Array([Vector2.ZERO, Vector2(size.x, 0), size, Vector2(0, size.y)]))
	for pa in polys:
		out.append_array(GDGeom.convex_parts(pa))
	return out
func _cur() -> Dictionary:
	if anim_index < 0 or anim_index >= frame_data.size():
		return { }
	var fl: Array = frame_data[anim_index]
	if fl.is_empty():
		return { }
	var fi: = clampi(anim.frame if anim else 0, 0, fl.size() - 1)
	return fl[fi]
func _refresh() -> void:
	if anim == null:
		return
	var f: = _cur()
	if f.is_empty():
		return
	var origin: Vector2 = f["origin"]
	var w: float = f["size"].x
	var cx: float = f["center"].x
	anim.flip_h = flip_x_on
	if flip_x_on:
		anim.offset = Vector2(2.0 * cx - w - origin.x, - origin.y)
	else:
		anim.offset = - origin
func _process(delta: float) -> void:
	super._process(delta)
	_refresh()
func _to_local(p: Vector2) -> Vector2:
	var f: = _cur()
	if f.is_empty():
		return p
	var origin: Vector2 = f["origin"]
	if flip_x_on:
		var cx: float = f["center"].x
		return Vector2(2.0 * cx - p.x - origin.x, p.y - origin.y)
	return Vector2(p.x - origin.x, p.y - origin.y)
func world_polygons() -> Array:
	var out: Array =[]
	var f: = _cur()
	if f.is_empty():
		return out
	var xf: = global_transform
	for part in f["mask"]:
		var wp: = PackedVector2Array()
		for p in part:
			wp.append(xf * _to_local(p))
		out.append(wp)
	return out
func set_anim_index(i: int) -> void:
	if anim == null:
		anim_index = i
		return
	if i == anim_index and anim.is_playing():
		return
	anim_index = i
	if anim.sprite_frames.has_animation(str(i)):
		anim.play(str(i))
	_refresh()
func get_anim_index() -> int:
	return anim_index
func has_animation_ended() -> bool:
	return anim != null and not anim.is_playing()
func set_flip_x(on: bool) -> void:
	flip_x_on = on
	_refresh()
func is_flipped_x() -> bool:
	return flip_x_on
func point_pos(point_name: String) -> Vector2:
	var f: = _cur()
	if f.is_empty():
		return scene_pos(global_position)
	if point_name == "origine":
		return scene_pos(global_transform * Vector2.ZERO)
	for p in f["points"]:
		if str(p.get("name", "")) == point_name:
			return scene_pos(global_transform * _to_local(_pt(p)))
	if point_name == "centre":
		return camera_center()
	return scene_pos(global_position)
