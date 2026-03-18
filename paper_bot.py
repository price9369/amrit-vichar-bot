 import requests
import re
import img2pdf
import asyncio
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8350157796:AAG2VKjJBq6_Uk2Ue_crotf3-Z-mZInGgCo"
CHAT_ID = "5412252920"

bot = Bot(token=BOT_TOKEN)

async def hi_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.lower()

    if "hi" in text:
        name = update.message.from_user.first_name
        await update.message.reply_text(f"You are welcome {name}")


async def check_epaper():

    today = datetime.now().strftime('%d %b %Y')

    url = "https://epaper.amritvichar.com/category/10/shahjahanpur-budaun-kasganj"

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)

    links = re.findall(r'href="([^"]*view/(\d+)/[^"]+)"', r.text)

    if not links:
        return

    latest = links[0][0]

    if not latest.startswith("http"):
        latest = "https://epaper.amritvichar.com" + latest

    html = requests.get(latest, headers=headers).text

    pages = sorted(set(re.findall(r'page-\d+-\d+\.jpg', html)))

    if not pages:
        return

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


async def scheduler():

    while True:

        await check_epaper()

        await asyncio.sleep(600)


async def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hi_reply))

    asyncio.create_task(scheduler())

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
