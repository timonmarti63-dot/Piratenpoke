"""Generiert Unity .meta-Dateien fuer alle Skripte + ScriptableObject-Instanzen.

Der Editor wuerde diese sonst beim ersten Import selbst erstellen. Wir
liefern sie mit, damit alle Referenzen (fileID + guid) schon vor dem
Editor-Import konsistent sind.

GUID-Strategie: MD5(path) -> 32 hex Zeichen -- deterministisch pro Pfad.
So bleiben Referenzen stabil, auch wenn das Skript neu generiert wird.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "Assets"


def path_guid(rel: str) -> str:
    """Deterministische 32-hex GUID fuer einen relativen Asset-Pfad."""
    h = hashlib.md5(rel.encode("utf-8")).hexdigest()
    return h  # bereits 32 hex


def write_meta(asset_path: Path, content: str) -> None:
    meta = asset_path.with_suffix(asset_path.suffix + ".meta")
    meta.write_text(content, encoding="utf-8")


def script_meta_yaml(guid: str) -> str:
    return dedent(f"""\
        fileFormatVersion: 2
        guid: {guid}
        MonoImporter:
          externalObjects: {{}}
          serializedVersion: 2
          defaultReferences: []
          executionOrder: 0
          icon: {{instanceID: 0}}
          userData:
          assetBundleName:
          assetBundleVariant:
        """)


def folder_meta_yaml(guid: str) -> str:
    return dedent(f"""\
        fileFormatVersion: 2
        guid: {guid}
        folderAsset: yes
        DefaultImporter:
          externalObjects: {{}}
          userData:
          assetBundleName:
          assetBundleVariant:
        """)


def native_meta_yaml(guid: str) -> str:
    return dedent(f"""\
        fileFormatVersion: 2
        guid: {guid}
        NativeFormatImporter:
          externalObjects: {{}}
          mainObjectFileID: 11400000
          userData:
          assetBundleName:
          assetBundleVariant:
        """)


def scene_meta_yaml(guid: str) -> str:
    return dedent(f"""\
        fileFormatVersion: 2
        guid: {guid}
        DefaultImporter:
          externalObjects: {{}}
          userData:
          assetBundleName:
          assetBundleVariant:
        """)


def asmdef_meta_yaml(guid: str) -> str:
    return dedent(f"""\
        fileFormatVersion: 2
        guid: {guid}
        AssemblyDefinitionImporter:
          externalObjects: {{}}
          userData:
          assetBundleName:
          assetBundleVariant:
        """)


def write_all_metas() -> dict[str, str]:
    """Fuer jede .cs / .asmdef / .asset / .unity / Ordner -> .meta."""
    guids: dict[str, str] = {}

    def rel(p: Path) -> str:
        return str(p.relative_to(ROOT)).replace(os.sep, "/")

    # Alle Verzeichnisse
    for d in ASSETS.rglob("*"):
        if d.is_dir():
            g = path_guid(rel(d))
            guids[rel(d)] = g
            write_meta(d, folder_meta_yaml(g))

    # Fuer jede Datei je nach Endung
    for f in ASSETS.rglob("*"):
        if not f.is_file() or f.suffix == ".meta": continue
        r = rel(f)
        g = path_guid(r)
        guids[r] = g

        if f.suffix == ".cs":
            write_meta(f, script_meta_yaml(g))
        elif f.suffix == ".asmdef":
            write_meta(f, asmdef_meta_yaml(g))
        elif f.suffix == ".unity":
            write_meta(f, scene_meta_yaml(g))
        else:  # .asset, .prefab, .mat, .png ...
            write_meta(f, native_meta_yaml(g))

    return guids


def create_skill_asset(name: str, display: str, element: int, power: int,
                       heal: int = 0, accuracy: float = 0.95,
                       target: int = 0, cooldown: int = 0,
                       vfx: int = 0, vfx_duration: float = 0.0,
                       vfx_color=(1.0, 1.0, 1.0, 0.0)) -> Path:
    """element: 0=None 1=Fire 2=Water 3=Stone 4=Wind. target: 0=SingleEnemy usw.
    vfx: 0=None 1=Slash 2=Projectile 3=Burst 4=Heal 5=Beam."""
    script_guid = path_guid("Assets/Scripts/ScriptableObjects/SkillSO.cs")
    r, g, b, a = vfx_color
    body = dedent(f"""\
        %YAML 1.1
        %TAG !u! tag:unity3d.com,2011:
        --- !u!114 &11400000
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_CorrespondingSourceObject: {{fileID: 0}}
          m_PrefabInstance: {{fileID: 0}}
          m_PrefabAsset: {{fileID: 0}}
          m_GameObject: {{fileID: 0}}
          m_Enabled: 1
          m_EditorHideFlags: 0
          m_Script: {{fileID: 11500000, guid: {script_guid}, type: 3}}
          m_Name: {name}
          m_EditorClassIdentifier:
          displayName: "{display}"
          description: ""
          element: {element}
          target: {target}
          power: {power}
          heal: {heal}
          accuracy: {accuracy}
          cooldown: {cooldown}
          vfx: {vfx}
          vfxColor: {{r: {r}, g: {g}, b: {b}, a: {a}}}
          vfxDuration: {vfx_duration}
        """)
    p = ASSETS / "Data" / "Skills" / f"{name}.asset"
    p.write_text(body, encoding="utf-8")
    return p


def create_item_asset(name: str, display: str, category: int, buy: int,
                      heal_amt: int = 0, atk: int = 0, defense: int = 0,
                      spd: int = 0, cures_poison: bool = False,
                      elem_bonus: int = 0) -> Path:
    script_guid = path_guid("Assets/Scripts/ScriptableObjects/ItemSO.cs")
    body = dedent(f"""\
        %YAML 1.1
        %TAG !u! tag:unity3d.com,2011:
        --- !u!114 &11400000
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_CorrespondingSourceObject: {{fileID: 0}}
          m_PrefabInstance: {{fileID: 0}}
          m_PrefabAsset: {{fileID: 0}}
          m_GameObject: {{fileID: 0}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {script_guid}, type: 3}}
          m_Name: {name}
          displayName: "{display}"
          description: ""
          category: {category}
          buyPrice: {buy}
          sellPrice: {buy // 2}
          healAmount: {heal_amt}
          curesPoison: {int(cures_poison)}
          attackBonus: {atk}
          defenseBonus: {defense}
          speedBonus: {spd}
          elementBonus: {elem_bonus}
        """)
    p = ASSETS / "Data" / "Items" / f"{name}.asset"
    p.write_text(body, encoding="utf-8")
    return p


def create_combatant_asset(kind: str, name: str, display: str, element: int,
                           color: tuple[float, float, float],
                           max_hp: int, atk: int, defense: int, speed: int,
                           skills: list[str],
                           extra: str = "") -> Path:
    """kind: 'Crew' oder 'Enemies'. skills: Liste von Skill-Asset-Namen."""
    so_name = "CrewMemberSO" if kind == "Crew" else "EnemyDataSO"
    script_guid = path_guid(f"Assets/Scripts/ScriptableObjects/{so_name}.cs")

    skill_yaml = ""
    for s in skills:
        g = path_guid(f"Assets/Data/Skills/{s}.asset")
        skill_yaml += f"    - {{fileID: 11400000, guid: {g}, type: 2}}\n"

    r, g, b = color
    body = dedent(f"""\
        %YAML 1.1
        %TAG !u! tag:unity3d.com,2011:
        --- !u!114 &11400000
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_CorrespondingSourceObject: {{fileID: 0}}
          m_PrefabInstance: {{fileID: 0}}
          m_PrefabAsset: {{fileID: 0}}
          m_GameObject: {{fileID: 0}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {script_guid}, type: 3}}
          m_Name: {name}
          displayName: "{display}"
          element: {element}
          placeholderColor: {{r: {r}, g: {g}, b: {b}, a: 1}}
          maxHp: {max_hp}
          baseAttack: {atk}
          baseDefense: {defense}
          speed: {speed}
          skills:
        """)
    body += skill_yaml if skill_yaml else "    []\n"
    if extra:
        body += extra
    p = ASSETS / "Data" / kind / f"{name}.asset"
    p.write_text(body, encoding="utf-8")
    return p


def main() -> None:
    # -- 1. Skills
    skills = [
        # (name, display, element, power, heal, accuracy, target, cooldown, vfx, vfx_dur, vfx_color)
        # vfx: 0=None 1=Slash 2=Projectile 3=Burst 4=Heal 5=Beam
        ("Skill_EmberSlash", "Glut-Klinge",  1, 18, 0,  0.95, 0, 0, 1, 0.4, (1.0, 0.5, 0.15, 1.0)),
        ("Skill_TideShot",   "Flutschuss",   2, 16, 0,  0.90, 0, 0, 2, 0.6, (0.3, 0.7, 1.0, 1.0)),
        ("Skill_GaleGust",   "Sturmboe",     4, 15, 0,  1.00, 0, 0, 3, 0.7, (0.7, 1.0, 0.75, 1.0)),
        ("Skill_VenomDart",  "Giftdolch",    0, 12, 0,  0.90, 0, 0, 2, 0.5, (0.6, 0.9, 0.3, 1.0)),
        ("Skill_QuickBandage","Bandagieren", 0,  0, 18, 1.00, 2, 0, 4, 0.9, (0.4, 1.0, 0.55, 1.0)),
    ]
    for args in skills:
        create_skill_asset(*args)

    # -- 2. Items
    items = [
        # (name, display, category, buy, heal_amt, atk, def, spd, cures_p, elem)
        ("Item_SmallPotion", "Kleiner Trank",   0, 15, 20, 0, 0, 0, False, 0),
        ("Item_BigPotion",   "Grosser Trank",   0, 40, 55, 0, 0, 0, False, 0),
        ("Item_Antidote",    "Gegengift",       0, 25,  0, 0, 0, 0, True,  0),
        ("Item_RustySaber",  "Rostiger Saebel", 1, 60,  0, 6, 0, 0, False, 0),
        ("Item_LeatherVest", "Lederweste",      2, 55,  0, 0, 5, 0, False, 0),
        ("Item_FlameCutlass","Feuersaebel",     1,120,  0,10, 0, 0, False, 1),
    ]
    for args in items:
        create_item_asset(*args)

    # -- 3. Crew (5 Mitglieder)
    create_combatant_asset("Crew", "Crew_Bran", "Kaeptn Bran", 1, (0.75, 0.20, 0.20),
                           max_hp=55, atk=14, defense=8, speed=10,
                           skills=["Skill_EmberSlash", "Skill_QuickBandage", "Skill_GaleGust"],
                           extra="  level: 3\n  xp: 0\n")
    create_combatant_asset("Crew", "Crew_Marina", "Marina die Kanonierin", 2, (0.20, 0.45, 0.85),
                           max_hp=48, atk=13, defense=7, speed=8,
                           skills=["Skill_TideShot", "Skill_QuickBandage"],
                           extra="  level: 3\n  xp: 0\n")
    create_combatant_asset("Crew", "Crew_Kite", "Kite die Spaeherin", 4, (0.40, 0.75, 0.45),
                           max_hp=42, atk=12, defense=6, speed=13,
                           skills=["Skill_GaleGust", "Skill_VenomDart"],
                           extra="  level: 3\n  xp: 0\n")
    create_combatant_asset("Crew", "Crew_Rocco", "Rocco Steinfaust", 3, (0.55, 0.50, 0.35),
                           max_hp=60, atk=15, defense=12, speed=6,
                           skills=["Skill_EmberSlash", "Skill_QuickBandage"],
                           extra="  level: 3\n  xp: 0\n")
    create_combatant_asset("Crew", "Crew_Nell", "Nell die Navigatorin", 0, (0.90, 0.85, 0.60),
                           max_hp=45, atk=11, defense=7, speed=12,
                           skills=["Skill_GaleGust", "Skill_QuickBandage"],
                           extra="  level: 3\n  xp: 0\n")

    # -- 4. Enemies
    create_combatant_asset("Enemies", "Enemy_WindBandit", "Wind-Bandit", 4, (0.30, 0.30, 0.35),
                           max_hp=36, atk=10, defense=5, speed=9,
                           skills=["Skill_GaleGust", "Skill_VenomDart"],
                           extra="  xpReward: 20\n  goldReward: 12\n  aiProfile: 0\n  isBoss: 0\n  troopLeaderId: \n")
    create_combatant_asset("Enemies", "Enemy_KelpholmCaptain", "Piraten-Kapitaen von Kelpholm", 2, (0.15, 0.15, 0.20),
                           max_hp=70, atk=14, defense=9, speed=10,
                           skills=["Skill_TideShot", "Skill_VenomDart"],
                           extra="  xpReward: 60\n  goldReward: 80\n  aiProfile: 0\n  isBoss: 1\n  troopLeaderId: kelpholm_captain\n")

    print("Assets erzeugt. Jetzt Metas schreiben...")
    guids = write_all_metas()
    print(f"Metas fertig ({len(guids)} Eintraege).")


if __name__ == "__main__":
    main()
