class_name Consumable extends Item
## Consumable — Trank / Antidot / Buff-Elixier.
##
## Effekt-Typen:
##   "heal"           — heilt `power` HP.
##   "cure_poison"    — entfernt Gift-Status.
##   "atk_up"         — +power Angriff für `duration` Runden.
##   "def_up"         — +power Verteidigung für `duration` Runden.
##
## Reine Datenklasse. Die Anwendung (auf einen Combatant) liegt beim
## BattleState.apply_item() bzw. Overworld-Menü.

@export var effect: StringName = &"heal"
@export var power: int = 20
@export var duration: int = 3    ## nur für Buffs relevant

## True: kann nur im Kampf eingesetzt werden. False: nur Overworld.
## Default (beide): true = nutzbar in beiden Kontexten.
@export var usable_in_combat: bool = true
@export var usable_in_overworld: bool = true
