"""Erzeugt HD-Kacheln + Player-Sprite im modernen Pokemon-Switch-Stil.

Referenz: Pokemon Sword/Shield und Scarlet/Violet -- 64x64 nativ gerendert
mit weichen Farbverlaeufen, Cel-Shading mit 6-10 Farbstufen, weichen
Alpha-Schatten und cinematischer Farbgebung. Kein Pixel-Upscale-Look mehr.

Ausgabe:
  assets/tiles/{grass,sand,path,water,tree,rock,plank,wall,door,roof}.png
  assets/tiles/atlas.png    (640x64, 10 Kacheln)
  assets/sprites/captain.png (64x64)
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

# --------------------------------------------------------------------------
# Farbpalette Switch-Aera (warm, ges\u00e4ttigt, cinematisch)
# --------------------------------------------------------------------------
# Gras (frisch, saftig)
GRASS_SHADOW = (48, 110, 55)
GRASS_BASE   = (85, 165, 80)
GRASS_MID    = (115, 195, 95)
GRASS_LIGHT  = (155, 220, 115)
GRASS_HL     = (200, 245, 155)

# Sand (warm, strandartig)
SAND_SHADOW  = (180, 150, 100)
SAND_BASE    = (225, 200, 145)
SAND_MID     = (240, 220, 170)
SAND_LIGHT   = (250, 235, 195)

# Pfad (Erde/Kies gemischt)
PATH_SHADOW  = (95, 70, 45)
PATH_BASE    = (145, 110, 75)
PATH_MID     = (170, 135, 95)
PATH_LIGHT   = (195, 165, 125)

# Wasser (tiefer Karibik-Look)
WATER_DEEP   = (20, 65, 125)
WATER_BASE   = (45, 120, 175)
WATER_MID    = (75, 155, 205)
WATER_LIGHT  = (125, 195, 225)
WATER_FOAM   = (225, 245, 255)

# Baum
TRUNK_DARK   = (55, 30, 15)
TRUNK_BASE   = (95, 60, 30)
TRUNK_LIGHT  = (140, 95, 50)
LEAF_SHADOW  = (30, 80, 40)
LEAF_BASE    = (55, 130, 55)
LEAF_MID     = (85, 165, 65)
LEAF_LIGHT   = (135, 200, 85)
LEAF_HL      = (185, 230, 115)

# Fels
ROCK_SHADOW  = (55, 55, 65)
ROCK_BASE    = (105, 105, 115)
ROCK_MID     = (140, 140, 150)
ROCK_LIGHT   = (185, 185, 195)
ROCK_HL      = (220, 220, 225)
ROCK_MOSS    = (95, 145, 75)

# Holz (Planken/Wand)
WOOD_DARK    = (60, 35, 20)
WOOD_SHADOW  = (105, 70, 40)
WOOD_BASE    = (160, 115, 70)
WOOD_LIGHT   = (200, 155, 100)
WOOD_HL      = (225, 190, 135)
WOOD_LINE    = (40, 20, 10)

# T\u00fcr
DOOR_DARK    = (55, 30, 15)
DOOR_BASE    = (110, 65, 30)
DOOR_LIGHT   = (150, 100, 55)
METAL_DARK   = (135, 110, 55)
METAL_BASE   = (215, 190, 110)
METAL_HL     = (245, 225, 165)

# Dach (Schiefer/Ziegel)
ROOF_SHADOW  = (55, 40, 55)
ROOF_BASE    = (100, 80, 100)
ROOF_MID     = (135, 115, 130)
ROOF_LIGHT   = (170, 150, 165)
ROOF_HL      = (200, 185, 195)

# Piraten-Captain
SKIN_SHADOW  = (200, 155, 115)
SKIN_BASE    = (245, 205, 165)
SKIN_HL      = (255, 225, 190)
COAT_DARK    = (85, 20, 25)
COAT_BASE    = (155, 40, 50)
COAT_LIGHT   = (200, 75, 85)
COAT_HL      = (230, 115, 125)
BELT         = (55, 30, 15)
BUCKLE       = (230, 200, 100)
BUCKLE_HL    = (255, 235, 155)
HAT_DARK     = (25, 20, 20)
HAT_BASE     = (55, 45, 45)
HAT_HL       = (95, 85, 85)
HAT_TRIM     = (215, 185, 110)
HAT_TRIM_HL  = (245, 220, 155)
BEARD_DARK   = (155, 135, 110)
BEARD_BASE   = (200, 180, 155)
BEARD_HL     = (230, 215, 195)
BOOT_DARK    = (40, 25, 15)
BOOT_BASE    = (75, 50, 30)
BOOT_HL      = (115, 85, 55)
BLACK        = (20, 15, 15)
SHADOW_ALPHA = (0, 0, 0, 90)

SIZE = 64


# --------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------
def new_img(size: int = SIZE, bg: tuple = (0, 0, 0, 0)) -> Image.Image:
    return Image.new("RGBA", (size, size), bg)


def blend(base: Image.Image, overlay: Image.Image) -> Image.Image:
    """Alpha-Overlay auf Base."""
    out = base.copy()
    out.alpha_composite(overlay)
    return out


def vertical_gradient(w: int, h: int, top: tuple, bottom: tuple) -> Image.Image:
    """Erzeugt einen vertikalen Verlauf."""
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b, 255)
    return img


def radial_gradient(w: int, h: int, cx: float, cy: float, radius: float,
                    inner: tuple, outer: tuple) -> Image.Image:
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            t = min(1.0, d / radius)
            r = int(inner[0] + (outer[0] - inner[0]) * t)
            g = int(inner[1] + (outer[1] - inner[1]) * t)
            b = int(inner[2] + (outer[2] - inner[2]) * t)
            a = 255
            if len(inner) == 4:
                a = int(inner[3] + ((outer[3] if len(outer) == 4 else 255) - inner[3]) * t)
            px[x, y] = (r, g, b, a)
    return img


def noise_overlay(w: int, h: int, colors: list, density: float = 0.15,
                  seed: int = 42) -> Image.Image:
    """Streu-Textur: zuf\u00e4llige Punkte in versch. Farben."""
    rng = random.Random(seed)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y in range(h):
        for x in range(w):
            if rng.random() < density:
                c = colors[rng.randrange(len(colors))]
                if len(c) == 3:
                    c = (*c, 255)
                px[x, y] = c
    return img


def soft_shadow(w: int, h: int, cx: float, cy: float, rx: float, ry: float,
                alpha: int = 100) -> Image.Image:
    """Weicher elliptischer Alpha-Schatten (unter Objekten)."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(0, 0, 0, alpha))
    return img.filter(ImageFilter.GaussianBlur(3))


