from io import BytesIO
from PIL import Image
from telebot import types
from helpers import load_image, send_image, say

TITLE = "Шакализация"
user_data = {}


def shakalize(img, level):
    img = img.convert("RGB")
    w, h = img.size
    scale = level + 1
    small_w = max(8, w // scale)
    small_h = max(8, h // scale)
    img = img.resize((small_w, small_h), Image.Resampling.BILINEAR)
    img = img.resize((w, h), Image.Resampling.NEAREST)

    quality = 40 - level * 7
    if quality < 1:
        quality = 1
    for i in range(level):
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        buf.seek(0)
        img = Image.open(buf).convert("RGB")
    return img


def register_shakalization_handlers(bot):
    @bot.message_handler(commands=["shakalization"])
    def start_shakal(message):
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
        for i in range(1, 6):
            buttons.append(types.InlineKeyboardButton(str(i), callback_data=f"shakal_{i}"))
        markup.add(*buttons)
        say(bot, message.chat.id, TITLE, "Уровень шакализации:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("shakal_"))
    def choose_level(call):
        uid = call.from_user.id
        if uid not in user_data or "image" not in user_data[uid]:
            bot.answer_callback_query(call.id, "Сначала отправьте картинку")
            return
        level = int(call.data.replace("shakal_", ""))
        result = shakalize(user_data[uid]["image"], level)
        bot.answer_callback_query(call.id)
        send_image(bot, call.message.chat.id, result, title=TITLE)
        user_data.pop(uid, None)
