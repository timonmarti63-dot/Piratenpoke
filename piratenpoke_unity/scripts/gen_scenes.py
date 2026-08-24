"""Erzeugt drei Unity-Scenes fuer den ersten spielbaren Kern:

  Boot.unity         -- SceneRouter + FadeOverlay + Bootstrap; laedt TestIsland
  TestIsland.unity   -- Rasen-Ebene, Player-Kapsel, Follow-Cam, Wind-Bandit
                        patrouilliert, Tunnel zum Dorf
  VillageKelpholm.unity -- Sand-Ebene mit zwei Haus-Cubes + Shop-NPC-Kapsel +
                        Kelpholm-Captain (Boss-Encounter)
  BattleArena.unity  -- Kleine Arena mit 3 Cinemachine-Kameras + BattleManager
                        + BattleHUD

Scenes werden minimalistisch geschrieben -- nur die notwendigen GameObjects
und Component-Referenzen; dank deterministischer GUIDs koennen die Skripte
korrekt binden.

Wenn Unity die Scene oeffnet, wird die Feinabstimmung fuer Terrain-Farbe,
UI-Details und Materials im Editor gemacht. Das Grundgeruest laeuft aber
sofort.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "Assets"
SCENES = ASSETS / "Scenes"


def path_guid(rel: str) -> str:
    return hashlib.md5(rel.encode("utf-8")).hexdigest()


# -- Script GUIDs (wir referenzieren die Skripte per GUID)
G = {
    "PlayerController3D":   path_guid("Assets/Scripts/Player/PlayerController3D.cs"),
    "InteractionRaycaster": path_guid("Assets/Scripts/Player/InteractionRaycaster.cs"),
    "FollowCameraRig":      path_guid("Assets/Scripts/Camera/FollowCameraRig.cs"),
    "EnemyPatrol":          path_guid("Assets/Scripts/Encounter/EnemyPatrol.cs"),
    "SceneRouter":          path_guid("Assets/Scripts/SceneManagement/SceneRouter.cs"),
    "SceneTunnel":          path_guid("Assets/Scripts/SceneManagement/SceneTunnel.cs"),
    "FadeOverlay":          path_guid("Assets/Scripts/SceneManagement/FadeOverlay.cs"),
    "BattleManager":        path_guid("Assets/Scripts/Battle/BattleManager.cs"),
    "BattleHUD":            path_guid("Assets/Scripts/UI/BattleHUD.cs"),
    "ShopUI":               path_guid("Assets/Scripts/UI/ShopUI.cs"),
    "VillageController":    path_guid("Assets/Scripts/World/VillageController.cs"),
    "ShopNpc":              path_guid("Assets/Scripts/World/ShopNpc.cs"),
    "BootStrap":            path_guid("Assets/Scripts/Utils/BootStrap.cs"),
}

# -- Asset GUIDs
A = {
    "Bran":            path_guid("Assets/Data/Crew/Crew_Bran.asset"),
    "Marina":          path_guid("Assets/Data/Crew/Crew_Marina.asset"),
    "Kite":            path_guid("Assets/Data/Crew/Crew_Kite.asset"),
    "WindBandit":      path_guid("Assets/Data/Enemies/Enemy_WindBandit.asset"),
    "KelpholmCaptain": path_guid("Assets/Data/Enemies/Enemy_KelpholmCaptain.asset"),
    "SmallPotion":     path_guid("Assets/Data/Items/Item_SmallPotion.asset"),
    "BigPotion":       path_guid("Assets/Data/Items/Item_BigPotion.asset"),
    "Antidote":        path_guid("Assets/Data/Items/Item_Antidote.asset"),
    "RustySaber":      path_guid("Assets/Data/Items/Item_RustySaber.asset"),
    "LeatherVest":     path_guid("Assets/Data/Items/Item_LeatherVest.asset"),
    "FlameCutlass":    path_guid("Assets/Data/Items/Item_FlameCutlass.asset"),
}


# --------------------------------------------------------------------------
# YAML-Blocks: kleine wiederverwendbare Snippets
# --------------------------------------------------------------------------
_fid_counter = 100

def fid() -> int:
    global _fid_counter
    _fid_counter += 1
    return _fid_counter


HEADER = dedent("""\
    %YAML 1.1
    %TAG !u! tag:unity3d.com,2011:
    --- !u!29 &1
    OcclusionCullingSettings:
      m_ObjectHideFlags: 0
      serializedVersion: 2
      m_OcclusionBakeSettings:
        smallestOccluder: 5
        smallestHole: 0.25
        backfaceThreshold: 100
      m_SceneGUID: 00000000000000000000000000000000
      m_OcclusionCullingData: {fileID: 0}
    --- !u!104 &2
    RenderSettings:
      m_ObjectHideFlags: 0
      serializedVersion: 10
      m_Fog: 0
      m_FogColor: {r: 0.5, g: 0.5, b: 0.5, a: 1}
      m_FogMode: 3
      m_FogDensity: 0.01
      m_LinearFogStart: 0
      m_LinearFogEnd: 300
      m_AmbientSkyColor: {r: 0.6, g: 0.7, b: 0.85, a: 1}
      m_AmbientEquatorColor: {r: 0.55, g: 0.6, b: 0.55, a: 1}
      m_AmbientGroundColor: {r: 0.4, g: 0.35, b: 0.3, a: 1}
      m_AmbientIntensity: 1
      m_AmbientMode: 0
      m_SubtractiveShadowColor: {r: 0.42, g: 0.478, b: 0.627, a: 1}
      m_SkyboxMaterial: {fileID: 10304, guid: 0000000000000000f000000000000000, type: 0}
      m_HaloStrength: 0.5
      m_FlareStrength: 1
      m_FlareFadeSpeed: 3
      m_HaloTexture: {fileID: 0}
      m_SpotCookie: {fileID: 10001, guid: 0000000000000000e000000000000000, type: 0}
      m_DefaultReflectionMode: 0
      m_DefaultReflectionResolution: 128
      m_ReflectionBounces: 1
      m_ReflectionIntensity: 1
      m_CustomReflection: {fileID: 0}
      m_Sun: {fileID: 0}
      m_IndirectSpecularColor: {r: 0.44657844, g: 0.4964466, b: 0.5748076, a: 1}
      m_UseRadianceAmbientProbe: 0
    --- !u!157 &3
    LightmapSettings:
      m_ObjectHideFlags: 0
      serializedVersion: 12
      m_GIWorkflowMode: 1
      m_EnableBakedLightmaps: 0
      m_EnableRealtimeLightmaps: 0
    --- !u!196 &4
    NavMeshSettings:
      serializedVersion: 2
      m_ObjectHideFlags: 0
      m_BuildSettings:
        agentTypeID: 0
        agentRadius: 0.5
        agentHeight: 2
        agentSlope: 45
        agentClimb: 0.4
      m_NavMeshData: {fileID: 0}
    """)


def light_yaml(go_id: int, tr_id: int, light_id: int) -> str:
    return dedent(f"""\
        --- !u!1 &{go_id}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {tr_id}}}
          - component: {{fileID: {light_id}}}
          m_Layer: 0
          m_Name: DirectionalLight
          m_IsActive: 1
        --- !u!4 &{tr_id}
        Transform:
          m_GameObject: {{fileID: {go_id}}}
          m_LocalRotation: {{x: 0.4, y: -0.15, z: 0.05, w: 0.9}}
          m_LocalPosition: {{x: 0, y: 10, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!108 &{light_id}
        Light:
          m_GameObject: {{fileID: {go_id}}}
          m_Enabled: 1
          serializedVersion: 10
          m_Type: 1
          m_Color: {{r: 1, g: 0.98, b: 0.88, a: 1}}
          m_Intensity: 1.2
          m_Range: 10
          m_SpotAngle: 30
          m_CookieSize: 10
          m_Shadows:
            m_Type: 2
            m_Resolution: -1
            m_CustomResolution: -1
            m_Strength: 0.8
            m_Bias: 0.05
            m_NormalBias: 0.4
            m_NearPlane: 0.2
            m_CullingMatrixOverride:
              e00: 1
              e01: 0
              e02: 0
              e03: 0
              e10: 0
              e11: 1
              e12: 0
              e13: 0
              e20: 0
              e21: 0
              e22: 1
              e23: 0
              e30: 0
              e31: 0
              e32: 0
              e33: 1
            m_UseCullingMatrixOverride: 0
          m_RenderMode: 0
          m_CullingMask:
            serializedVersion: 2
            m_Bits: 4294967295
        """)


def cube_yaml(go_id: int, tr_id: int, mf_id: int, mr_id: int, col_id: int,
              name: str, pos: tuple[float, float, float],
              scale: tuple[float, float, float], color=(0.4, 0.7, 0.4),
              is_trigger: int = 0, tag: str = "Untagged") -> str:
    x, y, z = pos
    sx, sy, sz = scale
    r, g, b = color
    return dedent(f"""\
        --- !u!1 &{go_id}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {tr_id}}}
          - component: {{fileID: {mf_id}}}
          - component: {{fileID: {mr_id}}}
          - component: {{fileID: {col_id}}}
          m_Layer: 0
          m_Name: {name}
          m_TagString: {tag}
          m_IsActive: 1
        --- !u!4 &{tr_id}
        Transform:
          m_GameObject: {{fileID: {go_id}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: {x}, y: {y}, z: {z}}}
          m_LocalScale: {{x: {sx}, y: {sy}, z: {sz}}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!33 &{mf_id}
        MeshFilter:
          m_GameObject: {{fileID: {go_id}}}
          m_Mesh: {{fileID: 10202, guid: 0000000000000000e000000000000000, type: 0}}
        --- !u!23 &{mr_id}
        MeshRenderer:
          m_GameObject: {{fileID: {go_id}}}
          m_Enabled: 1
          m_CastShadows: 1
          m_ReceiveShadows: 1
          m_DynamicOccludee: 1
          m_Materials:
          - {{fileID: 10303, guid: 0000000000000000f000000000000000, type: 0}}
          m_StaticShadowCaster: 0
          m_MotionVectors: 1
          m_LightProbeUsage: 1
          m_ReflectionProbeUsage: 1
          m_RayTracingMode: 2
          m_AdditionalVertexStreams: {{fileID: 0}}
        --- !u!65 &{col_id}
        BoxCollider:
          m_GameObject: {{fileID: {go_id}}}
          m_IsTrigger: {is_trigger}
          m_Enabled: 1
          serializedVersion: 2
          m_Size: {{x: 1, y: 1, z: 1}}
          m_Center: {{x: 0, y: 0, z: 0}}
        """)


def scene_settings() -> str:
    return HEADER


# --------------------------------------------------------------------------
# TestIsland: Player + Follow-Cam + Wind-Bandit + Tunnel
# --------------------------------------------------------------------------
def gen_test_island() -> str:
    global _fid_counter
    _fid_counter = 100
    parts = [scene_settings()]

    # Directional Light
    parts.append(light_yaml(fid(), fid(), fid()))

    # Ground-Plane (grosser Cube, sehr flach)
    parts.append(cube_yaml(fid(), fid(), fid(), fid(), fid(),
                           "Ground", (0, -0.5, 0), (60, 1, 60), (0.3, 0.55, 0.3)))

    # Baeume (10 Cubes, gruen, unregelmaessig verteilt)
    import random
    random.seed(42)
    for i in range(10):
        x = random.uniform(-25, 25); z = random.uniform(-25, 25)
        parts.append(cube_yaml(fid(), fid(), fid(), fid(), fid(),
                               f"Tree_{i}", (x, 1.0, z), (0.6, 2.0, 0.6),
                               (0.15, 0.4, 0.15)))

    # Player (Capsule + CharacterController + PlayerController + FollowCameraRig)
    player_go = fid(); player_tr = fid(); player_mf = fid(); player_mr = fid()
    player_cc = fid(); player_ctrl = fid(); player_raycaster = fid(); player_input = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{player_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {player_tr}}}
          - component: {{fileID: {player_mf}}}
          - component: {{fileID: {player_mr}}}
          - component: {{fileID: {player_cc}}}
          - component: {{fileID: {player_ctrl}}}
          - component: {{fileID: {player_raycaster}}}
          - component: {{fileID: {player_input}}}
          m_Layer: 0
          m_Name: Player
          m_TagString: Player
          m_IsActive: 1
        --- !u!4 &{player_tr}
        Transform:
          m_GameObject: {{fileID: {player_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 1.1, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!33 &{player_mf}
        MeshFilter:
          m_GameObject: {{fileID: {player_go}}}
          m_Mesh: {{fileID: 10208, guid: 0000000000000000e000000000000000, type: 0}}
        --- !u!23 &{player_mr}
        MeshRenderer:
          m_GameObject: {{fileID: {player_go}}}
          m_Enabled: 1
          m_CastShadows: 1
          m_ReceiveShadows: 1
          m_Materials:
          - {{fileID: 10303, guid: 0000000000000000f000000000000000, type: 0}}
        --- !u!143 &{player_cc}
        CharacterController:
          m_GameObject: {{fileID: {player_go}}}
          m_Enabled: 1
          serializedVersion: 3
          m_Height: 2
          m_Radius: 0.5
          m_SlopeLimit: 45
          m_StepOffset: 0.3
          m_SkinWidth: 0.08
          m_MinMoveDistance: 0
          m_Center: {{x: 0, y: 0, z: 0}}
        --- !u!114 &{player_ctrl}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {player_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['PlayerController3D']}, type: 3}}
          m_Name:
        --- !u!114 &{player_raycaster}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {player_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['InteractionRaycaster']}, type: 3}}
          m_Name:
        --- !u!114 &{player_input}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {player_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: b7c0e7c8f7c2a4b2a9d6f1e3c4b5a6d7, type: 3}}
          m_Name:
        """))

    # Camera-Rig (leerer GameObject mit FollowCameraRig-Script)
    cam_root_go = fid(); cam_root_tr = fid(); cam_root_script = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{cam_root_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {cam_root_tr}}}
          - component: {{fileID: {cam_root_script}}}
          m_Layer: 0
          m_Name: CameraRig
          m_IsActive: 1
        --- !u!4 &{cam_root_tr}
        Transform:
          m_GameObject: {{fileID: {cam_root_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 0, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!114 &{cam_root_script}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {cam_root_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['FollowCameraRig']}, type: 3}}
          m_Name:
        """))

    # Main Camera (mit CinemachineBrain - Kompontenten-Referenz per GUID einer Cinemachine-Assembly nicht moeglich ohne
    # dass wir die interne GUID kennen. Wir setzen nur die Camera; der Nutzer fuegt CinemachineBrain im Editor hinzu
    # oder ich lasse das FollowCameraRig-Script beim Start CinemachineBrain adden.)
    mc_go = fid(); mc_tr = fid(); mc_cam = fid(); mc_al = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{mc_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {mc_tr}}}
          - component: {{fileID: {mc_cam}}}
          - component: {{fileID: {mc_al}}}
          m_Layer: 0
          m_Name: Main Camera
          m_TagString: MainCamera
          m_IsActive: 1
        --- !u!4 &{mc_tr}
        Transform:
          m_GameObject: {{fileID: {mc_go}}}
          m_LocalRotation: {{x: 0.15, y: 0, z: 0, w: 0.98}}
          m_LocalPosition: {{x: 0, y: 4, z: -8}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!20 &{mc_cam}
        Camera:
          m_GameObject: {{fileID: {mc_go}}}
          m_Enabled: 1
          serializedVersion: 2
          m_ClearFlags: 1
          m_BackGroundColor: {{r: 0.5, g: 0.65, b: 0.85, a: 0}}
          m_FieldOfView: 55
          m_NearClipPlane: 0.3
          m_FarClipPlane: 500
          m_TargetTexture: {{fileID: 0}}
          m_Depth: -1
          m_CullingMask: {{serializedVersion: 2, m_Bits: 4294967295}}
        --- !u!81 &{mc_al}
        AudioListener:
          m_GameObject: {{fileID: {mc_go}}}
          m_Enabled: 1
        """))

    # Wind-Bandit (Capsule + EnemyPatrol)
    wp_a_go = fid(); wp_a_tr = fid()
    wp_b_go = fid(); wp_b_tr = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{wp_a_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {wp_a_tr}}}
          m_Layer: 0
          m_Name: WP_A
          m_IsActive: 1
        --- !u!4 &{wp_a_tr}
        Transform:
          m_GameObject: {{fileID: {wp_a_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: -6, y: 1, z: 5}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!1 &{wp_b_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {wp_b_tr}}}
          m_Layer: 0
          m_Name: WP_B
          m_IsActive: 1
        --- !u!4 &{wp_b_tr}
        Transform:
          m_GameObject: {{fileID: {wp_b_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 6, y: 1, z: 5}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        """))
    bandit_go = fid(); bandit_tr = fid(); bandit_mf = fid(); bandit_mr = fid()
    bandit_col = fid(); bandit_script = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{bandit_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {bandit_tr}}}
          - component: {{fileID: {bandit_mf}}}
          - component: {{fileID: {bandit_mr}}}
          - component: {{fileID: {bandit_col}}}
          - component: {{fileID: {bandit_script}}}
          m_Layer: 0
          m_Name: WindBandit
          m_IsActive: 1
        --- !u!4 &{bandit_tr}
        Transform:
          m_GameObject: {{fileID: {bandit_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 1, z: 5}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!33 &{bandit_mf}
        MeshFilter:
          m_GameObject: {{fileID: {bandit_go}}}
          m_Mesh: {{fileID: 10208, guid: 0000000000000000e000000000000000, type: 0}}
        --- !u!23 &{bandit_mr}
        MeshRenderer:
          m_GameObject: {{fileID: {bandit_go}}}
          m_Enabled: 1
          m_Materials:
          - {{fileID: 10303, guid: 0000000000000000f000000000000000, type: 0}}
        --- !u!136 &{bandit_col}
        CapsuleCollider:
          m_GameObject: {{fileID: {bandit_go}}}
          m_IsTrigger: 1
          m_Enabled: 1
          m_Radius: 0.7
          m_Height: 2
          m_Direction: 1
          m_Center: {{x: 0, y: 0, z: 0}}
        --- !u!114 &{bandit_script}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {bandit_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['EnemyPatrol']}, type: 3}}
          m_Name:
          enemyData: {{fileID: 11400000, guid: {A['WindBandit']}, type: 2}}
          waypointA: {{fileID: {wp_a_tr}}}
          waypointB: {{fileID: {wp_b_tr}}}
          moveSpeed: 1.6
          pauseAtWaypoint: 1.0
          capsuleRenderer: {{fileID: {bandit_mr}}}
        """))

    # Tunnel -> Village (grosser Trigger-Cube am Nordrand)
    tunnel_go = fid(); tunnel_tr = fid(); tunnel_col = fid(); tunnel_script = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{tunnel_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {tunnel_tr}}}
          - component: {{fileID: {tunnel_col}}}
          - component: {{fileID: {tunnel_script}}}
          m_Layer: 0
          m_Name: TunnelToVillage
          m_IsActive: 1
        --- !u!4 &{tunnel_tr}
        Transform:
          m_GameObject: {{fileID: {tunnel_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 1, z: 20}}
          m_LocalScale: {{x: 8, y: 3, z: 2}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!65 &{tunnel_col}
        BoxCollider:
          m_GameObject: {{fileID: {tunnel_go}}}
          m_IsTrigger: 1
          m_Enabled: 1
          m_Size: {{x: 1, y: 1, z: 1}}
          m_Center: {{x: 0, y: 0, z: 0}}
        --- !u!114 &{tunnel_script}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {tunnel_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['SceneTunnel']}, type: 3}}
          m_Name:
          target: 1
        """))

    return "\n".join(parts)


# --------------------------------------------------------------------------
# Boot-Scene: SceneRouter + FadeOverlay + Bootstrap; laedt TestIsland
# --------------------------------------------------------------------------
def gen_boot() -> str:
    global _fid_counter
    _fid_counter = 100
    parts = [scene_settings()]
    parts.append(light_yaml(fid(), fid(), fid()))

    # Boot GameObject
    b_go = fid(); b_tr = fid(); b_router = fid(); b_fade = fid(); b_boot = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{b_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {b_tr}}}
          - component: {{fileID: {b_router}}}
          - component: {{fileID: {b_fade}}}
          - component: {{fileID: {b_boot}}}
          m_Layer: 0
          m_Name: Boot
          m_IsActive: 1
        --- !u!4 &{b_tr}
        Transform:
          m_GameObject: {{fileID: {b_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 0, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!114 &{b_router}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {b_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['SceneRouter']}, type: 3}}
          m_Name:
        --- !u!114 &{b_fade}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {b_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['FadeOverlay']}, type: 3}}
          m_Name:
        --- !u!114 &{b_boot}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {b_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['BootStrap']}, type: 3}}
          m_Name:
          defaultParty:
          - {{fileID: 11400000, guid: {A['Bran']}, type: 2}}
          - {{fileID: 11400000, guid: {A['Marina']}, type: 2}}
          - {{fileID: 11400000, guid: {A['Kite']}, type: 2}}
          defaultItems:
          - {{fileID: 11400000, guid: {A['SmallPotion']}, type: 2}}
          - {{fileID: 11400000, guid: {A['Antidote']}, type: 2}}
          defaultGold: 100
        """))

    # Camera (fuer Fade-Rendering falls hier stehen bleibt)
    mc_go = fid(); mc_tr = fid(); mc_cam = fid(); mc_al = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{mc_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {mc_tr}}}
          - component: {{fileID: {mc_cam}}}
          - component: {{fileID: {mc_al}}}
          m_Layer: 0
          m_Name: Main Camera
          m_TagString: MainCamera
          m_IsActive: 1
        --- !u!4 &{mc_tr}
        Transform:
          m_GameObject: {{fileID: {mc_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 1, z: -5}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!20 &{mc_cam}
        Camera:
          m_GameObject: {{fileID: {mc_go}}}
          m_Enabled: 1
          m_ClearFlags: 2
          m_BackGroundColor: {{r: 0, g: 0, b: 0, a: 1}}
          m_FieldOfView: 60
          m_NearClipPlane: 0.3
          m_FarClipPlane: 100
        --- !u!81 &{mc_al}
        AudioListener:
          m_GameObject: {{fileID: {mc_go}}}
          m_Enabled: 1
        """))

    return "\n".join(parts)


# --------------------------------------------------------------------------
# VillageKelpholm: 2 Haeuser, Kelpholm-Captain (Boss)
# --------------------------------------------------------------------------
def gen_village() -> str:
    global _fid_counter
    _fid_counter = 100
    parts = [scene_settings()]
    parts.append(light_yaml(fid(), fid(), fid()))
    # Sand-Boden
    parts.append(cube_yaml(fid(), fid(), fid(), fid(), fid(),
                           "Sand", (0, -0.5, 0), (40, 1, 40), (0.85, 0.75, 0.5)))
    # Zwei Haus-Cubes
    parts.append(cube_yaml(fid(), fid(), fid(), fid(), fid(),
                           "House_Apothecary", (-5, 1.5, 4), (3, 3, 3), (0.5, 0.35, 0.2)))
    parts.append(cube_yaml(fid(), fid(), fid(), fid(), fid(),
                           "House_Blacksmith", (5, 1.5, 4), (3, 3, 3), (0.5, 0.35, 0.2)))

    # Player
    player_go = fid(); player_tr = fid(); player_mf = fid(); player_mr = fid()
    player_cc = fid(); player_ctrl = fid(); player_raycaster = fid(); player_input = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{player_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {player_tr}}}
          - component: {{fileID: {player_mf}}}
          - component: {{fileID: {player_mr}}}
          - component: {{fileID: {player_cc}}}
          - component: {{fileID: {player_ctrl}}}
          - component: {{fileID: {player_raycaster}}}
          - component: {{fileID: {player_input}}}
          m_Layer: 0
          m_Name: Player
          m_TagString: Player
          m_IsActive: 1
        --- !u!4 &{player_tr}
        Transform:
          m_GameObject: {{fileID: {player_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 1.1, z: -10}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!33 &{player_mf}
        MeshFilter:
          m_GameObject: {{fileID: {player_go}}}
          m_Mesh: {{fileID: 10208, guid: 0000000000000000e000000000000000, type: 0}}
        --- !u!23 &{player_mr}
        MeshRenderer:
          m_GameObject: {{fileID: {player_go}}}
          m_Enabled: 1
          m_Materials:
          - {{fileID: 10303, guid: 0000000000000000f000000000000000, type: 0}}
        --- !u!143 &{player_cc}
        CharacterController:
          m_GameObject: {{fileID: {player_go}}}
          m_Enabled: 1
          m_Height: 2
          m_Radius: 0.5
          m_SlopeLimit: 45
          m_StepOffset: 0.3
          m_SkinWidth: 0.08
          m_MinMoveDistance: 0
          m_Center: {{x: 0, y: 0, z: 0}}
        --- !u!114 &{player_ctrl}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {player_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['PlayerController3D']}, type: 3}}
          m_Name:
        --- !u!114 &{player_raycaster}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {player_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['InteractionRaycaster']}, type: 3}}
          m_Name:
        --- !u!114 &{player_input}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {player_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: b7c0e7c8f7c2a4b2a9d6f1e3c4b5a6d7, type: 3}}
          m_Name:
        """))

    # Camera Rig
    cam_root_go = fid(); cam_root_tr = fid(); cam_root_script = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{cam_root_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {cam_root_tr}}}
          - component: {{fileID: {cam_root_script}}}
          m_Layer: 0
          m_Name: CameraRig
          m_IsActive: 1
        --- !u!4 &{cam_root_tr}
        Transform:
          m_GameObject: {{fileID: {cam_root_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 0, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!114 &{cam_root_script}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {cam_root_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['FollowCameraRig']}, type: 3}}
          m_Name:
        """))
    # MainCam
    mc_go = fid(); mc_tr = fid(); mc_cam = fid(); mc_al = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{mc_go}
        GameObject:
          m_ObjectHideFlags: 0
          serializedVersion: 6
          m_Component:
          - component: {{fileID: {mc_tr}}}
          - component: {{fileID: {mc_cam}}}
          - component: {{fileID: {mc_al}}}
          m_Layer: 0
          m_Name: Main Camera
          m_TagString: MainCamera
          m_IsActive: 1
        --- !u!4 &{mc_tr}
        Transform:
          m_GameObject: {{fileID: {mc_go}}}
          m_LocalRotation: {{x: 0.15, y: 0, z: 0, w: 0.98}}
          m_LocalPosition: {{x: 0, y: 4, z: -8}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!20 &{mc_cam}
        Camera:
          m_GameObject: {{fileID: {mc_go}}}
          m_Enabled: 1
          m_ClearFlags: 1
          m_BackGroundColor: {{r: 0.5, g: 0.65, b: 0.85, a: 0}}
          m_FieldOfView: 55
          m_NearClipPlane: 0.3
          m_FarClipPlane: 500
        --- !u!81 &{mc_al}
        AudioListener:
          m_GameObject: {{fileID: {mc_go}}}
          m_Enabled: 1
        """))

    # Enemy-Group: Kelpholm-Captain patrouilliert
    eg_go = fid(); eg_tr = fid()
    wp_a_go = fid(); wp_a_tr = fid()
    wp_b_go = fid(); wp_b_tr = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{eg_go}
        GameObject:
          m_ObjectHideFlags: 0
          m_Component:
          - component: {{fileID: {eg_tr}}}
          m_Layer: 0
          m_Name: EnemyGroup
          m_IsActive: 1
        --- !u!4 &{eg_tr}
        Transform:
          m_GameObject: {{fileID: {eg_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 0, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!1 &{wp_a_go}
        GameObject:
          m_ObjectHideFlags: 0
          m_Component:
          - component: {{fileID: {wp_a_tr}}}
          m_Layer: 0
          m_Name: WP_A
          m_IsActive: 1
        --- !u!4 &{wp_a_tr}
        Transform:
          m_GameObject: {{fileID: {wp_a_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: -3, y: 1, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!1 &{wp_b_go}
        GameObject:
          m_ObjectHideFlags: 0
          m_Component:
          - component: {{fileID: {wp_b_tr}}}
          m_Layer: 0
          m_Name: WP_B
          m_IsActive: 1
        --- !u!4 &{wp_b_tr}
        Transform:
          m_GameObject: {{fileID: {wp_b_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 3, y: 1, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        """))
    cap_go = fid(); cap_tr = fid(); cap_mf = fid(); cap_mr = fid()
    cap_col = fid(); cap_script = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{cap_go}
        GameObject:
          m_ObjectHideFlags: 0
          m_Component:
          - component: {{fileID: {cap_tr}}}
          - component: {{fileID: {cap_mf}}}
          - component: {{fileID: {cap_mr}}}
          - component: {{fileID: {cap_col}}}
          - component: {{fileID: {cap_script}}}
          m_Layer: 0
          m_Name: KelpholmCaptain
          m_IsActive: 1
        --- !u!4 &{cap_tr}
        Transform:
          m_GameObject: {{fileID: {cap_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 1, z: 0}}
          m_LocalScale: {{x: 1.15, y: 1.15, z: 1.15}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!33 &{cap_mf}
        MeshFilter:
          m_GameObject: {{fileID: {cap_go}}}
          m_Mesh: {{fileID: 10208, guid: 0000000000000000e000000000000000, type: 0}}
        --- !u!23 &{cap_mr}
        MeshRenderer:
          m_GameObject: {{fileID: {cap_go}}}
          m_Enabled: 1
          m_Materials:
          - {{fileID: 10303, guid: 0000000000000000f000000000000000, type: 0}}
        --- !u!136 &{cap_col}
        CapsuleCollider:
          m_GameObject: {{fileID: {cap_go}}}
          m_IsTrigger: 1
          m_Enabled: 1
          m_Radius: 0.7
          m_Height: 2
          m_Direction: 1
          m_Center: {{x: 0, y: 0, z: 0}}
        --- !u!114 &{cap_script}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {cap_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['EnemyPatrol']}, type: 3}}
          m_Name:
          enemyData: {{fileID: 11400000, guid: {A['KelpholmCaptain']}, type: 2}}
          waypointA: {{fileID: {wp_a_tr}}}
          waypointB: {{fileID: {wp_b_tr}}}
          moveSpeed: 1.4
          pauseAtWaypoint: 1.5
          capsuleRenderer: {{fileID: {cap_mr}}}
        """))

    # Tunnel zurueck zur Testinsel
    tt_go = fid(); tt_tr = fid(); tt_col = fid(); tt_script = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{tt_go}
        GameObject:
          m_ObjectHideFlags: 0
          m_Component:
          - component: {{fileID: {tt_tr}}}
          - component: {{fileID: {tt_col}}}
          - component: {{fileID: {tt_script}}}
          m_Layer: 0
          m_Name: TunnelBack
          m_IsActive: 1
        --- !u!4 &{tt_tr}
        Transform:
          m_GameObject: {{fileID: {tt_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 1, z: -15}}
          m_LocalScale: {{x: 8, y: 3, z: 2}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!65 &{tt_col}
        BoxCollider:
          m_GameObject: {{fileID: {tt_go}}}
          m_IsTrigger: 1
          m_Enabled: 1
          m_Size: {{x: 1, y: 1, z: 1}}
          m_Center: {{x: 0, y: 0, z: 0}}
        --- !u!114 &{tt_script}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {tt_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['SceneTunnel']}, type: 3}}
          m_Name:
          target: 0
        """))

    # VillageController-Root
    vc_go = fid(); vc_tr = fid(); vc_script = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{vc_go}
        GameObject:
          m_ObjectHideFlags: 0
          m_Component:
          - component: {{fileID: {vc_tr}}}
          - component: {{fileID: {vc_script}}}
          m_Layer: 0
          m_Name: VillageRoot
          m_IsActive: 1
        --- !u!4 &{vc_tr}
        Transform:
          m_GameObject: {{fileID: {vc_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 0, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!114 &{vc_script}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {vc_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['VillageController']}, type: 3}}
          m_Name:
          villageId: kelpholm
          enemyGroup: {{fileID: {eg_go}}}
          safeGroup: {{fileID: 0}}
        """))

    return "\n".join(parts)


# --------------------------------------------------------------------------
# BattleArena: Arena + BattleManager + Spawn-Punkte + Kamera-Placeholder
# --------------------------------------------------------------------------
def gen_battle_arena() -> str:
    global _fid_counter
    _fid_counter = 100
    parts = [scene_settings()]
    parts.append(light_yaml(fid(), fid(), fid()))
    parts.append(cube_yaml(fid(), fid(), fid(), fid(), fid(),
                           "ArenaFloor", (0, -0.5, 0), (25, 1, 20), (0.35, 0.45, 0.5)))

    # Spawn-Punkte
    ps_go = fid(); ps_tr = fid()
    es_go = fid(); es_tr = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{ps_go}
        GameObject:
          m_ObjectHideFlags: 0
          m_Component:
          - component: {{fileID: {ps_tr}}}
          m_Layer: 0
          m_Name: PlayerSpawn
          m_IsActive: 1
        --- !u!4 &{ps_tr}
        Transform:
          m_GameObject: {{fileID: {ps_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: -3, y: 1, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!1 &{es_go}
        GameObject:
          m_ObjectHideFlags: 0
          m_Component:
          - component: {{fileID: {es_tr}}}
          m_Layer: 0
          m_Name: EnemySpawn
          m_IsActive: 1
        --- !u!4 &{es_tr}
        Transform:
          m_GameObject: {{fileID: {es_go}}}
          m_LocalRotation: {{x: 0, y: 180, z: 0, w: 0}}
          m_LocalPosition: {{x: 3, y: 1, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        """))

    # MainCam
    mc_go = fid(); mc_tr = fid(); mc_cam = fid(); mc_al = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{mc_go}
        GameObject:
          m_ObjectHideFlags: 0
          m_Component:
          - component: {{fileID: {mc_tr}}}
          - component: {{fileID: {mc_cam}}}
          - component: {{fileID: {mc_al}}}
          m_Layer: 0
          m_Name: Main Camera
          m_TagString: MainCamera
          m_IsActive: 1
        --- !u!4 &{mc_tr}
        Transform:
          m_GameObject: {{fileID: {mc_go}}}
          m_LocalRotation: {{x: 0.2, y: 0, z: 0, w: 0.98}}
          m_LocalPosition: {{x: 0, y: 4, z: -7}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!20 &{mc_cam}
        Camera:
          m_GameObject: {{fileID: {mc_go}}}
          m_Enabled: 1
          m_ClearFlags: 1
          m_BackGroundColor: {{r: 0.15, g: 0.2, b: 0.3, a: 0}}
          m_FieldOfView: 55
          m_NearClipPlane: 0.3
          m_FarClipPlane: 500
        --- !u!81 &{mc_al}
        AudioListener:
          m_GameObject: {{fileID: {mc_go}}}
          m_Enabled: 1
        """))

    # BattleManager-Root (Kameras + HUD-Refs bleiben null; wird zur Laufzeit gehandelt oder im Editor gesetzt)
    bm_go = fid(); bm_tr = fid(); bm_script = fid()
    parts.append(dedent(f"""\
        --- !u!1 &{bm_go}
        GameObject:
          m_ObjectHideFlags: 0
          m_Component:
          - component: {{fileID: {bm_tr}}}
          - component: {{fileID: {bm_script}}}
          m_Layer: 0
          m_Name: BattleManager
          m_IsActive: 1
        --- !u!4 &{bm_tr}
        Transform:
          m_GameObject: {{fileID: {bm_go}}}
          m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
          m_LocalPosition: {{x: 0, y: 0, z: 0}}
          m_LocalScale: {{x: 1, y: 1, z: 1}}
          m_Children: []
          m_Father: {{fileID: 0}}
        --- !u!114 &{bm_script}
        MonoBehaviour:
          m_ObjectHideFlags: 0
          m_GameObject: {{fileID: {bm_go}}}
          m_Enabled: 1
          m_Script: {{fileID: 11500000, guid: {G['BattleManager']}, type: 3}}
          m_Name:
          fallbackParty:
          - {{fileID: 11400000, guid: {A['Bran']}, type: 2}}
          fallbackLevel: 3
          playerSpawn: {{fileID: {ps_tr}}}
          enemySpawn: {{fileID: {es_tr}}}
        """))

    return "\n".join(parts)


def main() -> None:
    SCENES.mkdir(parents=True, exist_ok=True)
    (SCENES / "Boot.unity").write_text(gen_boot(), encoding="utf-8")
    (SCENES / "TestIsland.unity").write_text(gen_test_island(), encoding="utf-8")
    (SCENES / "VillageKelpholm.unity").write_text(gen_village(), encoding="utf-8")
    (SCENES / "BattleArena.unity").write_text(gen_battle_arena(), encoding="utf-8")
    print("4 Scenes geschrieben.")


if __name__ == "__main__":
    main()
