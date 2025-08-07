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
import asyncio

logging.basicConfig(level=logging.DEBUG)

bot_token = '6588452433:AAFf0uLB8y6wkA3hi0nU8o78HWla7wsdk9I'

# async function to send signals
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

            sorted_times = sorted(available_times)
            signals[animal] = sorted_times

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

        await context.bot.send_message(
            chat_id=-1001748407396,
            text=message,
            parse_mode='HTML',
            disable_notification=True
        )

    except Exception as e:
        logging.error(f"An error occurred: {e}")

async def main():
    app = ApplicationBuilder().token(bot_token).build()

    # 获取 job queue
    job_queue = app.job_queue

    # 当前时间
    current_time = datetime.now(pytz.timezone('America/Sao_Paulo'))
    seconds_until_next_hour = (60 - current_time.minute) * 60 - current_time.second

    # 安排任务：每小时一次，从下个整点开始
    job_queue.run_repeating(
        send_signals,
        interval=3600,
        first=timedelta(seconds=seconds_until_next_hour)
    )

    # 启动 bot
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
