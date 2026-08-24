extends CanvasLayer
## SceneRouter — globaler Szenenwechsel mit Fade + Zustands-Rückgabe (Autoload).
##
## Warum CanvasLayer als Autoload?
##   Wir wollen einen Overlay-ColorRect für den Fade, der über allen anderen
##   Szenen liegt. CanvasLayer als Autoload garantiert, dass der Overlay
##   auch nach Szenenwechsel oben bleibt.
##
## Nutzung:
##   SceneRouter.push_battle(player_data, enemy_data, on_finish_callable)
##   SceneRouter.change_world_scene("res://scenes/world/village.tscn")
##
## Auf Battle-Ende ruft der BattleController SceneRouter.finish_battle(outcome).

signal battle_finished(outcome: StringName)

const FADE_TIME: float = 0.35

var _fade: ColorRect
var _battle_scene_path: String = "res://scenes/combat/battle.tscn"
var _saved_world_scene: Node = null
var _saved_world_parent: Node = null
var _in_battle: bool = false

func is_in_battle() -> bool: return _in_battle

func _ready() -> void:
	layer = 100
	_fade = ColorRect.new()
	_fade.color = Color(0, 0, 0, 0)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_fade)

func fade_out() -> void:
	var t := create_tween()
	t.tween_property(_fade, "color:a", 1.0, FADE_TIME)
	await t.finished

func fade_in() -> void:
	var t := create_tween()
	t.tween_property(_fade, "color:a", 0.0, FADE_TIME)
	await t.finished

## Startet einen Kampf. `player_data` und `enemy_data_` sind CombatantData-Instanzen.
## Der Aufrufer kann sich mit `battle_finished` verbinden ODER `await`en.
func push_battle(player_data: CombatantData, enemy_data_: CombatantData) -> void:
	if _in_battle:
		return
	_in_battle = true

	await fade_out()

	# Weltszene aus dem Baum nehmen (nicht killen — wir kommen zurück).
	var tree := get_tree()
	var current_root: Node = tree.current_scene
	_saved_world_scene = current_root
	_saved_world_parent = current_root.get_parent()
	_saved_world_parent.remove_child(current_root)

	# Battle-Szene laden und einhängen.
	var packed: PackedScene = load(_battle_scene_path)
	var battle: Node = packed.instantiate()
	_saved_world_parent.add_child(battle)
	tree.current_scene = battle

	# Daten reichen.
	if battle.has_method("start"):
		battle.start(player_data, enemy_data_)

	await fade_in()

## Vom BattleController am Kampfende aufgerufen.
func finish_battle(outcome: StringName) -> void:
	if not _in_battle:
		return
	await fade_out()

	var tree := get_tree()
	var battle: Node = tree.current_scene
	battle.queue_free()

	# Weltszene zurück in den Baum.
	if _saved_world_scene != null and _saved_world_parent != null:
		_saved_world_parent.add_child(_saved_world_scene)
		tree.current_scene = _saved_world_scene

	_saved_world_scene = null
	_saved_world_parent = null
	_in_battle = false

	await fade_in()
	battle_finished.emit(outcome)