# --------------------------------------------------------------------------
# Tiles
# --------------------------------------------------------------------------
def tile_grass() -> Image.Image:
    # Basis: leichter Verlauf (oben etwas dunkler = Perspektive)
    base = vertical_gradient(SIZE, SIZE, GRASS_MID, GRASS_BASE)
    # Streu-Punkte (Bl\u00e4tter/Halme)
    dots = noise_overlay(SIZE, SIZE,
                         [GRASS_SHADOW, GRASS_LIGHT, GRASS_HL, GRASS_MID],
                         density=0.35, seed=11)
    base = blend(base, dots)
    # Ein paar sichtbare Grasb\u00fcschel (kleine Blades)
    d = ImageDraw.Draw(base)
    rng = random.Random(7)
    for _ in range(14):
        x = rng.randrange(3, SIZE - 3)
        y = rng.randrange(3, SIZE - 3)
        # Kleiner Halm (3 Pixel hoch mit heller Spitze)
        d.line([(x, y + 2), (x, y - 1)], fill=GRASS_SHADOW, width=1)
        d.point((x, y - 2), fill=GRASS_HL)
        d.line([(x - 1, y + 2), (x - 1, y)], fill=GRASS_MID, width=1)
    # Leichter Weichzeichner f\u00fcr HD-Look, dann etwas geschaerft (per Kontrast)
    base = base.filter(ImageFilter.SMOOTH)
    return base


