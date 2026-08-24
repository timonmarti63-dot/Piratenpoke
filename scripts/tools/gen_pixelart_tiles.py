"""Erzeugt Pixel-Art-Kacheln + Player-Sprite im Pokemon-Piraten-Stil.

- 64x64 pro Kachel, aber intern als 16x16-Grid gezeichnet und 4x hochskaliert
  (klassischer GBA/DS-Look, klare Pixel-Cluster).
- Warme Piraten-Farbpalette: verwittertes Holz, sattes Gras, tiefblaues Meer,
  Sand mit Kies-Textur, moosbedeckte Felsen, dunkle Zieldaecher.

Kachel-Indizes (Atlas-Spalten 0..9):
  0 grass   1 sand    2 path   3 water   4 tree
  5 rock    6 plank   7 wall   8 door    9 roof

Ausgabe:
  assets/tiles/*.png   (grass/sand/path/water/tree/rock/plank/wall/door/roof)
  assets/tiles/atlas.png  (10x1 Atlas, 640x64)
  assets/sprites/captain.png  (64x64 Piraten-Kapitaen)
"""
from __future__ import annotations

import os
from pathlib import Path
from PIL import Image

# --------------------------------------------------------------------------
# Palette (Pokemon-Gen4 Warmth + Pirate)
# --------------------------------------------------------------------------
GRASS_DARK   = (60, 130, 55)
GRASS_MID    = (95, 165, 75)
GRASS_LIGHT  = (140, 200, 100)
GRASS_HL     = (180, 225, 130)

SAND_DARK    = (170, 140, 90)
SAND_MID     = (215, 190, 130)
SAND_LIGHT   = (240, 220, 165)
SAND_HL      = (255, 240, 190)

PATH_DARK    = (110, 85, 55)
PATH_MID     = (155, 120, 80)
PATH_LIGHT   = (185, 150, 105)

WATER_DEEP   = (25, 65, 115)
WATER_MID    = (45, 105, 165)
WATER_LIGHT  = (85, 145, 200)
WATER_FOAM   = (200, 230, 245)

TREE_TRUNK   = (75, 45, 20)
TREE_DARK    = (35, 85, 40)
TREE_MID     = (55, 120, 55)
TREE_LIGHT   = (90, 160, 75)
TREE_HL      = (150, 210, 110)

ROCK_DARK    = (75, 75, 85)
ROCK_MID     = (120, 120, 130)
ROCK_LIGHT   = (170, 170, 180)
ROCK_MOSS    = (95, 140, 70)

PLANK_DARK   = (85, 55, 30)
PLANK_MID    = (140, 90, 50)
PLANK_LIGHT  = (185, 135, 80)
PLANK_LINE   = (60, 35, 15)

WALL_DARK    = (100, 70, 45)
WALL_MID     = (155, 115, 75)
WALL_LIGHT   = (200, 160, 110)
WALL_STONE   = (170, 155, 130)

DOOR_DARK    = (55, 30, 15)
DOOR_MID     = (110, 65, 30)
DOOR_LIGHT   = (155, 105, 55)
DOOR_METAL   = (215, 190, 120)  # Beschlaege
DOOR_FRAME   = (75, 45, 20)

ROOF_DARK    = (55, 40, 55)
ROOF_MID     = (95, 75, 90)
ROOF_LIGHT   = (140, 115, 130)
ROOF_HL      = (185, 165, 175)

BLACK        = (25, 20, 20)
BROWN_DK     = (50, 30, 15)

# Piraten-Kapitaen
SKIN         = (245, 205, 165)
SKIN_SHADOW  = (200, 155, 115)
COAT_DARK    = (100, 25, 30)
COAT_MID     = (155, 45, 55)
COAT_LIGHT   = (200, 75, 85)
BELT         = (55, 30, 15)
BUCKLE       = (230, 200, 100)
HAT_DARK     = (30, 25, 25)
HAT_MID      = (55, 45, 45)
HAT_TRIM     = (215, 190, 120)
BEARD        = (185, 165, 130)
BEARD_DARK   = (135, 115, 85)
BOOT         = (60, 40, 25)
BOOT_HL      = (100, 70, 45)

