from PIL import Image
from helpers import is_user_text, load_image, send_image, say

TITLE = "Пикселизация"
user_data = {}


def pixelate(img, block):
    w, h = img.size
    small_w = max(1, w // block)
    small_h = max(1, h // block)
    img = img.resize((small_w, small_h), Image.Resampling.NEAREST)
    return img.resize((w, h), Image.Resampling.NEAREST)


def register_pixelate_handlers(bot):
    @bot.message_handler(commands=["pixelate"])
    def start_pixelate(message):
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
        say(bot, message.chat.id, TITLE, "Отправьте размер пикселя, например: 16")

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "value"
        and is_user_text(m.text)
    )
    def get_value(message):
        uid = message.from_user.id
        try:
            block = int(message.text.strip())
        except ValueError:
            say(bot, message.chat.id, TITLE, "Отправьте целое число, например: 16")
            return
        if block < 2 or block > 100:
            say(bot, message.chat.id, TITLE, "Размер должен быть от 2 до 100")
            return
        result = pixelate(user_data[uid]["image"], block)
        send_image(bot, message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
