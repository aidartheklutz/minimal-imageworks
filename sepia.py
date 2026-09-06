from PIL import ImageOps
from helpers import load_image, send_image, say

TITLE = "Сепия"
user_data = {}


def register_sepia_handlers(bot):
    @bot.message_handler(commands=["sepia"])
    def start_sepia(message):
        user_data[message.from_user.id] = {"waiting": "photo"}
        say(bot, message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting") == "photo",
    )
    def get_photo(message):
        uid = message.from_user.id
        img = load_image(bot, message).convert("RGB")
        gray = ImageOps.grayscale(img)
        result = ImageOps.colorize(gray, "#704214", "#EDC9AF")
        send_image(bot, message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