def tile_sand() -> Image.Image:
    base = vertical_gradient(SIZE, SIZE, SAND_LIGHT, SAND_BASE)
    dots = noise_overlay(SIZE, SIZE,
                         [SAND_SHADOW, SAND_MID, SAND_LIGHT],
                         density=0.28, seed=21)
    base = blend(base, dots)
    # Muschel-Splitter: kleine hellere Punkte
    d = ImageDraw.Draw(base)
    rng = random.Random(3)
    for _ in range(6):
        x = rng.randrange(4, SIZE - 4)
        y = rng.randrange(4, SIZE - 4)
        d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=SAND_LIGHT)
    base = base.filter(ImageFilter.SMOOTH)
    return base


def tile_path() -> Image.Image:
    base = vertical_gradient(SIZE, SIZE, PATH_MID, PATH_BASE)
    dots = noise_overlay(SIZE, SIZE,
                         [PATH_SHADOW, PATH_LIGHT, PATH_MID],
                         density=0.30, seed=17)
    base = blend(base, dots)
    # Kleine Steine (mehr Detail)
    d = ImageDraw.Draw(base)
    rng = random.Random(5)
    for _ in range(9):
        x = rng.randrange(4, SIZE - 4)
        y = rng.randrange(4, SIZE - 4)
        r = rng.randrange(1, 3)
        d.ellipse([x - r, y - r, x + r, y + r], fill=ROCK_MID)
        d.ellipse([x - r, y - r, x, y], fill=ROCK_LIGHT)
    base = base.filter(ImageFilter.SMOOTH)
    return base


def tile_water() -> Image.Image:
    base = vertical_gradient(SIZE, SIZE, WATER_MID, WATER_BASE)
    # Wellenlinien: sinusf\u00f6rmig, mehrere Frequenzen
    d = ImageDraw.Draw(base)
    for wy_base in [10, 22, 36, 50]:
        pts_light = []
        pts_dark = []
        for x in range(SIZE):
            y = wy_base + int(2 * math.sin(x * 0.35 + wy_base * 0.5))
            pts_light.append((x, y))
            pts_dark.append((x, y + 3))
        for p in pts_light:
            d.point(p, fill=WATER_LIGHT)
        for p in pts_dark:
            d.point(p, fill=WATER_DEEP)
    # Schaumkroenchen (weich)
    rng = random.Random(9)
    for _ in range(5):
        x = rng.randrange(8, SIZE - 8)
        y = rng.randrange(8, SIZE - 8)
        d.ellipse([x - 2, y - 1, x + 2, y + 1], fill=WATER_FOAM)
        d.ellipse([x - 3, y, x + 3, y + 1], fill=WATER_LIGHT)
    base = base.filter(ImageFilter.GaussianBlur(0.7))
    return base


def tile_tree() -> Image.Image:
    # Basis: Gras-Untergrund
    base = tile_grass()
    d = ImageDraw.Draw(base)
    # Schatten unter der Krone (weich)
    sh = soft_shadow(SIZE, SIZE, SIZE / 2, SIZE / 2 + 8, 22, 8, alpha=90)
    base = blend(base, sh)
    d = ImageDraw.Draw(base)
    # Stamm
    d.rectangle([28, 42, 35, 56], fill=TRUNK_BASE)
    d.rectangle([28, 42, 30, 56], fill=TRUNK_DARK)
    d.rectangle([33, 42, 35, 56], fill=TRUNK_LIGHT)
    # Krone: mehrere \u00fcberlappende Ellipsen (voluminoes)
    # Basis-Ellipse
    d.ellipse([6, 6, 58, 44], fill=LEAF_BASE)
    # Highlight-Ellipse (Sonne von oben-links)
    d.ellipse([10, 8, 40, 30], fill=LEAF_MID)
    d.ellipse([14, 10, 34, 24], fill=LEAF_LIGHT)
    d.ellipse([18, 12, 28, 18], fill=LEAF_HL)
    # Schatten-Ellipse rechts-unten
    d.ellipse([28, 26, 56, 44], fill=LEAF_SHADOW)
    # \u00dcbergangs-Bl\u00e4tter (kleinere Kreise als Blattpolster)
    rng = random.Random(13)
    for _ in range(20):
        cx = rng.randrange(12, 52)
        cy = rng.randrange(8, 40)
        # Nur wenn im Bereich der Krone
        if (cx - 32) ** 2 / 26 ** 2 + (cy - 24) ** 2 / 18 ** 2 > 1.05:
            continue
        r = rng.randrange(3, 6)
        color = rng.choice([LEAF_MID, LEAF_LIGHT, LEAF_BASE, LEAF_HL])
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    # Weichzeichner f\u00fcr HD-Look
    base = base.filter(ImageFilter.GaussianBlur(0.5))
    # Nachschaerfen der Baumkontur mit dunklem Rand-Overlay
    outline = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    od = ImageDraw.Draw(outline)
    od.ellipse([5, 5, 59, 45], outline=LEAF_SHADOW, width=2)
    base = blend(base, outline)
    return base


