"""In-memory PNG and SVG QR generation."""

from __future__ import annotations

from io import BytesIO
from typing import BinaryIO

import qrcode
import qrcode.image.svg
from PIL import Image

from validators import ValidationError, contrast_ratio, require_text, validate_color

ERROR_LEVELS = {"Low": qrcode.constants.ERROR_CORRECT_L, "Medium": qrcode.constants.ERROR_CORRECT_M,
                "Quartile": qrcode.constants.ERROR_CORRECT_Q, "High": qrcode.constants.ERROR_CORRECT_H}


def generate_png(payload: str, foreground: str = "#111827", background: str = "#FFFFFF", size: int = 720,
                 border: int = 4, error_correction: str = "Medium", logo: BinaryIO | bytes | None = None) -> bytes:
    payload = require_text(payload, "Payload")
    validate_color(foreground); validate_color(background)
    if not 240 <= size <= 1600: raise ValidationError("Image size must be between 240 and 1,600 pixels.")
    if not 4 <= border <= 12: raise ValidationError("Quiet zone must be between 4 and 12 modules.")
    if error_correction not in ERROR_LEVELS: raise ValidationError("Unknown error correction level.")
    correction = qrcode.constants.ERROR_CORRECT_H if logo else ERROR_LEVELS[error_correction]
    qr = qrcode.QRCode(version=None, error_correction=correction, box_size=10, border=border)
    qr.add_data(payload); qr.make(fit=True)
    image = qr.make_image(fill_color=foreground, back_color=background).convert("RGB")
    image = image.resize((size, size), Image.Resampling.NEAREST)
    if logo:
        try:
            source = BytesIO(logo) if isinstance(logo, bytes) else logo
            mark = Image.open(source); mark.load(); mark = mark.convert("RGBA")
        except Exception as exc:
            raise ValidationError("The logo is not a valid image.") from exc
        limit = max(1, size // 5)
        mark.thumbnail((limit, limit), Image.Resampling.LANCZOS)
        x, y = (size - mark.width) // 2, (size - mark.height) // 2
        pad = max(4, size // 100)
        canvas = Image.new("RGBA", (mark.width + 2 * pad, mark.height + 2 * pad), background)
        canvas.alpha_composite(mark, (pad, pad)); image.paste(canvas, (x - pad, y - pad), canvas)
    output = BytesIO(); image.save(output, format="PNG", optimize=True)
    return output.getvalue()


def generate_svg(payload: str, foreground: str = "#111827", background: str = "#FFFFFF", border: int = 4,
                 error_correction: str = "Medium") -> bytes:
    payload = require_text(payload, "Payload"); validate_color(foreground); validate_color(background)
    if not 4 <= border <= 12: raise ValidationError("Quiet zone must be between 4 and 12 modules.")
    if error_correction not in ERROR_LEVELS: raise ValidationError("Unknown error correction level.")
    qr = qrcode.QRCode(error_correction=ERROR_LEVELS[error_correction], box_size=10, border=border,
                       image_factory=qrcode.image.svg.SvgPathFillImage)
    qr.add_data(payload); qr.make(fit=True)
    out = BytesIO(); qr.make_image(fill_color=foreground, back_color=background).save(out)
    return out.getvalue()


def has_good_contrast(foreground: str, background: str) -> bool:
    return contrast_ratio(foreground, background) >= 4.5

