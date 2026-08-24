class_name ScenePortal extends Node2D
## ScenePortal — trigger für Szenenwechsel (Tunnel / Dorf-Eingang / Tür).
##
## Wenn der Spieler auf die konfigurierte Kachel läuft, wechselt SceneRouter
## in die Zielszene und ruft dort `set_spawn_cell(spawn_cell)` auf.

@export var player_path: NodePath
@export var trigger_cell: Vector2i = Vector2i(0, 0)
@export var target_scene: String = ""
@export var spawn_cell: Vector2i = Vector2i(1, 1)

## Optional: nur zeigen, wenn das Ziel-Dorf sicher ist bzw. unsicher. Bei
## `village_id_required_safe`: Portal ist nur aktiv, wenn Dorf befreit.
@export var village_id_required_safe: StringName = &""

var _player: PlayerController
var _triggered: bool = false

func _ready() -> void:
	_player = get_node_or_null(player_path) as PlayerController
	position = Vector2(
		trigger_cell.x * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE / 2.0,
		trigger_cell.y * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE / 2.0
	)
	# Kleiner blauer Punkt als Marker.
	var marker := ColorRect.new()
	var s: int = 20
	marker.size = Vector2(s, s)
	marker.position = Vector2(-s / 2.0, -s / 2.0)
	marker.color = Color(0.3, 0.8, 1.0, 0.6)
	add_child(marker)
	set_process(true)

func _process(_delta: float) -> void:
	if _triggered or _player == null or target_scene == "":
		return
	if SceneRouter.is_in_battle():
		return
	if village_id_required_safe != &"" and not VillageState.is_safe(village_id_required_safe):
		return
	var pcell: Vector2i = Vector2i(
		int(_player.position.x) / GameConfig.TILE_SIZE,
		int(_player.position.y) / GameConfig.TILE_SIZE
	)
	if pcell == trigger_cell:
		_triggered = true
		SceneRouter.change_world_scene(target_scene, spawn_cell)
