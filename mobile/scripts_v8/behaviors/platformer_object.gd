extends GDBehavior
var gravity: = 1000.0
var acceleration: = 1500.0
var deceleration: = 1500.0
var max_speed: = 250.0
var jump_speed: = 600.0
var jump_sustain: = 0.2
var max_fall: = 700.0
var speed: = Vector2.ZERO
var on_floor: = false
var enabled: = true
var _jump_timer: = 0.0
var _jump_held_prev: = false
var _jumping: = false
var _jump_held_since_start: = false
var _jump_v: = 0.0
var _fall_v: = 0.0
const MAX_DELTA: = 0.05
var _floor_node: Node2D = null
var _floor_last: = Vector2.ZERO
func _behavior_ready() -> void:
	var d: Dictionary = beh_data
	gravity = float(d.get("gravity", gravity))
	acceleration = float(d.get("acceleration", acceleration))
	deceleration = float(d.get("deceleration", deceleration))
	max_speed = float(d.get("maxSpeed", max_speed))
	jump_speed = float(d.get("jumpSpeed", jump_speed))
	jump_sustain = float(d.get("jumpSustainTime", jump_sustain))
	max_fall = float(d.get("maxFallingSpeed", max_fall))
func _process(frame_delta: float) -> void:
	if not enabled or obj == null:
		return
	var delta: = minf(frame_delta, MAX_DELTA)
	_carry_with_floor()
	_push_out_of_floor()
	var left: = GD.key_held("Left")
	var right: = GD.key_held("Right")
	var jump_down: = GD.key_held("Up") or GD.key_held("Space")
	if right and not left:
		speed.x = minf(speed.x + acceleration * delta, max_speed)
	elif left and not right:
		speed.x = maxf(speed.x - acceleration * delta, - max_speed)
	else:
		speed.x = move_toward(speed.x, 0.0, deceleration * delta)
	var jump_edge: = jump_down and not _jump_held_prev
	_jump_held_prev = jump_down
	if on_floor and jump_edge:
		_jumping = true
		_jump_v = jump_speed
		_fall_v = 0.0
		_jump_timer = 0.0
		_jump_held_since_start = true
		on_floor = false
	var dy: = 0.0
	if not on_floor:
		if _jumping:
			if not jump_down:
				_jump_held_since_start = false
			_jump_timer += delta
			var prev_jump: = _jump_v
			if not(_jump_held_since_start and _jump_timer < jump_sustain):
				_jump_v -= gravity * delta
			dy +=((- prev_jump - _jump_v) / 2.0) * delta
		var prev_fall: = _fall_v
		_fall_v = minf(_fall_v + gravity * delta, max_fall)
		dy +=((_fall_v + prev_fall) / 2.0) * delta
		if _jumping and _jump_v < 0.0:
			_jumping = false
			_jump_v = 0.0
	else:
		_jumping = false
		_jump_v = 0.0
		_fall_v = 0.0
	speed.y = _fall_v - _jump_v
	_move_x(speed.x * delta)
	_move_y(dy)
	_update_floor()
func is_jumping() -> bool:
	return not on_floor and speed.y < 0.0
func is_falling() -> bool:
	return not on_floor and speed.y > 0.0
func _solid_hit(offset: Vector2) -> Node2D:
	var r: = obj.scene_rect()
	r.position += offset
	for s in obj.get_tree().get_nodes_in_group("gd_solid"):
		if s == obj or not is_instance_valid(s):
			continue
		if r.intersects(s.scene_rect()):
			return s
	return null
func _move_x(dx: float) -> void:
	var steps: = int(ceil(absf(dx)))
	if steps == 0:
		return
	var step: = dx / steps
	for i in steps:
		obj.position.x += step
		if _solid_hit(Vector2.ZERO) != null:
			obj.position.x -= step
			speed.x = 0.0
			break
func _move_y(dy: float) -> void:
	var steps: = int(ceil(absf(dy)))
	if steps == 0:
		return
	var step: = dy / steps
	for i in steps:
		obj.position.y += step
		var hit: = _solid_hit(Vector2.ZERO)
		if hit != null:
			obj.position.y -= step
			if step > 0.0:
				on_floor = true
				_floor_node = hit
				_floor_last = hit.position
				_fall_v = 0.0
			else:
				_jumping = false
				_jump_v = 0.0
			speed.y = _fall_v - _jump_v
			break
const PUSH_OUT_MAX: = 12.0
func _push_out_of_floor() -> void:
	var r: = obj.scene_rect()
	for s in obj.get_tree().get_nodes_in_group("gd_solid"):
		if s == obj or not is_instance_valid(s):
			continue
		var sr: Rect2 = s.scene_rect()
		if not r.intersects(sr) or sr.position.y <= r.position.y + r.size.y * 0.5:
			continue
		var depth: = r.end.y - sr.position.y
		if depth > 0.0 and depth <= PUSH_OUT_MAX:
			obj.position.y -= depth
			r.position.y -= depth
			if speed.y > 0.0:
				speed.y = 0.0
				_fall_v = 0.0
func _update_floor() -> void:
	if speed.y < 0.0:
		on_floor = false
		return
	var below: = _solid_hit(Vector2(0, 1))
	if below != null:
		on_floor = true
		_floor_node = below
		_floor_last = below.position
	else:
		on_floor = false
		_floor_node = null
func _carry_with_floor() -> void:
	if on_floor and is_instance_valid(_floor_node):
		var d: = _floor_node.position - _floor_last
		if d != Vector2.ZERO:
			obj.position += d
		_floor_last = _floor_node.position
