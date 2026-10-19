"""Input validation helpers for QR Code Studio."""

from __future__ import annotations

import re
from urllib.parse import urlparse

MAX_PAYLOAD_LENGTH = 4096
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


class ValidationError(ValueError):
    """Raised when user input cannot safely form a useful QR payload."""


def require_text(value: str, label: str = "Value", max_length: int = MAX_PAYLOAD_LENGTH) -> str:
    value = (value or "").strip()
    if not value:
        raise ValidationError(f"{label} is required.")
    if len(value) > max_length:
        raise ValidationError(f"{label} must be {max_length:,} characters or fewer.")
    return value


def validate_url(value: str, label: str = "URL") -> str:
    value = require_text(value, label, 2048)
    parsed = urlparse(value)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        raise ValidationError(f"{label} must be a complete http:// or https:// address.")
    if parsed.username or parsed.password:
        raise ValidationError(f"{label} must not contain embedded credentials.")
    return value


def validate_phone(value: str, label: str = "Phone number") -> str:
    value = require_text(value, label, 32)
    compact = re.sub(r"[\s().-]", "", value)
    if not re.fullmatch(r"\+?\d{5,15}", compact):
        raise ValidationError(f"{label} must contain 5–15 digits and may begin with +.")
    return compact


def validate_email(value: str) -> str:
    value = require_text(value, "Email address", 254)
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
        raise ValidationError("Enter a valid email address.")
    return value


def validate_color(value: str) -> str:
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value or ""):
        raise ValidationError("Color must use the #RRGGBB format.")
    return value.upper()


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(hex_color: str) -> float:
        channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        channels = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
        return .2126 * channels[0] + .7152 * channels[1] + .0722 * channels[2]
    a, b = luminance(validate_color(foreground)), luminance(validate_color(background))
    light, dark = max(a, b), min(a, b)
    return (light + .05) / (dark + .05)

