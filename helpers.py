from io import BytesIO
from PIL import Image


def is_user_text(text):
    return bool(text) and not text.startswith("/")


def titled(name, text):
    return f"<b>{name}</b>\n\n{text}"


def say(bot, chat_id, title, text, reply_markup=None):
    bot.send_message(
        chat_id,
        titled(title, text),
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


def load_image(bot, message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    data = bot.download_file(file_info.file_path)
    img = Image.open(BytesIO(data))
    if img.mode == "P":
        img = img.convert("RGBA")
    elif img.mode == "LA":
        img = img.convert("RGBA")
    elif img.mode == "CMYK":
        img = img.convert("RGB")
    return img


def send_image(bot, chat_id, img, title=None, caption=None):
    buf = BytesIO()
    extra = {}
    if title and caption:
        extra["caption"] = titled(title, caption)
        extra["parse_mode"] = "HTML"
    elif title:
        extra["caption"] = f"<b>{title}</b>"
        extra["parse_mode"] = "HTML"
    elif caption:
        extra["caption"] = caption

    if img.mode == "RGBA":
        img.save(buf, format="PNG")
        buf.seek(0)
        buf.name = "result.png"
        bot.send_document(chat_id, buf, **extra)
    else:
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=95)
        buf.seek(0)
        buf.name = "result.jpg"
        bot.send_photo(chat_id, buf, **extra)


def parse_hex(text):
    text = text.strip()
    if text.startswith("#"):
        text = text[1:]
    if len(text) != 6:
        return None
    try:
        r = int(text[0:2], 16)
        g = int(text[2:4], 16)
        b = int(text[4:6], 16)
        return (r, g, b)
    except ValueError:
        return None


def parse_two_ints(text):
    parts = text.replace("x", " ").replace("х", " ").replace(",", " ").replace("×", " ").split()
    if len(parts) != 2:
        return None
    try:
        a = int(parts[0])
        b = int(parts[1])
    except ValueError:
        return None
    if a <= 0 or b <= 0:
        return None
    return a, b
