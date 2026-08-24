class_name Item extends Resource
## Item — Basisklasse für alles im Inventar.
##
## Item selbst ist bewusst abstrakt (keine Effekt-Logik). Konkrete Subklassen:
##   - Consumable  (Tränke, Antidote, Buff-Elixiere)
##   - Weapon      (fest ausrüstbar, +base_attack)
##   - Armor       (fest ausrüstbar, +base_defense)
##
## Konkrete Effekt-Ausführung liegt bei den Subklassen — nicht hier. So bleibt
## die Basis frei von Kampf-/Inventar-Kopplung.

@export var id: StringName = &""                ## eindeutige ID, z.B. &"potion_small"
@export var display_name: String = "Item"
@export_multiline var description: String = ""
@export var buy_price: int = 10
@export var sell_price: int = 5
@export var icon: Texture2D
