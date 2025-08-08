import os
import pytz
import logging
from datetime import datetime, time, timedelta
from fastapi import FastAPI
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
# 自动回退到 Render 外网域名
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
TARGET_CHAT_ID = -1001748407396  # 群 ID

# Signal 数据
signals = {
    "🐯 Fortuna do Tigre 🐯": ["Sinal 1", "Sinal 2"],
    "🐇 Fortuna do Coelho 🐇": ["Sinal A", "Sinal B"],
    "🐁 Fortuna do Rato 🐁": ["Sinal X", "Sinal Y"],
    "🐂 Fortuna do Boi 🐂": ["Sinal M", "Sinal N"],
    "🐲 Fortuna do Dragão 🐲": ["Sinal P", "Sinal Q"],
}

# 创建 FastAPI
app = FastAPI()

# Bot 实例
bot = Bot(token=BOT_TOKEN)

# 每小时整点发送 signals
async def send_signals(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(pytz.timezone("Asia/Phnom_Penh")).strftime("%Y-%m-%d %H:%M:%S")
    message = f"📢 信号更新 ({now})\n\n"
    for name, sigs in signals.items():
        message += f"{name}\n" + "\n".join(sigs) + "\n\n"
    await bot.send_message(chat_id=TARGET_CHAT_ID, text=message)
    logger.info("✅ 已发送信号到群")

# /start 命令
async def start(update, context):
    await update.message.reply_text("Bot 正在运行，每小时会自动发送 signals 到群。")

# 主程序
async def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .updater(None)
        .build()
    )

    # 绑定命令
    application.add_handler(CommandHandler("start", start))

    # 设置 webhook
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    logger.info(f"✅ Webhook 已设置为 {WEBHOOK_URL}/webhook")

    # 定时任务：每小时整点
    tz = pytz.timezone("Asia/Phnom_Penh")
    now = datetime.now(tz)
    first_run = tz.localize(datetime.combine(now.date(), time(now.hour))) + timedelta(hours=1)
    application.job_queue.run_repeating(send_signals, interval=3600, first=first_run)

    # FastAPI 接口
    @app.post("/webhook")
    async def webhook_handler(update: dict):
        await application.update_queue.put(update)
        return {"status": "ok"}

    await application.initialize()
    await application.start()
    await application.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
