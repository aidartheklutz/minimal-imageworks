from io import BytesIO
import qrcode
from telebot import types
from helpers import is_user_text, say

TITLE = "Генератор QR-кодов"
user_data = {}


def parse_hex(text):
    text = text.strip()
    if text.startswith("#"):
        text = text[1:]
    if len(text) != 6:
        return None
    try:
        int(text, 16)
        return "#" + text.upper()
    except ValueError:
        return None


def make_qr(text, fill_color="black", back_color="white"):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    buf.name = "qr.png"
    return buf


def ask_for_text(bot, chat_id):
    say(bot, chat_id, TITLE, "Отправьте текст или ссылку")


def ask_for_black(bot, chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Обычный чёрный", callback_data="qr_default_black"))
    say(
        bot,
        chat_id,
        TITLE,
        "Отправьте HEX-код для чёрного цвета, например #000000.\n"
        "Кнопка ниже оставит обычный чёрный цвет.",
        reply_markup=markup,
    )


def ask_for_white(bot, chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Обычный белый", callback_data="qr_default_white"))
    say(
        bot,
        chat_id,
        TITLE,
        "Отправьте HEX-код для белого цвета, например #FFFFFF.\n"
        "Кнопка ниже оставит обычный белый цвет.",
        reply_markup=markup,
    )


def send_qr(bot, chat_id, uid):
    text = user_data[uid]["text"]
    fill = user_data[uid].get("fill_color", "black")
    back = user_data[uid].get("back_color", "white")
    qr_image = make_qr(text, fill, back)
    bot.send_photo(chat_id, qr_image, caption=f"<b>{TITLE}</b>", parse_mode="HTML")
    user_data.pop(uid, None)


def register_qr_handlers(bot):
    @bot.message_handler(commands=["qr"])
    def start_qr(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Стандартный режим", callback_data="qr_mode_standard"),
            types.InlineKeyboardButton("Расширенный режим", callback_data="qr_mode_advanced"),
        )
        say(bot, message.chat.id, TITLE, "Выберите режим:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data in ("qr_mode_standard", "qr_mode_advanced"))
    def choose_mode(call):
        uid = call.from_user.id
        bot.answer_callback_query(call.id)
        if call.data == "qr_mode_standard":
            user_data[uid] = {
                "fill_color": "black",
                "back_color": "white",
                "waiting": "text",
            }
            ask_for_text(bot, call.message.chat.id)
        else:
            user_data[uid] = {"waiting": "hex_black"}
            ask_for_black(bot, call.message.chat.id)

    @bot.callback_query_handler(func=lambda c: c.data == "qr_default_black")
    def default_black(call):
        uid = call.from_user.id
        if uid not in user_data or user_data[uid].get("waiting") != "hex_black":
            bot.answer_callback_query(call.id)
            return
        user_data[uid]["fill_color"] = "black"
        user_data[uid]["waiting"] = "hex_white"
        bot.answer_callback_query(call.id)
        ask_for_white(bot, call.message.chat.id)

    @bot.callback_query_handler(func=lambda c: c.data == "qr_default_white")
    def default_white(call):
        uid = call.from_user.id
        if uid not in user_data or user_data[uid].get("waiting") != "hex_white":
            bot.answer_callback_query(call.id)
            return
        user_data[uid]["back_color"] = "white"
        user_data[uid]["waiting"] = "text"
        bot.answer_callback_query(call.id)
        ask_for_text(bot, call.message.chat.id)

    @bot.message_handler(
        func=lambda m: m.from_user.id in user_data
        and user_data[m.from_user.id].get("waiting") in ("hex_black", "hex_white", "text")
        and is_user_text(m.text)
    )
    def handle_qr_text(message):
        uid = message.from_user.id
        waiting = user_data[uid]["waiting"]

        if waiting == "hex_black":
            color = parse_hex(message.text)
            if color is None:
                say(bot, message.chat.id, TITLE, "Неверный HEX-код. Попробуйте ещё раз, например #1A2B3C")
                return
            user_data[uid]["fill_color"] = color
            user_data[uid]["waiting"] = "hex_white"
            ask_for_white(bot, message.chat.id)
            return

        if waiting == "hex_white":
            color = parse_hex(message.text)
            if color is None:
                say(bot, message.chat.id, TITLE, "Неверный HEX-код. Попробуйте ещё раз, например #FFFFFF")
                return
            user_data[uid]["back_color"] = color
            user_data[uid]["waiting"] = "text"
            ask_for_text(bot, message.chat.id)
            return

        text = message.text.strip()
        if text == "":
            say(bot, message.chat.id, TITLE, "Отправьте текст или ссылку")
            return
        user_data[uid]["text"] = text
        send_qr(bot, message.chat.id, uid)
