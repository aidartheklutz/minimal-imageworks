from io import BytesIO
from PIL import Image
from telebot import types
from helpers import say, titled

TITLE = "Разделение картинки"
user_data = {}


def split_image(image_bytes, direction, parts):
    img = Image.open(BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")

    width, height = img.size
    pieces = []

    if direction == "vertical":
        part_width = width // parts
        for i in range(parts):
            left = i * part_width
            right = width if i == parts - 1 else (i + 1) * part_width
            piece = img.crop((left, 0, right, height))
            buf = BytesIO()
            piece.save(buf, format="JPEG")
            buf.seek(0)
            buf.name = f"part_{i + 1}.jpg"
            pieces.append(buf)
    else:
        part_height = height // parts
        for i in range(parts):
            top = i * part_height
            bottom = height if i == parts - 1 else (i + 1) * part_height
            piece = img.crop((0, top, width, bottom))
            buf = BytesIO()
            piece.save(buf, format="JPEG")
            buf.seek(0)
            buf.name = f"part_{i + 1}.jpg"
            pieces.append(buf)

    return pieces


def register_split_handlers(bot):
    @bot.message_handler(commands=["split"])
    def start_split(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Вертикально", callback_data="dir_vertical"),
            types.InlineKeyboardButton("Горизонтально", callback_data="dir_horizontal"),
        )
        say(bot, message.chat.id, TITLE, "Как поделить картинку?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data in ("dir_vertical", "dir_horizontal"))
    def choose_direction(call):
        direction = "vertical" if call.data == "dir_vertical" else "horizontal"
        user_data[call.from_user.id] = {
            "direction": direction,
            "waiting_photo": True,
        }
        bot.answer_callback_query(call.id)
        say(bot, call.message.chat.id, TITLE, "Отправьте картинку")

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id].get("waiting_photo"),
    )
    def get_photo(message):
        uid = message.from_user.id

        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        image_bytes = bot.download_file(file_info.file_path)

        user_data[uid]["image"] = image_bytes
        user_data[uid]["waiting_photo"] = False

        markup = types.InlineKeyboardMarkup()
        buttons = []
        for i in range(1, 6):
            buttons.append(types.InlineKeyboardButton(str(i), callback_data=f"parts_{i}"))
        markup.add(*buttons)
        say(bot, message.chat.id, TITLE, "На сколько равных частей поделить?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("parts_"))
    def choose_parts(call):
        uid = call.from_user.id
        if uid not in user_data or "image" not in user_data[uid]:
            bot.answer_callback_query(call.id, "Сначала отправьте картинку")
            return

        parts = int(call.data.replace("parts_", ""))
        direction = user_data[uid]["direction"]
        image_bytes = user_data[uid]["image"]
        bot.answer_callback_query(call.id)

        pieces = split_image(image_bytes, direction, parts)
        for i, piece in enumerate(pieces, 1):
            bot.send_photo(
                call.message.chat.id,
                piece,
                caption=titled(TITLE, f"Часть {i}"),
                parse_mode="HTML",
            )

        user_data.pop(uid, None)
