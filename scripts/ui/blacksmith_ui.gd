extends Control
## BlacksmithUI — verkauft Weapons/Armors, prüft Element-Restriktionen,
## und rüstet direkt an ein wählbares Crew-Mitglied aus.

@onready var title_label: Label = %Title
@onready var gold_label: Label = %Gold
@onready var crew_select: OptionButton = %CrewSelect
@onready var list: VBoxContainer = %ItemList
@onready var back_btn: Button = %BackBtn
@onready var status_label: Label = %Status

var _stock: Array = []

func _ready() -> void:
	back_btn.pressed.connect(_close)
	crew_select.item_selected.connect(func(_i): _refresh_list())
	Inventory.gold_changed.connect(_refresh_gold)
	Inventory.crew_changed.connect(_populate_crew)

func open(title: String, stock: Array) -> void:
	title_label.text = title
	_stock = stock
	_populate_crew()
	_refresh_gold(Inventory.gold)
	_refresh_list()

func _populate_crew() -> void:
	crew_select.clear()
	for i in range(Inventory.crew.size()):
		var c: CrewMember = Inventory.crew[i]
		crew_select.add_item("%s (%s)" % [c.display_name, String(c.element).capitalize()], i)
	crew_select.selected = clamp(Inventory.active_index, 0, max(0, Inventory.crew.size() - 1))

func _selected_crew() -> CrewMember:
	if Inventory.crew.is_empty():
		return null
	var idx: int = crew_select.get_selected_id()
	if idx < 0 or idx >= Inventory.crew.size():
		return null
	return Inventory.crew[idx]

func _refresh_gold(g: int = -1) -> void:
	if g < 0: g = Inventory.gold
	gold_label.text = "Gold: %d" % g

func _refresh_list() -> void:
	for child in list.get_children():
		child.queue_free()
	var crew: CrewMember = _selected_crew()
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

		var stat_lbl := Label.new()
		if it is Weapon:
			stat_lbl.text = "+%d Atk" % (it as Weapon).attack_bonus
		elif it is Armor:
			stat_lbl.text = "+%d Def" % (it as Armor).defense_bonus
		stat_lbl.custom_minimum_size = Vector2(80, 0)
		row.add_child(stat_lbl)

		var price_lbl := Label.new()
		price_lbl.text = "%d G" % it.buy_price
		price_lbl.custom_minimum_size = Vector2(60, 0)
		row.add_child(price_lbl)

		var buy_btn := Button.new()
		buy_btn.text = "Kaufen & Anlegen"
		var can_equip: bool = true
		if it is Weapon:
			can_equip = crew != null and (it as Weapon).can_be_equipped_by(crew)
		elif it is Armor:
			can_equip = crew != null and (it as Armor).can_be_equipped_by(crew)
		buy_btn.disabled = Inventory.gold < it.buy_price or not can_equip
		if not can_equip:
			buy_btn.tooltip_text = "%s kann das nicht tragen." % (crew.display_name if crew else "?")
		buy_btn.pressed.connect(_on_buy.bind(it))
		row.add_child(buy_btn)
		list.add_child(row)

func _on_buy(item: Item) -> void:
	var crew: CrewMember = _selected_crew()
	if crew == null:
		status_label.text = "Kein Crew-Mitglied ausgewählt."
		return
	if not Inventory.spend_gold(item.buy_price):
		status_label.text = "Nicht genug Gold."
		return
	Inventory.add_item(item, 1)   # kurz durch den Beutel, dann ausrüsten
	var equipped: bool = false
	if item is Weapon:
		equipped = Inventory.equip_weapon(crew, item)
	elif item is Armor:
		equipped = Inventory.equip_armor(crew, item)
	if equipped:
		status_label.text = "%s trägt jetzt %s." % [crew.display_name, item.display_name]
	else:
		# Sollte durch die Vorprüfung nicht passieren, aber Rollback für den Fall.
		Inventory.remove_item(item, 1)
		Inventory.add_gold(item.buy_price)
		status_label.text = "Konnte nicht anlegen."
	_refresh_list()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_close()

func _close() -> void:
	var p: Node = get_parent()
	if p is CanvasLayer:
		p.queue_free()
	else:
		queue_free()
