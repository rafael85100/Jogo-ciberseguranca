extends GDBehavior
var _tweens: Dictionary = { }
func add_object_position_tween2(tween_name: String, x: float, y: float, easing: String, duration: float, _extra = null) -> void:
	_tweens.erase(tween_name)
	_tweens[tween_name] = { "kind": "pos", "from": obj.position, "to": Vector2(x, y),
		"easing": easing, "duration": duration, "t": 0.0 }
func add_object_opacity_tween2(tween_name: String, value: float, easing: String, duration: float, _extra = null) -> void:
	_tweens.erase(tween_name)
	_tweens[tween_name] = { "kind": "alpha", "from": obj.get_opacity(), "to": value,
		"easing": easing, "duration": duration, "t": 0.0 }
func add_object_width_tween2(tween_name: String, width: float, easing: String, duration: float, _extra = null) -> void:
	_tweens.erase(tween_name)
	_tweens[tween_name] = { "kind": "width", "from": obj.get_width(), "to": width,
		"easing": easing, "duration": duration, "t": 0.0 }
func remove_tween(tween_name: String) -> void:
	_tweens.erase(tween_name)
func stop_tween(tween_name: String) -> void:
	_tweens.erase(tween_name)
func _process(delta: float) -> void:
	for tween_name in _tweens.keys():
		var tw: Dictionary = _tweens[tween_name]
		tw["t"] += delta
		var k: = 1.0 if float(tw["duration"]) <= 0.0 else clampf(float(tw["t"]) / float(tw["duration"]), 0.0, 1.0)
		var e: = ease_value(str(tw["easing"]), k)
		match str(tw["kind"]):
			"pos":
				obj.position =(tw["from"] as Vector2).lerp(tw["to"], e)
			"alpha":
				obj.set_opacity(lerpf(float(tw["from"]), float(tw["to"]), e))
			"width":
				obj.set_width(lerpf(float(tw["from"]), float(tw["to"]), e))
		if k >= 1.0:
			_tweens.erase(tween_name)
static func ease_value(easing: String, k: float) -> float:
	match easing:
		"easeInQuad":
			return k * k
		"easeOutQuad":
			return 1.0 -(1.0 - k) *(1.0 - k)
		"easeFromTo", "easeInOutQuad":
			return 2.0 * k * k if k < 0.5 else 1.0 - pow(-2.0 * k + 2.0, 2) / 2.0
		_:
			return k
