"""Erzeugt alle Charakter-Sprites im HD-Switch-Stil.

Baut auf gen_hd_tiles.py auf (gleiche Palette + Techniken).

Sprites (alle 64x64, Top-Down-Ansicht):
  captain.png       -- Kaeptn Bran (rot, Feuer) -- existiert bereits
  marina.png        -- Marina die Kanonierin (blau, Wasser)
  kite.png          -- Kite die Spaeherin (gruen, Wind)
  wind_bandit.png   -- Wind-Bandit (grauer Umhang, Maske)
  kelpholm_captain.png -- Piraten-Kapitaen von Kelpholm (dunkel, Wasser)
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SIZE = 64
BLACK = (20, 15, 15)


# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
# Haut-Toene
SKIN_LIGHT   = (255, 225, 190)
SKIN_BASE    = (245, 205, 165)
SKIN_SHADOW  = (200, 155, 115)
SKIN_TAN     = (200, 155, 115)
SKIN_TAN_HL  = (225, 180, 140)

# Kaeptn Bran (Feuer, rot)
BRAN_COAT    = (155, 40, 50)
BRAN_LIGHT   = (200, 75, 85)
BRAN_DARK    = (85, 20, 25)

# Marina (Wasser, blau)
MARINA_COAT  = (35, 90, 155)
MARINA_LIGHT = (70, 135, 200)
MARINA_DARK  = (20, 55, 100)
MARINA_HAIR  = (75, 55, 30)
MARINA_HAIR_HL = (135, 100, 60)

# Kite (Wind, gruen)
KITE_COAT    = (65, 130, 65)
KITE_LIGHT   = (110, 175, 100)
KITE_DARK    = (35, 85, 40)
KITE_HAIR    = (215, 175, 90)
KITE_HAIR_HL = (245, 215, 140)

# Wind-Bandit (Bandit-Look: dunkelgrauer Umhang, rote Maske)
BANDIT_CLOAK = (55, 55, 65)
BANDIT_LIGHT = (95, 95, 105)
BANDIT_DARK  = (25, 25, 30)
BANDIT_MASK  = (155, 40, 50)
BANDIT_MASK_HL = (200, 75, 85)

# Kelpholm-Captain (Boss: schwarz-rot, sinistrer)
CAP_COAT     = (35, 35, 45)
CAP_LIGHT    = (75, 65, 85)
CAP_DARK     = (15, 15, 20)
CAP_ACCENT   = (155, 20, 30)
CAP_ACCENT_HL= (200, 55, 65)

# Gold / Metall
GOLD_BASE    = (215, 185, 110)
GOLD_HL      = (245, 220, 155)
GOLD_DARK    = (135, 110, 55)
SILVER_BASE  = (185, 190, 200)
SILVER_HL    = (230, 235, 240)

# Bart-Farben
BEARD_WHITE_DARK = (155, 135, 110)
BEARD_WHITE_BASE = (200, 180, 155)
BEARD_WHITE_HL   = (230, 215, 195)
BEARD_BLACK_DARK = (25, 20, 15)
BEARD_BLACK_BASE = (55, 45, 35)
BEARD_BLACK_HL   = (95, 80, 60)

# Hut
HAT_DARK     = (25, 20, 20)
HAT_BASE     = (55, 45, 45)
HAT_HL       = (95, 85, 85)

# Stiefel
BOOT_DARK    = (40, 25, 15)
BOOT_BASE    = (75, 50, 30)
BOOT_HL      = (115, 85, 55)

# Guertel
BELT         = (55, 30, 15)


# --------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------
def new_img() -> Image.Image:
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def soft_shadow(cx: float, cy: float, rx: float, ry: float,
                alpha: int = 110) -> Image.Image:
    img = new_img()
    d = ImageDraw.Draw(img)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(0, 0, 0, alpha))
    return img.filter(ImageFilter.GaussianBlur(3))


def draw_shadow(base: Image.Image, cx=32, cy=58, rx=13, ry=4, alpha=110) -> Image.Image:
    """Weicher Boden-Schatten unter der Figur."""
    sh = soft_shadow(cx, cy, rx, ry, alpha=alpha)
    out = base.copy()
    out.alpha_composite(sh)
    return out


def draw_boots(d: ImageDraw.ImageDraw, coat_dark, coat_hl) -> None:
    """Standard-Stiefel + Beinansatz."""
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


def draw_coat(d: ImageDraw.ImageDraw, base, light, dark) -> None:
    """Piraten-Mantel-Silhouette."""
    d.polygon([(16, 30), (16, 52), (18, 55), (46, 55), (48, 52), (48, 30)],
              fill=base)
    d.polygon([(16, 30), (16, 52), (18, 55), (20, 55), (20, 32)],
              fill=light)
    d.line([(18, 30), (18, 55)], fill=light, width=1)
    d.polygon([(44, 32), (44, 55), (46, 55), (48, 52), (48, 30)],
              fill=dark)
    d.rectangle([16, 51, 48, 55], fill=dark)
    d.rectangle([31, 42, 33, 55], fill=dark)


def draw_belt(d: ImageDraw.ImageDraw) -> None:
    """Guertel mit goldener Schnalle."""
    d.rectangle([16, 45, 48, 49], fill=BELT)
    d.rectangle([28, 44, 36, 50], fill=GOLD_BASE)
    d.rectangle([29, 45, 35, 49], fill=GOLD_HL)
    d.rectangle([31, 46, 33, 48], fill=BELT)


def draw_head_skin(d: ImageDraw.ImageDraw,
                   skin_base=SKIN_BASE, skin_hl=SKIN_LIGHT, skin_shadow=SKIN_SHADOW) -> None:
    """Standard-Kopf 20x18 (Rundung)."""
    d.ellipse([22, 16, 42, 34], fill=skin_base)
    d.ellipse([22, 16, 42, 26], fill=skin_hl)
    d.ellipse([22, 28, 42, 34], fill=skin_shadow)


def draw_eyes(d: ImageDraw.ImageDraw, ex=(26, 36), ey=22) -> None:
    for x in ex:
        d.ellipse([x, ey, x + 2, ey + 2], fill=BLACK)
        d.point((x + 1, ey), fill=(255, 255, 255))


# --------------------------------------------------------------------------
# Kaeptn Bran (bestehend, aber wir malen ihn neu fuer Konsistenz)
# --------------------------------------------------------------------------
def sprite_bran() -> Image.Image:
    base = new_img()
    base = draw_shadow(base)
    d = ImageDraw.Draw(base)

    draw_boots(d, BRAN_COAT, BRAN_LIGHT)
    draw_coat(d, BRAN_COAT, BRAN_LIGHT, BRAN_DARK)
    # Bran hat 3 Goldknoepfe entlang der Mitte
    for cy in [34, 42, 48]:
        d.ellipse([30, cy, 34, cy + 4], fill=GOLD_BASE)
        d.ellipse([30, cy, 33, cy + 3], fill=GOLD_HL)
        d.point((31, cy + 1), fill=(255, 255, 255))
    draw_belt(d)
    draw_head_skin(d)
    draw_eyes(d)
    # Nase
    d.line([(31, 26), (32, 27)], fill=SKIN_SHADOW, width=1)
    # Weisser Piratenbart
    d.pieslice([20, 24, 44, 40], start=15, end=165, fill=BEARD_WHITE_BASE)
    d.pieslice([21, 26, 43, 38], start=20, end=160, fill=BEARD_WHITE_HL)
    d.pieslice([20, 24, 44, 40], start=15, end=165,
               outline=BEARD_WHITE_DARK, width=1)
    d.line([(26, 28), (30, 29)], fill=BEARD_WHITE_DARK, width=1)
    d.line([(34, 29), (38, 28)], fill=BEARD_WHITE_DARK, width=1)
    # Dreispitzhut
    hat = [(14, 18), (20, 6), (32, 2), (44, 6), (50, 18), (46, 20),
           (32, 22), (18, 20)]
    d.polygon(hat, fill=HAT_BASE)
    d.polygon([(16, 17), (20, 8), (28, 5), (32, 4), (30, 8), (24, 14), (18, 19)],
              fill=HAT_HL)
    for i in range(len(hat)):
        d.line([hat[i], hat[(i + 1) % len(hat)]], fill=GOLD_BASE, width=1)
    d.line([(14, 18), (50, 18)], fill=GOLD_BASE, width=2)
    d.line([(15, 19), (49, 19)], fill=GOLD_HL, width=1)
    d.ellipse([30, 8, 34, 12], fill=GOLD_HL)
    d.point((31, 10), fill=HAT_DARK)
    d.point((33, 10), fill=HAT_DARK)
    for i in range(len(hat)):
        d.line([hat[i], hat[(i + 1) % len(hat)]], fill=HAT_DARK, width=1)
    # Epauletten
    d.ellipse([12, 30, 20, 38], fill=GOLD_BASE)
    d.ellipse([13, 31, 19, 37], fill=GOLD_HL)
    d.ellipse([44, 30, 52, 38], fill=GOLD_BASE)
    d.ellipse([45, 31, 51, 37], fill=GOLD_HL)

    return base.filter(ImageFilter.GaussianBlur(0.5))


# --------------------------------------------------------------------------
# Marina die Kanonierin (blauer Mantel, brauner Zopf, Bandana)
# --------------------------------------------------------------------------
def sprite_marina() -> Image.Image:
    base = new_img()
    base = draw_shadow(base)
    d = ImageDraw.Draw(base)

    draw_boots(d, MARINA_COAT, MARINA_LIGHT)
    draw_coat(d, MARINA_COAT, MARINA_LIGHT, MARINA_DARK)
    # Marina hat Bronze-Ankerknoepfe (silber)
    for cy in [34, 42, 48]:
        d.ellipse([30, cy, 34, cy + 4], fill=SILVER_BASE)
        d.ellipse([30, cy, 33, cy + 3], fill=SILVER_HL)
    draw_belt(d)
    # Zopf hinter dem Kopf (haengt links unten)
    d.polygon([(18, 22), (14, 40), (16, 42), (20, 26)], fill=MARINA_HAIR)
    d.polygon([(15, 30), (16, 41), (17, 42), (18, 32)], fill=MARINA_HAIR_HL)
    draw_head_skin(d, skin_base=SKIN_TAN, skin_hl=SKIN_TAN_HL, skin_shadow=(160, 115, 80))
    draw_eyes(d)
    # Mund (klein, laecheln)
    d.line([(30, 30), (34, 30)], fill=(120, 60, 60), width=1)
    # Rotes Bandana (statt Hut) — Halbmond um Stirn
    d.pieslice([18, 10, 46, 26], start=180, end=360, fill=MARINA_COAT)
    d.pieslice([19, 11, 45, 22], start=190, end=350, fill=MARINA_LIGHT)
    d.pieslice([18, 10, 46, 26], start=180, end=360, outline=MARINA_DARK, width=1)
    # Bandana-Zipfel rechts
    d.polygon([(44, 16), (52, 12), (50, 22), (44, 22)], fill=MARINA_COAT)
    d.polygon([(46, 15), (50, 14), (48, 20)], fill=MARINA_LIGHT)
    # Kleine Anker-Silhouette in der Mitte des Bandanas
    d.line([(32, 16), (32, 20)], fill=GOLD_HL, width=1)
    d.arc([29, 18, 35, 22], start=0, end=180, fill=GOLD_HL, width=1)
    # Epauletten silber
    d.ellipse([12, 30, 20, 38], fill=SILVER_BASE)
    d.ellipse([13, 31, 19, 37], fill=SILVER_HL)
    d.ellipse([44, 30, 52, 38], fill=SILVER_BASE)
    d.ellipse([45, 31, 51, 37], fill=SILVER_HL)

    return base.filter(ImageFilter.GaussianBlur(0.5))


# --------------------------------------------------------------------------
# Kite die Spaeherin (gruener Umhang, blondes Haar, Fernrohr)
# --------------------------------------------------------------------------
def sprite_kite() -> Image.Image:
    base = new_img()
    base = draw_shadow(base)
    d = ImageDraw.Draw(base)

    draw_boots(d, KITE_COAT, KITE_LIGHT)
    # Kites Umhang ist schmaler / eher Weste
    d.polygon([(18, 30), (18, 52), (20, 55), (44, 55), (46, 52), (46, 30)],
              fill=KITE_COAT)
    d.polygon([(18, 30), (18, 52), (20, 55), (22, 55), (22, 32)], fill=KITE_LIGHT)
    d.polygon([(42, 32), (42, 55), (44, 55), (46, 52), (46, 30)], fill=KITE_DARK)
    d.rectangle([18, 51, 46, 55], fill=KITE_DARK)
    d.rectangle([31, 42, 33, 55], fill=KITE_DARK)
    # Braune Lederknoepfe
    brown = (110, 65, 30)
    for cy in [36, 44]:
        d.ellipse([30, cy, 34, cy + 4], fill=brown)
        d.ellipse([30, cy, 33, cy + 3], fill=(150, 100, 55))
    d.rectangle([18, 45, 46, 49], fill=BELT)
    d.rectangle([28, 44, 36, 50], fill=(110, 65, 30))
    d.rectangle([29, 45, 35, 49], fill=(150, 100, 55))
    # Blondes Haar (rundum, ueber Ohren)
    d.ellipse([20, 14, 44, 32], fill=KITE_HAIR)
    d.ellipse([20, 14, 44, 24], fill=KITE_HAIR_HL)
    # Gesicht (Haut)
    d.ellipse([23, 18, 41, 32], fill=SKIN_BASE)
    d.ellipse([23, 18, 41, 25], fill=SKIN_LIGHT)
    draw_eyes(d, ex=(27, 35), ey=23)
    # Mund
    d.line([(31, 29), (33, 29)], fill=(120, 60, 60), width=1)
    # Pony-Fransen
    d.polygon([(24, 18), (28, 22), (26, 15)], fill=KITE_HAIR)
    d.polygon([(40, 18), (36, 22), (38, 15)], fill=KITE_HAIR)
    # Federhut (breite Kappe mit Feder rechts)
    d.pieslice([16, 8, 48, 24], start=180, end=360, fill=KITE_COAT)
    d.pieslice([17, 9, 47, 20], start=190, end=350, fill=KITE_LIGHT)
    d.pieslice([16, 8, 48, 24], start=180, end=360, outline=KITE_DARK, width=1)
    # Feder oben rechts
    d.polygon([(44, 8), (54, 2), (52, 12), (46, 14)], fill=(255, 235, 155))
    d.polygon([(46, 8), (52, 4), (50, 11)], fill=(230, 195, 90))
    d.line([(45, 9), (53, 3)], fill=GOLD_DARK, width=1)
    # Fernrohr in der Hand rechts (kleines Detail)
    d.rectangle([46, 40, 54, 44], fill=(60, 45, 30))
    d.rectangle([46, 40, 54, 41], fill=(120, 90, 60))
    d.ellipse([44, 39, 48, 45], fill=SILVER_BASE)

    return base.filter(ImageFilter.GaussianBlur(0.5))


# --------------------------------------------------------------------------
# Wind-Bandit (dunkler Umhang, rote Maske, schmal)
# --------------------------------------------------------------------------
def sprite_wind_bandit() -> Image.Image:
    base = new_img()
    base = draw_shadow(base, alpha=140)  # dunklerer Schatten
    d = ImageDraw.Draw(base)

    # Beine (schwarze Hose statt Stiefel-Detail)
    d.rectangle([22, 48, 30, 60], fill=BANDIT_DARK)
    d.rectangle([34, 48, 42, 60], fill=BANDIT_DARK)
    d.rectangle([22, 60, 30, 62], fill=BOOT_BASE)
    d.rectangle([34, 60, 42, 62], fill=BOOT_BASE)
    # Umhang (Kapuzen-Silhouette, breit unten)
    d.polygon([(14, 22), (10, 55), (18, 60), (46, 60), (54, 55), (50, 22)],
              fill=BANDIT_CLOAK)
    d.polygon([(14, 22), (10, 55), (18, 60), (22, 60), (20, 24)],
              fill=BANDIT_LIGHT)
    d.polygon([(44, 24), (46, 60), (54, 55), (50, 22)], fill=BANDIT_DARK)
    d.line([(14, 22), (10, 55)], fill=BANDIT_DARK, width=1)
    d.line([(50, 22), (54, 55)], fill=BANDIT_DARK, width=1)
    # Bruststuecke
    d.line([(32, 22), (32, 55)], fill=BANDIT_DARK, width=1)
    # Kapuze / Kopf
    # Kapuzen-Konturen
    d.pieslice([16, 8, 48, 34], start=180, end=360, fill=BANDIT_CLOAK)
    d.pieslice([16, 8, 48, 34], start=180, end=360, outline=BANDIT_DARK, width=1)
    d.pieslice([18, 10, 46, 30], start=190, end=350, fill=BANDIT_LIGHT)
    # Gesicht (schmaler Ausschnitt)
    d.ellipse([24, 18, 40, 32], fill=SKIN_SHADOW)
    d.ellipse([24, 18, 40, 26], fill=SKIN_BASE)
    # Rote Maske (breiter Streifen ueber Augen)
    d.rectangle([22, 22, 42, 27], fill=BANDIT_MASK)
    d.rectangle([22, 22, 42, 23], fill=BANDIT_MASK_HL)
    # Augen (rote Maske hat zwei Loecher)
    d.ellipse([26, 23, 28, 26], fill=BLACK)
    d.ellipse([36, 23, 38, 26], fill=BLACK)
    d.point((27, 24), fill=(255, 100, 100))
    d.point((37, 24), fill=(255, 100, 100))
    # Mund grimmig
    d.line([(29, 29), (35, 29)], fill=(80, 40, 40), width=1)
    d.line([(30, 30), (34, 30)], fill=(60, 30, 30), width=1)
    # Krummer Wind-Dolch (an Guertel links)
    d.line([(20, 44), (16, 52)], fill=SILVER_BASE, width=2)
    d.line([(20, 44), (16, 52)], fill=SILVER_HL, width=1)
    d.rectangle([19, 42, 21, 46], fill=BELT)
    d.rectangle([19, 42, 20, 46], fill=GOLD_DARK)

    return base.filter(ImageFilter.GaussianBlur(0.5))


# --------------------------------------------------------------------------
# Kelpholm-Captain (Boss: schwarz-rot, grosser Hut, schwarzer Bart, Saebel)
# --------------------------------------------------------------------------
def sprite_kelpholm() -> Image.Image:
    base = new_img()
    base = draw_shadow(base, rx=15, ry=5, alpha=130)
    d = ImageDraw.Draw(base)

    draw_boots(d, CAP_COAT, CAP_LIGHT)
    draw_coat(d, CAP_COAT, CAP_LIGHT, CAP_DARK)
    # Rote Akzente an Kanten (Boss-Farbcode)
    d.polygon([(16, 30), (16, 33), (18, 33), (18, 30)], fill=CAP_ACCENT)
    d.polygon([(46, 30), (46, 33), (48, 33), (48, 30)], fill=CAP_ACCENT)
    d.rectangle([16, 51, 48, 53], fill=CAP_ACCENT)
    # Grosse Goldknoepfe
    for cy in [34, 42, 48]:
        d.ellipse([29, cy, 35, cy + 5], fill=GOLD_BASE)
        d.ellipse([30, cy + 1, 34, cy + 4], fill=GOLD_HL)
    # Guertel mit rotem Emblem
    d.rectangle([16, 45, 48, 49], fill=BELT)
    d.rectangle([28, 44, 36, 50], fill=CAP_ACCENT)
    d.rectangle([29, 45, 35, 49], fill=CAP_ACCENT_HL)
    d.rectangle([31, 46, 33, 48], fill=BELT)
    # Kopf (getanned)
    draw_head_skin(d, skin_base=SKIN_TAN, skin_hl=SKIN_TAN_HL, skin_shadow=(140, 100, 70))
    # Boese Augen (schmaler)
    d.rectangle([26, 22, 28, 24], fill=BLACK)
    d.rectangle([36, 22, 38, 24], fill=BLACK)
    # Rote Augenbrauen (finster)
    d.line([(25, 20), (29, 21)], fill=CAP_ACCENT, width=1)
    d.line([(35, 21), (39, 20)], fill=CAP_ACCENT, width=1)
    # Schwarzer Bart (voll, boese)
    d.pieslice([18, 22, 46, 42], start=15, end=165, fill=BEARD_BLACK_BASE)
    d.pieslice([19, 24, 45, 40], start=20, end=160, fill=BEARD_BLACK_HL)
    d.pieslice([18, 22, 46, 42], start=15, end=165, outline=BEARD_BLACK_DARK, width=1)
    # Kelpholm-Hut (grosser Zylinder-Dreispitz mit rotem Band)
    hat = [(10, 20), (16, 4), (32, 0), (48, 4), (54, 20), (48, 22),
           (32, 24), (16, 22)]
    d.polygon(hat, fill=CAP_DARK)
    d.polygon([(12, 19), (18, 6), (28, 3), (32, 2), (30, 6), (22, 16), (16, 21)],
              fill=CAP_LIGHT)
    # Rotes Band um den Hut
    d.rectangle([10, 20, 54, 22], fill=CAP_ACCENT)
    d.rectangle([11, 20, 53, 21], fill=CAP_ACCENT_HL)
    # Totenkopf in der Mitte
    d.ellipse([28, 10, 36, 18], fill=SILVER_HL)
    d.ellipse([28, 10, 36, 18], outline=CAP_DARK, width=1)
    d.point((30, 13), fill=CAP_DARK)
    d.point((34, 13), fill=CAP_DARK)
    d.line([(30, 16), (34, 16)], fill=CAP_DARK, width=1)
    # Hut-Kontur
    for i in range(len(hat)):
        d.line([hat[i], hat[(i + 1) % len(hat)]], fill=BLACK, width=1)
    # Epauletten schwarz-gold
    d.ellipse([10, 28, 20, 40], fill=GOLD_BASE)
    d.ellipse([12, 30, 18, 38], fill=CAP_DARK)
    d.ellipse([13, 31, 17, 37], fill=CAP_ACCENT)
    d.ellipse([44, 28, 54, 40], fill=GOLD_BASE)
    d.ellipse([46, 30, 52, 38], fill=CAP_DARK)
    d.ellipse([47, 31, 51, 37], fill=CAP_ACCENT)
    # Saebel an der rechten Seite
    d.line([(52, 46), (58, 58)], fill=SILVER_BASE, width=2)
    d.line([(52, 46), (58, 58)], fill=SILVER_HL, width=1)
    d.rectangle([50, 44, 54, 48], fill=GOLD_BASE)
    d.rectangle([51, 45, 53, 47], fill=GOLD_HL)

    return base.filter(ImageFilter.GaussianBlur(0.5))


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main() -> None:
    root = Path(__file__).resolve().parents[2]
    sprites_dir = root / "assets" / "sprites"
    sprites_dir.mkdir(parents=True, exist_ok=True)

    sprites = [
        ("captain.png",          sprite_bran()),
        ("marina.png",           sprite_marina()),
        ("kite.png",             sprite_kite()),
        ("wind_bandit.png",      sprite_wind_bandit()),
        ("kelpholm_captain.png", sprite_kelpholm()),
    ]
    for name, img in sprites:
        img.save(sprites_dir / name)
        print(f"  wrote {name}")


if __name__ == "__main__":
    main()
