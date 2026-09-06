import os
from dotenv import load_dotenv
import telebot as tbot
from telebot import types
from split_img import register_split_handlers
from qr_gen import register_qr_handlers
from resize import register_resize_handlers
from crop import register_crop_handlers
from rotate_flip import register_rotate_flip_handlers
from aspect_ratio import register_aspect_ratio_handlers
from padding import register_padding_handlers
from round_corners import register_round_corners_handlers
from grayscale import register_grayscale_handlers
from invert import register_invert_handlers
from brightness_contrast import register_brightness_contrast_handlers
from saturation import register_saturation_handlers
from hue import register_hue_handlers
from blur import register_blur_handlers
from sharpen import register_sharpen_handlers
from pixelate import register_pixelate_handlers
from posterize import register_posterize_handlers
from sepia import register_sepia_handlers
from palette import register_palette_handlers
from replace_color import register_replace_color_handlers
from shakalization import register_shakalization_handlers
from alt_text import register_describe_handlers

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = tbot.TeleBot(TOKEN)

register_split_handlers(bot)
register_qr_handlers(bot)
register_resize_handlers(bot)
register_crop_handlers(bot)
register_rotate_flip_handlers(bot)
register_aspect_ratio_handlers(bot)
register_padding_handlers(bot)
register_round_corners_handlers(bot)
register_grayscale_handlers(bot)
register_invert_handlers(bot)
register_brightness_contrast_handlers(bot)
register_saturation_handlers(bot)
register_hue_handlers(bot)
register_blur_handlers(bot)
register_sharpen_handlers(bot)
register_pixelate_handlers(bot)
register_posterize_handlers(bot)
register_sepia_handlers(bot)
register_palette_handlers(bot)
register_replace_color_handlers(bot)
register_shakalization_handlers(bot)
register_describe_handlers(bot)


@bot.message_handler(commands=["start"])
def start(message):
    text = (
        "<b>Добро пожаловать в Minimal Imageworks!</b> \n"
        "Выберите нужную вам функцию, отправив одну из команд ниже. После этого просто следуйте инструкциям.\n\n"

        "<b>Инструменты</b>\n"
        "✱ /split – делит картинку на равные части по вертикали или горизонтали\n"
        "✱ /qr – создаёт QR-код из текста или ссылки\n"
        "✱ /describe – описывает, что изображено на картинке\n"
        "\n"

        "<b>Размер и положение</b>\n"
        "✱ /resize – меняет размер картинки: можно задать точные размеры, процент или вписать её в рамку\n"
        "✱ /crop – обрезает картинку свободно или по соотношению сторон: 1:1, 4:3, 16:9, 9:16\n"
        "✱ /rotate – поворачивает картинку на 90°, 180° или 270°, а также отражает её по горизонтали или вертикали\n"
        "✱ /aspect – меняет соотношение сторон: обрезает лишнее или добавляет поля, чтобы сохранить всю картинку\n"
        "✱ /padding – добавляет поля вокруг картинки с выбранной толщиной и цветом\n"
        "✱ /round – скругляет углы картинки или вписывает её в круг\n"
        "\n"

        "<b>Цвет и изображение</b>\n"
        "✱ /grayscale – превращает картинку в оттенки серого\n"
        "✱ /invert – инвертирует цвета картинки\n"
        "✱ /brightness – меняет яркость и контраст картинки\n"
        "✱ /saturation – увеличивает или уменьшает насыщенность цветов\n"
        "✱ /hue – сдвигает оттенок всех цветов картинки\n"
        "✱ /sepia – применяет эффект сепии\n"
        "✱ /posterize – уменьшает количество оттенков, делая цвета более резкими и плоскими\n"
        "✱ /replacecolor – заменяет выбранный цвет на другой\n"
        "✱ /palette – определяет основные цвета картинки и показывает их в HEX\n"
        "\n"

        "<b>Качество и эффекты</b>\n"
        "✱ /blur – размывает картинку с выбранной силой эффекта\n"
        "✱ /sharpen – повышает резкость и делает детали более выраженными\n"
        "✱ /pixelate – пикселизирует картинку, заменяя участки изображения крупными пикселями\n"
        "✱ /shakalization – сильно сжимает картинку, превращая её в изображение сомнительного качества\n"
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@bot.message_handler(
    func=lambda m: True,
    content_types=[
        "text",
        "photo",
        "document",
        "sticker",
        "audio",
        "video",
        "voice",
        "animation",
        "video_note",
        "location",
        "contact",
        "dice",
    ],
)
def fallback(message):
    start(message)


bot.infinity_polling()
