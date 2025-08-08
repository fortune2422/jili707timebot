import os
import pytz
import logging
from fastapi import FastAPI, Request
from telegram import Bot
from telegram.ext import Application, CommandHandler
from telegram.ext import ApplicationBuilder
from telegram.ext import ContextTypes
from datetime import datetime

# 日志
logging.basicConfig(level=logging.INFO)

# 环境变量
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TARGET_CHAT_ID = -1001748407396  # 群ID

# 定义 signals
signals = {
    "🐯 Fortuna do Tigre 🐯": [],
    "🐇 Fortuna do Coelho 🐇": [],
    "🐁 Fortuna do Rato 🐁": [],
    "🐂 Fortuna do Boi 🐂": [],
    "🐲 Fortuna do Dragão 🐲": [],
}

# FastAPI 用于 webhook
app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    await application.update_queue.put(await request.json())
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "ok"}

# 定时任务：每小时发送 signals
async def send_signals(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(pytz.timezone("Asia/Bangkok")).strftime("%Y-%m-%d %H:%M")
    message = f"📢 Sinais - {now}\n\n"
    for animal, data in signals.items():
        message += f"{animal}:\n"
        if data:
            for sig in data:
                message += f" - {sig}\n"
        else:
            message += " (Sem sinais no momento)\n"
        message += "\n"

    await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=message)

# /start 命令
async def start(update, context):
    await update.message.reply_text("✅ Bot está ativo e enviará sinais a cada hora!")

# 启动 Application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# 添加命令
application.add_handler(CommandHandler("start", start))

# 添加定时任务（每小时整点）
application.job_queue.run_repeating(
    send_signals,
    interval=3600,
    first=0,  # 启动时立即执行一次
    name="hourly_signals"
)

# 启动 Webhook
async def main():
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    logging.info(f"Webhook set to {WEBHOOK_URL}/webhook")

import asyncio
asyncio.get_event_loop().run_until_complete(main())

# 启动 FastAPI（Uvicorn）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
