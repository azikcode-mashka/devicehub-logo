import asyncio
import os 
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from PIL import Image
from io import BytesIO

load_dotenv()
# ========== CONFIG ==========
TOKEN = os.getenv("BOT_TOKEN")
LOGO_PATH = "logo.png"
MARGIN = 50
# ============================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🧠 store user position choice
user_position = {}  # user_id -> position


# ---------- COMMANDS ----------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "📸 Rasmni yuboring\n"
        "Logo joylashuvini tanlang:\n"
        "/tl – yuqori chap\n"
        "/tr – yuqori o'ng\n"
        "/bl – pastki chap\n"
        "/br – pastki o'ng"
    )


@dp.message(Command("tl"))
async def top_left(message: types.Message):
    user_position[message.from_user.id] = "tl"
    await message.answer("✅ Joylashuv o‘rnatildi: YUQORI CHAP")


@dp.message(Command("tr"))
async def top_right(message: types.Message):
    user_position[message.from_user.id] = "tr"
    await message.answer("✅ Joylashuv o‘rnatildi: YUQORI O'NG")


@dp.message(Command("bl"))
async def bottom_left(message: types.Message):
    user_position[message.from_user.id] = "bl"
    await message.answer("✅ Joylashuv o‘rnatildi: PASTKI CHAP")


@dp.message(Command("br"))
async def bottom_right(message: types.Message):
    user_position[message.from_user.id] = "br"
    await message.answer("Joylashuv o‘rnatildi: PASTKI O'NG")


# ---------- PHOTO HANDLER ----------
@dp.message(F.photo)
async def add_logo(message: types.Message):
    position = user_position.get(message.from_user.id, "br")  # default

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)

    photo_buffer = BytesIO()
    await bot.download_file(file.file_path, photo_buffer)
    photo_buffer.seek(0)

    base = Image.open(photo_buffer).convert("RGBA")
    logo = Image.open(LOGO_PATH).convert("RGBA")

    bw, bh = base.size
    lw, lh = logo.size

    # 🔧 resize logo (20% width)
    max_w = int(bw * 0.2)
    if lw > max_w:
        ratio = max_w / lw
        logo = logo.resize(
            (int(lw * ratio), int(lh * ratio)),
            Image.Resampling.LANCZOS
        )
        lw, lh = logo.size

    # 📍 position logic
    if position == "tl":
        x, y = MARGIN, MARGIN
    elif position == "tr":
        x, y = bw - lw - MARGIN, MARGIN
    elif position == "bl":
        x, y = MARGIN, bh - lh - MARGIN
    else:  # br
        x, y = bw - lw - MARGIN, bh - lh - MARGIN

    base.paste(logo, (x, y), logo)

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
