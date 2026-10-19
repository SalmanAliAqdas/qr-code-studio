import pytest
from validators import ValidationError, contrast_ratio, validate_color, validate_email, validate_phone, validate_url

def test_url_rules():
    assert validate_url("https://example.com") == "https://example.com"
    with pytest.raises(ValidationError): validate_url("ftp://example.com")
    with pytest.raises(ValidationError): validate_url("https://user:pass@example.com")

def test_contact_validators():
    assert validate_email("me@example.com") == "me@example.com"
    assert validate_phone("+92 300 1234567") == "+923001234567"
    with pytest.raises(ValidationError): validate_email("bad")

def test_colors_and_contrast():
    assert validate_color("#abcdef") == "#ABCDEF"
    assert contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21)

