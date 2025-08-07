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

from fastapi import FastAPI, Request
import uvicorn

# ✅ 设置日志输出
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ✅ Telegram Bot Token 和 Webhook 路径
bot_token = os.getenv("BOT_TOKEN")  # 建议放入环境变量
WEBHOOK_PATH = f"/webhook/{bot_token}"
WEBHOOK_URL = f"https://your-render-url.onrender.com{WEBHOOK_PATH}"  # ⛳ 修改为你的 Render 域名

# ✅ FastAPI 应用实例
app = FastAPI()

# ✅ Telegram Application
application = ApplicationBuilder().token(bot_token).build()

# ✅ /ping 命令响应
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive!")

# ✅ 错误处理器
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("🚨 Exception while handling update:", exc_info=context.error)

# ✅ 定时任务函数
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

        TARGET_CHAT_ID = -1001748407396  # ✅ 替换为你的频道 ID

        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=message,
            parse_mode='HTML',
            disable_notification=True
        )
        logging.info("✅ Sinais enviados com sucesso.")

    except Exception as e:
        logging.error(f"❌ Erro ao enviar sinais: {e}")

# ✅ 机器人启动后执行任务（设定定时发送）
async def on_startup():
    await application.bot.delete_webhook()
    logging.info("🧹 旧 webhook 已清除")
    
    # 设置 webhook
    await application.bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook set: {WEBHOOK_URL}")

    # 初始化 Application
    await application.initialize()
    await application.start()

    # 设置定时任务
    job_queue = application.job_queue
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(brazil_tz)
    seconds_until_next_hour = (60 - now.minute) * 60 - now.second

    job_queue.run_repeating(
        send_signals,
        interval=3600,
        first=timedelta(seconds=seconds_until_next_hour)
    )
    logging.info("⏰ Agendador de sinais iniciado.")

# ✅ FastAPI 接收 Telegram 推送
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    update = await request.json()
    await application.update_queue.put(Update.de_json(update, application.bot))
    return {"ok": True}

# ✅ Render 健康检查用（非必要）
@app.get("/")
async def root():
    return {"status": "ok"}

# ✅ 注册 handler 和错误处理器
application.add_handler(CommandHandler("ping", ping))
application.add_error_handler(error_handler)

# ✅ 启动入口
if __name__ == "__main__":
    import asyncio
    asyncio.run(on_startup())
    uvicorn.run("jili:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
