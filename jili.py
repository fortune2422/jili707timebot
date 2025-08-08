import os
import pytz
import logging
from datetime import datetime, time, timedelta
from fastapi import FastAPI, Request
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import uvicorn
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
TARGET_CHAT_ID = -1001748407396  # 你的群 ID

# 测试信号数据
signals = {
    "🐯 Fortuna do Tigre 🐯": ["Sinal 1", "Sinal 2"],
    "🐇 Fortuna do Coelho 🐇": ["Sinal A", "Sinal B"],
    "🐁 Fortuna do Rato 🐁": ["Sinal X", "Sinal Y"],
    "🐂 Fortuna do Boi 🐂": ["Sinal M", "Sinal N"],
    "🐲 Fortuna do Dragão 🐲": ["Sinal P", "Sinal Q"],
}

# FastAPI 应用
app = FastAPI()
bot = Bot(token=BOT_TOKEN)

# 发送信号函数
async def send_signals(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S")
    message = f"📢 信号更新 ({now})\n\n"
    for name, sigs in signals.items():
        message += f"{name}\n" + "\n".join(sigs) + "\n\n"
    await bot.send_message(chat_id=TARGET_CHAT_ID, text=message)
    logger.info("✅ 已发送信号到群")

# /start 命令
async def start(update, context):
    await update.message.reply_text("Bot 正在运行，每小时会自动发送 signals 到群。")

# 初始化 Application
async def setup_application():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .updater(None)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

    tz = pytz.timezone("America/Sao_Paulo")
    now = datetime.now(tz)

    # ⏱ 启动时立即执行一次
    asyncio.create_task(send_signals(None))

    # ⏱ 计算下一个整点
    first_run = tz.localize(datetime.combine(now.date(), time(now.hour))) + timedelta(hours=1)

    # 每小时执行一次
    application.job_queue.run_repeating(send_signals, interval=3600, first=first_run)

    @app.post("/webhook")
    async def webhook_handler(request: Request):
        data = await request.json()
        await application.update_queue.put(data)
        return {"status": "ok"}

    # 健康检查
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    await application.initialize()
    await application.start()
    logger.info("🚀 Bot 已启动（Webhook 模式）")

if __name__ == "__main__":
    asyncio.run(setup_application())
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
