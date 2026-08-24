class_name EnemyEncounter extends Node2D
## EnemyEncounter — sichtbarer Gegner auf der Weltkarte.
##
## Blockiert eine Kachel (Solid) und triggert bei "Berührung" (= wenn der
## Spieler auf die 4 orthogonal angrenzenden Kacheln stößt) einen Kampf.
## Wir arbeiten hier bewusst kachelbasiert statt mit Physik-Areas — passt
## zu Grid-Movement und ist deterministisch.
##
## Konfiguration:
##   - encounter_cell:  Zellposition auf der TileMap
##   - player_data:     CombatantData für die aktive Crew (Test-Setup)
##   - enemy_data:      EnemyData des Gegners
##   - vanish_on_win:   nach Sieg vom Feld nehmen? (Standard: true)

@export var world_tilemap_path: NodePath
@export var player_path: NodePath
@export var encounter_cell: Vector2i = Vector2i(6, 2)

@export var player_data: CombatantData
@export var enemy_data: EnemyData
@export var vanish_on_win: bool = true

var _player: PlayerController
var _defeated: bool = false

func _ready() -> void:
	_player = get_node_or_null(player_path) as PlayerController
	position = Vector2(
		encounter_cell.x * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE / 2.0,
		encounter_cell.y * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE / 2.0
	)
	# Optionaler visueller Marker — kleines rotes Quadrat.
	var marker := ColorRect.new()
	var s: int = GameConfig.TILE_SIZE - 16
	marker.size = Vector2(s, s)
	marker.position = Vector2(-s / 2.0, -s / 2.0)
	marker.color = Color(0.85, 0.2, 0.2, 1.0)
	add_child(marker)

	# Auf Bewegungsende des Spielers hören → Nähe prüfen.
	# Wir nutzen `_process`, da der PlayerController pro Frame prüft, ob
	# er sich bewegt — hier reicht ein einfacher Polling-Check.
	set_process(true)

	# Nach Sieg wollen wir informiert werden.
	SceneRouter.battle_finished.connect(_on_battle_finished)

func _process(_delta: float) -> void:
	if _defeated or _player == null:
		return
	if SceneRouter.is_in_battle():
		return
	var pcell: Vector2i = _player_cell()
	# Trigger, wenn der Spieler direkt neben mir steht UND versucht,
	# in meine Zelle zu laufen. Vereinfachung für v0.3: schon Nachbarschaft reicht.
	var diff: Vector2i = encounter_cell - pcell
	var adjacent: bool = (abs(diff.x) + abs(diff.y)) == 1
	if adjacent:
		_trigger()

func _player_cell() -> Vector2i:
	# PlayerController hält `_cell` privat. Wir rechnen aus der Position zurück.
	var ts: int = GameConfig.TILE_SIZE
	return Vector2i(
		int(_player.position.x) / ts,
		int(_player.position.y) / ts
	)

func _trigger() -> void:
	if player_data == null or enemy_data == null:
		push_warning("EnemyEncounter: player_data oder enemy_data fehlt.")
		return
	_defeated = true  # sperren, damit nicht doppelt getriggert wird
	SceneRouter.push_battle(player_data, enemy_data)

func _on_battle_finished(outcome: StringName) -> void:
	match outcome:
		&"player_win":
			if vanish_on_win:
				queue_free()
		&"player_fled":
			# Kurze Sperre, damit man nicht sofort erneut reinläuft.
			_defeated = false
			await get_tree().create_timer(0.6).timeout
		&"enemy_win":
			# In v0.3: Kampf endet, Held bleibt liegen; Game-Over-Screen kommt in v0.4.
			_defeated = false
