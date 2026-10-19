from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse
import pytest
import payloads
from validators import ValidationError

def test_website_and_text():
    assert payloads.website("https://example.com/x") == "https://example.com/x"
    assert payloads.plain_text(" hello ") == "hello"

def test_wifi_escaping():
    assert payloads.wifi("Cafe;Net", r"a,b\c", "WPA", True) == r"WIFI:T:WPA;S:Cafe\;Net;P:a\,b\\c;H:true;;"

def test_whatsapp_email_phone_sms():
    assert payloads.whatsapp("+1 555 123 4567", "Hi there") == "https://wa.me/15551234567?text=Hi+there"
    assert parse_qs(urlparse(payloads.email("a@example.com", "Hi there", "A&B")).query) == {"subject":["Hi there"], "body":["A&B"]}
    assert payloads.phone("+1 (555) 123-4567") == "tel:+15551234567"
    assert payloads.sms("+15551234567", "hello world").endswith("?body=hello+world")

def test_vcard_escaping():
    value = payloads.vcard("Doe, Jane", "A;B")
    assert "FN:Doe\\, Jane" in value and "ORG:A\\;B" in value and value.endswith("\r\n")

def test_calendar():
    start = datetime(2026, 1, 1, 10); result = payloads.calendar_event("Meet, greet", start, start + timedelta(hours=1), "A;B")
    assert "BEGIN:VCALENDAR" in result and "SUMMARY:Meet\\, greet" in result and "DTEND:20260101T110000" in result

def test_invalid_inputs():
    with pytest.raises(ValidationError): payloads.plain_text(" ")
    with pytest.raises(ValidationError): payloads.website("javascript:alert(1)")
    with pytest.raises(ValidationError): payloads.wifi("network", "", "WPA")

