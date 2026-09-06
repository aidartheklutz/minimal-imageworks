# Minimal Imageworks

Minimal Imageworks is a lightweight Telegram bot for everyday image editing and generation. Send a photo (or text for QR codes), choose a command, and follow the guided steps. The bot processes the image with Pillow and returns the result directly in the chat.

The live bot is available at [t.me/imgworks_bot](https://t.me/imgworks_bot).

## How It Works

Users interact with the bot through simple commands. Most tools follow the same flow:

1. Send a command (e.g. `/resize`).
2. Send a photo when prompted.
3. Choose options via inline buttons or by typing values (sizes, percentages, HEX colors, etc.).
4. Receive the processed image (JPEG for RGB, PNG for images with transparency).

### Available commands

**Splitting & creation**

- `/split` – Divides an image into equal parts vertically or horizontally.
- `/qr` – Generates a QR code from text or a link. Supports standard black/white or custom fill/background colors via HEX codes.

**Size & position**

- `/resize` – Changes image size: exact dimensions, percentage scale, or fit within a maximum width/height while preserving aspect ratio.
- `/crop` – Crops freely or to common aspect ratios (1:1, 4:3, 16:9, 9:16).
- `/rotate` – Rotates 90/180/270 degrees or flips horizontally/vertically.
- `/aspect` – Adjusts aspect ratio by cropping excess or adding padding to keep the full image.
- `/padding` – Adds borders of chosen thickness and color around the image.
- `/round` – Rounds the corners or fits the image into a circle.

**Color & image**

- `/grayscale` – Converts the image to grayscale.
- `/invert` – Inverts all colors.
- `/brightness` – Adjusts brightness and contrast.
- `/saturation` – Increases or decreases color saturation.
- `/hue` – Shifts the hue of all colors.
- `/sepia` – Applies a classic sepia tone.
- `/posterize` – Reduces the number of color levels for a flat, poster-like look.
- `/replacecolor` – Replaces one color with another.
- `/palette` – Extracts the dominant colors and shows them as HEX values.

**Quality & effects**

- `/blur` – Applies Gaussian blur with selectable strength.
- `/sharpen` – Increases sharpness and detail.
- `/pixelate` – Pixelates the image by replacing areas with large blocks.
- `/shakalization` – Heavily compresses and downsamples the image for a deliberately low-quality deep-fried look (selectable intensity levels).

Any unrecognized message or media falls back to the welcome message that lists all commands.

## Tech Stack

- **Python**
- **pyTelegramBotAPI** (TeleBot) – Telegram Bot API wrapper
- **Pillow** – Image loading, manipulation, and saving
- **qrcode** – QR code generation
- **python-dotenv** – Loading the bot token from environment variables

The project is organized into small focused modules (one per feature) that register their own handlers, plus shared helpers for loading/sending images and parsing user input.

## License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this project as long as the original license and copyright notice are included.
