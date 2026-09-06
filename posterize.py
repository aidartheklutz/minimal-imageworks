from PIL import ImageOps
from telebot import types
from helpers import load_image, send_image, say

TITLE = "Постеризация"
user_data = {}


def register_posterize_handlers(bot):
    @bot.message_handler(commands=["posterize"])
    def start_posterize(message):
        user_data[message.from_user.id] = {"waiting": "photo"}
        say(bot, message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting") == "photo",
    )
    def get_photo(message):
        uid = message.from_user.id
        user_data[uid]["image"] = load_image(bot, message)
        user_data[uid]["waiting"] = "level"
        markup = types.InlineKeyboardMarkup()
        buttons = []
        for i in range(2, 9):
            buttons.append(types.InlineKeyboardButton(str(i), callback_data=f"posterize_{i}"))
        markup.add(*buttons)
        say(bot, message.chat.id, TITLE, "Выберите уровень постеризации:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("posterize_"))
    def choose_level(call):
        uid = call.from_user.id
        if uid not in user_data or "image" not in user_data[uid]:
            bot.answer_callback_query(call.id, "Сначала отправьте картинку")
            return
        level = int(call.data.replace("posterize_", ""))
        img = user_data[uid]["image"].convert("RGB")
        result = ImageOps.posterize(img, level)
        bot.answer_callback_query(call.id)
        send_image(bot, call.message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
