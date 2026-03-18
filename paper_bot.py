import requests, os, re, img2pdf, asyncio
from datetime import datetime
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
BOT_TOKEN = "8350157796:AAG2VKjJBq6_Uk2Ue_crotf3-Z-mZInGgCo"
CHAT_ID = "5412252920" # Aapki personal ID jahan auto-message jayega

# --- FUNCTIONS FOR DOWNLOADING ---

async def get_amrit_vichar():
    today = datetime.now()
    headers = {"User-Agent": "Mozilla/5.0"}
    target_url = "https://epaper.amritvichar.com/category/10/shahjahanpur-budaun-kasganj"
    resp = requests.get(target_url, headers=headers, timeout=20)
    links = re.findall(r'href="([^"]*view/(\d+)/[^"]+)"', resp.text)
    if links:
        latest_url = links[0][0] if links[0][0].startswith('http') else "https://epaper.amritvichar.com" + links[0][0]
        p_resp = requests.get(latest_url, headers=headers)
        all_pages = sorted(list(set(re.findall(r'page-\d+-\d+\.jpg', p_resp.text))))
        if all_pages:
            images = [requests.get(f"https://epaper.amritvichar.com/media/{today.strftime('%Y-%m')}/{p}", headers=headers).content for p in all_pages]
            filename = f"Amrit_Vichar_{today.strftime('%d_%m')}.pdf"
            with open(filename, "wb") as f:
                f.write(img2pdf.convert(images))
            return filename
    return None

async def get_amar_ujala():
    today = datetime.now()
    date_au = today.strftime("%Y%m%d")
    city = "shahjahanpur"
    headers = {"User-Agent": "Mozilla/5.0"}
    au_images = []
    for i in range(1, 19):
        p = str(i).zfill(2)
        page_url = f"https://epaper.amarujala.com/{city}/{date_au}/{p}.html?format=img&ed_code={city}"
        r = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        img_tag = next((img.get("src") for img in soup.find_all("img") if img.get("src") and "hdimage" in img.get("src")), None)
        if img_tag:
            au_images.append(requests.get(img_tag, headers={"User-Agent": "Mozilla/5.0", "Referer": page_url}).content)
    if au_images:
        filename = f"Amar_Ujala_{today.strftime('%d_%m')}.pdf"
        with open(filename, "wb") as f:
            f.write(img2pdf.convert(au_images))
        return filename
    return None

# --- BOT HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📰 Amrit Vichar", callback_query_data='av')],
        [InlineKeyboardButton("📰 Amar Ujala", callback_query_data='au')],
        [InlineKeyboardButton("🤖 Funny Quote", callback_query_data='funny')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = "🙏 Welcome to My Bot!\n\nMain Amrit Vichar aur Amar Ujala download kar sakta hoon.\nAap kaun sa paper padhna pasand karenge?"
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    if data == 'funny':
        quotes = ["Padh lo beta, mauka hai, baki sab dhokha hai! 😂", "News padhne se akal aati hai, aur baki cheezon se... khair chhodo! 😜"]
        import random
        await query.edit_message_text(text=random.choice(quotes))
        return

    await query.edit_message_text(text="⏳ File taiyar ho rahi hai, thoda sabr rakhein...")
    
    file = await get_amrit_vichar() if data == 'av' else await get_amar_ujala()
    
    if file:
        await context.bot.send_document(chat_id=chat_id, document=open(file, 'rb'), caption="✅ Ye lijiye aapka paper! (Memory Cleaned 🧹)")
        os.remove(file) # Server se delete
    else:
        await context.bot.send_message(chat_id=chat_id, text="❌ Sorry! Aaj ka paper abhi aaya nahi hai.")

# --- AUTOMATION RUNNER ---
async def auto_run():
    bot = Bot(token=BOT_TOKEN)
    today = datetime.now().strftime('%d %b')
    await bot.send_message(chat_id=CHAT_ID, text=f"☀️ Good Morning All of You!\n\nAbhi subah ke 6 baj rahe hain aur main aapke liye paper le aaya hoon. Have a Great Day! ✨")
    
    for func in [get_amrit_vichar, get_amar_ujala]:
        file = await func()
        if file:
            await bot.send_document(chat_id=CHAT_ID, document=open(file, 'rb'))
            os.remove(file)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        asyncio.run(auto_run())
    else:
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_click))
        print("Bot is running...")
        app.run_polling()
