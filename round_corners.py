from PIL import Image, ImageDraw
from telebot import types
from helpers import is_user_text, load_image, send_image, say

TITLE = "Скругление и круг"
user_data = {}


def round_corners(img, radius):
    img = img.convert("RGBA")
    w, h = img.size
    radius = min(radius, w // 2, h // 2)
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    img.putalpha(mask)
    return img


def fit_circle(img):
    img = img.convert("RGBA")
    w, h = img.size
    size = min(w, h)
    left = (w - size) // 2
    top = (h - size) // 2
    img = img.crop((left, top, left + size, top + size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    img.putalpha(mask)
    return img


def register_round_corners_handlers(bot):
    @bot.message_handler(commands=["round"])
    def start_round(message):
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
        markup.add(
            types.InlineKeyboardButton("Скруглить углы", callback_data="round_corners"),
            types.InlineKeyboardButton("Вписать в круг", callback_data="round_circle"),
        )
        say(bot, message.chat.id, TITLE, "Что сделать с картинкой?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data == "round_circle")
    def do_circle(call):
        uid = call.from_user.id
        if uid not in user_data or "image" not in user_data[uid]:
            bot.answer_callback_query(call.id, "Сначала отправьте картинку")
            return
        result = fit_circle(user_data[uid]["image"])
        bot.answer_callback_query(call.id)
        send_image(bot, call.message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)

    @bot.callback_query_handler(func=lambda c: c.data == "round_corners")
    def ask_radius(call):
        uid = call.from_user.id
        if uid not in user_data or "image" not in user_data[uid]:
            bot.answer_callback_query(call.id, "Сначала отправьте картинку")
            return
        user_data[uid]["waiting"] = "radius"
        bot.answer_callback_query(call.id)
        say(bot, call.message.chat.id, TITLE, "Отправьте радиус скругления, например: 50")

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") == "radius"
        and is_user_text(m.text)
    )
    def get_radius(message):
        uid = message.from_user.id
        try:
            radius = int(message.text.strip())
        except ValueError:
            say(bot, message.chat.id, TITLE, "Отправьте целое число, например: 50")
            return
        if radius <= 0:
            say(bot, message.chat.id, TITLE, "Радиус должен быть больше 0")
            return
        result = round_corners(user_data[uid]["image"], radius)
        send_image(bot, message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
