class_name CrewMember extends CombatantData
## CrewMember — Crew-spezifische Erweiterungen.
##
## Enthält Fortschritt (Level/XP) und Equipment-Slots.
## `weapon` / `armor` sind Referenzen — kein Duplikat im Inventar.

@export_group("Fortschritt")
@export var level: int = 1
@export var xp: int = 0

@export_group("Equipment")
@export var weapon: Weapon
@export var armor: Armor

## Legacy-Felder aus v0.3 (bleiben für Rückwärts-Kompatibilität in bestehenden
## .tres, werden aber nicht mehr genutzt, wenn `weapon`/`armor` gesetzt sind).
@export var weapon_bonus_attack: int = 0
@export var armor_bonus_defense: int = 0

func effective_attack() -> int:
	var bonus: int = weapon.attack_bonus if weapon != null else weapon_bonus_attack
	return base_attack + bonus

func effective_defense() -> int:
	var bonus: int = armor.defense_bonus if armor != null else armor_bonus_defense
	return base_defense + bonus
