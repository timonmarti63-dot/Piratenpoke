"""Erzeugt scenes/world/village_kelpholm.tscn — Dorf Kelpholm.

Atlas-Codes (v0.4):
  0 grass, 1 sand, 2 path, 3 water, 4 tree, 5 rock,
  6 plank, 7 wall, 8 door, 9 roof

Layout 20x11:
  - Grasrand mit Baum-Grenze
  - Zentraler Sandplatz
  - Zwei Häuser (Apotheke links, Schmiede rechts) mit Dach/Wand/Tür
  - Ausgang zurück zum Testraum unten in der Mitte
"""
from __future__ import annotations
from pathlib import Path

W, H = 20, 11
G, S, P, W_, T, R, PL, WA, DR, RF = range(10)

grid = [[G for _ in range(W)] for _ in range(H)]

# Baumgrenze
for x in range(W):
    grid[0][x] = T
    grid[H - 1][x] = T
for y in range(H):
    grid[y][0] = T
    grid[y][W - 1] = T

# Zentraler Sandplatz (3 Zeilen breit)
for y in range(4, 7):
    for x in range(2, W - 2):
        grid[y][x] = S

# Pfad zur Ausgangs-Kachel unten Mitte + Öffnung durch Baumgrenze
for y in range(7, H):
    grid[y][W // 2] = P

# Haus links = Apotheke (bei x=3..6, y=2..4)
def build_house(x0: int, y0: int, w: int = 4, h: int = 3, door_x: int = 1) -> None:
    for yy in range(y0, y0 + h):
        for xx in range(x0, x0 + w):
            grid[yy][xx] = WA
    # Dach oberste Reihe
    for xx in range(x0, x0 + w):
        grid[y0][xx] = RF
    # Tür an der unteren Reihe
    grid[y0 + h - 1][x0 + door_x] = DR
    # Holzboden davor
    grid[y0 + h][x0 + door_x] = PL

build_house(3, 2, 4, 3, door_x=1)   # Apotheke, Tür bei (4,4)
build_house(13, 2, 4, 3, door_x=2)  # Schmiede, Tür bei (15,4)

# Ausgang: unten Mitte auf Path (grid ist schon Path an der Stelle)

# tile_data
def encode_pos(x: int, y: int) -> int:
    v = ((y & 0xFFFF) << 16) | (x & 0xFFFF)
    return v - (1 << 32) if v >= (1 << 31) else v

nums: list[int] = []
for y in range(H):
    for x in range(W):
        nums.append(encode_pos(x, y))
        nums.append(0)
        nums.append(grid[y][x])

tile_data_str = ", ".join(str(n) for n in nums)

tscn = f"""[gd_scene load_steps=13 format=3]

[ext_resource type="TileSet" path="res://assets/tiles/world_tileset.tres" id="1"]
[ext_resource type="PackedScene" path="res://scenes/world/player.tscn" id="2"]
[ext_resource type="Script" path="res://scripts/entities/village_controller.gd" id="3"]
[ext_resource type="Script" path="res://scripts/entities/enemy_encounter.gd" id="4"]
[ext_resource type="Script" path="res://scripts/entities/shop_portal.gd" id="5"]
[ext_resource type="Script" path="res://scripts/entities/scene_portal.gd" id="6"]
[ext_resource type="Resource" path="res://data/enemies/kelpholm_captain.tres" id="7"]
[ext_resource type="Resource" path="res://data/items/small_potion.tres" id="8"]
[ext_resource type="Resource" path="res://data/items/big_potion.tres" id="9"]
[ext_resource type="Resource" path="res://data/items/antidote.tres" id="10"]
[ext_resource type="Resource" path="res://data/items/rusty_saber.tres" id="11"]
[ext_resource type="Resource" path="res://data/items/leather_vest.tres" id="12"]
[ext_resource type="Resource" path="res://data/items/flame_cutlass.tres" id="13"]
[ext_resource type="Resource" path="res://data/items/atk_elixir.tres" id="14"]

[node name="Village" type="Node2D"]
script = ExtResource("3")
village_id = &"kelpholm"
player_path = NodePath("Player")
encounters_path = NodePath("Encounters")
safe_group_path = NodePath("SafeGroup")

[node name="World" type="TileMap" parent="."]
tile_set = ExtResource("1")
format = 2
layer_0/name = "ground"
layer_0/tile_data = PackedInt32Array({tile_data_str})

[node name="Player" parent="." instance=ExtResource("2")]
start_cell = Vector2i(10, 9)

[node name="Encounters" type="Node2D" parent="."]

[node name="TroopLeader" type="Node2D" parent="Encounters"]
script = ExtResource("4")
world_tilemap_path = NodePath("../../World")
player_path = NodePath("../../Player")
encounter_cell = Vector2i(10, 5)
enemy_data = ExtResource("7")
vanish_on_win = true
troop_leader_id = &"kelpholm_captain"

[node name="SafeGroup" type="Node2D" parent="."]

[node name="Apothecary" type="Node2D" parent="SafeGroup"]
script = ExtResource("5")
player_path = NodePath("../../Player")
portal_cell = Vector2i(4, 4)
shop_type = &"apothecary"
shop_title = "Apotheke"
color = Color(0.6, 0.9, 0.4, 1.0)
stock = [ExtResource("8"), ExtResource("9"), ExtResource("10"), ExtResource("14")]

[node name="Blacksmith" type="Node2D" parent="SafeGroup"]
script = ExtResource("5")
player_path = NodePath("../../Player")
portal_cell = Vector2i(15, 4)
shop_type = &"blacksmith"
shop_title = "Schmiede"
color = Color(1.0, 0.6, 0.2, 1.0)
stock = [ExtResource("11"), ExtResource("12"), ExtResource("13")]

[node name="ExitPortal" type="Node2D" parent="."]
script = ExtResource("6")
player_path = NodePath("../Player")
trigger_cell = Vector2i(10, 10)
target_scene = "res://scenes/world/world.tscn"
spawn_cell = Vector2i(8, 7)
"""

out = Path(__file__).resolve().parents[2] / "scenes" / "world" / "village_kelpholm.tscn"
out.write_text(tscn, encoding="utf-8")
print(f"village_kelpholm.tscn geschrieben ({W}x{H})")
