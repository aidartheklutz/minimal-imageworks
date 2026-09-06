from PIL import Image
from telebot import types
from helpers import load_image, send_image, say

TITLE = "Поворот и отражение"
user_data = {}


def register_rotate_flip_handlers(bot):
    @bot.message_handler(commands=["rotate"])
    def start_rotate(message):
        user_data[message.from_user.id] = {"waiting": "photo"}
        say(bot, message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting") == "photo",
    )
    def get_photo(message):
        uid = message.from_user.id
        user_data[uid]["image"] = load_image(bot, message)
        user_data[uid]["waiting"] = "action"
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("90° вправо", callback_data="rot_90_cw"),
            types.InlineKeyboardButton("90° влево", callback_data="rot_90_ccw"),
        )
        markup.add(types.InlineKeyboardButton("180°", callback_data="rot_180"))
        markup.row(
            types.InlineKeyboardButton("Отразить по горизонтали", callback_data="flip_h"),
            types.InlineKeyboardButton("Отразить по вертикали", callback_data="flip_v"),
        )
        say(bot, message.chat.id, TITLE, "Что сделать с картинкой?", reply_markup=markup)

    @bot.callback_query_handler(
        func=lambda c: c.data in ("rot_90_cw", "rot_90_ccw", "rot_180", "flip_h", "flip_v")
    )
    def do_rotate(call):
        uid = call.from_user.id
        if uid not in user_data or "image" not in user_data[uid]:
            bot.answer_callback_query(call.id, "Сначала отправьте картинку")
            return
        img = user_data[uid]["image"]
        if call.data == "rot_90_cw":
            result = img.transpose(Image.Transpose.ROTATE_270)
        elif call.data == "rot_90_ccw":
            result = img.transpose(Image.Transpose.ROTATE_90)
        elif call.data == "rot_180":
            result = img.transpose(Image.Transpose.ROTATE_180)
        elif call.data == "flip_h":
            result = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        else:
            result = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        bot.answer_callback_query(call.id)
        send_image(bot, call.message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