def tile_rock() -> Image.Image:
    base = tile_grass()
    # Weicher Schatten unter Fels
    sh = soft_shadow(SIZE, SIZE, SIZE / 2, SIZE / 2 + 12, 24, 8, alpha=100)
    base = blend(base, sh)
    d = ImageDraw.Draw(base)
    # Grosser Fels: unregelm\u00e4ssige Ellipse
    d.ellipse([6, 12, 58, 54], fill=ROCK_BASE)
    # Highlight (Sonne oben-links) durch kleinere Ellipsen
    d.ellipse([10, 14, 40, 34], fill=ROCK_MID)
    d.ellipse([12, 16, 32, 28], fill=ROCK_LIGHT)
    d.ellipse([16, 18, 26, 24], fill=ROCK_HL)
    # Schattenseite unten-rechts
    d.ellipse([30, 34, 58, 54], fill=ROCK_SHADOW)
    # Kanten / Risse (kleine dunkle Linien)
    d.line([(20, 30), (28, 42)], fill=ROCK_SHADOW, width=1)
    d.line([(38, 24), (44, 40)], fill=ROCK_SHADOW, width=1)
    d.line([(24, 46), (36, 50)], fill=ROCK_SHADOW, width=1)
    # Moos-Flecken oben (weich)
    d.ellipse([14, 12, 22, 16], fill=ROCK_MOSS)
    d.ellipse([30, 13, 38, 17], fill=ROCK_MOSS)
    d.ellipse([44, 15, 50, 19], fill=ROCK_MOSS)
    # Kontur
    outline = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    od = ImageDraw.Draw(outline)
    od.ellipse([5, 11, 59, 55], outline=ROCK_SHADOW, width=2)
    base = blend(base, outline)
    base = base.filter(ImageFilter.GaussianBlur(0.4))
    return base


def tile_plank() -> Image.Image:
    """Holzboden mit realistischer Maserung."""
    base = vertical_gradient(SIZE, SIZE, WOOD_LIGHT, WOOD_BASE)
    d = ImageDraw.Draw(base)
    # 4 horizontale Planken (Fugen alle 16 Pixel)
    for y_line in [15, 31, 47, 63]:
        d.rectangle([0, y_line, SIZE - 1, y_line], fill=WOOD_LINE)
    # Highlight-Streifen oberhalb jeder Fuge
    for y in [0, 16, 32, 48]:
        d.rectangle([0, y, SIZE - 1, y], fill=WOOD_HL)
    # Maserung: gewellte Linien pro Planke
    rng = random.Random(19)
    for planke_y in [0, 16, 32, 48]:
        for _ in range(3):
            y = planke_y + rng.randrange(3, 12)
            wave_off = rng.uniform(0, math.tau)
            pts = []
            for x in range(SIZE):
                yy = y + int(math.sin(x * 0.15 + wave_off))
                pts.append((x, yy))
            color = rng.choice([WOOD_SHADOW, WOOD_LIGHT, WOOD_DARK])
            for p in pts:
                d.point(p, fill=color)
    # N\u00e4gel (dunkle Punkte an Ecken)
    for cx in [4, 60]:
        for cy in [4, 20, 36, 52]:
            d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=WOOD_LINE)
            d.point((cx, cy), fill=METAL_BASE)
    base = base.filter(ImageFilter.SMOOTH)
    return base


