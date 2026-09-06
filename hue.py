from PIL import Image
from helpers import is_user_text, load_image, send_image, say

TITLE = "Оттенок"
user_data = {}


def shift_hue(img, degrees):
    img = img.convert("RGB")
    hsv = img.convert("HSV")
    h, s, v = hsv.split()
    shift = int(degrees / 360 * 255)
    h = h.point(lambda p: (p + shift) % 256)
    return Image.merge("HSV", (h, s, v)).convert("RGB")


def register_hue_handlers(bot):
    @bot.message_handler(commands=["hue"])
    def start_hue(message):
        user_data[message.from_user.id] = {"waiting": "photo"}
        say(bot, message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting") == "photo",
    )
    def get_photo(message):
        uid = message.from_user.id
        user_data[uid]["image"] = load_image(bot, message)
        user_data[uid]["waiting"] = "value"
        say(bot, message.chat.id, TITLE, "Отправьте сдвиг оттенка от -180 до 180, например: 30")

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "value"
        and is_user_text(m.text)
    )
    def get_value(message):
        uid = message.from_user.id
        try:
            degrees = float(message.text.replace(",", ".").strip())
        except ValueError:
            say(bot, message.chat.id, TITLE, "Отправьте число, например: 30")
            return
        if degrees < -180 or degrees > 180:
            say(bot, message.chat.id, TITLE, "Значение должно быть от -180 до 180")
            return
        result = shift_hue(user_data[uid]["image"], degrees)
        send_image(bot, message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
