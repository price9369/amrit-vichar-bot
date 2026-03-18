import requests, os, re, img2pdf, asyncio
from datetime import datetime
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
BOT_TOKEN = "8350157796:AAG2VKjJBq6_Uk2Ue_crotf3-Z-mZInGgCo"
CHAT_ID = "5412252920"

# --- DOWNLOADER FUNCTIONS ---

async def get_amrit_vichar():
    try:
        today = datetime.now()
        headers = {"User-Agent": "Mozilla/5.0"}
        target_url = "https://epaper.amritvichar.com/category/10/shahjahanpur-budaun-kasganj"
        resp = requests.get(target_url, headers=headers, timeout=15)
        links = re.findall(r'href="([^"]*view/(\d+)/[^"]+)"', resp.text)
        if links:
            latest_url = links[0][0] if links[0][0].startswith('http') else "https://epaper.amritvichar.com" + links[0][0]
            p_resp = requests.get(latest_url, headers=headers, timeout=15)
            all_pages = sorted(list(set(re.findall(r'page-\d+-\d+\.jpg', p_resp.text))))
            if all_pages:
                images = []
                date_path = today.strftime("%Y-%m")
                for p in all_pages:
                    img = requests.get(f"https://epaper.amritvichar.com/media/{date_path}/{p}", headers=headers, timeout=10).content
                    images.append(img)
                filename = f"Amrit_Vichar_{today.strftime('%d_%m')}.pdf"
                with open(filename, "wb") as f:
                    f.write(img2pdf.convert(images))
                return filename
    except Exception as e:
        print(f"AV Error: {e}")
    return None

async def get_amar_ujala():
    try:
        today = datetime.now()
        date_au = today.strftime("%Y%m%d")
        city = "shahjahanpur"
        headers = {"User-Agent": "Mozilla/5.0"}
        au_images = []
        # Pages ko 16 tak limit kiya hai speed ke liye
        for i in range(1, 17):
            p = str(i).zfill(2)
            page_url = f"https://epaper.amarujala.com/{city}/{date_au}/{p}.html?format=img&ed_code={city}"
            try:
                r = requests.get(page_url, headers=headers, timeout=7)
                soup = BeautifulSoup(r.text, "html.parser")
                img_tag = next((img.get("src") for img in soup.find_all("img") if img.get("src") and "hdimage" in img.get("src")), None)
                if img_tag:
                    img_data = requests.get(img_tag, headers={"User-Agent": "Mozilla/5.0", "Referer": page_url}, timeout=7).content
                    au_images.append(img_data)
                else:
                    break # Agla page nahi hai to ruk jao
            except:
                continue
        if au_images:
            filename = f"Amar_Ujala_{today.strftime('%d_%m')}.pdf"
            with open(filename, "wb") as f:
                f.write(img2pdf.convert(au_images))
            return filename
    except Exception as e:
        print(f"AU Error: {e}")
    return None

# --- BOT COMMANDS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📰 Amrit Vichar Download", callback_query_data='av')],
        [InlineKeyboardButton("📰 Amar Ujala Download", callback_query_data='au')],
        [InlineKeyboardButton("🃏 Funny Quote", callback_query_data='funny')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_msg = (
        "🙏 Namaste!\n\n"
        "Main aapka E-Paper Assistant hoon.\n"
        "Niche diye gaye button par click karke aap paper download kar sakte hain."
    )
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'funny':
        import random
        jokes = ["Aapka paper download ho raha hai, tab tak ek chai pee lo! ☕", "News padhne se gyan badhta hai, aur bot use karne se time bachta hai! 😎"]
        await query.message.reply_text(random.choice(jokes))
        return

    # User ko update dena
    paper_name = "Amrit Vichar" if query.data == 'av' else "Amar Ujala"
    status_msg = await query.edit_message_text(text=f"⏳ {paper_name} download ho raha hai... (Isme 1-2 minute lag sakte hain)")

    # Download shuru
    file = await get_amrit_vichar() if query.data == 'av' else await get_amar_ujala()

    if file:
        await context.bot.send_document(
            chat_id=query.message.chat_id, 
            document=open(file, 'rb'), 
            caption=f"✅ {paper_name} taiyar hai!\n🧹 Server cleaned."
        )
        os.remove(file) # File delete taaki server clean rahe
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="❌ Maafi chahta hoon! Aaj ka paper website par nahi mila.")

# --- AUTO MODE (SCHEDULED) ---

async def auto_mode():
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="☀️ Good Morning! Aaj ke papers download kiye ja rahe hain...")
    
    papers = [("Amrit Vichar", get_amrit_vichar), ("Amar Ujala", get_amar_ujala)]
    for name, func in papers:
        file = await func()
        if file:
            await bot.send_document(chat_id=CHAT_ID, document=open(file, 'rb'), caption=f"📰 {name}")
            os.remove(file)
    print("Auto run complete.")

if __name__ == "__main__":
    import sys
    # Agar GitHub Action se '--auto' command aaye
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        asyncio.run(auto_mode())
    else:
        # Normal Bot Mode (Manual Command ke liye)
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_buttons))
        print("Bot is listening for commands...")
        app.run_polling()