# --------------------------------------------------------------------------
# Hilfsfunktionen: 16x16 Grid, 4x hochskalieren
# --------------------------------------------------------------------------
GRID = 16
SCALE = 4  # -> 64x64


def new_grid() -> list[list[tuple[int, int, int, int]]]:
    return [[(0, 0, 0, 0) for _ in range(GRID)] for _ in range(GRID)]


def px(g, x: int, y: int, color: tuple[int, int, int], alpha: int = 255) -> None:
    if 0 <= x < GRID and 0 <= y < GRID:
        g[y][x] = (color[0], color[1], color[2], alpha)


def fill(g, color: tuple[int, int, int]) -> None:
    for y in range(GRID):
        for x in range(GRID):
            g[y][x] = (color[0], color[1], color[2], 255)


def rect(g, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            px(g, xx, yy, color)


def to_image(g) -> Image.Image:
    img = Image.new("RGBA", (GRID, GRID))
    for y in range(GRID):
        for x in range(GRID):
            img.putpixel((x, y), g[y][x])
    return img.resize((GRID * SCALE, GRID * SCALE), Image.NEAREST)


# --------------------------------------------------------------------------
# Tiles
# --------------------------------------------------------------------------
def tile_grass() -> Image.Image:
    g = new_grid()
    fill(g, GRASS_MID)
    # Zufaellig wirkendes Muster, aber deterministisch:
    darks = [(1, 1), (5, 2), (11, 1), (14, 3), (2, 7), (7, 8), (13, 9),
             (4, 12), (10, 13), (0, 5), (15, 6)]
    lights = [(3, 3), (8, 2), (12, 4), (6, 6), (9, 10), (2, 11),
              (14, 11), (5, 14), (11, 14)]
    hls = [(4, 4), (13, 5), (7, 12), (10, 7)]
    for x, y in darks:
        px(g, x, y, GRASS_DARK)
    for x, y in lights:
        px(g, x, y, GRASS_LIGHT)
    for x, y in hls:
        px(g, x, y, GRASS_HL)
    # Graeser (kleine vertikale Stiele)
    for cx, cy in [(3, 8), (11, 6), (8, 14)]:
        px(g, cx, cy, GRASS_DARK)
        px(g, cx, cy - 1, GRASS_LIGHT)
    return to_image(g)


def tile_sand() -> Image.Image:
    g = new_grid()
    fill(g, SAND_MID)
    darks = [(2, 2), (7, 4), (12, 3), (4, 8), (10, 9), (1, 12),
             (14, 12), (6, 13), (11, 14), (15, 6)]
    lights = [(3, 1), (9, 2), (13, 5), (5, 6), (7, 10), (2, 10),
              (11, 11), (14, 8), (0, 7), (8, 7)]
    hls = [(4, 3), (10, 5), (6, 11), (12, 9)]
    for x, y in darks:
        px(g, x, y, SAND_DARK)
    for x, y in lights:
        px(g, x, y, SAND_LIGHT)
    for x, y in hls:
        px(g, x, y, SAND_HL)
    return to_image(g)


def tile_path() -> Image.Image:
    g = new_grid()
    fill(g, PATH_MID)
    # Trampelpfad mit Steinen
    darks = [(1, 3), (5, 2), (10, 4), (13, 1), (2, 8), (7, 7), (11, 9),
             (14, 12), (4, 13), (0, 11)]
    lights = [(3, 1), (8, 3), (12, 5), (6, 5), (9, 8), (14, 8),
              (3, 10), (11, 12), (5, 14)]
    for x, y in darks:
        px(g, x, y, PATH_DARK)
    for x, y in lights:
        px(g, x, y, PATH_LIGHT)
    # 2-3 kleine Steine
    for cx, cy in [(4, 5), (11, 7), (6, 12)]:
        px(g, cx, cy, ROCK_MID)
        px(g, cx + 1, cy, ROCK_LIGHT)
        px(g, cx, cy + 1, ROCK_DARK)
    return to_image(g)


def tile_water() -> Image.Image:
    g = new_grid()
    fill(g, WATER_MID)
    # Wellenmuster wie Pokemon-Ozean: horizontale Sinus-ish Linien
    for y, phase in [(2, 0), (6, 3), (10, 1), (14, 5)]:
        for x in range(GRID):
            if ((x + phase) // 2) % 3 == 0:
                px(g, x, y, WATER_LIGHT)
            elif ((x + phase) // 2) % 3 == 1:
                px(g, x, y, WATER_DEEP)
    # Schaumkroenchen: ~3 Stueck
    for cx, cy in [(4, 3), (11, 7), (7, 11)]:
        px(g, cx, cy, WATER_FOAM)
        px(g, cx + 1, cy, WATER_FOAM)
        px(g, cx, cy + 1, WATER_LIGHT)
    return to_image(g)


def tile_tree() -> Image.Image:
    g = new_grid()
    # Gras darunter
    fill(g, GRASS_MID)
    for x, y in [(1, 14), (5, 15), (10, 14), (14, 15), (7, 13)]:
        px(g, x, y, GRASS_LIGHT)
    for x, y in [(2, 13), (12, 13), (0, 15), (15, 14)]:
        px(g, x, y, GRASS_DARK)
    # Baumkrone: rund, 12x10
    crown = [
        (5, 1), (6, 1), (7, 1), (8, 1), (9, 1),  (10, 1),
        (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2), (12, 2),
        (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 3), (12, 3), (13, 3),
        (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (11, 4), (12, 4), (13, 4),
        (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5), (13, 5),
        (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6), (12, 6), (13, 6),
        (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7), (12, 7),
        (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (11, 8),
        (5, 9), (6, 9), (9, 9), (10, 9),
    ]
    for x, y in crown:
        px(g, x, y, TREE_MID)
    # Schatten am Unterrand + linke Seite
    shade = [(2, 6), (2, 5), (3, 7), (4, 8), (5, 9), (6, 9),
             (7, 8), (8, 8), (9, 9), (10, 9), (11, 8), (12, 7), (13, 6), (13, 5)]
    for x, y in shade:
        px(g, x, y, TREE_DARK)
    # Kontur
    outline = [
        (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0),
        (4, 1), (11, 1),
        (2, 2), (13, 2),
        (1, 3), (14, 3),
        (1, 4), (14, 4),
        (1, 5), (14, 5),
        (1, 6), (14, 6),
        (2, 7), (13, 7),
        (3, 8), (12, 8),
        (4, 9), (7, 9), (8, 9), (11, 9),
    ]
    for x, y in outline:
        px(g, x, y, TREE_TRUNK)
    # Highlights (Sonne rechts oben)
    for x, y in [(6, 2), (7, 2), (8, 2), (5, 3), (6, 3), (7, 3),
                 (4, 4), (5, 4), (8, 5)]:
        px(g, x, y, TREE_LIGHT)
    for x, y in [(6, 2), (7, 3)]:
        px(g, x, y, TREE_HL)
    # Stamm
    for x in [7, 8]:
        for y in [9, 10, 11, 12]:
            px(g, x, y, TREE_TRUNK)
    px(g, 7, 10, BROWN_DK)
    px(g, 8, 11, BROWN_DK)
    return to_image(g)


def tile_rock() -> Image.Image:
    g = new_grid()
    fill(g, GRASS_MID)
    for x, y in [(1, 14), (13, 15), (7, 15), (14, 12)]:
        px(g, x, y, GRASS_LIGHT)
    # Grosser Fels 12x10, unregelmaessig
    body = [
        (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2),
        (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 3), (12, 3),
        (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (11, 4), (12, 4), (13, 4),
        (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5), (13, 5),
        (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6), (12, 6), (13, 6),
        (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7), (12, 7), (13, 7),
        (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (11, 8), (12, 8), (13, 8),
        (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (11, 9), (12, 9),
        (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10),
        (5, 11), (6, 11), (7, 11), (8, 11), (9, 11), (10, 11),
    ]
    for x, y in body:
        px(g, x, y, ROCK_MID)
    # Kontur
    outline = [
        (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1),
        (4, 2), (11, 2),
        (3, 2), (12, 2),
        (2, 3), (13, 3),
        (1, 4), (14, 4),
        (1, 5), (14, 5),
        (1, 6), (14, 6),
        (1, 7), (14, 7),
        (1, 8), (14, 8),
        (2, 9), (13, 9),
        (3, 10), (12, 10),
        (4, 11), (11, 11),
        (5, 12), (6, 12), (7, 12), (8, 12), (9, 12), (10, 12),
    ]
    for x, y in outline:
        px(g, x, y, ROCK_DARK)
    # Highlight-Seite oben links (Sonne)
    hls = [(4, 3), (5, 3), (6, 3), (3, 4), (4, 4), (5, 4), (6, 4),
           (3, 5), (4, 5), (5, 5), (3, 6), (4, 6)]
    for x, y in hls:
        px(g, x, y, ROCK_LIGHT)
    # Schatten unten rechts
    darks = [(10, 8), (11, 8), (12, 8), (10, 9), (11, 9), (12, 9),
             (11, 10), (10, 10), (9, 11), (10, 11)]
    for x, y in darks:
        px(g, x, y, ROCK_DARK)
    # Moos-Flecken
    moss = [(6, 2), (9, 2), (13, 6), (7, 4)]
    for x, y in moss:
        px(g, x, y, ROCK_MOSS)
    return to_image(g)


def tile_plank() -> Image.Image:
    """Holzboden (fuer Hausinnere / Pier)."""
    g = new_grid()
    fill(g, PLANK_MID)
    # 4 horizontale Planken je 4px hoch
    for y_line in [3, 7, 11, 15]:
        for x in range(GRID):
            px(g, x, y_line, PLANK_LINE)
    # Maserung: dunkle + helle Strichel
    darks = [(2, 1), (8, 1), (13, 2),
             (4, 5), (11, 5), (1, 6),
             (6, 9), (14, 9), (3, 10),
             (9, 13), (12, 14), (1, 13)]
    lights = [(5, 1), (11, 2), (7, 4),
              (2, 5), (9, 6), (14, 4),
              (4, 9), (10, 10), (1, 8),
              (7, 12), (13, 13), (11, 14)]
    # Nur zeichnen wenn nicht auf Planken-Linie
    def safe(x, y, c):
        if y not in (3, 7, 11, 15):
            px(g, x, y, c)
    for x, y in darks:
        safe(x, y, PLANK_DARK)
    for x, y in lights:
        safe(x, y, PLANK_LIGHT)
    # Naegel
    for cx, cy in [(1, 1), (14, 1), (1, 5), (14, 5), (1, 9),
                   (14, 9), (1, 13), (14, 13)]:
        px(g, cx, cy, PLANK_DARK)
    return to_image(g)


def tile_wall() -> Image.Image:
    """Hauswand: verwittertes Holz vertikal (kachelbar in alle Richtungen)."""
    g = new_grid()
    fill(g, WALL_MID)
    # Vier vertikale Planken durch dunkle Fugen getrennt
    for x in [3, 7, 11, 15]:
        for y in range(GRID):
            px(g, x, y, WALL_DARK)
    # Highlight-Kante links jeder Planke (Sonne von rechts)
    for x in [4, 8, 12]:
        for y in range(GRID):
            px(g, x, y, WALL_LIGHT)
    # Verwitterungs-Details (Maserung)
    knots = [(1, 3), (5, 8), (9, 2), (13, 11),
             (2, 12), (6, 5), (10, 14), (14, 6)]
    for x, y in knots:
        px(g, x, y, WALL_DARK)
    # Kleine Aufhellungen
    for x, y in [(1, 10), (5, 2), (9, 9), (13, 4), (2, 6), (14, 12)]:
        px(g, x, y, WALL_STONE)
    # Naegel oben und unten (Piraten-Optik)
    for x in [2, 6, 10, 14]:
        px(g, x, 0, PLANK_LINE)
        px(g, x, 15, PLANK_LINE)
    return to_image(g)


def tile_door() -> Image.Image:
    """Tuer mit Beschlaegen und Piraten-Muenzen-Klopfer."""
    g = new_grid()
    fill(g, WALL_MID)
    # Wand-Kontur wie tile_wall
    for x in [2, 5, 9, 13]:
        for y in range(0, 3):
            px(g, x, y, WALL_DARK)
    # Tuer-Rahmen
    for x in range(3, 13):
        px(g, x, 1, DOOR_FRAME)
    for y in range(1, 15):
        px(g, 3, y, DOOR_FRAME)
        px(g, 12, y, DOOR_FRAME)
    for x in range(3, 13):
        px(g, x, 15, DOOR_FRAME)
    # Tuerblatt
    for y in range(2, 15):
        for x in range(4, 12):
            px(g, x, y, DOOR_MID)
    # Holzmaserung vertikal
    for y in range(2, 15):
        px(g, 5, y, DOOR_DARK)
        px(g, 8, y, DOOR_DARK)
        px(g, 11, y, DOOR_DARK)
    # Highlights
    for y in [3, 6, 9, 12]:
        px(g, 6, y, DOOR_LIGHT)
        px(g, 9, y, DOOR_LIGHT)
    # Quer-Balken oben und unten
    for x in range(4, 12):
        px(g, x, 4, DOOR_DARK)
        px(g, x, 12, DOOR_DARK)
    # Muenz-Klopfer in der Mitte (Piraten-Detail!)
    px(g, 7, 7, DOOR_METAL)
    px(g, 8, 7, DOOR_METAL)
    px(g, 7, 8, DOOR_METAL)
    px(g, 8, 8, DOOR_METAL)
    px(g, 7, 6, DOOR_DARK)
    px(g, 8, 6, DOOR_DARK)
    # Beschlag-Klinke
    px(g, 10, 8, DOOR_METAL)
    px(g, 10, 9, DOOR_METAL)
    return to_image(g)


def tile_roof() -> Image.Image:
    """Schindeldach in warmem Grau (Basis fuer Farb-Marker im Shop)."""
    g = new_grid()
    fill(g, ROOF_MID)
    # 4 versetzte Schindelreihen
    for y in range(GRID):
        row_off = (y // 4) * 2  # Versatz alle 4 Zeilen
        for x in range(GRID):
            xi = (x + row_off) % 4
            if xi == 0:
                px(g, x, y, ROOF_DARK)   # Fugen zwischen Schindeln
    # Highlight-Oberkante jeder Schindelreihe
    for y in [0, 4, 8, 12]:
        for x in range(GRID):
            row_off = (y // 4) * 2
            xi = (x + row_off) % 4
            if xi in (1, 2):
                px(g, x, y, ROOF_HL)
            elif xi == 3:
                px(g, x, y, ROOF_LIGHT)
    # Firstlinie oben (dunkler Rand)
    for x in range(GRID):
        px(g, x, 0, ROOF_DARK)
    return to_image(g)


# --------------------------------------------------------------------------
# Player: Piraten-Kapitaen von oben (Top-Down, Dreispitz + roter Mantel)
# --------------------------------------------------------------------------
def sprite_captain() -> Image.Image:
    g = new_grid()
    # Kompletter transparenter Hintergrund
    # Silhouette (grob 10x14, zentriert)
    #
    # Dreispitzhut (breit, mit goldenem Rand)
    hat = [
        (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1),
        (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2),
        (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 3), (12, 3),
    ]
    for x, y in hat:
        px(g, x, y, HAT_MID)
    # Hutkrone dunkler
    for x in [6, 7, 8, 9]:
        px(g, x, 1, HAT_DARK)
    # Rand (Trikorn-Spitzen dunkler)
    for x, y in [(3, 3), (4, 3), (11, 3), (12, 3), (5, 2), (10, 2), (4, 2), (11, 2)]:
        px(g, x, y, HAT_DARK)
    # Goldener Rand
    for x, y in [(6, 3), (7, 3), (8, 3), (9, 3)]:
        px(g, x, y, HAT_TRIM)
    # Kopf (Haut)
    for y in range(4, 7):
        for x in range(5, 11):
            px(g, x, y, SKIN)
    # Ohren / Wangen Schatten
    for x, y in [(5, 5), (10, 5), (5, 6), (10, 6)]:
        px(g, x, y, SKIN_SHADOW)
    # Augen
    px(g, 6, 5, BLACK)
    px(g, 9, 5, BLACK)
    # Bart
    for x, y in [(6, 7), (7, 7), (8, 7), (9, 7),
                 (5, 7), (10, 7),
                 (6, 8), (7, 8), (8, 8), (9, 8)]:
        px(g, x, y, BEARD)
    for x, y in [(5, 8), (10, 8), (7, 8), (8, 8)]:
        px(g, x, y, BEARD_DARK)
    # Mantel-Schultern (breit)
    for y in range(8, 12):
        for x in range(4, 12):
            px(g, x, y, COAT_MID)
    # Mantel-Kanten dunkler
    for y in range(8, 12):
        px(g, 4, y, COAT_DARK)
        px(g, 11, y, COAT_DARK)
    # Highlight-Streifen
    for y in [9, 10]:
        px(g, 5, y, COAT_LIGHT)
        px(g, 10, y, COAT_LIGHT)
    # Goldknopf-Reihe (Piraten-Mantel)
    for y in [9, 10, 11]:
        px(g, 7, y, BUCKLE)
        px(g, 8, y, BUCKLE)
    # Guertel
    for x in range(4, 12):
        px(g, x, 12, BELT)
    px(g, 7, 12, BUCKLE)  # Guertelschnalle
    px(g, 8, 12, BUCKLE)
    # Beine / Stiefel (aus Vogelperspektive: nur Ansatz sichtbar)
    for y in range(13, 15):
        for x in [5, 6, 7]:
            px(g, x, y, BOOT)
        for x in [8, 9, 10]:
            px(g, x, y, BOOT)
    px(g, 7, 13, COAT_DARK)  # Mantelschlitz
    px(g, 8, 13, COAT_DARK)
    # Stiefel-Highlights
    px(g, 5, 13, BOOT_HL)
    px(g, 10, 13, BOOT_HL)
    # Boden-Schatten (dezent)
    for x in [6, 7, 8, 9]:
        px(g, x, 15, (0, 0, 0, 80))
    return to_image(g)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main() -> None:
    root = Path(__file__).resolve().parents[2]
    tiles_dir = root / "assets" / "tiles"
    sprites_dir = root / "assets" / "sprites"
    tiles_dir.mkdir(parents=True, exist_ok=True)
    sprites_dir.mkdir(parents=True, exist_ok=True)

    tiles = [
        ("grass", tile_grass()),
        ("sand",  tile_sand()),
        ("path",  tile_path()),
        ("water", tile_water()),
        ("tree",  tile_tree()),
        ("rock",  tile_rock()),
        ("plank", tile_plank()),
        ("wall",  tile_wall()),
        ("door",  tile_door()),
        ("roof",  tile_roof()),
    ]

    # Einzel-PNGs
    for name, img in tiles:
        img.save(tiles_dir / f"{name}.png")
        print(f"  wrote {name}.png")

    # Atlas 10x1
    atlas = Image.new("RGBA", (10 * 64, 64), (0, 0, 0, 0))
    for i, (_, img) in enumerate(tiles):
        atlas.paste(img, (i * 64, 0))
    atlas.save(tiles_dir / "atlas.png")
    print(f"  wrote atlas.png ({atlas.size})")

    # Captain
    cap = sprite_captain()
    cap.save(sprites_dir / "captain.png")
    print(f"  wrote captain.png ({cap.size})")


if __name__ == "__main__":
    main()
