class_name Skill extends Resource
## Skill — eine Kampf-Aktion (bis zu 4 pro Charakter).
##
## Effekt-Typen (aktuell unterstützt):
##   "damage"    — normaler Schaden. Nutzt Damage-Formel + Typen-Multiplikator.
##   "heal"      — heilt den Anwender um `power` HP (kein Typ-Bonus).
##   "poison"    — wendet Gift auf das Ziel an (Schaden über Zeit, siehe BattleState).
##   "def_buff"  — Verteidigungs-Boost für den Anwender (temporär).
##
## Alle .tres-Instanzen liegen unter data/skills/.

@export var display_name: String = "Unbenannter Skill"
@export var element: StringName = &"none"    ## "fire" | "water" | "stone" | "wind" | "none"

## Bei "damage": Schadens-Grundwert. Bei "heal": HP-Betrag. Bei "def_buff": +Def pro Turn.
@export var power: int = 20

## Trefferchance 0.0–1.0.
@export var accuracy: float = 1.0

@export var effect: StringName = &"damage"   ## siehe Kommentar oben

## Wie viele Runden hält ein Buff / DoT? Ignoriert für "damage" und "heal".
@export var duration: int = 3

@export_multiline var description: String = ""
