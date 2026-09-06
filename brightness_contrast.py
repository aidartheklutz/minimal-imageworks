from PIL import ImageEnhance
from helpers import is_user_text, load_image, send_image, say

TITLE = "Яркость и контраст"
user_data = {}


def register_brightness_contrast_handlers(bot):
    @bot.message_handler(commands=["brightness"])
    def start_bright(message):
        user_data[message.from_user.id] = {"waiting": "photo"}
        say(bot, message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting") == "photo",
    )
    def get_photo(message):
        uid = message.from_user.id
        user_data[uid]["image"] = load_image(bot, message)
        user_data[uid]["waiting"] = "values"
        say(
            bot,
            message.chat.id,
            TITLE,
            "Отправьте яркость и контраст от 0.1 до 3.0, например: 1.2 1.0\n1.0 — без изменений",
        )

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "values"
        and is_user_text(m.text)
    )
    def get_values(message):
        uid = message.from_user.id
        parts = message.text.replace(",", ".").split()
        if len(parts) != 2:
            say(bot, message.chat.id, TITLE, "Отправьте два числа, например: 1.2 1.0")
            return
        try:
            brightness = float(parts[0])
            contrast = float(parts[1])
        except ValueError:
            say(bot, message.chat.id, TITLE, "Отправьте два числа, например: 1.2 1.0")
            return
        if brightness < 0.1 or brightness > 3 or contrast < 0.1 or contrast > 3:
            say(bot, message.chat.id, TITLE, "Значения должны быть от 0.1 до 3.0")
            return
        img = user_data[uid]["image"].convert("RGB")
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        send_image(bot, message.chat.id, img, title=TITLE)
        user_data.pop(uid, None)
