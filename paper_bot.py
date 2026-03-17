import requests, os, re, img2pdf, asyncio
from datetime import datetime
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def download_and_send():
    today = datetime.now()
    date_str = today.strftime("%d-%B-%Y").lower()
    date_path = today.strftime("%Y-%m")
    
    target_url = "https://epaper.amritvichar.com/category/10/shahjahanpur-budaun-kasganj"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        resp = requests.get(target_url, headers=headers, timeout=20)
        links = re.findall(r'href="([^"]*view/(\d+)/[^"]+)"', resp.text)
        
        if not links:
            print("❌ No edition found.")
            return

        latest_url = links[0][0] if links[0][0].startswith('http') else "https://epaper.amritvichar.com" + links[0][0]
        p_resp = requests.get(latest_url, headers=headers)
        all_pages = sorted(list(set(re.findall(r'page-\d+-\d+\.jpg', p_resp.text))))
        
        images = []
        base_img_url = f"https://epaper.amritvichar.com/media/{date_path}/"
        
        for p in all_pages:
            img_res = requests.get(base_img_url + p, headers=headers).content
            images.append(img_res)
        
        if images:
            pdf_name = f"Amrit_Vichar_Shahjahanpur_{today.strftime('%d-%m-%y')}.pdf"
            with open(pdf_name, "wb") as f:
                f.write(img2pdf.convert(images))
            
            bot = Bot(token=BOT_TOKEN)
            async with bot:
                await bot.send_document(chat_id=CHAT_ID, document=open(pdf_name, 'rb'), caption=f"📰 आज का अमृत विचार\n📅 {today.strftime('%d %b %Y')}")
            print("✅ Sent!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(download_and_send())
