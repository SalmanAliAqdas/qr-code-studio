"""Standards-based payload builders."""

from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import quote, urlencode

from validators import ValidationError, require_text, validate_email, validate_phone, validate_url


def plain_text(text: str) -> str:
    return require_text(text, "Text")


def website(url: str) -> str:
    return validate_url(url)


def _wifi_escape(value: str) -> str:
    return "".join("\\" + c if c in "\\;,\"" else c for c in value)


def wifi(ssid: str, password: str = "", security: str = "WPA", hidden: bool = False) -> str:
    ssid = require_text(ssid, "Network name", 64)
    security = security.upper()
    if security not in {"WPA", "WEP", "NOPASS"}:
        raise ValidationError("Unsupported Wi-Fi security type.")
    if security != "NOPASS" and not password:
        raise ValidationError("Password is required for a secured network.")
    return f"WIFI:T:{security};S:{_wifi_escape(ssid)};P:{_wifi_escape(password)};H:{str(hidden).lower()};;"


def whatsapp(phone: str, message: str = "") -> str:
    number = validate_phone(phone).lstrip("+")
    return f"https://wa.me/{number}" + (f"?{urlencode({'text': message})}" if message else "")


def email(recipient: str, subject: str = "", body: str = "") -> str:
    recipient = validate_email(recipient)
    query = urlencode({k: v for k, v in {"subject": subject, "body": body}.items() if v})
    return f"mailto:{recipient}" + (f"?{query}" if query else "")


def phone(number: str) -> str:
    return f"tel:{validate_phone(number)}"


def sms(number: str, message: str = "") -> str:
    base = f"sms:{validate_phone(number)}"
    return base + (f"?{urlencode({'body': message})}" if message else "")


def _vcard_escape(value: str) -> str:
    return (value or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def vcard(full_name: str, organization: str = "", number: str = "", address: str = "", url: str = "") -> str:
    full_name = require_text(full_name, "Full name", 120)
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{_vcard_escape(full_name)}"]
    if organization: lines.append(f"ORG:{_vcard_escape(organization)}")
    if number: lines.append(f"TEL:{validate_phone(number)}")
    if address: lines.append(f"EMAIL:{validate_email(address)}")
    if url: lines.append(f"URL:{validate_url(url)}")
    lines.extend(["END:VCARD", ""])
    return "\r\n".join(lines)


def location(query: str) -> str:
    return "https://www.google.com/maps/search/?" + urlencode({"api": "1", "query": require_text(query, "Location", 300)})


def _ical_escape(value: str) -> str:
    return (value or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def calendar_event(title: str, start: datetime, end: datetime, event_location: str = "", description: str = "") -> str:
    title = require_text(title, "Event title", 200)
    if end <= start:
        raise ValidationError("End time must be after start time.")
    def stamp(dt: datetime) -> str:
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt.strftime("%Y%m%dT%H%M%SZ")
        return dt.strftime("%Y%m%dT%H%M%S")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//QR Code Studio//EN", "BEGIN:VEVENT",
             f"DTSTART:{stamp(start)}", f"DTEND:{stamp(end)}", f"SUMMARY:{_ical_escape(title)}"]
    if event_location: lines.append(f"LOCATION:{_ical_escape(event_location)}")
    if description: lines.append(f"DESCRIPTION:{_ical_escape(description)}")
    lines.extend(["END:VEVENT", "END:VCALENDAR", ""])
    return "\r\n".join(lines)


def document_url(url: str) -> str:
    return validate_url(url, "Document URL")


def payment_url(url: str) -> str:
    return validate_url(url, "Payment URL")

