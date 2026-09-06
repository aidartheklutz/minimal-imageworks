from telebot import types
from helpers import is_user_text, load_image, send_image, say

TITLE = "Обрезка"
user_data = {}

RATIOS = {
    "crop_1_1": (1, 1),
    "crop_4_3": (4, 3),
    "crop_16_9": (16, 9),
    "crop_9_16": (9, 16),
}


def crop_to_ratio(img, rw, rh):
    w, h = img.size
    target = rw / rh
    current = w / h
    if current > target:
        new_w = int(h * target)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    new_h = int(w / target)
    top = (h - new_h) // 2
    return img.crop((0, top, w, top + new_h))


def register_crop_handlers(bot):
    @bot.message_handler(commands=["crop"])
    def start_crop(message):
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
        markup.add(types.InlineKeyboardButton("Свободная обрезка", callback_data="crop_free"))
        markup.row(
            types.InlineKeyboardButton("1:1", callback_data="crop_1_1"),
            types.InlineKeyboardButton("4:3", callback_data="crop_4_3"),
        )
        markup.row(
            types.InlineKeyboardButton("16:9", callback_data="crop_16_9"),
            types.InlineKeyboardButton("9:16", callback_data="crop_9_16"),
        )
        say(bot, message.chat.id, TITLE, "Как обрезать картинку?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data == "crop_free")
    def crop_free(call):
        uid = call.from_user.id
        if uid not in user_data or "image" not in user_data[uid]:
            bot.answer_callback_query(call.id, "Сначала отправьте картинку")
            return
        user_data[uid]["waiting"] = "coords"
        bot.answer_callback_query(call.id)
        say(
            bot,
            call.message.chat.id,
            TITLE,
            "Отправьте координаты: лево верх право низ, например: 10 10 400 300",
        )

    @bot.callback_query_handler(func=lambda c: c.data in RATIOS)
    def crop_ratio(call):
        uid = call.from_user.id
        if uid not in user_data or "image" not in user_data[uid]:
            bot.answer_callback_query(call.id, "Сначала отправьте картинку")
            return
        rw, rh = RATIOS[call.data]
        result = crop_to_ratio(user_data[uid]["image"], rw, rh)
        bot.answer_callback_query(call.id)
        send_image(bot, call.message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "coords"
        and is_user_text(m.text)
    )
    def get_coords(message):
        uid = message.from_user.id
        parts = message.text.replace(",", " ").split()
        if len(parts) != 4:
            say(bot, message.chat.id, TITLE, "Нужно 4 числа, например: 10 10 400 300")
            return
        try:
            left, top, right, bottom = [int(p) for p in parts]
        except ValueError:
            say(bot, message.chat.id, TITLE, "Нужно 4 числа, например: 10 10 400 300")
            return
        img = user_data[uid]["image"]
        w, h = img.size
        left = max(0, min(left, w - 1))
        top = max(0, min(top, h - 1))
        right = max(left + 1, min(right, w))
        bottom = max(top + 1, min(bottom, h))
        result = img.crop((left, top, right, bottom))
        send_image(bot, message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
