extends Node
## InputBuffer — globaler Richtungs-Puffer (Autoload).
##
## Speichert die zuletzt gedrückte Bewegungsrichtung. Der PlayerController
## kann kurz vor Ende einer Bewegung `consume()` aufrufen, um den bereits
## registrierten nächsten Input abzugreifen — das ergibt flüssiges,
## nicht-stotterndes Grid-Movement, ohne dass der Spieler exakt timen muss.
##
## Diagonale Bewegung ist ausgeschlossen: bei mehreren gedrückten Tasten
## gewinnt die zuletzt gedrückte Richtung.

signal direction_changed(dir: Vector2i)

const DIR_NONE  := Vector2i.ZERO
const DIR_UP    := Vector2i(0, -1)
const DIR_DOWN  := Vector2i(0,  1)
const DIR_LEFT  := Vector2i(-1, 0)
const DIR_RIGHT := Vector2i( 1, 0)

## Aktuell im Puffer stehende Richtung.
var _buffered: Vector2i = DIR_NONE

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("move_up"):
		_set_dir(DIR_UP)
	elif event.is_action_pressed("move_down"):
		_set_dir(DIR_DOWN)
	elif event.is_action_pressed("move_left"):
		_set_dir(DIR_LEFT)
	elif event.is_action_pressed("move_right"):
		_set_dir(DIR_RIGHT)

func _set_dir(dir: Vector2i) -> void:
	_buffered = dir
	direction_changed.emit(dir)

## Gibt die aktuell gedrückte Richtung zurück (Polling — für kontinuierliche
## Bewegung solange eine Taste gehalten wird). Priorisiert die zuletzt
## gedrückte Richtung, um Diagonalen zu vermeiden.
func current_held() -> Vector2i:
	# Wenn die gepufferte Richtung noch gehalten wird → sie gewinnt.
	if _buffered != DIR_NONE and _is_held(_buffered):
		return _buffered
	# Sonst irgendeine andere gehaltene Richtung.
	if Input.is_action_pressed("move_up"):    return DIR_UP
	if Input.is_action_pressed("move_down"):  return DIR_DOWN
	if Input.is_action_pressed("move_left"):  return DIR_LEFT
	if Input.is_action_pressed("move_right"): return DIR_RIGHT
	return DIR_NONE

## Konsumiert den Puffer und gibt ihn zurück. Wird vom PlayerController
## kurz vor Ende einer Bewegung aufgerufen, um "queued" Inputs abzuholen.
func consume() -> Vector2i:
	var d := _buffered
	_buffered = DIR_NONE
	return d

func _is_held(dir: Vector2i) -> bool:
	match dir:
		DIR_UP:    return Input.is_action_pressed("move_up")
		DIR_DOWN:  return Input.is_action_pressed("move_down")
		DIR_LEFT:  return Input.is_action_pressed("move_left")
		DIR_RIGHT: return Input.is_action_pressed("move_right")
		_: return false
