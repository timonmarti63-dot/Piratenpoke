# Piratenpoke — Game Design Document

> Rundenbasiertes 2D-Top-Down-Piraten-RPG im Pokémon-Stil.
> Engine: **Godot 4.x (GDScript)** · Kachelgröße: **64 × 64 px** · Plattform: **PC (Tastatur + Maus)**.

---

## 1. Aussehen der Welt (Art Direction & Raster)

Die Spielwelt ist ein klassisches 2D-Top-Down-RPG.

- **Struktur:** Alles basiert auf einem strikten Kachel-Raster (Grid). Die Welt ist aus quadratischen Blöcken (Tiles) aufgebaut — **64 × 64 Pixel pro Kachel**.
- **Platzhalter-Phase:** Zu Beginn bestehen alle Objekte (Bäume, Häuser, Berge) aus farbigen Rechtecken.
- **Atmosphäre:** Die Welt ist in klare Biome unterteilt (helles Grasland, dunkler Wald, feuriger Vulkan). Befindet sich ein Gebiet im "feindlichen" Zustand, ist die Beleuchtung düster; nach der Befreiung wird sie hell und freundlich.

## 2. Bewegung in der Welt (Grid-Movement & PC-Steuerung)

- **Steuerung:** Bewegung über `W`, `A`, `S`, `D` oder die Pfeiltasten. Interaktion über `E` oder `Enter`.
- **Grid-Lock:** Der Charakter bewegt sich exakt von einem Feld zum nächsten. Keine halben Schritte, keine diagonale Bewegung.
- **Input Buffering:** Der nächste Tastendruck wird schon kurz vor Ende der aktuellen Bewegung registriert — verhindert Stottern.
- **Kollision:** Jedes Feld hat eine unsichtbare Eigenschaft: `Walkable` (begehbar) oder `Solid` (blockiert).

## 3. Charaktere in der Welt

- **Der Captain:** Avatar des Spielers. Bewegt sich über die Weltkarte, kämpft aber nicht direkt selbst.
- **Die Crew (9 Mitglieder):** Einzigartige Piraten, in den Dörfern rekrutierbar. Sie sind die eigentlichen Kämpfer.
- **NPCs:** Händler (Schmied, Apotheker, Schiffsbauer) und Dorfbewohner. Meist auf festen Grid-Positionen oder mit zufälligen Routen.
- **Gegner:** Wilde Feinde (auf Wegen oder im hohen Gras) und Boss-Gegner, die feste Kacheln blockieren.

## 4. Charakter-Eigenschaften (Stats & Typen)

Jedes Crew-Mitglied und jeder Gegner besitzt ein Datenblatt (in Godot: `CrewMember` / `EnemyData` als **Custom Resource**):

- **Typ / Element:** Feuer, Wasser, Stein, Wind — bestimmt Stärken und Schwächen im Kampf.
- **Basis-Attribute:**
  - `max_hp` — Maximale Lebenspunkte
  - `base_attack` — Physischer / magischer Schaden
  - `base_defense` — Schadensverringerung bei Treffern
  - `speed` — Reihenfolge im Kampf, Fluchtchance
- **Sonderfertigkeiten (Skills):** Bis zu 4 Attacken pro Charakter (Schaden, Heilung, Status-Effekte wie Gift, Buffs).

## 5. Apotheke, Schmiede und Arenen

- **Apotheke:** Kauf von Verbrauchsgütern (Heiltränke, Gegengift, temporäre Buffs).
- **Schmiede:** Dauerhafte Ausrüstung — Waffen werden an bestimmte Crew-Mitglieder gebunden und erhöhen `base_attack` permanent.
- **Arenen:** End-Herausforderung jeder großen Insel. Rätsel-Dungeon auf dem Grid + Bosskampf. Sieg schaltet die nächste Insel frei.

## 6. Dörfer / Städte und Übergänge

- **State Machine (Dorf-Zustand):** Dörfer haben `is_safe: bool`.
  - `false` → Dorf von Feinden überrannt, Shops zu, Kämpfe triggern.
  - Truppenführer besiegt → `true`. NPCs erscheinen, Shops öffnen.
- **Übergänge (Szenenwechsel):** Zwischen Biomen liegen "Tunnel". Beim Betreten:
  1. Input deaktivieren
  2. `FadeOut` (schwarz)
  3. Neue Tilemap laden
  4. `FadeIn`
  Gleiches gilt für Häuser.

## 7. Schiff 1 (Early Game) & Schiff 2 (Endgame)