def tile_wall() -> Image.Image:
    """Verwitterte vertikale Holzwand."""
    base = vertical_gradient(SIZE, SIZE, WOOD_BASE, WOOD_SHADOW)
    d = ImageDraw.Draw(base)
    # 4 vertikale Planken
    for x_line in [15, 31, 47, 63]:
        d.rectangle([x_line, 0, x_line, SIZE - 1], fill=WOOD_LINE)
    # Highlight links neben jeder Fuge (Sonne von rechts)
    for x in [16, 32, 48]:
        d.rectangle([x, 0, x, SIZE - 1], fill=WOOD_HL)
    # Maserung vertikal
    rng = random.Random(23)
    for planke_x in [0, 16, 32, 48]:
        for _ in range(3):
            x = planke_x + rng.randrange(3, 12)
            wave_off = rng.uniform(0, math.tau)
            for y in range(SIZE):
                xx = x + int(math.sin(y * 0.13 + wave_off))
                d.point((xx, y), fill=rng.choice([WOOD_SHADOW, WOOD_LIGHT, WOOD_DARK]))
    # \u00c4ste / Astl\u00f6cher (dunkle Kreise)
    for _ in range(3):
        cx = rng.randrange(6, SIZE - 6)
        cy = rng.randrange(6, SIZE - 6)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=WOOD_DARK)
        d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=WOOD_LINE)
    # N\u00e4gel oben/unten
    for cy in [3, 60]:
        for cx in [6, 22, 38, 54]:
            d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=WOOD_LINE)
            d.point((cx, cy), fill=METAL_BASE)
    base = base.filter(ImageFilter.SMOOTH)
    return base


def tile_door() -> Image.Image:
    """T\u00fcr mit Beschl\u00e4gen und M\u00fcnzklopfer."""
    # Basis wie Wand (Rahmen)
    base = tile_wall()
    d = ImageDraw.Draw(base)
    # T\u00fcrblatt zentriert
    d.rectangle([12, 4, 51, 60], fill=DOOR_BASE)
    # Rahmen (dunkler)
    d.rectangle([12, 4, 51, 5], fill=DOOR_DARK)
    d.rectangle([12, 4, 13, 60], fill=DOOR_DARK)
    d.rectangle([50, 4, 51, 60], fill=DOOR_DARK)
    d.rectangle([12, 59, 51, 60], fill=DOOR_DARK)
    # Vertikale Holzmaserung im T\u00fcrblatt
    for x_line in [22, 32, 42]:
        d.rectangle([x_line, 6, x_line, 58], fill=DOOR_DARK)
    for x in [23, 33, 43]:
        d.rectangle([x, 6, x, 58], fill=DOOR_LIGHT)
    # Quer-Balken oben und unten
    d.rectangle([13, 14, 50, 17], fill=DOOR_DARK)
    d.rectangle([13, 46, 50, 49], fill=DOOR_DARK)
    d.rectangle([14, 15, 49, 16], fill=DOOR_LIGHT)
    d.rectangle([14, 47, 49, 48], fill=DOOR_LIGHT)
    # M\u00fcnzklopfer (Gold-Ring in der Mitte)
    d.ellipse([27, 27, 37, 37], fill=METAL_DARK)
    d.ellipse([28, 28, 36, 36], fill=METAL_BASE)
    d.ellipse([29, 29, 35, 35], fill=METAL_HL)
    # Innenloch
    d.ellipse([30, 30, 34, 34], fill=DOOR_DARK)
    # Klinke rechts
    d.ellipse([44, 34, 47, 40], fill=METAL_DARK)
    d.ellipse([44, 34, 46, 38], fill=METAL_BASE)
    d.point((45, 35), fill=METAL_HL)
    base = base.filter(ImageFilter.SMOOTH)
    return base


