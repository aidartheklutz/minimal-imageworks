from PIL import ImageFilter
from helpers import is_user_text, load_image, send_image, say

TITLE = "Размытие"
user_data = {}


def register_blur_handlers(bot):
    @bot.message_handler(commands=["blur"])
    def start_blur(message):
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
        say(bot, message.chat.id, TITLE, "Отправьте силу размытия, например: 5")

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "value"
        and is_user_text(m.text)
    )
    def get_value(message):
        uid = message.from_user.id
        try:
            radius = float(message.text.replace(",", ".").strip())
        except ValueError:
            say(bot, message.chat.id, TITLE, "Отправьте число, например: 5")
            return
        if radius <= 0 or radius > 50:
            say(bot, message.chat.id, TITLE, "Значение должно быть от 1 до 50")
            return
        result = user_data[uid]["image"].filter(ImageFilter.GaussianBlur(radius))
        send_image(bot, message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
