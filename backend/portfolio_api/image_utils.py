"""
Image optimization utilities for uploaded files.

Converts images to WebP format with intelligent quality selection
to minimize file size while preserving visual quality.
"""

import io
import os
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image


# Maximum dimensions for uploaded images (width, height)
MAX_DIMENSIONS = (1920, 1920)

# WebP quality — start high and reduce only if file is still too large
WEBP_INITIAL_QUALITY = 85
WEBP_MIN_QUALITY = 60
# Target max file size in bytes (500 KB)
TARGET_MAX_SIZE = 500 * 1024


def optimize_image(image_field, max_dimensions=MAX_DIMENSIONS):
    """
    Optimize an uploaded image:
      1. Open with Pillow
      2. Resize if larger than max_dimensions (preserving aspect ratio)
      3. Convert to WebP with adaptive quality
      4. Return a new ContentFile with .webp extension

    Returns (ContentFile, new_filename) or (None, None) if the file
    is not an image or cannot be processed.
    """
    if not image_field:
        return None, None

    try:
        image_field.seek(0)
        img = Image.open(image_field)
    except Exception:
        return None, None

    # Preserve RGBA for images with transparency, otherwise use RGB
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")

    # ---- Resize if exceeding max dimensions ----
    img.thumbnail(max_dimensions, Image.LANCZOS)

    # ---- Adaptive WebP compression ----
    quality = WEBP_INITIAL_QUALITY
    webp_bytes = _encode_webp(img, quality)

    # Iteratively lower quality until we hit the target or the floor
    while len(webp_bytes) > TARGET_MAX_SIZE and quality > WEBP_MIN_QUALITY:
        quality -= 5
        webp_bytes = _encode_webp(img, quality)

    # Build new filename
    original_name = Path(image_field.name).stem
    new_filename = f"{original_name}.webp"

    return ContentFile(webp_bytes), new_filename


def _encode_webp(img: Image.Image, quality: int) -> bytes:
    """Encode a PIL Image to WebP bytes."""
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=quality, method=6)  # method 6 = slowest but best compression
    return buffer.getvalue()


def delete_file(path):
    """Safely delete a file from disk if it exists."""
    if path and os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass
