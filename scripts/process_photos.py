#!/usr/bin/env python3
"""Make web-safe copies of photos for the site.

Drop originals into raw-photos/ (gitignored), then run:
    python3 scripts/process_photos.py            # all photos in raw-photos/
    python3 scripts/process_photos.py foo.jpg    # just these

Each photo is rotated upright, resized to at most 2400px on its long side,
and saved to assets/images/ with all EXIF (GPS, camera, timestamps) removed.
A 900px thumbnail also goes to assets/images/thumbs/ for the photos page.
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw-photos"
OUT = ROOT / "assets" / "images"
THUMBS = OUT / "thumbs"
MAX_SIDE = 2400
THUMB_SIDE = 900


def save_clean(im: Image.Image, dst: Path, side: int) -> None:
    im = im.copy()
    im.thumbnail((side, side))
    # No exif= argument, so Pillow writes no metadata.
    im.save(dst, quality=82, optimize=True, progressive=True)
    status = "EXIF LEAKED!" if Image.open(dst).getexif() else "clean"
    print(f"  {dst.relative_to(ROOT)}  {im.size[0]}x{im.size[1]}  "
          f"{dst.stat().st_size // 1024} KB  {status}")


def process(src: Path) -> None:
    print(src.name)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    THUMBS.mkdir(exist_ok=True)
    save_clean(im, OUT / (src.stem + ".jpg"), MAX_SIDE)
    save_clean(im, THUMBS / (src.stem + ".jpg"), THUMB_SIDE)


def main() -> None:
    names = sys.argv[1:]
    srcs = [RAW / n for n in names] if names else sorted(
        p for p in RAW.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".heic", ".webp"})
    for src in srcs:
        process(src)


if __name__ == "__main__":
    main()
