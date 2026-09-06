from PIL import Image
from telebot import types
from helpers import load_image, send_image, say

TITLE = "Соотношение сторон"
user_data = {}

RATIOS = {
    "aspect_1_1": (1, 1),
    "aspect_4_3": (4, 3),
    "aspect_16_9": (16, 9),
    "aspect_9_16": (9, 16),
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


def pad_to_ratio(img, rw, rh):
    if img.mode == "RGBA":
        fill = (255, 255, 255, 255)
    else:
        img = img.convert("RGB")
        fill = (255, 255, 255)
    w, h = img.size
    target = rw / rh
    current = w / h
    if current > target:
        new_h = int(w / target)
        result = Image.new(img.mode, (w, new_h), fill)
        y = (new_h - h) // 2
        if img.mode == "RGBA":
            result.paste(img, (0, y), img)
        else:
            result.paste(img, (0, y))
    else:
        new_w = int(h * target)
        result = Image.new(img.mode, (new_w, h), fill)
        x = (new_w - w) // 2
        if img.mode == "RGBA":
            result.paste(img, (x, 0), img)
        else:
            result.paste(img, (x, 0))
    return result


def register_aspect_ratio_handlers(bot):
    @bot.message_handler(commands=["aspect"])
    def start_aspect(message):
        user_data[message.from_user.id] = {"waiting": "photo"}
        say(bot, message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting") == "photo",
    )
    def get_photo(message):
        uid = message.from_user.id
        user_data[uid]["image"] = load_image(bot, message)
        user_data[uid]["waiting"] = "ratio"
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("1:1", callback_data="aspect_1_1"),
            types.InlineKeyboardButton("4:3", callback_data="aspect_4_3"),
        )
        markup.row(
            types.InlineKeyboardButton("16:9", callback_data="aspect_16_9"),
            types.InlineKeyboardButton("9:16", callback_data="aspect_9_16"),
        )
        say(bot, message.chat.id, TITLE, "Какое соотношение сторон нужно?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data in RATIOS)
    def choose_ratio(call):
        uid = call.from_user.id
        if uid not in user_data or "image" not in user_data[uid]:
            bot.answer_callback_query(call.id, "Сначала отправьте картинку")
            return
        user_data[uid]["ratio"] = RATIOS[call.data]
        user_data[uid]["waiting"] = "method"
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Обрезать", callback_data="aspect_crop"),
            types.InlineKeyboardButton("Добавить поля", callback_data="aspect_pad"),
        )
        say(bot, call.message.chat.id, TITLE, "Обрезать лишнее или добавить поля?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data in ("aspect_crop", "aspect_pad"))
    def apply_aspect(call):
        uid = call.from_user.id
        if uid not in user_data or "image" not in user_data[uid] or "ratio" not in user_data[uid]:
            bot.answer_callback_query(call.id, "Сначала отправьте картинку")
            return
        img = user_data[uid]["image"]
        rw, rh = user_data[uid]["ratio"]
        if call.data == "aspect_crop":
            result = crop_to_ratio(img, rw, rh)
        else:
            result = pad_to_ratio(img, rw, rh)
        bot.answer_callback_query(call.id)
        send_image(bot, call.message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
