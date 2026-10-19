"""Streamlit entrypoint for QR Code Studio."""

from datetime import datetime, timedelta
from io import BytesIO
import re

import streamlit as st
from PIL import Image

import payloads
from qr_generator import ERROR_LEVELS, generate_png, generate_svg, has_good_contrast
from qr_scanner import identify_content, scan_image
from validators import MAX_UPLOAD_BYTES, ValidationError

st.set_page_config(page_title="QR Code Studio", page_icon="▦", layout="wide")
st.markdown("""<style>
.block-container{padding-top:1.4rem;max-width:1180px}.hero{padding:.8rem 0 1rem}.hero h1{font-size:2rem;margin:0}.hero p{opacity:.72;margin:.25rem 0 0}
[data-testid="stSidebar"]{border-right:1px solid rgba(128,128,128,.18)}
</style><div class="hero"><h1>▦ QR Code Studio</h1><p>Create, customize, download, and safely inspect QR codes—entirely in memory.</p></div>""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigate", ["Generate QR", "Scan QR", "QR Guide / Help", "About"])
st.sidebar.caption("No accounts, APIs, tracking, or permanent storage.")


def make_payload(kind: str) -> str:
    if kind == "Website URL": return payloads.website(st.text_input("Website URL", "https://example.com"))
    if kind == "Plain text": return payloads.plain_text(st.text_area("Text", "Hello from QR Code Studio", max_chars=4096))
    if kind == "Wi-Fi credentials":
        ssid = st.text_input("Network name", max_chars=64); password = st.text_input("Password", type="password", max_chars=128)
        security = st.selectbox("Security", ["WPA", "WEP", "NOPASS"], format_func=lambda x: {"WPA":"WPA / WPA2 / WPA3 compatible", "WEP":"WEP", "NOPASS":"Open network"}[x])
        hidden = st.checkbox("Hidden network")
        return payloads.wifi(ssid, password, security, hidden)
    if kind == "WhatsApp message": return payloads.whatsapp(st.text_input("International phone number", "+15551234567"), st.text_area("Prefilled message (optional)", max_chars=1000))
    if kind == "Email": return payloads.email(st.text_input("Recipient", "hello@example.com"), st.text_input("Subject (optional)", max_chars=200), st.text_area("Body (optional)", max_chars=2000))
    if kind == "Phone call": return payloads.phone(st.text_input("Telephone number", "+15551234567"))
    if kind == "SMS": return payloads.sms(st.text_input("Phone number", "+15551234567"), st.text_area("Message (optional)", max_chars=1000))
    if kind == "Contact card (vCard)":
        name = st.text_input("Full name", max_chars=120); org = st.text_input("Organization", max_chars=120)
        phone = st.text_input("Phone", max_chars=32); email = st.text_input("Email", max_chars=254); url = st.text_input("Website", max_chars=2048)
        return payloads.vcard(name, org, phone, email, url)
    if kind == "Google Maps / location": return payloads.location(st.text_input("Address, place, or coordinates", "Central Park, New York"))
    if kind == "Calendar event":
        title = st.text_input("Event title", max_chars=200); c1, c2 = st.columns(2)
        start = c1.datetime_input("Starts", datetime.now().replace(second=0, microsecond=0) + timedelta(hours=1))
        end = c2.datetime_input("Ends", datetime.now().replace(second=0, microsecond=0) + timedelta(hours=2))
        place = st.text_input("Location", max_chars=300); desc = st.text_area("Description", max_chars=1000)
        st.caption("Calendar import support varies by scanner and device; the code contains a standard iCalendar event.")
        return payloads.calendar_event(title, start, end, place, desc)
    if kind == "PDF or document URL":
        st.info("The QR code stores a public link, not the document itself.")
        return payloads.document_url(st.text_input("Public document URL", "https://example.com/document.pdf"))
    st.warning("Use only a trusted payment link. Banking credentials are never requested or stored. Compatibility depends on the payment provider.")
    return payloads.payment_url(st.text_input("Payment URL", "https://example.com/pay"))


if page == "Generate QR":
    left, right = st.columns([1.25, 1], gap="large")
    with left:
        kind = st.selectbox("QR code type", ["Website URL", "Plain text", "Wi-Fi credentials", "WhatsApp message", "Email", "Phone call", "SMS", "Contact card (vCard)", "Google Maps / location", "Calendar event", "PDF or document URL", "Payment URL"])
        try: payload = make_payload(kind)
        except ValidationError as exc: payload = ""; st.info(str(exc))
        with st.expander("Customize"):
            a, b = st.columns(2); foreground = a.color_picker("Foreground", "#111827"); background = b.color_picker("Background", "#FFFFFF")
            size = st.slider("PNG image size", 240, 1600, 720, 40); border = st.slider("Quiet zone (modules)", 4, 12, 4)
            level = st.selectbox("Error correction", list(ERROR_LEVELS), index=1)
            logo_file = st.file_uploader("Optional logo (PNG/JPG/WEBP, max 2 MB)", type=["png", "jpg", "jpeg", "webp"])
            logo = logo_file.getvalue() if logo_file else None
            if logo and len(logo) > 2 * 1024 * 1024: st.error("Logo must be 2 MB or smaller."); logo = None
            if logo: st.caption("A logo uses high error correction and is limited to 20% of the code. Always test decorated codes.")
        if not has_good_contrast(foreground, background): st.warning("Low color contrast may make this QR code difficult to scan.")
    with right:
        st.subheader("Preview")
        if payload:
            try:
                png = generate_png(payload, foreground, background, size, border, level, logo)
                st.image(png, width=min(size, 460))
                safe_name = re.sub(r"[^a-z0-9]+", "-", kind.lower()).strip("-")
                verified = False
                try:
                    verified = payload in scan_image(png)
                except ValidationError:
                    pass
                if not verified:
                    st.warning("Automatic verification could not decode this design. Test it on a device or use the plain high-contrast version below.")
                    plain_png = generate_png(payload, "#000000", "#FFFFFF", size, max(4, border), "High")
                    st.download_button("Download plain verified-style PNG", plain_png, f"{safe_name}-plain.png", "image/png", use_container_width=True)
                d1, d2 = st.columns(2)
                d1.download_button("Download PNG", png, f"{safe_name}.png", "image/png", use_container_width=True)
                svg = generate_svg(payload, foreground, background, border, "High" if logo else level)
                d2.download_button("Download SVG", svg, f"{safe_name}.svg", "image/svg+xml", use_container_width=True)
                if logo: st.caption("SVG download does not include the raster logo; it uses high error correction for customization after export.")
                with st.expander("Payload details"):
                    st.write(f"Type: **{kind}**")
                    if kind == "Wi-Fi credentials": st.caption("Payload hidden because it may contain a password.")
                    else: st.code(payload, language=None)
            except (ValidationError, ValueError) as exc: st.error(str(exc))
        else: st.caption("Complete the required fields to create a preview.")

elif page == "Scan QR":
    st.subheader("Scan QR from an image")
    st.warning("QR content is untrusted. This app never opens links or executes decoded content.")
    upload = st.file_uploader("Upload PNG, JPG, JPEG, or WEBP (max 10 MB)", type=["png", "jpg", "jpeg", "webp"])
    if upload:
        data = upload.getvalue()
        if len(data) > MAX_UPLOAD_BYTES: st.error("Image must be 10 MB or smaller.")
        else:
            try:
                image = Image.open(BytesIO(data)); image.verify(); st.image(data, caption="Uploaded image", width=520)
                results = scan_image(data)
                if not results: st.warning("No QR code was detected. Try a sharper, larger, well-lit image with the full quiet zone visible.")
                for index, value in enumerate(results, 1):
                    st.success(f"QR code {index}: {identify_content(value)}")
                    st.text_area("Decoded text (select and copy manually)", value, key=f"decoded-{index}", height=130)
            except (ValidationError, OSError) as exc: st.error(str(exc))

elif page == "QR Guide / Help":
    st.subheader("QR code essentials")
    st.markdown("""
**What is a QR code?** A two-dimensional barcode that stores text. Phones commonly interpret that text as a link, contact, Wi-Fi setup, or another action.

**Static vs dynamic.** This app creates static codes: the content is embedded and cannot be edited after printing. A dynamic code stores a redirect URL managed by a separate online service; redirect management is not included here.

**How scanning works.** A camera locates the three corner markers, corrects perspective, and decodes the module grid. Error correction can recover some obscured modules, but it is not a guarantee.

**Quiet zone and size.** Keep at least four blank modules around the code. Print sharply, avoid stretching, and use roughly 2.5 cm / 1 inch or larger for simple codes; dense payloads need more space.

**Safe scanning.** Check a link's domain before opening it. QR codes may lead to phishing or malware. Never enter credentials on an unexpected site.

**Why scans fail.** Low contrast, blur, glare, tiny printing, excessive data, damaged corners, cropped quiet zones, and oversized logos are common causes. Use dark modules on a light background and test on several devices.
""")
else:
    st.subheader("About")
    st.write("QR Code Studio is a privacy-conscious, open-source Streamlit application for generating and decoding static QR codes.")
    st.markdown("Data is processed in application memory and is not sent to external APIs or intentionally persisted. Your hosting platform still processes requests and uploads during normal operation.")
    st.caption("Version 1.0 · Python 3.11+ · Streamlit · qrcode · Pillow · OpenCV")

