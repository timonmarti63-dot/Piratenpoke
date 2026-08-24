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

## 🗺️ Aktueller Stand — v0.2

Startbares Grundgerüst:

- **Autoloads** `GameConfig` (Konstanten) und `InputBuffer` (globaler Richtungs-Puffer).
- **`PlayerController`** mit Grid-Lock, Kollision über TileMap-Property `solid` und nahtlosem Input-Buffering.
- **Testraum** (16 × 9 Kacheln) mit Baumrand, Pfad, Felsen als Hindernis und Sand + Wasser-Teich.
- **Platzhalter-Assets** — farbige 64 × 64 PNGs (Gras, Sand, Pfad, Wasser, Baum, Fels + Captain-Sprite).

**Start:** Godot 4.x → `Import` → `project.godot` → `F5`. Bewegung mit `WASD` / Pfeilen. Wasser, Bäume und Felsen blockieren, Sand/Pfad/Gras sind begehbar.

### Platzhalter regenerieren

```bash
python scripts/tools/gen_placeholder_tiles.py   # Einzel-PNGs neu
python scripts/tools/gen_tileset_atlas.py       # Atlas neu bauen
python scripts/tools/gen_world_tscn.py          # Testkarte neu bauen
```

## 🚀 Erste Öffnung in Godot

1. Godot 4.x herunterladen: <https://godotengine.org/download>
2. In Godot: `Import` → dieses Repo-Verzeichnis auswählen → `project.godot`
3. Godot legt beim ersten Öffnen automatisch den `.godot/`-Ordner an (bereits in `.gitignore`).

## 🗺️ Roadmap

- [x] **v0.1** — GDD + Projektstruktur
- [x] **v0.2** — Grid-Movement, Input-Buffering, Kollision, Testraum
- [ ] **v0.3** — Combat Scene, Stats, Typen-Multiplikator, 1-gegen-1 Rundenkampf
- [ ] **v0.4** — Dorf mit `is_safe`-Zustand, Apotheke + Schmiede UI
- [ ] **v0.5** — Schiff 1, Ozean-Tilemap, Häfen
- [ ] **v0.6** — Gym, XP-System, Level-Ups
- [ ] **v0.7** — Erste 3 Inseln komplett spielbar
- [ ] **v1.0** — Schiff 2 + Splittermeer + 12 Endgame-Inseln

Details siehe [`docs/GDD.md`](docs/GDD.md).
