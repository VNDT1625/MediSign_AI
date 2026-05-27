"""Crop docs/background.png to its visible bounding box and emit
optimized variants under apps/web_next/public/."""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "background.png"
OUT_DIR = ROOT / "apps" / "web_next" / "public"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def find_bbox(im: Image.Image) -> tuple[int, int, int, int]:
    """Bounding box of non-white pixels (alpha or RGB).

    Treat anything where (alpha < 250) OR (RGB differs from white by > 6)
    as foreground content. Robust against off-white backgrounds and
    semi-transparent edges.
    """
    rgba = im.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    if pixels is None:
        return (0, 0, width, height)

    min_x = width
    min_y = height
    max_x = -1
    max_y = -1

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            is_bg = a < 5 or (r > 248 and g > 248 and b > 248 and a > 240)
            if is_bg:
                continue
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y

    if max_x < 0:
        return (0, 0, width, height)
    # Pad by 8px
    pad = 8
    return (
        max(0, min_x - pad),
        max(0, min_y - pad),
        min(width, max_x + 1 + pad),
        min(height, max_y + 1 + pad),
    )


def main() -> None:
    im = Image.open(SRC).convert("RGBA")
    bbox = find_bbox(im)
    print(f"src={im.size} bbox={bbox}")
    cropped = im.crop(bbox)
    print(f"cropped={cropped.size}")

    # Save full-quality cropped PNG
    cropped.save(OUT_DIR / "logo.png", optimize=True)

    # Webp variant (better compression for large brand mark)
    cropped.save(OUT_DIR / "logo.webp", quality=90, method=6)

    # Tiny favicon-style version (256px)
    h = 256
    w = int(round(cropped.size[0] * (h / cropped.size[1])))
    small = cropped.resize((w, h), Image.LANCZOS)
    small.save(OUT_DIR / "logo-256.png", optimize=True)

    print(f"Wrote {OUT_DIR/'logo.png'}, {OUT_DIR/'logo.webp'}, {OUT_DIR/'logo-256.png'}")


if __name__ == "__main__":
    main()