def tile_roof() -> Image.Image:
    """Schindeldach mit weicher Textur."""
    base = vertical_gradient(SIZE, SIZE, ROOF_LIGHT, ROOF_BASE)
    d = ImageDraw.Draw(base)
    # 4 Schindelreihen mit versetzten Fugen
    for row in range(4):
        y0 = row * 16
        y1 = y0 + 16
        offset = 8 if row % 2 == 0 else 0
        # Vertikale Fugen alle 16 Pixel, versetzt
        for x in range(-8, SIZE + 16, 16):
            xx = x + offset
            if 0 <= xx < SIZE:
                d.rectangle([xx, y0, xx, y1], fill=ROOF_SHADOW)
        # Horizontale Fuge oben (dunkler)
        d.rectangle([0, y0, SIZE - 1, y0], fill=ROOF_SHADOW)
        # Highlight-Streifen unter jeder horizontalen Fuge
        d.rectangle([0, y0 + 1, SIZE - 1, y0 + 2], fill=ROOF_HL)
        # Rundung jeder Schindel unten (dunkler Bogen)
        for x in range(-8, SIZE + 16, 16):
            xx = x + offset
            d.arc([xx - 1, y1 - 4, xx + 15, y1 + 4], start=0, end=180,
                  fill=ROOF_SHADOW, width=1)
    # Textur-Rauschen
    dots = noise_overlay(SIZE, SIZE,
                         [ROOF_SHADOW, ROOF_LIGHT, ROOF_MID],
                         density=0.15, seed=29)
    base = blend(base, dots)
    base = base.filter(ImageFilter.SMOOTH)
    return base


