import io
import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from PIL import Image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Menga istalgan rasm yuboring! Men unga mos tavsif, ma'lumot va funksiyalarini yozib beraman."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_message = await update.message.reply_text("📸 Rasm qabul qilindi. AI tahlil qilmoqda...")
    
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        image = Image.open(io.BytesIO(photo_bytes))

        prompt = """
        Ushbu rasmni batafsil tahlil qiling va o'zbek tilida quyidagi tartibda ma'lumot bering:
        1. 📝 **Qisqacha tavsif (Description):** Rasmda nima tasvirlangan?
        2. ℹ️ **Batafsil ma'lumot:** Ob'ekt, joy yoki voqea haqida muhim tafsilotlar.
        3. ⚙️ **Asosiy xususiyatlar / Funksiyalar:** Agar rasmda mahsulot, qurilma yoki ilova bo'lsa, uning funksiyalari va imkoniyatlarini sanab o'ting.
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt]
        )

        await status_message.edit_text(response.text, parse_mode='Markdown')

    except Exception as e:
        await status_message.edit_text(f"Xatolik yuz berdi: {str(e)}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
