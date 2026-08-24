# 🏴‍☠️ Piratenpoke

Ein rundenbasiertes 2D-Top-Down-Piraten-RPG im Pokémon-Stil. Der Captain segelt mit seiner 9-köpfigen Crew durch 3 Startinseln und 12 Endgame-Inseln im "Splittermeer".

## 🔧 Tech-Stack

- **Engine:** [Godot 4.x](https://godotengine.org/) (GDScript)
- **Grid:** TileMap, 64 × 64 px pro Kachel
- **Daten:** Custom `Resource`-Klassen für Crew, Gegner, Items, Skills
- **Plattform:** PC (Tastatur `WASD` / Pfeile / `E` / `Enter`, Maus für Menüs)

## 📁 Projektstruktur

```
piratenpoke/
├── project.godot           # Godot-Projektdatei (Input-Map, Fenster, Auflösung)
├── docs/
│   └── GDD.md              # Vollständiges Game Design Document
├── assets/
│   ├── tiles/              # TileSet-Grafiken (später Platzhalter → Pixel-Art)
│   ├── sprites/            # Captain, Crew, NPCs, Gegner
│   └── audio/              # Musik & SFX
├── scenes/
│   ├── world/              # Weltkarte, Dörfer, Dungeons, Tunnel
│   ├── combat/             # Rundenbasierte Combat Scene
│   ├── ship/               # Ozean-Tilemap, Schiff 1 & 2
│   └── ui/                 # Menüs, Shops, Gym, Inventar, Hafen
├── scripts/
│   ├── core/               # GameManager, SceneLoader, InputBuffer, TypeChart
│   ├── entities/           # PlayerController (Grid-Movement), NPC, Enemy
│   ├── combat/             # BattleController, DamageCalc, TurnQueue
│   ├── ui/                 # ShopUI, GymUI, InventoryUI, PortUI
│   └── data/               # Basisklassen für Resources
└── data/                   # Konkrete Resource-Instanzen (.tres)
    ├── crew/               # 9 Crew-Mitglieder
    ├── enemies/            # Wilde Feinde + Bosse
    ├── items/              # Tränke, Waffen, Rüstungen
    ├── skills/             # Alle Attacken / Fertigkeiten
    └── islands/            # Insel-Konfigurationen (3 + 12)
```

## 🗺️ Aktueller Stand — v0.4 (verifiziert)

Spielbares Grundgerüst **inkl. Kampfsystem, Dorf, Läden und Party** — vollständig durch Headless-Smoke-Tests (38/38 grün) und einen manuellen Playtest mit Godot 4.3 + `xvfb-run` verifiziert (Testraum, Dorf unsicher/sicher, Kampf, Apotheke, Schmiede).

- **Autoloads (in Ladereihenfolge):** `GameConfig`, `InputBuffer`, `TypeChart`, `SceneRouter`, `Inventory`, `VillageState`, `Bootstrap`.
- **`PlayerController`** mit Grid-Lock, Kollision, nahtlosem Input-Buffering. Interaktion via `E` / `Enter`.
- **Rundenbasierter Kampf** mit vollständiger Party:
  - 4-Buttons-Menü: Kämpfen / Item / Wechseln / Flucht.
  - Skills, Items (Heilung, Gegengift, Buffs), Crew-Wechsel im Kampf, Flucht-Chance.
  - Auto-Wechsel bei KO, Sieg vergibt XP + Gold.
- **Item-Hierarchie** (Custom Resources): `Item` → `Consumable` / `Weapon` / `Armor`.
  Waffen und Rüstungen können auf Elemente beschränkt sein (`allowed_elements`).
- **Dorf Kelpholm** mit `is_safe`-Zustand:
  - Vor Sieg über den Truppenführer: Encounter aktiv, Läden geschlossen.
  - Nach Sieg: Truppenführer verschwindet, Apotheke + Schmiede öffnen.
- **Apotheke** (Consumables) und **Schmiede** (Waffen/Rüstungen mit Element-Prüfung, direktes Anlegen).
- **Testraum** mit Wind-Bandit-Encounter und **Portal ins Dorf** (Kachel `8,7`).

**Start:** Godot 4.x → `Import` → `project.godot` → `F5`.
Mit `WASD` bewegen, `E` interagiert (Läden), `Enter` bestätigt.

> Getestet mit **Godot 4.3.stable**. Frühere 4.x-Versionen sind nicht offiziell unterstützt.

### Startzustand

- 3 Crew: Käpt’n Bran (Feuer), Marina die Kanonierin (Wasser), Kite die Späherin (Wind).
- 120 Gold, 3 kleine Tränke, 1 Gegengift.
- Ziel-Route: Wind-Bandit → Dorf → Truppenführer → Läden.

### Assets regenerieren

```bash
python scripts/tools/gen_pixelart_tiles.py      # v0.4: Pixel-Art Kacheln + Captain-Sprite
```

Erzeugt alle 10 Tile-PNGs, `atlas.png` und `captain.png` im
Pokémon-Gen-4-Piraten-Stil (16×16 gemalt, 4× hochskaliert). Nach einer
Regenerierung Godot einmal starten, damit der Import-Cache neu aufgebaut wird
(oder `.godot/imported/` löschen).

`gen_placeholder_tiles.py` und `gen_tileset_atlas.py` sind DEPRECATED
(einfarbige Platzhalter aus v0.1).

> ⚠️ **`gen_world_tscn.py` und `gen_village_tscn.py` sind ab v0.4 DEPRECATED.**
> Sie erzeugen TileMap-Daten im Format 2 mit falschem Encoding — Godot 4.3
> rendert daraus graue Kacheln. Neue Karten stattdessen im Godot-Editor
> oder per `TileMap.set_cell(layer, coords, source_id, atlas_coords)` in einem
> `SceneTree`-Tool anlegen (siehe Commit `cf64a68`).

## 🚀 Erste Öffnung in Godot

1. Godot 4.x herunterladen: <https://godotengine.org/download>
2. In Godot: `Import` → dieses Repo-Verzeichnis auswählen → `project.godot`
3. Godot legt beim ersten Öffnen automatisch den `.godot/`-Ordner an (bereits in `.gitignore`).

## 🗺️ Roadmap

- [x] **v0.1** — GDD + Projektstruktur
- [x] **v0.2** — Grid-Movement, Input-Buffering, Kollision, Testraum
- [x] **v0.3** — Combat Scene, Stats, Typen-Multiplikator, 1-gegen-1 Rundenkampf
- [x] **v0.4** — Party-Kampf (Wechseln/Item), Item-Hierarchie (`Consumable`/`Weapon`/`Armor`), `VillageState`, Dorf Kelpholm, Apotheke, Schmiede, Element-Restriktionen fürs Anlegen
- [ ] **v0.5** — Schiff 1, Ozean-Tilemap, Häfen, freie Reise zwischen den 3 Startinseln
- [ ] **v0.6** — Gym, XP-System, Level-Ups, Fertigkeitsbaum
- [ ] **v0.7** — Erste 3 Inseln komplett spielbar (Dungeons, Sidequests, alle 9 Crew rekrutierbar)
- [ ] **v1.0** — Schiff 2 + Splittermeer + 12 Endgame-Inseln

Details siehe [`docs/GDD.md`](docs/GDD.md).
