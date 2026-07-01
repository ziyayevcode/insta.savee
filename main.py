import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv
import google.generativeai as genai
from generator import generate_pdf

# 1. Konfiguratsiya
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# 3. AI va Bot initsializatsiyasi
genai.configure(api_key=GEMINI_API_KEY)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 4. Asosiy Handler
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Salom! Mavzuni yuboring, men sizga professional PDF prezentatsiya tayyorlab beraman.")

@dp.message(F.text)
async def handle_topic(message: Message):
    status_msg = await message.answer("🔍 Prezentatsiya strukturasini yaratmoqdaman...")
    
    try:
        # Gemini modelini chaqirish
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Mavzu: {message.text}. Shu mavzu bo'yicha 5 ta slaydli, Tailwind CSS ishlatilgan professional HTML kod yozib ber."
        response = model.generate_content(prompt)
        
        # HTML kodini tozalash
        html_content = response.text.replace("```html", "").replace("```", "").strip()
        
        await status_msg.edit_text("⚙️ PDF fayl render qilinmoqda...")
        
        # PDF yaratish
        output_file = f"presentation_{message.chat.id}.pdf"
        await generate_pdf(html_content, output_file)
        
        # Faylni yuborish
        await message.answer_document(FSInputFile(output_file))
        await status_msg.delete()
        
        # Faylni o'chirish (tozalik uchun)
        if os.path.exists(output_file):
            os.remove(output_file)
            
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await status_msg.edit_text("❌ Prezentatsiya yaratishda xatolik yuz berdi. Iltimos, boshqa mavzu sinab ko'ring.")

# 5. Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
