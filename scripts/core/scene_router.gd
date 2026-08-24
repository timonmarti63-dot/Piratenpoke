extends CanvasLayer
## SceneRouter — globaler Szenenwechsel mit Fade + Kampf-Push/Pop (Autoload).
##
## Zwei Modi:
##   push_battle(party, active_idx, enemy_data)
##       World-Szene aus dem Baum nehmen, Combat einhängen. Nach Kampfende
##       `finish_battle(outcome)` → World zurück, `battle_finished` feuern.
##
##   change_world_scene(path, spawn_cell=null)
##       Aktuelle Szene ersetzen (kein Zurück). Für Tunnel/Haus-Übergänge.
##       Optional wird die Zielszene mit `set_spawn_cell(cell)` aufgerufen,
##       falls sie diese Methode hat — z. B. um den Player an der Tür zu
##       spawnen.

signal battle_finished(outcome: StringName)
signal world_scene_changed(scene: Node)

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

# --- Battle Push/Pop --------------------------------------------------

func push_battle(party: Array, active_index: int, enemy_data_: CombatantData) -> void:
	if _in_battle:
		return
	_in_battle = true
	await fade_out()

	var tree := get_tree()
	var current_root: Node = tree.current_scene
	_saved_world_scene = current_root
	_saved_world_parent = current_root.get_parent()
	_saved_world_parent.remove_child(current_root)

	var packed: PackedScene = load(_battle_scene_path)
	var battle: Node = packed.instantiate()
	_saved_world_parent.add_child(battle)
	tree.current_scene = battle

	if battle.has_method("start"):
		battle.start(party, active_index, enemy_data_)

	await fade_in()

func finish_battle(outcome: StringName) -> void:
	if not _in_battle:
		return
	await fade_out()

	var tree := get_tree()
	var battle: Node = tree.current_scene
	battle.queue_free()

	if _saved_world_scene != null and _saved_world_parent != null:
		_saved_world_parent.add_child(_saved_world_scene)
		tree.current_scene = _saved_world_scene

	_saved_world_scene = null
	_saved_world_parent = null
	_in_battle = false

	await fade_in()
	battle_finished.emit(outcome)

# --- World-Szenenwechsel ---------------------------------------------

## Wechselt die Weltszene komplett (kein Rücksprung wie bei Battle).
## Wenn die Zielszene eine `set_spawn_cell(cell)`-Methode hat, wird sie
## damit aufgerufen — praktisch für Tür-Positionen.
func change_world_scene(path: String, spawn_cell = null) -> void:
	await fade_out()
	var packed: PackedScene = load(path)
	if packed == null:
		push_error("SceneRouter: Szene nicht gefunden: %s" % path)
		await fade_in()
		return
	var new_scene: Node = packed.instantiate()
	var tree := get_tree()
	var old_scene: Node = tree.current_scene
	var parent: Node = old_scene.get_parent()
	parent.add_child(new_scene)
	old_scene.queue_free()
	tree.current_scene = new_scene
	if spawn_cell != null:
		if new_scene.has_method("set_spawn_cell"):
			new_scene.set_spawn_cell(spawn_cell)
		else:
			# Fallback: PlayerController irgendwo in der Szene finden.
			for p in tree.get_nodes_in_group("player_controller"):
				if p.has_method("set_spawn_cell"):
					p.set_spawn_cell(spawn_cell)
	world_scene_changed.emit(new_scene)
	await fade_in()
