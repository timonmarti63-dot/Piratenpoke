extends Node
## TypeChart — Element-Effektivitäts-Matrix (Autoload).
##
## Design: klassisches Stein-Wasser-Feuer-Wind-Dreieck plus Kreuz.
##   Feuer  → stark gg. Wind   (Feuer bläht sich im Wind auf), schwach gg. Wasser, Stein
##   Wasser → stark gg. Feuer,                                    schwach gg. Wind, Stein
##   Stein  → stark gg. Feuer, Wasser                             schwach gg. Wind
##   Wind   → stark gg. Stein, Wasser                             schwach gg. Feuer
##
## Diese Werte sind bewusst symmetrisch verteilt — kein Element ist objektiv
## besser. Feintuning kommt im Balancing-Pass (v0.7+).
##
## Multiplier: 2.0 = stark, 0.5 = schwach, 1.0 = neutral, 0.0 = immun (aktuell unbenutzt).

const NEUTRAL: float = 1.0

## Attacker → { Defender: Multiplier }
const CHART: Dictionary = {
	&"fire": {
		&"wind":  2.0,
		&"water": 0.5,
		&"stone": 0.5,
	},
	&"water": {
		&"fire":  2.0,
		&"wind":  0.5,
		&"stone": 0.5,
	},
	&"stone": {
		&"fire":  2.0,
		&"water": 2.0,
		&"wind":  0.5,
	},
	&"wind": {
		&"stone": 2.0,
		&"water": 2.0,
		&"fire":  0.5,
	},
}

func multiplier(attacker: StringName, defender: StringName) -> float:
	if attacker == &"none" or defender == &"none":
		return NEUTRAL
	var row: Dictionary = CHART.get(attacker, {})
	return row.get(defender, NEUTRAL)

## UI-Hilfe: liefert einen Text wie "sehr effektiv!" / "kaum wirksam…".
func describe(mult: float) -> String:
	if mult >= 1.99:
		return "Sehr effektiv!"
	if mult <= 0.51 and mult > 0.0:
		return "Kaum wirksam…"
	if mult == 0.0:
		return "Hat keine Wirkung."
	return ""
