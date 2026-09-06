from PIL import ImageOps
from telebot import types
from helpers import is_user_text, load_image, send_image, parse_hex, say

TITLE = "Рамка"
user_data = {}


def register_padding_handlers(bot):
    @bot.message_handler(commands=["padding"])
    def start_padding(message):
        user_data[message.from_user.id] = {"waiting": "photo"}
        say(bot, message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting") == "photo",
    )
    def get_photo(message):
        uid = message.from_user.id
        user_data[uid]["image"] = load_image(bot, message)
        user_data[uid]["waiting"] = "thickness"
        say(bot, message.chat.id, TITLE, "Отправьте толщину рамки в пикселях, например: 20")

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "thickness"
        and is_user_text(m.text)
    )
    def get_thickness(message):
        uid = message.from_user.id
        try:
            thickness = int(message.text.strip())
        except ValueError:
            say(bot, message.chat.id, TITLE, "Отправьте целое число, например: 20")
            return
        if thickness <= 0 or thickness > 500:
            say(bot, message.chat.id, TITLE, "Толщина должна быть от 1 до 500")
            return
        user_data[uid]["thickness"] = thickness
        user_data[uid]["waiting"] = "color"
        say(bot, message.chat.id, TITLE, "Отправьте HEX-цвет рамки, например: #000000")

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "color"
        and is_user_text(m.text)
    )
    def get_color(message):
        uid = message.from_user.id
        color = parse_hex(message.text)
        if color is None:
            say(bot, message.chat.id, TITLE, "Неверный HEX-код. Попробуйте ещё раз, например #000000")
            return
        img = user_data[uid]["image"]
        thickness = user_data[uid]["thickness"]
        if img.mode == "RGBA":
            fill = (color[0], color[1], color[2], 255)
        else:
            img = img.convert("RGB")
            fill = color
        result = ImageOps.expand(img, border=thickness, fill=fill)
        send_image(bot, message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
