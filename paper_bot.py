import requests, os, re, img2pdf, asyncio
from datetime import datetime
from telegram import Bot

# आपका डेटा (यहाँ टोकन और आईडी पहले से सेट हैं)
BOT_TOKEN = "8350157796:AAG2VKjJBq6_Uk2Ue_crotf3-Z-mZInGgCo"
CHAT_ID = "5412252920"

async def download_and_send():
    today = datetime.now()
    bot = Bot(token=BOT_TOKEN)
    
    try:
        # --- TEST MESSAGE ---
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=f"🚀 टेस्ट मैसेज: बोट चालू है और काम कर रहा है!\nसमय: {today.strftime('%H:%M:%S')}")
        # --------------------

        target_url = "https://epaper.amritvichar.com/category/10/shahjahanpur-budaun-kasganj"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        resp = requests.get(target_url, headers=headers, timeout=20)
        links = re.findall(r'href="([^"]*view/(\d+)/[^"]+)"', resp.text)
        
        if not links:
            async with bot:
                await bot.send_message(chat_id=CHAT_ID, text="❌ वेबसाइट पर अभी पेपर का लिंक नहीं मिला।")
            return

        latest_url = links[0][0] if links[0][0].startswith('http') else "https://epaper.amritvichar.com" + links[0][0]
        p_resp = requests.get(latest_url, headers=headers)
        all_pages = sorted(list(set(re.findall(r'page-\d+-\d+\.jpg', p_resp.text))))
        
        images = []
        date_path = today.strftime("%Y-%m")
        base_img_url = f"https://epaper.amritvichar.com/media/{date_path}/"
        
        for p in all_pages:
            img_res = requests.get(base_img_url + p, headers=headers).content
            images.append(img_res)
        
        if images:
            pdf_name = f"Test_Paper_{today.strftime('%d_%m')}.pdf"
            with open(pdf_name, "wb") as f:
                f.write(img2pdf.convert(images))
            
            async with bot:
                await bot.send_document(chat_id=CHAT_ID, document=open(pdf_name, 'rb'), caption="✅ टेस्ट सफल! फाइल मिल गई।")

    except Exception as e:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ एरर: {str(e)}")

if __name__ == "__main__":
    asyncio.run(download_and_send())
