from helpers import is_user_text, load_image, send_image, parse_hex, say
from palette import format_palette_text

TITLE = "Замена цвета"
user_data = {}


def replace_color(img, src, dst, tolerance):
    img = img.convert("RGBA")
    pixels = img.load()
    w, h = img.size
    sr, sg, sb = src
    dr, dg, db = dst
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if abs(r - sr) <= tolerance and abs(g - sg) <= tolerance and abs(b - sb) <= tolerance:
                pixels[x, y] = (dr, dg, db, a)
    return img


def register_replace_color_handlers(bot):
    @bot.message_handler(commands=["replacecolor"])
    def start_replace(message):
        user_data[message.from_user.id] = {"waiting": "photo"}
        say(bot, message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting") == "photo",
    )
    def get_photo(message):
        uid = message.from_user.id
        img = load_image(bot, message)
        user_data[uid]["image"] = img
        user_data[uid]["waiting"] = "old_color"
        text = format_palette_text(img) + "\n\nОтправьте цвет, который нужно заменить, например: #FF0000"
        say(bot, message.chat.id, TITLE, text)

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "old_color"
        and is_user_text(m.text)
    )
    def get_old_color(message):
        uid = message.from_user.id
        color = parse_hex(message.text)
        if color is None:
            say(bot, message.chat.id, TITLE, "Неверный HEX-код. Попробуйте ещё раз, например #FF0000")
            return
        user_data[uid]["old_color"] = color
        user_data[uid]["waiting"] = "new_color"
        say(bot, message.chat.id, TITLE, "Отправьте новый цвет, например: #00FF00")

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "new_color"
        and is_user_text(m.text)
    )
    def get_new_color(message):
        uid = message.from_user.id
        color = parse_hex(message.text)
        if color is None:
            say(bot, message.chat.id, TITLE, "Неверный HEX-код. Попробуйте ещё раз, например #00FF00")
            return
        user_data[uid]["new_color"] = color
        user_data[uid]["waiting"] = "tolerance"
        say(bot, message.chat.id, TITLE, "Отправьте допуск от 0 до 100, например: 30")

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "tolerance"
        and is_user_text(m.text)
    )
    def get_tolerance(message):
        uid = message.from_user.id
        try:
            tolerance = int(message.text.strip())
        except ValueError:
            say(bot, message.chat.id, TITLE, "Отправьте целое число, например: 30")
            return
        if tolerance < 0 or tolerance > 100:
            say(bot, message.chat.id, TITLE, "Допуск должен быть от 0 до 100")
            return
        result = replace_color(
            user_data[uid]["image"],
            user_data[uid]["old_color"],
            user_data[uid]["new_color"],
            tolerance,
        )
        send_image(bot, message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
