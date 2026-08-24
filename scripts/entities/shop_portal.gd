class_name ShopPortal extends Node2D
## ShopPortal — steht auf einer Kachel; wenn der Spieler orthogonal
## benachbart steht und die Interakt-Taste drückt (E / Enter), öffnet
## sich der passende Shop.
##
## Typen: "apothecary" (Apotheke) | "blacksmith" (Schmiede) | "gym" (v0.6)

@export var player_path: NodePath
@export var portal_cell: Vector2i = Vector2i(1, 1)
@export var shop_type: StringName = &"apothecary"
@export var shop_title: String = "Apotheke"

## Inventar-Angebot (Array[Item] .tres-Referenzen)
@export var stock: Array = []

@export var color: Color = Color(0.9, 0.7, 0.2, 1.0)

var _player: PlayerController

func _ready() -> void:
	_player = get_node_or_null(player_path) as PlayerController
	position = Vector2(
		portal_cell.x * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE / 2.0,
		portal_cell.y * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE / 2.0
	)
	var marker := ColorRect.new()
	var s: int = GameConfig.TILE_SIZE - 20
	marker.size = Vector2(s, s)
	marker.position = Vector2(-s / 2.0, -s / 2.0)
	marker.color = color
	add_child(marker)

	var lbl := Label.new()
	lbl.text = shop_title
	lbl.position = Vector2(-30, -GameConfig.TILE_SIZE)
	add_child(lbl)

	set_process_unhandled_input(true)

func _unhandled_input(event: InputEvent) -> void:
	if _player == null:
		return
	if not event.is_action_pressed("interact"):
		return
	var pcell: Vector2i = Vector2i(
		int(_player.position.x) / GameConfig.TILE_SIZE,
		int(_player.position.y) / GameConfig.TILE_SIZE
	)
	var diff: Vector2i = portal_cell - pcell
	if (abs(diff.x) + abs(diff.y)) != 1:
		return
	_open()

func _open() -> void:
	var packed: PackedScene
	match shop_type:
		&"blacksmith":
			packed = load("res://scenes/ui/blacksmith.tscn")
		_:
			packed = load("res://scenes/ui/shop.tscn")
	if packed == null:
		push_error("ShopPortal: Shop-Szene nicht gefunden für Typ %s" % shop_type)
		return
	var ui: Node = packed.instantiate()
	# In einen CanvasLayer wickeln, damit die UI nicht mit der Kamera scrollt.
	var layer := CanvasLayer.new()
	layer.layer = 50
	layer.add_child(ui)
	get_tree().current_scene.add_child(layer)
	if ui.has_method("open"):
		ui.open(shop_title, stock)
