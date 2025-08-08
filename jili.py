# jili.py
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)
import pytz
import random
import logging
import os

from fastapi import FastAPI, Request
import uvicorn

# ✅ 日志配置
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ✅ Token & Webhook
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN 环境变量未设置")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://your-render-url.onrender.com{WEBHOOK_PATH}"  # 改成你的 Render 域名

# ✅ FastAPI 应用
app = FastAPI()

# ✅ Telegram Application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# === 命令处理 ===
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive!")

# === 错误处理器 ===
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("🚨 Exception while handling update:", exc_info=context.error)

# === 定时任务函数 ===
async def send_signals(context: ContextTypes.DEFAULT_TYPE):
    try:
        signals = {
            "🐯 Fortuna do Tigre 🐯": [],
            "🐇 Fortuna do Coelho 🐇": [],
            "🐁 Fortuna do Rato 🐁": [],
            "🐂 Fortuna do Boi 🐂": [],
            "🐲 Fortuna do Dragão 🐲": [],
        }

        num_times = 6
        brazil_timezone = pytz.timezone('America/Sao_Paulo')
        current_time = datetime.now(brazil_timezone)
        start_time = current_time.replace(minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)

        for animal in signals.keys():
            available_times = set()
            while len(available_times) < num_times:
                random_minutes = random.randint(0, 59)
                signal_time = start_time + timedelta(minutes=random_minutes)
                if (
                    signal_time >= current_time
                    and signal_time < end_time
                    and signal_time.strftime("%H:%M") not in available_times
                ):
                    available_times.add(signal_time.strftime("%H:%M"))

            signals[animal] = sorted(available_times)

        message = """<b>🚨 Jili707 Alerta de Sinais Estratégias: Horário Pagantes ⏰.</b>

<b>⏰ Fuso Horário: Brasil - São Paulo ⏰.</b>

<b>👉🏻 Confira nosso site oficial: <a href='https://app027.jili707.com'>https://app027.jili707.com</a></b>\n\n"""

        for animal, times in signals.items():
            message += f"<b>{animal}\n</b>\n"
            message += "<pre>"
            for time in times:
                message += f"✅ <b>{time}</b>  "
            message += "</pre>\n\n"

        next_signal_time = current_time + timedelta(hours=1)
        message += f"<b>⚠️ O próximo sinal será às {next_signal_time.strftime('%H:%M')} ⏰</b>"

        TARGET_CHAT_ID = -1001748407396  # 改成你的频道 ID

        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=message,
            parse_mode='HTML',
            disable_notification=True
        )
        logging.info("✅ Sinais enviados com sucesso.")

    except Exception as e:
        logging.error(f"❌ Erro ao enviar sinais: {e}")

# === 启动时执行（设置 Webhook & 定时任务） ===
@app.on_event("startup")
async def on_startup():
    await application.bot.delete_webhook()
    logging.info("🧹 旧 webhook 已清除")

    await application.bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook set: {WEBHOOK_URL}")

    # 启动 Application
    await application.initialize()
    await application.start()

    # 设置定时任务
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(brazil_tz)
    seconds_until_next_hour = (60 - now.minute) * 60 - now.second

    application.job_queue.run_repeating(
        send_signals,
        interval=3600,
        first=timedelta(seconds=seconds_until_next_hour)
    )
    logging.info("⏰ 定时任务已启动")

# === Telegram Webhook 接收 ===
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    update = await request.json()
    await application.update_queue.put(Update.de_json(update, application.bot))
    return {"ok": True}

# === 健康检查 ===
@app.get("/")
async def root():
    return {"status": "ok"}

# === 注册命令 ===
application.add_handler(CommandHandler("ping", ping))
application.add_error_handler(error_handler)

# === 启动 uvicorn ===
if __name__ == "__main__":
    uvicorn.run("jili:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
