extends Control
## ShopUI — generischer Consumables-Shop (Apotheke).
##
## Öffnet über ShopPortal. Zeigt Inventar-Gold, Angebot des Shops mit
## Preis, Kauf-Button. Verkauf ist im MVP absichtlich weggelassen.
##
## Schließt sich auf ESC oder "Zurück".

@onready var title_label: Label = %Title
@onready var gold_label: Label = %Gold
@onready var list: VBoxContainer = %ItemList
@onready var back_btn: Button = %BackBtn
@onready var status_label: Label = %Status

var _stock: Array = []

func _ready() -> void:
	back_btn.pressed.connect(_close)
	Inventory.gold_changed.connect(_refresh_gold)
	Inventory.items_changed.connect(_refresh_list)

func open(title: String, stock: Array) -> void:
	title_label.text = title
	_stock = stock
	_refresh_gold(Inventory.gold)
	_refresh_list()

func _refresh_gold(g: int = -1) -> void:
	if g < 0: g = Inventory.gold
	gold_label.text = "Gold: %d" % g

func _refresh_list() -> void:
	for child in list.get_children():
		child.queue_free()
	if _stock.is_empty():
		var lbl := Label.new()
		lbl.text = "Ausverkauft."
		list.add_child(lbl)
		return
	for it in _stock:
		if not (it is Item):
			continue
		var row := HBoxContainer.new()
		var name_lbl := Label.new()
		name_lbl.text = it.display_name
		name_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		name_lbl.tooltip_text = it.description
		row.add_child(name_lbl)
		var price_lbl := Label.new()
		price_lbl.text = "%d G" % it.buy_price
		price_lbl.custom_minimum_size = Vector2(60, 0)
		row.add_child(price_lbl)
		var owned_lbl := Label.new()
		owned_lbl.text = "x%d" % Inventory.count_of(it)
		owned_lbl.custom_minimum_size = Vector2(48, 0)
		row.add_child(owned_lbl)
		var buy_btn := Button.new()
		buy_btn.text = "Kaufen"
		buy_btn.disabled = Inventory.gold < it.buy_price
		buy_btn.pressed.connect(_on_buy.bind(it))
		row.add_child(buy_btn)
		list.add_child(row)

func _on_buy(item: Item) -> void:
	if not Inventory.spend_gold(item.buy_price):
		status_label.text = "Nicht genug Gold."
		return
	Inventory.add_item(item, 1)
	status_label.text = "%s gekauft." % item.display_name
	_refresh_list()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_close()

func _close() -> void:
	# Falls in einen CanvasLayer eingewickelt, den ganzen Layer entfernen.
	var p: Node = get_parent()
	if p is CanvasLayer:
		p.queue_free()
	else:
		queue_free()
