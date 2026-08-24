class_name DamageCalc extends RefCounted
## DamageCalc — reine Berechnung, keine Nebeneffekte.
##
## Formel (aus GDD §9):
##   damage = (attacker.attack / defender.defense) * skill.power * type_multiplier
##
## Wir clampen defense >= 1, damit keine Division durch 0 möglich ist,
## und runden am Ende. Minimum-Schaden = 1, damit ein Skill immer *irgendwas* macht.

static func compute(
	attacker_attack: int,
	defender_defense: int,
	skill_power: int,
	type_multiplier: float
) -> int:
	var def: float = float(max(1, defender_defense))
	var raw: float = (float(attacker_attack) / def) * float(skill_power) * type_multiplier
	return max(1, int(round(raw)))

## Bequemer Wrapper für Skill-Objekte.
static func for_skill(
	attacker_stats: CombatantData,
	defender_stats: CombatantData,
	skill: Skill,
	type_multiplier: float,
	attacker_bonus_attack: int = 0,
	defender_bonus_defense: int = 0
) -> int:
	var atk: int = attacker_stats.base_attack + attacker_bonus_attack
	var def: int = defender_stats.base_defense + defender_bonus_defense
	return compute(atk, def, skill.power, type_multiplier)
