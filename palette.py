from PIL import Image, ImageDraw
from helpers import load_image, send_image, say

TITLE = "Палитра цветов"
user_data = {}


def get_dominant_colors(img, n=5):
    img = img.convert("RGB").resize((150, 150))
    quantized = img.quantize(colors=n)
    palette = quantized.getpalette()
    counts = quantized.getcolors()
    counts.sort(key=lambda item: item[0], reverse=True)
    colors = []
    for count, idx in counts[:n]:
        r, g, b = palette[idx * 3: idx * 3 + 3]
        colors.append((r, g, b))
    return colors


def make_palette_image(colors):
    n = len(colors)
    img = Image.new("RGB", (n * 80, 80))
    draw = ImageDraw.Draw(img)
    for i, color in enumerate(colors):
        draw.rectangle((i * 80, 0, (i + 1) * 80, 80), fill=color)
    return img


def register_palette_handlers(bot):
    @bot.message_handler(commands=["palette"])
    def start_palette(message):
        user_data[message.from_user.id] = {"waiting": "photo"}
        say(bot, message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting") == "photo",
    )
    def get_photo(message):
        uid = message.from_user.id
        img = load_image(bot, message)
        colors = get_dominant_colors(img)
        hex_list = []
        for r, g, b in colors:
            hex_list.append(f"#{r:02X}{g:02X}{b:02X}")
        text = "Основные цвета:\n" + "\n".join(hex_list)
        send_image(bot, message.chat.id, make_palette_image(colors), title=TITLE)
        say(bot, message.chat.id, TITLE, text)
        user_data.pop(uid, None)
