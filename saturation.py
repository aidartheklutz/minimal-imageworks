from PIL import ImageEnhance
from helpers import is_user_text, load_image, send_image, say

TITLE = "Насыщенность"
user_data = {}


def register_saturation_handlers(bot):
    @bot.message_handler(commands=["saturation"])
    def start_sat(message):
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
        say(
            bot,
            message.chat.id,
            TITLE,
            "Отправьте насыщенность от 0 до 3.0, например: 1.5\n1.0 — без изменений, 0 — без цвета",
        )

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "value"
        and is_user_text(m.text)
    )
    def get_value(message):
        uid = message.from_user.id
        try:
            value = float(message.text.replace(",", ".").strip())
        except ValueError:
            say(bot, message.chat.id, TITLE, "Отправьте число, например: 1.5")
            return
        if value < 0 or value > 3:
            say(bot, message.chat.id, TITLE, "Значение должно быть от 0 до 3.0")
            return
        img = user_data[uid]["image"].convert("RGB")
        result = ImageEnhance.Color(img).enhance(value)
        send_image(bot, message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
