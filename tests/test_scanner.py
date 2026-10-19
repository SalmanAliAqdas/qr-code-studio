from io import BytesIO
from PIL import Image
import pytest
from qr_generator import generate_png
from qr_scanner import identify_content, scan_image
from validators import ValidationError

def test_uploaded_image_processing():
    assert scan_image(generate_png("WIFI:T:WPA;S:test;P:pass;;")) == ["WIFI:T:WPA;S:test;P:pass;;"]
    assert identify_content("https://example.com") == "URL"
    assert identify_content("BEGIN:VCARD\nEND:VCARD") == "Contact card"

def test_missing_qr():
    out = BytesIO(); Image.new("RGB", (300, 300), "white").save(out, "PNG")
    assert scan_image(out.getvalue()) == []

def test_invalid_image():
    with pytest.raises(ValidationError): scan_image(b"not an image")
    with pytest.raises(ValidationError): scan_image(b"")

