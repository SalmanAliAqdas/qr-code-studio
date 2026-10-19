"""Safe, in-memory QR image decoding."""

from __future__ import annotations

import cv2
import numpy as np

from validators import MAX_UPLOAD_BYTES, ValidationError


def scan_image(data: bytes) -> list[str]:
    if not data: raise ValidationError("The uploaded image is empty.")
    if len(data) > MAX_UPLOAD_BYTES: raise ValidationError("Image must be 10 MB or smaller.")
    array = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None: raise ValidationError("The upload is not a readable image.")
    detector = cv2.QRCodeDetector()
    try:
        ok, decoded, _, _ = detector.detectAndDecodeMulti(image)
        if ok:
            values = [value for value in decoded if value]
            if values: return values
    except cv2.error:
        pass
    value, _, _ = detector.detectAndDecode(image)
    return [value] if value else []


def identify_content(value: str) -> str:
    upper = value.upper()
    if value.startswith(("http://", "https://")): return "URL"
    if upper.startswith("WIFI:"): return "Wi-Fi credentials"
    if upper.startswith("BEGIN:VCARD"): return "Contact card"
    if upper.startswith("BEGIN:VCALENDAR"): return "Calendar event"
    if value.startswith("mailto:"): return "Email"
    if value.startswith("tel:"): return "Phone"
    if value.startswith("sms:"): return "SMS"
    return "Plain text"
