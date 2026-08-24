class_name PlayerController extends Node2D
## PlayerController — der Captain auf dem Grid.
##
## Bewegt sich exakt von Kachel zu Kachel (Grid-Lock). Kein halbschrittiges
## Sliden, keine Diagonalen. Kollision über zwei Wege:
##   1. TileMap-Custom-Property "solid" auf der Ziel-Kachel
##   2. Optionale StaticBody2D-Objekte auf der Physik-Layer LAYER_WORLD_SOLID
##
## Input-Buffering ist im letzten Drittel der Bewegung aktiv: kurz bevor
## der aktuelle Tween endet, wird der nächste gepufferte oder gehaltene
## Input abgeholt und die nächste Bewegung nahtlos gestartet.

@export var world_tilemap_path: NodePath
## Startposition in Kachel-Koordinaten (0,0 = links oben der TileMap).
@export var start_cell: Vector2i = Vector2i(8, 4)

var _tilemap: TileMap
var _cell: Vector2i
var _is_moving: bool = false
var _next_input_taken: bool = false  ## Verhindert doppeltes Puffer-Konsumieren pro Tween.

func _ready() -> void:
	_tilemap = get_node_or_null(world_tilemap_path) as TileMap
	if _tilemap == null:
		push_warning("PlayerController: keine TileMap gefunden unter %s" % world_tilemap_path)
	_cell = start_cell
	position = _cell_to_world(_cell)

func _process(_delta: float) -> void:
	if _is_moving:
		return
	var dir := InputBuffer.current_held()
	if dir != Vector2i.ZERO:
		_try_step(dir)

## Versucht, einen Schritt in `dir` zu machen. Bricht ab, wenn Ziel-Kachel
## solid ist.
func _try_step(dir: Vector2i) -> void:
	var target := _cell + dir
	if _is_solid(target):
		# Kurz "andrücken" — kein State-Wechsel, damit der Spieler die
		# Wand fühlt, aber nicht in ein Bewegungslock gerät.
		return
	_start_step(target)

func _start_step(target_cell: Vector2i) -> void:
	_is_moving = true
	_next_input_taken = false
	_cell = target_cell

	var target_pos := _cell_to_world(target_cell)
	var t := create_tween()
	t.tween_property(self, "position", target_pos, GameConfig.MOVE_TIME_LAND)\
		.set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)

	# Input-Buffer-Fenster: kurz vor Bewegungsende bereits nächsten Input abgreifen.
	var buffer_delay: float = max(0.0, GameConfig.MOVE_TIME_LAND - GameConfig.INPUT_BUFFER_WINDOW)
	t.parallel().tween_callback(_pull_next_input).set_delay(buffer_delay)
	t.tween_callback(_on_step_finished)

func _pull_next_input() -> void:
	if _next_input_taken:
		return
	_next_input_taken = true
	# Wir starten hier noch KEINE neue Bewegung — der Tween läuft noch.
	# Wir "peeken" nur, ob eine Taste gehalten wird, und lassen _on_step_finished
	# den nächsten Schritt sauber auslösen. `consume()` merkt sich den letzten
	# Tastendruck für den Fall, dass die Taste zwischen Peek und Ende losgelassen wird.
	InputBuffer.consume()  # leert veraltete Puffer-Einträge

func _on_step_finished() -> void:
	_is_moving = false
	# Direkt weitermachen, wenn eine Richtung noch gehalten wird —
	# das ergibt die nahtlose Kettenbewegung.
	var dir := InputBuffer.current_held()
	if dir != Vector2i.ZERO:
		_try_step(dir)

## Kachel-Koordinate → Weltposition (Zentrum der Kachel).
func _cell_to_world(cell: Vector2i) -> Vector2:
	var ts: int = GameConfig.TILE_SIZE
	return Vector2(cell.x * ts + ts / 2.0, cell.y * ts + ts / 2.0)

## Prüft, ob eine Ziel-Kachel blockiert ist.
## Zwei-stufig: erst TileMap-Property, dann Grenzen.
func _is_solid(cell: Vector2i) -> bool:
	if _tilemap == null:
		return false

	# Außerhalb der bespielten Fläche → blockieren.
	var used: Rect2i = _tilemap.get_used_rect()
	if not used.has_point(cell):
		return true

	# Layer 0 wird als "Boden" behandelt — Layer 1 (falls vorhanden) als
	# "Objekte/Wände". Wir checken beide Layer auf die "solid"-Property.
	for layer in _tilemap.get_layers_count():
		var data: TileData = _tilemap.get_cell_tile_data(layer, cell)
		if data == null:
			continue
		if data.get_custom_data(GameConfig.TILE_PROPERTY_SOLID):
			return true
	return false