# --------------------------------------------------------------------------
# Captain-Sprite (Top-Down, moderner Switch-Look)
# --------------------------------------------------------------------------
def sprite_captain() -> Image.Image:
    base = new_img(SIZE)
    d = ImageDraw.Draw(base)

    # Boden-Schatten weich
    sh = soft_shadow(SIZE, SIZE, 32, 56, 14, 4, alpha=110)
    base = blend(base, sh)
    d = ImageDraw.Draw(base)

    # ---- Beine + Stiefel (32 + 12 breit, unterer Bereich) ----
    # Linkes Stiefel
    d.rectangle([21, 50, 29, 60], fill=BOOT_BASE)
    d.rectangle([21, 50, 22, 60], fill=BOOT_DARK)
    d.rectangle([28, 50, 29, 60], fill=BOOT_HL)
    d.ellipse([21, 58, 30, 62], fill=BOOT_BASE)
    d.ellipse([21, 58, 30, 62], outline=BOOT_DARK, width=1)
    # Rechtes Stiefel
    d.rectangle([35, 50, 43, 60], fill=BOOT_BASE)
    d.rectangle([35, 50, 36, 60], fill=BOOT_DARK)
    d.rectangle([42, 50, 43, 60], fill=BOOT_HL)
    d.ellipse([34, 58, 43, 62], fill=BOOT_BASE)
    d.ellipse([34, 58, 43, 62], outline=BOOT_DARK, width=1)

    # ---- Mantel (breit, unten leicht ausgestellt) ----
    coat = [
        (16, 30), (16, 52),
        (48, 52), (48, 30),
    ]
    d.polygon([(16, 30), (16, 52), (18, 55), (46, 55), (48, 52), (48, 30)],
              fill=COAT_BASE)
    # Highlights linke Kante (Sonne von links oben)
    d.polygon([(16, 30), (16, 52), (18, 55), (20, 55), (20, 32)],
              fill=COAT_LIGHT)
    d.line([(18, 30), (18, 55)], fill=COAT_HL, width=1)
    # Schatten rechte Kante
    d.polygon([(44, 32), (44, 55), (46, 55), (48, 52), (48, 30)],
              fill=COAT_DARK)
    # Untere Mantelkante dunkler
    d.rectangle([16, 51, 48, 55], fill=COAT_DARK)
    d.line([(16, 52), (48, 52)], fill=COAT_DARK, width=1)
    # Mantel-Schlitz Mitte
    d.rectangle([31, 42, 33, 55], fill=COAT_DARK)

    # Goldknopf-Reihe (3 Kn\u00f6pfe)
    for cy in [34, 42, 48]:
        d.ellipse([30, cy, 34, cy + 4], fill=BUCKLE)
        d.ellipse([30, cy, 33, cy + 3], fill=BUCKLE_HL)
        d.point((31, cy + 1), fill=(255, 255, 255))

    # G\u00fcrtel (horizontal)
    d.rectangle([16, 45, 48, 49], fill=BELT)
    # G\u00fcrtelschnalle (gross, gold)
    d.rectangle([28, 44, 36, 50], fill=BUCKLE)
    d.rectangle([29, 45, 35, 49], fill=BUCKLE_HL)
    d.rectangle([31, 46, 33, 48], fill=BELT)

    # ---- Kopf (Haut) ----
    # Gesicht als Ellipse
    d.ellipse([22, 16, 42, 34], fill=SKIN_BASE)
    d.ellipse([22, 16, 42, 26], fill=SKIN_HL)
    d.ellipse([22, 28, 42, 34], fill=SKIN_SHADOW)
    # Augen
    d.ellipse([26, 22, 28, 24], fill=BLACK)
    d.ellipse([36, 22, 38, 24], fill=BLACK)
    d.point((27, 22), fill=(255, 255, 255))
    d.point((37, 22), fill=(255, 255, 255))
    # Nase (leichter Schatten)
    d.line([(31, 26), (32, 27)], fill=SKIN_SHADOW, width=1)

    # ---- Bart (weisser Piratenbart, gross) ----
    d.pieslice([20, 24, 44, 40], start=15, end=165, fill=BEARD_BASE)
    d.pieslice([21, 26, 43, 38], start=20, end=160, fill=BEARD_HL)
    # Bart-Konturen
    d.pieslice([20, 24, 44, 40], start=15, end=165, outline=BEARD_DARK, width=1)
    # Schnurrbart-Andeutung
    d.line([(26, 28), (30, 29)], fill=BEARD_DARK, width=1)
    d.line([(34, 29), (38, 28)], fill=BEARD_DARK, width=1)

    # ---- Dreispitzhut (breit, gold-getrimmt) ----
    # Drei Spitzen: mittig h\u00f6her, links + rechts geneigt
    hat_points = [
        (14, 18),   # links unten
        (20, 6),    # linke Spitze
        (32, 2),    # Mittelspitze
        (44, 6),    # rechte Spitze
        (50, 18),   # rechts unten
        (46, 20),
        (32, 22),   # Mitte Unterrand
        (18, 20),
    ]
    d.polygon(hat_points, fill=HAT_BASE)
    # Highlight (Sonne von oben links)
    hl_points = [
        (16, 17), (20, 8), (28, 5), (32, 4), (30, 8), (24, 14), (18, 19),
    ]
    d.polygon(hl_points, fill=HAT_HL)
    # Goldener Rand
    for i in range(len(hat_points)):
        a = hat_points[i]
        b = hat_points[(i + 1) % len(hat_points)]
        d.line([a, b], fill=HAT_TRIM, width=1)
    d.line([(14, 18), (50, 18)], fill=HAT_TRIM, width=2)
    d.line([(15, 19), (49, 19)], fill=HAT_TRIM_HL, width=1)
    # Sch\u00e4del-Emblem in der Mitte (Piraten!)
    d.ellipse([30, 8, 34, 12], fill=HAT_TRIM_HL)
    d.point((31, 10), fill=HAT_DARK)
    d.point((33, 10), fill=HAT_DARK)
    # Hut-Kontur
    for i in range(len(hat_points)):
        a = hat_points[i]
        b = hat_points[(i + 1) % len(hat_points)]
        d.line([a, b], fill=HAT_DARK, width=1)

    # ---- Schulterst\u00fccke (Epauletten) mit Goldfranse ----
    d.ellipse([12, 30, 20, 38], fill=BUCKLE)
    d.ellipse([13, 31, 19, 37], fill=BUCKLE_HL)
    d.ellipse([44, 30, 52, 38], fill=BUCKLE)
    d.ellipse([45, 31, 51, 37], fill=BUCKLE_HL)

    # Feine Weichzeichnung f\u00fcr HD-Look, dann etwas nachschaerfen der Konturen
    base = base.filter(ImageFilter.GaussianBlur(0.5))
    return base


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

    for name, img in tiles:
        img.save(tiles_dir / f"{name}.png")
        print(f"  wrote {name}.png")

    atlas = Image.new("RGBA", (10 * SIZE, SIZE), (0, 0, 0, 0))
    for i, (_, img) in enumerate(tiles):
        atlas.paste(img, (i * SIZE, 0))
    atlas.save(tiles_dir / "atlas.png")
    print(f"  wrote atlas.png ({atlas.size})")

    cap = sprite_captain()
    cap.save(sprites_dir / "captain.png")
    print(f"  wrote captain.png ({cap.size})")


if __name__ == "__main__":
    main()
