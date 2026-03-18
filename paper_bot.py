 import requests, re, img2pdf, asyncio
from datetime import datetime, time
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8350157796:AAG2VKjJBq6_Uk2Ue_crotf3-Z-mZInGgCo"
CHAT_ID = "5412252920"

bot = Bot(token=BOT_TOKEN)

# ---------- HI REPLY FUNCTION ----------

async def hi_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.lower()

    if "hi" in text:
        name = update.message.from_user.first_name
        await update.message.reply_text(f"😊 You are welcome {name}")

# ---------- EPAPER FUNCTION ----------

async def check_epaper():

    today = datetime.now().strftime('%d %b %Y')

    target_url = "https://epaper.amritvichar.com/category/10/shahjahanpur-budaun-kasganj"

    headers = {"User-Agent": "Mozilla/5.0"}

    try:

        resp = requests.get(target_url, headers=headers, timeout=20)

        links = re.findall(r'href="([^"]*view/(\d+)/[^"]+)"', resp.text)

        if not links:
            return False

        latest_url = links[0][0]

        if not latest_url.startswith("http"):
            latest_url = "https://epaper.amritvichar.com" + latest_url

        page_html = requests.get(latest_url, headers=headers).text

        pages = sorted(set(re.findall(r'page-\d+-\d+\.jpg', page_html)))

        if not pages:
            return False

        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"📰 आज का अमृत विचार मिल गया\n📄 Pages: {len(pages)}\nPDF बना रहा हूँ..."
        )

        images = []

        folder = datetime.now().strftime("%Y-%m")

        for p in pages:

            img_url = f"https://epaper.amritvichar.com/media/{folder}/{p}"

            img = requests.get(img_url, headers=headers).content

            images.append(img)

        pdf_name = f"Amrit_Vichar_{datetime.now().strftime('%d_%m_%Y')}.pdf"

        with open(pdf_name, "wb") as f:
            f.write(img2pdf.convert(images))

        await bot.send_document(
            chat_id=CHAT_ID,
            document=open(pdf_name, "rb"),
            caption=f"📰 Amrit Vichar\n📅 {today}"
        )

        return True

    except Exception as e:

        await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Error: {e}")

        return False

# ---------- SCHEDULER ----------

async def scheduler():

    while True:

        now = datetime.now().time()

        start = time(6, 0)

        if now >= start:

            print("Checking paper...")

            found = await check_epaper()

            if found:
                print("Paper sent")
                break

        await asyncio.sleep(600)  # 10 minutes

# ---------- MAIN ----------

async def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hi_reply))

    asyncio.create_task(scheduler())

    print("Bot Running...")

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
