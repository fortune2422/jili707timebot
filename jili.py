import os
import logging
import pytz
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 日志设置
logging.basicConfig(level=logging.INFO)

# 环境变量
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"

# 目标群 ID（改成你自己的）
TARGET_CHAT_ID = -1001748407396

# 定时任务：发送信号
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
        brazil_timezone = pytz.timezone("America/Sao_Paulo")
        current_time = datetime.now(brazil_timezone)
        start_time = current_time.replace(minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)

        for animal in signals:
            available_times = set()
            while len(available_times) < num_times:
                random_minutes = random.randint(0, 59)
                signal_time = start_time + timedelta(minutes=random_minutes)
                if (
                    current_time <= signal_time < end_time
                    and signal_time.strftime("%H:%M") not in available_times
                ):
                    available_times.add(signal_time.strftime("%H:%M"))
            signals[animal] = sorted(available_times)

        message = (
            "<b>🚨 Jili707 Alerta de Sinais Estratégias: Horário Pagantes ⏰.</b>\n\n"
            "<b>⏰ Fuso Horário: Brasil - São Paulo ⏰.</b>\n\n"
            "<b>👉🏻 Confira nosso site oficial: "
            "<a href='https://app027.jili707.com'>https://app027.jili707.com</a></b>\n\n"
        )

        for animal, times in signals.items():
            message += f"<b>{animal}</b>\n<pre>"
            message += "  ".join([f"✅ {t}" for t in times])
            message += "</pre>\n\n"

        next_signal_time = current_time + timedelta(hours=1)
        message += f"<b>⚠️ O próximo sinal será às {next_signal_time.strftime('%H:%M')} ⏰</b>"

        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=message,
            parse_mode="HTML",
            disable_notification=True,
        )
    except Exception as e:
        logging.error(f"❌ 发送信号出错: {e}")

# 启动时设置定时任务
async def on_startup(app):
    brazil_time = datetime.now(pytz.timezone("America/Sao_Paulo"))
    seconds_until_next_hour = (60 - brazil_time.minute) * 60 - brazil_time.second

    app.job_queue.run_repeating(
        send_signals,
        interval=3600,
        first=timedelta(seconds=seconds_until_next_hour),
    )
    logging.info("✅ 定时任务已启动")

# ping 命令
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive!")

def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .build()
    )

    app.add_handler(CommandHandler("ping", ping))

    logging.info(f"🚀 启动 Webhook: {WEBHOOK_URL}")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
