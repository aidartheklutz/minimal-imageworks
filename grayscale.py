from helpers import load_image, send_image, say

TITLE = "Чёрно-белое"
user_data = {}


def register_grayscale_handlers(bot):
    @bot.message_handler(commands=["grayscale"])
    def start_grayscale(message):
        user_data[message.from_user.id] = {"waiting": "photo"}
        say(bot, message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting") == "photo",
    )
    def get_photo(message):
        uid = message.from_user.id
        img = load_image(bot, message)
        result = img.convert("L").convert("RGB")
        send_image(bot, message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
