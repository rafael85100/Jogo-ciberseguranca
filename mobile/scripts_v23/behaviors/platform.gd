extends GDBehavior
# v23: plataformas "Jumpthru" (atravessa por baixo, segura por cima) ficam num grupo proprio;
# as outras continuam solidas, como antes.
func _behavior_ready() -> void:
	if str(beh_data.get("platformType", "")) == "Jumpthru":
		obj.add_to_group("gd_jumpthru")
	else:
		obj.add_to_group("gd_solid")
