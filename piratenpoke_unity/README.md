# Piratenpoke – Unity 3D (Switch-Pokémon-Stil)

Portierung des 2D-Godot-Prototyps (`../`) auf Unity 6 mit URP, Cinemachine
und dem neuen Input System. Umgesetzt nach dem GDD "3D Switch RPG Style".

## Version

- **Unity:** 6000.0.23f1 (Unity 6 LTS-Zweig)
- **Render Pipeline:** URP 17
- **Input:** Input System 1.11
- **Kamera:** Cinemachine 3.1

Wenn du eine andere 6.x-Version installiert hast, ändere die Zeilen in
`ProjectSettings/ProjectVersion.txt` – Unity migriert dann beim ersten Öffnen.

## Erstes Öffnen

1. `Unity Hub` → **Add** → Ordner `piratenpoke_unity/` wählen.
2. Unity öffnet das Projekt. Beim ersten Start werden alle Packages
   geladen (URP, Cinemachine, Input System, TextMeshPro) – kann 2–5 min
   dauern.
3. TMP-Essentials-Dialog erscheint → **Import TMP Essentials** klicken.
4. Wenn Unity nach einem Input Actions Asset fragt: **Create One**
   akzeptieren, benenne es `PlayerInputActions.inputactions`, füge zwei
   Action Maps hinzu ("Gameplay") mit Actions:
   - `Move` (Value/Vector2, WASD + Left Stick)
   - `Run`  (Button, Left Shift + Left Stick Press)
   - `Jump` (Button, Space + South Button)
   - `Interact` (Button, E + West Button)
5. Am Player-GameObject in `TestIsland.unity`: `PlayerInput`-Komponente
   → Actions-Asset zuweisen, Behaviour auf **Send Messages** (nicht Invoke Unity Events).

> Die `.unity`-Scenes wurden serverseitig generiert. Die Skripte binden sich
> per GUID (siehe `scripts/gen_meta_and_assets.py`). Wenn du Skripte
> umbenennst, die GUID in der zugehörigen `.meta`-Datei fest halten oder
> neu generieren.

## Play-Test

- Öffne `Assets/Scenes/Boot.unity` und drücke **Play**.
- Boot lädt automatisch die Default-Party (Bran, Marina, Kite) ins
  Inventory und wechselt zu `TestIsland`.
- WASD läuft, `Shift` = rennen, `Space` = Sprung.
- Der Wind-Bandit patrouilliert – berühren = Kampf-Scene.
- Der Tunnel im Norden führt ins Dorf mit dem Kelpholm-Captain.

## Ordnerstruktur

```
piratenpoke_unity/
├── Assets/
│   ├── Data/
│   │   ├── Crew/         5 CrewMemberSO (Bran, Marina, Kite, Rocco, Nell)
│   │   ├── Enemies/      2 EnemyDataSO (WindBandit, KelpholmCaptain)
│   │   ├── Items/        6 ItemSO (Tränke, Waffen, Rüstung)
│   │   └── Skills/       5 SkillSO
│   ├── Scenes/           Boot / TestIsland / VillageKelpholm / BattleArena
│   ├── Scripts/          C#-Quellcode (mit Assembly Definition)
│   │   ├── Battle/
│   │   ├── Camera/
│   │   ├── Data/
│   │   ├── Encounter/
│   │   ├── Player/
│   │   ├── SceneManagement/
│   │   ├── ScriptableObjects/
│   │   ├── UI/
│   │   ├── Utils/
│   │   └── World/
│   └── ... (Materials, Prefabs, Settings – noch leer)
├── Packages/manifest.json
├── ProjectSettings/
└── scripts/              Python-Generatoren (nur für Wartung)
```

## Was funktioniert bereits (Sprint 1)

- 3D-Player mit `CharacterController` + Follow-Camera-Rig (Cinemachine)
- Sichtbare 3D-Feinde, die patrouillieren und den Kampf auslösen
- Fade-Übergänge zwischen Overworld / Village / Battle
- Rundenbasierter Kampf mit Element-Matrix (Fire > Wind > Stone > Water > Fire)
- ScriptableObjects für 5 Crew, 2 Feinde, 5 Skills, 6 Items
- `Inventory` und `VillageState` als statische Autoloads
- BattleHUD mit HP-Balken + dynamischen Skill-Buttons
- Shop-System (ShopUI + ShopNpc mit Raycast-Interaktion)

## Was fehlt (kommende Sprints)

- Cinemachine-Kamera-Wechsel im Battle (3 Kameras noch nicht verkabelt)
- Ozean-Scene + Schiffs-Controller
- Weitere 2 Inseln + 12 Endgame-Inseln
- Charakter-Modelle (aktuell Capsule-Placeholder mit farblichem Element-Code)
- Musik & Sound Effects
- Save/Load
- Level-Up- und XP-Logik

## Migrations-Notizen vom 2D-Godot-Vorprojekt

- `.tres` (Godot) → `.asset` (Unity ScriptableObject)
- `Autoload` (Godot) → `static class` (`Inventory`, `VillageState`)
- `TileMap` → 3D-Terrain / Cubes als Platzhalter
- `Node2D` + `Sprite2D` → `GameObject` + `MeshRenderer` (Primitives)
- Godot-Signals → C#-`event Action<>` (siehe `VillageState.VillageLiberated`)

Die alte 2D-Godot-Version bleibt im `main`-Branch erhalten (Tag `v0.4`).
Der 3D-Rewrite lebt in diesem Ordner unterhalb des Repos, damit beide
parallel existieren können.
