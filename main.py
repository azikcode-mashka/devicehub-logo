import asyncio
import os
from io import BytesIO

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
from PIL import Image

# 🔹 Load env vars (works locally & on Railway)
load_dotenv()

# ========== CONFIG ==========
TOKEN = os.getenv("BOT_TOKEN")
LOGO_PATH = "logo.png"
MARGIN = 50
# ============================

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("📸 Rasmni yuboring. Men logoni pastki o'ng burchakka joylashtiraman.")


@dp.message(F.photo)
async def add_logo(message: types.Message):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)

    # ⬇️ Download photo to RAM
    photo_buffer = BytesIO()
    await bot.download_file(file.file_path, photo_buffer)
    photo_buffer.seek(0)

    # 🖼 Open images
    base = Image.open(photo_buffer).convert("RGBA")
    logo = Image.open(LOGO_PATH).convert("RGBA")

    bw, bh = base.size
    lw, lh = logo.size

    # 🔧 Resize logo (20% of image width)
    max_w = int(bw * 0.2)
    if lw > max_w:
        ratio = max_w / lw
        logo = logo.resize(
            (int(lw * ratio), int(lh * ratio)),
            Image.Resampling.LANCZOS
        )
        lw, lh = logo.size

    # 📍 Bottom-right position
    x = bw - lw - MARGIN
    y = bh - lh - MARGIN

    base.paste(logo, (x, y), logo)

    # 📤 Save result to RAM
    result = BytesIO()
    base.convert("RGB").save(result, format="JPEG", quality=95)
    result.seek(0)

    await message.answer_photo(
        types.BufferedInputFile(
            result.read(),
            filename="result.jpg"
        )
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
