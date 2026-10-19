from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import pytest
from qr_generator import generate_png, generate_svg
from validators import ValidationError

def test_png_output_and_round_trip():
    payload = "https://example.com/test"
    data = generate_png(payload)
    assert data.startswith(b"\x89PNG")
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(image)
    assert decoded == payload

def test_plain_text_and_svg():
    assert generate_png("hello").startswith(b"\x89PNG")
    svg = generate_svg("hello")
    assert b"<svg" in svg and b"<path" in svg

def test_logo_forces_valid_png_and_input_checks():
    logo = BytesIO(); Image.new("RGB", (300, 100), "red").save(logo, "PNG")
    assert generate_png("logo payload", logo=logo.getvalue(), error_correction="Low").startswith(b"\x89PNG")
    with pytest.raises(ValidationError): generate_png("")
    with pytest.raises(ValidationError): generate_png("x", border=1)

