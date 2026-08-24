class_name CombatantData extends Resource
## CombatantData — Basisklasse für Crew und Gegner.
##
## Enthält ausschließlich statische Stats + Skill-Liste. Die veränderliche
## Kampflaufzeit (aktuelle HP, aktive Buffs, Gift-Ticker) lebt in
## BattleState.Combatant, nicht hier — damit bleiben Resource-Dateien
## deterministisch und wiederverwendbar zwischen Kämpfen.

@export var display_name: String = "Unbekannt"
@export var element: StringName = &"none"       ## "fire" | "water" | "stone" | "wind" | "none"

@export_group("Basis-Attribute")
@export var max_hp: int = 40
@export var base_attack: int = 10
@export var base_defense: int = 6
@export var speed: int = 8

@export_group("Skills")
## Bis zu 4 Skills. Weitere werden im Menü ignoriert.
## Untypisiertes Array für saubere .tres-Serialisierung; wir prüfen im Code auf null.
@export var skills: Array = []

@export_group("Portrait / UI")
@export var portrait: Texture2D
