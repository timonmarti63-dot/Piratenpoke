extends Node
## Bootstrap — initialisiert Startzustand des Spiels (Autoload, läuft nach den
## anderen Autoloads dank alphabetischer Reihenfolge → wir zwingen die
## Reihenfolge über die project.godot-Reihenfolge).
##
## Verantwortung: Inventar + Startcrew + Dorf-Registrierung. Läuft nur einmal.
##
## Später (v0.6) übernimmt hier auch das Laden eines Speicherstands.

const STARTER_CREW := [
	"res://data/crew/blaze_captain.tres",
	"res://data/crew/tide_gunner.tres",
	"res://data/crew/gale_scout.tres",
]

const STARTER_ITEMS := {
	"res://data/items/small_potion.tres": 3,
	"res://data/items/antidote.tres": 1,
}

const STARTING_GOLD := 120

func _ready() -> void:
	# Nur beim ersten Start initialisieren.
	if Inventory.crew.size() > 0:
		return
	for path in STARTER_CREW:
		var rc: Resource = load(path)
		if rc is CrewMember:
			Inventory.add_crew(rc)
	for path in STARTER_ITEMS.keys():
		var ri: Resource = load(path)
		if ri is Item:
			Inventory.add_item(ri, STARTER_ITEMS[path])
	Inventory.gold = STARTING_GOLD
	Inventory.gold_changed.emit(Inventory.gold)
	# Dorf-Registrierung
	VillageState.register_village(&"kelpholm", &"kelpholm_captain")
