class_name EnemyData extends CombatantData
## EnemyData — Gegner-spezifische Erweiterungen.

@export_group("Kampf-Belohnung")
@export var xp_reward: int = 15
@export var gold_reward: int = 8

@export_group("KI")
## "random" — wählt zufällig einen Skill mit Trefferchance > 0.
## "aggressive" — bevorzugt Skills mit "damage"-Effekt.
@export var ai_profile: StringName = &"random"

@export_group("Boss-Flag")
## Wenn true: Flucht ist deaktiviert.
@export var is_boss: bool = false
