from io import BytesIO
from urllib.parse import urlparse
import hashlib
import re

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

PHONE_REGEX = re.compile(r"^(8|\+7)\d{10}$")
AVATAR_SIZE = 150
AVATAR_FONT_SIZE = 64
AVATAR_VERTICAL_OFFSET = 4
AVATAR_COLORS = ("#E8EEF7", "#EFEAF8", "#EAF5EF", "#F7EFE8", "#F1F1F4")
AVATAR_TEXT_COLOR = "#111111"
GITHUB_DOMAIN = "github.com"


def normalize_phone(phone):
    normalized_phone = (phone or "").replace(" ", "").replace("-", "")
    normalized_phone = normalized_phone.replace("(", "").replace(")", "")
    if normalized_phone.startswith("8") and len(normalized_phone) == 11:
        return "+7" + normalized_phone[1:]
    return normalized_phone


def validate_phone(phone):
    normalized_phone = normalize_phone(phone)

    if not normalized_phone:
        return None

    if not PHONE_REGEX.match(normalized_phone):
        raise ValidationError("Укажите телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")

    return normalized_phone


def validate_github_url(url):
    if not url:
        return

    hostname = urlparse(url).hostname or ""
    if hostname.lower() != GITHUB_DOMAIN:
        raise ValidationError("Ссылка должна вести на GitHub.")


def make_default_avatar(name, email):
    first_letter = (name or email or "?")[0].upper()
    digest = hashlib.md5((email or first_letter).encode()).hexdigest()
    background_color = AVATAR_COLORS[int(digest[0], 16) % len(AVATAR_COLORS)]

    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), background_color)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", AVATAR_FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), first_letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (AVATAR_SIZE - text_width) / 2
    y = (AVATAR_SIZE - text_height) / 2 - AVATAR_VERTICAL_OFFSET
    draw.text((x, y), first_letter, fill=AVATAR_TEXT_COLOR, font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())