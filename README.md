# Minimal Imageworks

![banner](./assets/banner_git.png)

Minimal Imageworks is a lightweight Telegram bot for everyday image editing and generation. Choose a command, send a photo (or text for QR codes), and follow the guided steps. The bot processes the image with Pillow and returns the result directly in the chat.

The live bot will soon be available at [t.me/imgworks_bot](https://t.me/imgworks_bot).

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
- `/describe` – Sends the photo to a vision model (Qwen3.8-27B) and returns a short Russian caption of what is in the image (5 uses per user every 12 hours).

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
- **python-dotenv** – Loading secrets from environment variables
- **requests** – Hugging Face Inference API calls for `/describe`

The project is organized into small focused modules (one per feature) that register their own handlers, plus shared helpers for loading/sending images and parsing user input.

## Setting up `/describe`

Image captions are generated in `alt_text.py` through the [Hugging Face Inference Router](https://huggingface.co/docs/inference-providers). On your machine:

1. Create a Hugging Face account and generate an access token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2. Put the token in a `.env` file in the project root (this file is gitignored):

```
BOT_TOKEN=your_telegram_bot_token
HF_TOKEN=hf_your_token_here
```

3. Install dependencies, including `requests`.
4. Add a `query` function that posts the chat-completions payload. `alt_text.py` imports it as `from hf_auth import query`, so create `hf_auth.py` in the project root with that function. Example:

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"

def query(payload):
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
    }
    response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
    return response.json()

response = query({
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe this image in one sentence."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
                    }
                }
            ]
        }
    ],
    "model": "Qwen/Qwen3.8-27B:ovhcloud"
})

print(response["choices"][0]["message"])
```

`alt_text.py` calls `query(...)` with the captioning prompt and the user's photo as a `data:image/jpeg;base64,...` URL instead of a public image link.

Each user can run `/describe` up to 5 times per 12 hours. There is no server-side database: usage is stored locally in `describe_usage.json` in the project root (the file is gitignored). The JSON object maps each Telegram user ID to a list of Unix timestamps for successful caption requests. On every check, timestamps older than 12 hours are dropped, so the limit is a rolling window rather than a calendar day. Failed API calls do not consume a use.

## License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this project as long as the original license and copyright notice are included.
