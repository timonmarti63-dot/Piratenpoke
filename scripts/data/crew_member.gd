class_name CrewMember extends CombatantData
## CrewMember — Crew-spezifische Erweiterungen.
##
## Fügt XP, Level und Ausrüstungsslots hinzu. Waffen/Rüstungen sind noch
## nicht als eigene Klassen modelliert (kommt in v0.4 mit der Schmiede) —
## erstmal flache Bonus-Werte.

@export_group("Fortschritt")
@export var level: int = 1
@export var xp: int = 0

@export_group("Gear (v0.4 noch nicht persistent)")
@export var weapon_bonus_attack: int = 0
@export var armor_bonus_defense: int = 0

## Hilfsfunktionen — effektive Werte inkl. Gear.
func effective_attack() -> int:
	return base_attack + weapon_bonus_attack

func effective_defense() -> int:
	return base_defense + armor_bonus_defense
