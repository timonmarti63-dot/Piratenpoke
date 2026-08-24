class_name EnemyEncounter extends Node2D
## EnemyEncounter — sichtbarer Gegner auf der Weltkarte.
##
## Ab v0.4 nutzt der Kampf die aktuelle Inventory-Party (dynamisch) statt
## einer fest verdrahteten Test-Crew. Wenn `enemy_data` fehlt: kein Kampf.
##
## Trigger: der Spieler steht orthogonal benachbart zur Encounter-Kachel.

@export var world_tilemap_path: NodePath
@export var player_path: NodePath
@export var encounter_cell: Vector2i = Vector2i(6, 2)

@export var enemy_data: EnemyData
@export var vanish_on_win: bool = true

## Optional: eindeutige ID des Truppenführers. Wenn gesetzt und dieser Gegner
## besiegt wird, wechselt das Dorf in den `is_safe`-Zustand (Village-Logik).
@export var troop_leader_id: StringName = &""

var _player: PlayerController
var _defeated: bool = false

func _ready() -> void:
	_player = get_node_or_null(player_path) as PlayerController
	position = Vector2(
		encounter_cell.x * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE / 2.0,
		encounter_cell.y * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE / 2.0
	)
	var marker := ColorRect.new()
	var s: int = GameConfig.TILE_SIZE - 16
	marker.size = Vector2(s, s)
	marker.position = Vector2(-s / 2.0, -s / 2.0)
	marker.color = Color(0.85, 0.2, 0.2, 1.0)
	add_child(marker)

	set_process(true)
	SceneRouter.battle_finished.connect(_on_battle_finished)

func _process(_delta: float) -> void:
	if _defeated or _player == null or enemy_data == null:
		return
	if SceneRouter.is_in_battle():
		return
	var pcell: Vector2i = _player_cell()
	var diff: Vector2i = encounter_cell - pcell
	if (abs(diff.x) + abs(diff.y)) == 1:
		_trigger()

func _player_cell() -> Vector2i:
	var ts: int = GameConfig.TILE_SIZE
	return Vector2i(int(_player.position.x) / ts, int(_player.position.y) / ts)

func _trigger() -> void:
	if Inventory.crew.is_empty():
		push_warning("EnemyEncounter: Inventory-Crew ist leer.")
		return
	_defeated = true
	SceneRouter.push_battle(Inventory.crew, Inventory.active_index, enemy_data)

func _on_battle_finished(outcome: StringName) -> void:
	match outcome:
		&"player_win":
			if troop_leader_id != &"":
				VillageState.mark_leader_defeated(troop_leader_id)
			if vanish_on_win:
				queue_free()
		&"player_fled":
			_defeated = false
			await get_tree().create_timer(0.6).timeout
		&"enemy_win":
			_defeated = false
