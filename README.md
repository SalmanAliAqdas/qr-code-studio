# QR Code Studio

QR Code Studio is a polished, privacy-conscious Streamlit application for creating, customizing, downloading, and scanning static QR codes. It works locally without accounts, API keys, external databases, or third-party QR services.

## Features

- Generate QR codes for websites, text, Wi-Fi, WhatsApp, email, phone calls, SMS, vCards, map locations, calendar events, document links, and payment links
- Customize foreground/background colors, PNG size, quiet zone, error correction, and an optional center logo
- Download generated codes as PNG or SVG, entirely from memory
- Decode one or multiple codes from PNG, JPG, JPEG, or WEBP images with OpenCV
- Classify decoded content without visiting links or executing data
- Responsive navigation with dedicated Generate, Scan, Guide, and About sections
- Input validation, upload limits, contrast warnings, and privacy-focused behavior

## Screenshots

Add screenshots of the Generate and Scan screens here after running the application locally.

## Technology stack

- Python 3.11+
- Streamlit
- `qrcode` and Pillow
- OpenCV Headless and NumPy
- pytest

## Installation and local usage

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Supported QR formats

| Format | Encoded content |
|---|---|
| Website | Valid HTTP or HTTPS URL |
| Plain text | UTF-8 text |
| Wi-Fi | Standard `WIFI:` payload with WPA, WEP, or open security |
| WhatsApp | Encoded `wa.me` link |
| Email | `mailto:` URI with optional subject and body |
| Phone / SMS | `tel:` or `sms:` URI |
| Contact | vCard 3.0 |
| Location | Google Maps search URL |
| Calendar | iCalendar event payload |
| Document / payment | User-provided HTTPS or HTTP link |

Calendar, Wi-Fi, SMS, and payment behavior can vary between scanner apps and operating systems. Payment codes are ordinary user-supplied links, not provider-specific banking QR integrations.

## Scanning

Open **Scan QR**, upload a supported image of up to 10 MB, and review the decoded text. The application attempts OpenCV multi-code detection first and falls back to single-code detection. It never automatically opens decoded links. Treat every scanned result as untrusted, verify domains carefully, and avoid entering credentials on unexpected pages.

## Project structure

```text
.
├── app.py                 # Streamlit interface
├── payloads.py            # Payload builders and escaping
├── qr_generator.py        # In-memory PNG and SVG generation
├── qr_scanner.py          # OpenCV decoding and classification
├── validators.py          # Validation and contrast checks
├── requirements.txt
├── .streamlit/config.toml
└── tests/
    ├── test_generator.py
    ├── test_payloads.py
    ├── test_scanner.py
    └── test_validators.py
```

## Testing

The tests require no network access or credentials.

```bash
python -m pytest -q
```

They cover payload construction and escaping, validation, PNG/SVG output, logo behavior, QR encode/decode round trips, invalid images, and images with no QR code.

## Streamlit Community Cloud deployment

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create an app from the repository.
3. Select `app.py` as the entrypoint.
4. Deploy. No secrets or additional system packages are required.

The app uses the headless OpenCV package and keeps image sizes bounded for normal cloud resource limits.

## Security and privacy

- Payloads and uploads are processed in memory and are not intentionally persisted or logged.
- No data is sent to external APIs by the application.
- File extensions, decoded image validity, input lengths, and URLs are validated.
- Uploaded content and decoded text are never executed.
- Wi-Fi payload details are hidden from the interface because they can contain passwords.
- A hosting platform necessarily processes requests and uploads during normal application operation; consult the host's privacy policy when deploying publicly.

## Limitations

- Version 1.0 does not include webcam scanning, dynamic redirects, analytics, user accounts, history, or cloud storage.
- Static QR content cannot be changed after printing. Editable dynamic codes require a separately hosted redirect service.
- Decorated, low-contrast, damaged, dense, or very small QR codes may not scan reliably. Always test important codes on multiple devices before distribution.
- OpenCV's ability to decode multiple or highly stylized codes depends on image quality.
- SVG export remains a clean vector QR and does not embed an uploaded raster logo.

## Future enhancements

- Optional browser-camera scanning with explicit consent
- Batch generation and download
- More structured payload standards and localization
- Automated accessibility checks and print-layout templates
