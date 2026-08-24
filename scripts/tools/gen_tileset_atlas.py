"""Kombiniert die einzelnen Kachel-PNGs zu einem 6x1-Atlas für Godot."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TILES = ROOT / "assets" / "tiles"
TILE = 64

# Reihenfolge = Atlas-Spalten-Index. Muss mit tileset.tres übereinstimmen!
ORDER = ["grass", "sand", "path", "water", "tree", "rock"]

atlas = Image.new("RGBA", (TILE * len(ORDER), TILE), (0, 0, 0, 0))
for i, name in enumerate(ORDER):
    img = Image.open(TILES / f"{name}.png").convert("RGBA")
    atlas.paste(img, (i * TILE, 0))

out = TILES / "atlas.png"
atlas.save(out)
print(f"Atlas geschrieben: {out}  Reihenfolge: {ORDER}")
