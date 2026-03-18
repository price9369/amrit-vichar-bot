import requests, os, re, img2pdf, asyncio
from datetime import datetime
from telegram import Bot

# आपका डेटा (टोकन और आईडी)
BOT_TOKEN = "8350157796:AAG2VKjJBq6_Uk2Ue_crotf3-Z-mZInGgCo"
CHAT_ID = "5412252920"

async def test_and_run():
    bot = Bot(token=BOT_TOKEN)
    today = datetime.now().strftime('%d %b %Y')
    
    try:
        # 1. गुड मॉर्निंग मैसेज के साथ शुरुआत
        async with bot:
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=f"☀️ Good Morning!\n\n🚀 बोट चालू हो गया है और आज ({today}) का शाहजहाँपुर अमृत विचार पेपर खोज रहा हूँ..."
            )

        # 2. पेपर खोजने की प्रक्रिया
        target_url = "https://epaper.amritvichar.com/category/10/shahjahanpur-budaun-kasganj"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(target_url, headers=headers, timeout=20)
        
        links = re.findall(r'href="([^"]*view/(\d+)/[^"]+)"', resp.text)
        
        if not links:
            async with bot:
                await bot.send_message(chat_id=CHAT_ID, text="❌ माफी चाहता हूँ, आज का पेपर अभी वेबसाइट पर नहीं मिला।")
            return

        # 3. पन्ने डाउनलोड करना
        latest_url = links[0][0] if links[0][0].startswith('http') else "https://epaper.amritvichar.com" + links[0][0]
        p_resp = requests.get(latest_url, headers=headers)
        all_pages = sorted(list(set(re.findall(r'page-\d+-\d+\.jpg', p_resp.text))))
        
        if all_pages:
            async with bot:
                await bot.send_message(chat_id=CHAT_ID, text=f"📄 {len(all_pages)} पन्ने मिल गए हैं। फाइल बनाकर भेज रहा हूँ, कृपया थोड़ा इंतज़ार करें...")
            
            images = []
            date_path = datetime.now().strftime("%Y-%m")
            for p in all_pages:
                img_res = requests.get(f"https://epaper.amritvichar.com/media/{date_path}/{p}", headers=headers).content
                images.append(img_res)
            
            pdf_name = f"Amrit_Vichar_{datetime.now().strftime('%d_%m')}.pdf"
            with open(pdf_name, "wb") as f:
                f.write(img2pdf.convert(images))
            
            async with bot:
                await bot.send_document(
                    chat_id=CHAT_ID, 
                    document=open(pdf_name, 'rb'), 
                    caption=f"📰 आज का अमृत विचार तैयार है।\n📅 {today}\n✅ आपका दिन शुभ हो!"
                )
        
    except Exception as e:
        async with bot:
            await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ एरर आया: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_and_run())
