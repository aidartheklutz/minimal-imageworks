from PIL import Image
from telebot import types
from helpers import is_user_text, load_image, send_image, parse_two_ints, say

TITLE = "Изменение размера"
user_data = {}


def fit_within(img, max_w, max_h):
    w, h = img.size
    scale = min(max_w / w, max_h / h, 1)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)


def register_resize_handlers(bot):
    @bot.message_handler(commands=["resize"])
    def start_resize(message):
        user_data[message.from_user.id] = {"waiting": "photo"}
        say(bot, message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting") == "photo",
    )
    def get_photo(message):
        uid = message.from_user.id
        user_data[uid]["image"] = load_image(bot, message)
        user_data[uid]["waiting"] = "mode"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Точный размер", callback_data="resize_exact"))
        markup.add(types.InlineKeyboardButton("Процент", callback_data="resize_percent"))
        markup.add(types.InlineKeyboardButton("Вписать в размер", callback_data="resize_fit"))
        say(bot, message.chat.id, TITLE, "Как изменить размер?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data in ("resize_exact", "resize_percent", "resize_fit"))
    def choose_mode(call):
        uid = call.from_user.id
        if uid not in user_data or "image" not in user_data[uid]:
            bot.answer_callback_query(call.id, "Сначала отправьте картинку")
            return
        bot.answer_callback_query(call.id)
        if call.data == "resize_exact":
            user_data[uid]["waiting"] = "exact"
            say(bot, call.message.chat.id, TITLE, "Отправьте ширину и высоту, например: 800 600")
        elif call.data == "resize_percent":
            user_data[uid]["waiting"] = "percent"
            say(bot, call.message.chat.id, TITLE, "Отправьте процент, например: 50")
        else:
            user_data[uid]["waiting"] = "fit"
            say(bot, call.message.chat.id, TITLE, "Отправьте максимальные ширину и высоту, например: 800 600")

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") in ("exact", "percent", "fit")
        and is_user_text(m.text)
    )
    def get_values(message):
        uid = message.from_user.id
        waiting = user_data[uid]["waiting"]
        img = user_data[uid]["image"]

        if waiting == "percent":
            try:
                percent = float(message.text.replace(",", ".").strip())
            except ValueError:
                say(bot, message.chat.id, TITLE, "Отправьте число, например: 50")
                return
            if percent <= 0 or percent > 500:
                say(bot, message.chat.id, TITLE, "Процент должен быть от 1 до 500")
                return
            scale = percent / 100
            w = max(1, int(img.size[0] * scale))
            h = max(1, int(img.size[1] * scale))
            result = img.resize((w, h), Image.Resampling.LANCZOS)
        else:
            size = parse_two_ints(message.text)
            if size is None:
                say(bot, message.chat.id, TITLE, "Отправьте два числа, например: 800 600")
                return
            w, h = size
            if waiting == "exact":
                result = img.resize((w, h), Image.Resampling.LANCZOS)
            else:
                result = fit_within(img, w, h)

        send_image(bot, message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
