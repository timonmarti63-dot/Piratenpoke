extends Node2D
## VillageController — Root-Skript einer Dorf-Szene.
##
## Verantwortung:
##   1. Auf Village-Zustand reagieren: NPCs zeigen/verstecken, Boss-Encounter
##      nur zeigen wenn `is_safe = false`.
##   2. Spawn-Position des Players setzen (für Eingänge/Türen).
##   3. Shop-UI öffnen, wenn Spieler mit einem Händler-Portal interagiert.
##
## Erwartete Kinder-Nodes (per NodePath konfigurierbar):
##   - Player  (Player-Szene)
##   - World   (TileMap)
##   - Encounters/*  (EnemyEncounter-Nodes)
##   - SafeNPCs/*    (Container mit friedlichen NPCs & Shop-Portalen)

@export var village_id: StringName = &"kelpholm"
@export var player_path: NodePath
@export var encounters_path: NodePath
@export var safe_group_path: NodePath

var _player: PlayerController

func _ready() -> void:
	_player = get_node_or_null(player_path) as PlayerController
	_apply_state()
	VillageState.village_liberated.connect(_on_village_liberated)

func set_spawn_cell(cell: Vector2i) -> void:
	if _player == null:
		_player = get_node_or_null(player_path) as PlayerController
	if _player != null:
		_player.position = Vector2(
			cell.x * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE / 2.0,
			cell.y * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE / 2.0
		)

func _apply_state() -> void:
	var safe: bool = VillageState.is_safe(village_id)
	var enc: Node = get_node_or_null(encounters_path)
	if enc != null:
		enc.visible = not safe
		for child in enc.get_children():
			child.set_process(not safe)
	var safe_grp: Node = get_node_or_null(safe_group_path)
	if safe_grp != null:
		safe_grp.visible = safe
		for child in safe_grp.get_children():
			child.set_process(safe)

func _on_village_liberated(vid: StringName) -> void:
	if vid == village_id:
		_apply_state()
