extends Node
## GameConfig — globale Konstanten (Autoload).
##
## Wird als Autoload "GameConfig" registriert (siehe project.godot).
## Zentrale Wahrheit für Kachelgröße, Bewegungsgeschwindigkeit etc.

## Kantenlänge einer Kachel in Pixeln.
const TILE_SIZE: int = 64

## Sekunden pro Feld-Schritt an Land.
## 0.14 ergibt ~7 Kacheln pro Sekunde — flüssig, aber nicht zu schnell.
const MOVE_TIME_LAND: float = 0.14

## Sekunden pro Feld-Schritt auf dem Wasser (Schiff 1 — wird später
## durch Segel-Upgrades weiter reduziert).
const MOVE_TIME_SEA: float = 0.28

## Zeitfenster (in Sekunden vor Bewegungsende), in dem der nächste
## Tastendruck bereits gepuffert wird. Verhindert Stottern beim
## Halten oder schnellen Nachdrücken einer Richtung.
const INPUT_BUFFER_WINDOW: float = 0.08

## Physik-Kollisions-Layer.
## Layer 1 = Player, Layer 2 = feste Welt (Wände, Bäume, Häuser).
const LAYER_PLAYER: int = 1
const LAYER_WORLD_SOLID: int = 2

## Custom-Data-Layer-Name auf der TileMap:
## Kacheln mit dieser Property = true blockieren Bewegung.
const TILE_PROPERTY_SOLID: StringName = &"solid"
