extends Node
## Inventory — globaler Beutel, Gold und Crew-Roster (Autoload).
##
## Persistenter Zustand über Szenen hinweg. Speichern/Laden kommt in v0.6+.
##
## Beutel-Modell:
##   items: Dictionary[Item, int]   — Stack-Anzahl pro Item-Resource
##   Waffen und Rüstungen können nur EINMAL im Bag liegen; werden sie
##   ausgerüstet, verschwinden sie aus dem Bag (Referenz wandert zum CrewMember).

signal gold_changed(new_amount: int)
signal items_changed
signal crew_changed

var gold: int = 100
var items: Dictionary = {}          ## Item -> int (Anzahl)
var crew: Array = []                ## Array[CrewMember]
var active_index: int = 0           ## aktueller Kämpfer-Index in `crew`

func active_crew() -> CrewMember:
	if crew.is_empty():
		return null
	active_index = clamp(active_index, 0, crew.size() - 1)
	return crew[active_index]

## Gold ----------------------------------------------------------------

func add_gold(amount: int) -> void:
	gold += amount
	gold_changed.emit(gold)

func spend_gold(amount: int) -> bool:
	if amount > gold:
		return false
	gold -= amount
	gold_changed.emit(gold)
	return true

## Items ---------------------------------------------------------------

func add_item(item: Item, count: int = 1) -> void:
	if item == null or count <= 0:
		return
	items[item] = items.get(item, 0) + count
	items_changed.emit()

func remove_item(item: Item, count: int = 1) -> bool:
	var have: int = items.get(item, 0)
	if have < count:
		return false
	have -= count
	if have <= 0:
		items.erase(item)
	else:
		items[item] = have
	items_changed.emit()
	return true

func count_of(item: Item) -> int:
	return items.get(item, 0)

## Filter-Helfer für UIs.
func consumables() -> Array:
	var out: Array = []
	for it in items.keys():
		if it is Consumable:
			out.append(it)
	return out

func weapons_in_bag() -> Array:
	var out: Array = []
	for it in items.keys():
		if it is Weapon:
			out.append(it)
	return out

## Crew ----------------------------------------------------------------

func add_crew(member: CrewMember) -> void:
	if member == null or member in crew:
		return
	crew.append(member)
	crew_changed.emit()

func set_active(index: int) -> void:
	if index < 0 or index >= crew.size():
		return
	active_index = index
	crew_changed.emit()

## Equipment -----------------------------------------------------------

## Rüstet Waffe an `member` aus. Vorherige Waffe wandert zurück in den Bag.
## Gibt false zurück, wenn Element-Restriktion greift.
func equip_weapon(member: CrewMember, weapon: Weapon) -> bool:
	if member == null or weapon == null:
		return false
	if not weapon.can_be_equipped_by(member):
		return false
	if member.weapon != null:
		add_item(member.weapon, 1)
	remove_item(weapon, 1)
	member.weapon = weapon
	crew_changed.emit()
	return true

func equip_armor(member: CrewMember, armor: Armor) -> bool:
	if member == null or armor == null:
		return false
	if not armor.can_be_equipped_by(member):
		return false
	if member.armor != null:
		add_item(member.armor, 1)
	remove_item(armor, 1)
	member.armor = armor
	crew_changed.emit()
	return true
