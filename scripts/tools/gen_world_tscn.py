"""Erzeugt scenes/world/world.tscn mit einer 16x9-Testkarte.

Kachel-Codes (Atlas-Spalte 0-5):
  0 grass, 1 sand, 2 path, 3 water, 4 tree, 5 rock

Layout (16 Spalten x 9 Zeilen):
  - Rand rundherum: tree
  - Boden: grass
  - Ein Pfad quer durch: path
  - Zwei Felsen als Hindernis
  - Kleiner Wasser-Teich unten rechts
"""
from __future__ import annotations
from pathlib import Path

W, H = 16, 9

# Kürzel für die Lesbarkeit
G, S, P, W_, T, R = 0, 1, 2, 3, 4, 5

# Basis: Gras + Rand aus Bäumen
grid = [[G for _ in range(W)] for _ in range(H)]
for x in range(W):
    grid[0][x] = T
    grid[H - 1][x] = T
for y in range(H):
    grid[y][0] = T
    grid[y][W - 1] = T

# Pfad in Zeile 4 (waagerecht)
for x in range(1, W - 1):
    grid[4][x] = P

# Zwei Felsen als Hindernis
grid[2][5] = R
grid[6][10] = R

# Sandstrand + Wasserteich unten rechts
for y in range(6, 8):
    for x in range(11, 14):
        grid[y][x] = S
grid[7][12] = W_
grid[7][13] = W_

# Godot TileMap-Format:
# tile_data ist ein PackedInt32Array mit 3 ints pro Kachel:
#   [encoded_pos, source_id, encoded_atlas_coords_with_alt]
# encoded_pos: (y & 0xFFFF) << 16 | (x & 0xFFFF)  — beide 16-bit signed
# encoded_atlas: (alt_tile << 16) | (atlas_y << 8) | atlas_x    für alt=0, atlas_y=0:
#                                                             = atlas_x
# Quelle: Godot 4 TileMap-Serialisierungsformat.
def encode_pos(x: int, y: int) -> int:
    ux = x & 0xFFFF
    uy = y & 0xFFFF
    v = (uy << 16) | ux
    # 32-bit signed
    if v >= (1 << 31):
        v -= 1 << 32
    return v


nums: list[int] = []
for y in range(H):
    for x in range(W):
        atlas_x = grid[y][x]
        nums.append(encode_pos(x, y))
        nums.append(0)                        # source_id = 0
        nums.append(atlas_x)                  # atlas coords (x=atlas_x, y=0, alt=0)

tile_data_str = ", ".join(str(n) for n in nums)

tscn = f"""[gd_scene load_steps=4 format=3]

[ext_resource type="TileSet" path="res://assets/tiles/world_tileset.tres" id="1"]
[ext_resource type="PackedScene" path="res://scenes/world/player.tscn" id="2"]

[node name="Root" type="Node2D"]

[node name="World" type="TileMap" parent="."]
tile_set = ExtResource("1")
format = 2
layer_0/name = "ground"
layer_0/tile_data = PackedInt32Array({tile_data_str})

[node name="Player" parent="." instance=ExtResource("2")]
"""

out = Path(__file__).resolve().parents[2] / "scenes" / "world" / "world.tscn"
out.write_text(tscn, encoding="utf-8")
print(f"world.tscn geschrieben: {out}  ({W}x{H} Kacheln, {len(nums) // 3} Zellen)")
