"""
Push-button QR generator with centered logo and white rounded border.
- Size: 800x800
- Logo: 25% of QR width
- Event ID auto-generated from local time (America/Toronto): YYYYMMDD-HHMM
- URL signed via itsdangerous TimestampSigner for tamper protection
"""
import os
import pendulum
import qrcode
from typing import Tuple
from qrcode.constants import ERROR_CORRECT_H
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from PIL import Image, ImageDraw

# This was for 18 Nov. "https://docs.google.com/forms/d/e/1FAIpQLScApizmJXN9oPhs6veoFaWeUcNWNZ4ljrB8k6jWP6z_9SN9uA/viewform?usp=dialog"
# for nov 25 "https://docs.google.com/forms/d/e/1FAIpQLSelh_uJQf4C0Oq8XZJIRWCTZLcyHIL_wSTqdbr1XXvuVZq1kg/viewform?usp=publish-editor"
# for dec 2: "https://docs.google.com/forms/d/e/1FAIpQLScgbNYbVw7eNbw6LcREGgIVDHgdvkw5-KWsdDRrjoDdSmqYEA/viewform?usp=publish-editor"
# for dec 9: "https://docs.google.com/forms/d/e/1FAIpQLSdhofn_ub91wclVpfyIOKABKHY7JlWlvruCpDyRwqzPxvG8zw/viewform?usp=publish-editor"
# This is for dec 16 "https://docs.google.com/forms/d/e/1FAIpQLSfXRe3_elg9QNHDRMNy4SsLW6_fcuHeMcbGXTq3P6WW5VsX5w/viewform?usp=publish-editor"


# --------- CONFIG -----------
load_dotenv()
SECRET = os.getenv("SECRET_KEY", "PLACEHOLDER")


BASE_URL: str = ""
LOGO_PATH: str        = "static/Odyssey_Logo.png"

QR_SIZE: int          = 800
LOGO_SCALE: float     = 0.25
BORDER_FRAC: float    = 0.03
CORNER_RADIUS: int    = 18
VALID_FOR_HOURS: int  = 48
SIGN_SALT: str        = "attendance-token"
TIMEZONE: str         = "America/Toronto"
# ---------------------------


def _round_corners(img: Image.Image, radius: int) -> Image.Image:
    """ Round out the corners of an image."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    width, height= img.size
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=255)
    img.putalpha(mask)
    return img

def _rounded_rect(size: Tuple[int, int], radius: int, color=(255, 255, 255, 255)) -> Image.Image:
    """Create an RGBA rounded-rectangle image."""
    width, height = size
    rect = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=255)
    overlay = Image.new("RGBA", (width, height), color)
    rect.paste(overlay, (0, 0), mask)
    return rect

def generate_qr_code_with_image() -> str:
    """
    Generate a qr code with an image in the center.
    Image is semantically optional.
    Keep the logo less than a quarter of QR width for quality.
    """
    if not BASE_URL:
        raise RuntimeError("BASE_URL is empty.")
    
    now_local = pendulum.now(TIMEZONE)
    event_id = now_local.format("YYYYMMDD-HHmm")
    issued_at = pendulum.now("UTC")
    expires_at = issued_at.add(hours=VALID_FOR_HOURS)

    payload: dict = {
        "event_id": event_id,
        "issued_at": issued_at.to_iso8601_string(),
        "expires_at": expires_at.to_iso8601_string(),
    }
    serializer = URLSafeTimedSerializer(SECRET, salt=SIGN_SALT)
    token = serializer.dumps(payload)

    url = f"{BASE_URL}/?event={event_id}&sig={token}"

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    qr_img= qr_img.resize((QR_SIZE, QR_SIZE), Image.Resampling.LANCZOS)

    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        max_w = int(QR_SIZE * LOGO_SCALE)
        max_h = int(QR_SIZE * LOGO_SCALE)
        logo.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

        border_px = max(2, int(logo.width * BORDER_FRAC))
        bordered_size = (logo.width + 2 * border_px, logo.height + 2 * border_px)
        border_bg = _rounded_rect(bordered_size, radius=CORNER_RADIUS, color=(255, 255, 255, 255))
        logo = _round_corners(logo, CORNER_RADIUS)

        bx = (qr_img.width - border_bg.width) // 2
        by = (qr_img.height - border_bg.height) // 2
        qr_img.alpha_composite(border_bg, (bx, by))

        lx = bx + border_px
        ly = by + border_px
        qr_img.alpha_composite(logo, (lx, ly))

    out_png = f"QR_{event_id}.png"
    qr_img.save(out_png)

    print("Event:   ", event_id)
    print("Issued:  ", issued_at.to_iso8601_string())
    print("Expires: ", expires_at.to_iso8601_string(), f"(~{VALID_FOR_HOURS}h)")
    print("URL:     ", url)
    print("QR saved:", out_png)
    return out_png


if __name__ == "__main__":
    generate_qr_code_with_image()