extends GDBehavior
# Replica a extensao TimedBackAndForthMovement do GDevelop:
# sem espelhamento anda no sentido positivo, vira ao passar de Distance
# e o Timeout so vale quando o objeto fica parado (preso).
var vertical: = false
var speed: = 0.0
var distance: = 0.0
var timeout: = 2.0
var _start: = 0.0
var _last: = 0.0
var _timecheck: = 0.0
var _timer: = 0.0
func _behavior_ready() -> void:
	vertical = bool(beh_data.get("Vertical", false))
	speed = float(beh_data.get("Speed", 0.0))
	distance = float(beh_data.get("Distance", 0.0))
	timeout = float(beh_data.get("Timeout", 2.0))
	_start = float(beh_data.get("StartPosition", 0.0))
func _pos() -> float:
	return obj.position.y if vertical else obj.position.x
func _flipped() -> bool:
	if vertical:
		return obj.has_method("is_flipped_y") and obj.is_flipped_y()
	return obj.has_method("is_flipped_x") and obj.is_flipped_x()
func _set_flip(on: bool) -> void:
	if vertical:
		if obj.has_method("set_flip_y"):
			obj.set_flip_y(on)
	elif obj.has_method("set_flip_x"):
		obj.set_flip_x(on)
func _turn(on: bool) -> void:
	_start = roundf(_pos())
	_timer = 0.0
	_set_flip(on)
func _process(delta: float) -> void:
	if obj == null:
		return
	_timer += delta
	if _start == 0.0:
		_timer = 0.0
		_start = roundf(_pos())
	if not _flipped() and _pos() > _start + distance:
		_turn(true)
	if _flipped() and _pos() < _start - distance:
		_turn(false)
	if _timecheck != _timer and _last == roundf(_pos()):
		if _timer >= timeout and _flipped():
			_turn(false)
		if _timer >= timeout and not _flipped():
			_turn(true)
	var dir: = -1.0 if _flipped() else 1.0
	if vertical:
		obj.add_force_xy(0.0, dir * speed)
	else:
		obj.add_force_xy(dir * speed, 0.0)
	_last = roundf(_pos())
	_timecheck = _timer
