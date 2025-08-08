# jilibot.py
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
import asyncio

from fastapi import FastAPI, Request
import uvicorn

# =============================
# 📌 基础配置
# =============================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")  # 从环境变量读取
if not BOT_TOKEN:
    raise ValueError("❌ 请先设置 BOT_TOKEN 环境变量！")

RENDER_URL = os.getenv("RENDER_URL", "https://your-render-url.onrender.com")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "-1001748407396"))  # 默认频道 ID

# =============================
# 📌 FastAPI + Telegram Bot 实例
# =============================
app = FastAPI()
application = ApplicationBuilder().token(BOT_TOKEN).build()

# =============================
# 📌 /ping 测试命令
# =============================
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive!")

# =============================
# 📌 错误处理
# =============================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("🚨 Exception while handling update:", exc_info=context.error)

# =============================
# 📌 定时任务：发送信号
# =============================
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
        brazil_tz = pytz.timezone('America/Sao_Paulo')
        current_time = datetime.now(brazil_tz)
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

        message = (
            "<b>🚨 Jili707 Alerta de Sinais Estratégias: Horário Pagantes ⏰.</b>\n\n"
            "<b>⏰ Fuso Horário: Brasil - São Paulo ⏰.</b>\n\n"
            "<b>👉🏻 Confira nosso site oficial: <a href='https://app027.jili707.com'>https://app027.jili707.com</a></b>\n\n"
        )

        for animal, times in signals.items():
            message += f"<b>{animal}</b>\n<pre>"
            for time in times:
                message += f"✅ <b>{time}</b>  "
            message += "</pre>\n\n"

        next_signal_time = current_time + timedelta(hours=1)
        message += f"<b>⚠️ O próximo sinal será às {next_signal_time.strftime('%H:%M')} ⏰</b>"

        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=message,
            parse_mode='HTML',
            disable_notification=True
        )
        logging.info("✅ Sinais enviados com sucesso.")

    except Exception as e:
        logging.error(f"❌ Erro ao enviar sinais: {e}")

# =============================
# 📌 启动时设置 Webhook & 定时任务
# =============================
async def on_startup():
    await application.initialize()
    await application.start()

    # 清除旧 webhook
    await application.bot.delete_webhook()
    logging.info("🧹 旧 webhook 已清除")

    # 设置新 webhook
    await application.bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook 已设置: {WEBHOOK_URL}")

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

# =============================
# 📌 FastAPI 路由
# =============================
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    update = await request.json()
    await application.update_queue.put(Update.de_json(update, application.bot))
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

# =============================
# 📌 注册 Handler
# =============================
application.add_handler(CommandHandler("ping", ping))
application.add_error_handler(error_handler)

# =============================
# 📌 主程序入口
# =============================
if __name__ == "__main__":
    asyncio.run(on_startup())
    uvicorn.run("jilibot:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