Das Schiff navigiert auf einer separaten Wasser-Tilemap.

- **Schiff 1** — Erste 3 Inseln: Kleines Piratenschiff, reine Fortbewegung zwischen den Häfen.
- **Schiff 2** — Nach den 3 Bossen: Aufgerüstete Galeone mit **Kanonen**. Damit können auf der Wasser-Map Blockaden (Felsenriffe, Strudel) weggeschossen werden, um das verborgene **"Splittermeer"** mit den 12 Endgame-Inseln zu erreichen.

## 8. Attribute und Verbesserungs-System

- **XP:** Nach jedem gewonnenen Kampf erhalten beteiligte Crew-Mitglieder XP. Level-Up → Basis-Attribute steigen leicht.
- **Manuelle Verbesserung:** Überschüssiges Gold + XP im **Gym** (siehe §12) einsetzen, um Lieblingscharaktere über das Level-Limit hinaus zu pushen.

## 9. Kampfsystem

- **Ablauf:** Gegner-Berührung → `Combat Scene`. **1-gegen-1**, rundenbasiert (Pokémon-Style).
- **Initiative:** `speed`-Vergleich, höherer Wert beginnt.
- **Menü** (Maus oder Tastatur, 4 Befehle):
  1. **Kämpfen** — Skill auswählen
  2. **Item** — Inventar öffnen
  3. **Wechseln** — Aktiven Kämpfer tauschen (kostet 1 Runde)
  4. **Flucht** — Bei Bossen deaktiviert
- **Schadensformel:**
  `(attack / defense) * skill_power * type_multiplier`

## 10. Inventar, Waffen, Rüstung und Tränke

- **Globales Inventar:** Der Captain trägt einen unendlichen Beutel für das ganze Team.
- **Tränke (Consumables):** Nutzung im Kampf oder in der Oberwelt, heilen HP oder Status. Verbrauchen sich.
- **Waffen & Rüstungen (Gear):** Fest einem Crew-Mitglied zugewiesen. **1 Waffe + 1 Rüstung** pro Charakter. Addieren flache Werte auf `base_attack` / `base_defense`.

## 11. Shop-System (Apotheke & Schmiede)

- **Apotheke-UI:** Fenster zeigt Gold und kaufbare Tränke. Klick → Gold abziehen, Item ins globale Inventar.
- **Schmiede-UI:** Kaufbare Waffen. Prüft vor Kauf, ob das Crew-Mitglied die Waffe tragen darf (Sumpf-Healer ≠ Bergbau-Axt). Nach Kauf: Gold abziehen, automatisch ausrüsten.

## 12. Gym (Trainingslager)

Spezielles Gebäude in Dörfern (oder Apotheken-Anbau). **Min-Maxing für Endgame.**

- Spieler wählt Crew-Mitglied.
- Investiert Gold (oder Trainings-Tokens) → Basis-Stats permanent erhöhen.
- Beispiel: `500 Gold → max_hp +20`.
- Ermöglicht das Meistern der 12 schweren Endgame-Inseln.

## 13. Hafen (Schiffs-Upgrades)

In jedem Dorf mit Meerzugang: Schiffsbauer-NPC am Steg. UI-Fenster für:

- **Rumpf-Panzerung:** Bei See-Monster-Angriffen sinkt das Schiff nicht sofort (Game-Over-Schutz).
- **Bessere Segel:** Senkt Timer zwischen Grid-Bewegungen auf dem Wasser → schnellere Fahrt.
- **Kanonen (nur Schiff 2):** Aktions-Taste auf Ozean-Map freigeschaltet → Hindernisse zerstören.

---

## Anhang: Datenstruktur-Skizzen (Godot Custom Resources)

```gdscript
# CrewMember.gd
class_name CrewMember extends Resource

@export var display_name: String
@export var element: String  # "fire" | "water" | "stone" | "wind"
@export var max_hp: int
@export var base_attack: int
@export var base_defense: int
@export var speed: int
@export var skills: Array[Skill] = []      # max. 4
@export var equipped_weapon: Weapon
@export var equipped_armor: Armor
@export var level: int = 1
@export var xp: int = 0
```

```gdscript
# Skill.gd
class_name Skill extends Resource

@export var name: String
@export var element: String
@export var power: int
@export var accuracy: float = 1.0
@export var effect: String  # "damage" | "heal" | "poison" | "def_buff" ...
```

```gdscript
# Typen-Matrix (global, z. B. in TypeChart.gd Autoload)
# type_multiplier[attacker][defender] = float
```
