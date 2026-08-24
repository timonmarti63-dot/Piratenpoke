"""[DEPRECATED v0.4] Erzeugt farbige 64x64 Platzhalter-Kacheln + den Player-Sprite.

Dieses Skript erzeugt nur einfarbige Rechtecke. Ab v0.4 werden die Assets
von `gen_pixelart_tiles.py` als echte Pixel-Art im Pokémon-Piraten-Stil
generiert. Dieses Skript wird nur noch zur Erst-Bootstrap-Referenz aufbewahrt.

Wird einmalig ausgeführt, um `assets/tiles/*.png` und `assets/sprites/captain.png`
zu generieren. In der Pixel-Art-Phase werden diese Dateien einfach
überschrieben — die Godot-Szene bleibt unverändert.
"""

from __future__ import annotations
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError as e:
    raise SystemExit("pip install pillow  # wird für die Platzhalter benötigt") from e

TILE = 64
ROOT = Path(__file__).resolve().parents[2]
TILES_DIR = ROOT / "assets" / "tiles"
SPRITES_DIR = ROOT / "assets" / "sprites"
TILES_DIR.mkdir(parents=True, exist_ok=True)
SPRITES_DIR.mkdir(parents=True, exist_ok=True)


def solid(name: str, fill: tuple[int, int, int], border: tuple[int, int, int]) -> None:
    """Einfarbige Kachel mit dunklem Rand — damit man das Grid im Test sieht."""
    img = Image.new("RGBA", (TILE, TILE), fill + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, TILE - 1, TILE - 1], outline=border + (255,), width=2)
    img.save(TILES_DIR / f"{name}.png")


def tree() -> None:
    """'Baum' = Grasboden + brauner Stamm + grüne Krone."""
    img = Image.new("RGBA", (TILE, TILE), (140, 200, 110, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, TILE - 1, TILE - 1], outline=(90, 140, 70, 255), width=2)
    # Stamm
    d.rectangle([28, 40, 36, 60], fill=(110, 70, 40, 255))
    # Krone
    d.ellipse([12, 8, 52, 44], fill=(50, 120, 60, 255), outline=(30, 80, 40, 255), width=2)
    img.save(TILES_DIR / "tree.png")


def rock() -> None:
    """'Fels' = grauer Klotz."""
    img = Image.new("RGBA", (TILE, TILE), (110, 110, 120, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, TILE - 1, TILE - 1], outline=(60, 60, 70, 255), width=2)
    d.polygon([(10, 50), (20, 20), (44, 16), (54, 48)], fill=(150, 150, 160, 255),
              outline=(70, 70, 80, 255))
    img.save(TILES_DIR / "rock.png")


def captain() -> None:
    """Captain-Platzhalter — roter Kreis mit schwarzer Umrandung, damit er auffällt."""
    img = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([12, 12, TILE - 12, TILE - 12], fill=(220, 60, 60, 255),
              outline=(30, 20, 20, 255), width=3)
    # Piratenhut-Andeutung
    d.polygon([(16, 20), (48, 20), (32, 8)], fill=(20, 20, 20, 255))
    img.save(SPRITES_DIR / "captain.png")


def main() -> None:
    solid("grass",  (140, 200, 110), (90, 140, 70))   # begehbar
    solid("sand",   (232, 210, 150), (170, 145, 90))  # begehbar
    solid("water",  (70, 130, 200),  (40, 80, 140))   # solid
    solid("path",   (200, 180, 130), (140, 120, 80))  # begehbar
    tree()   # solid
    rock()   # solid
    # v0.4: Dorfmaterialien
    solid("plank",  (200, 170, 120), (130, 100, 70))  # begehbar (Holzboden)
    solid("wall",   (150, 140, 130), (80, 70, 60))    # solid (Hauswand)
    solid("door",   (110, 70, 40),   (70, 40, 20))    # begehbar (Tür)
    solid("roof",   (170, 60, 60),   (110, 30, 30))   # solid (Dach)
    captain()
    print(f"OK — geschrieben nach {TILES_DIR} und {SPRITES_DIR}")


if __name__ == "__main__":
    main()
