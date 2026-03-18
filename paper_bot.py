 import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8350157796:AAG2VKjJBq6_Uk2Ue_crotf3-Z-mZInGgCo"
CHAT_ID = "5412252920"

async def reply_hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    text = update.message.text.lower()
    
    if "hello" in text:
        user_name = update.message.from_user.first_name
        
        await update.message.reply_text(
            f"😊 Hello {user_name}\nYou are welcome!"
        )

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_hello))

print("Bot Running...")

app.run_polling()
