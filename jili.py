from datetime import datetime, timedelta
from telegram.ext import Updater, CallbackContext
import pytz
import random
from telegram import Update
import logging

logging.basicConfig(level=logging.DEBUG)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = '6588452433:AAFf0uLB8y6wkA3hi0nU8o78HWla7wsdk9I'

# Define the function to send signals
def send_signals(context: CallbackContext):
    try:
        # Define the signals for each animal (replace with your signal generation logic)
        signals = {
            "🐯 Fortuna do Tigre 🐯": [],
            "🐇 Fortuna do Coelho 🐇": [],
            "🐁 Fortuna do Rato 🐁": [],
            "🐂 Fortuna do Boi 🐂": [],
            "🐲 Fortuna do Dragão 🐲": [],
        }

        # Define the number of future times to generate for each animal
        num_times = 6  # Change to 6 for a 6x6 grid

        # Get the current time in Brazil's timezone
        brazil_timezone = pytz.timezone('America/Sao_Paulo')
        current_time = datetime.now(brazil_timezone)

        # Calculate the start time for the current hour
        start_time = current_time.replace(minute=0, second=0, microsecond=0)

        # Calculate the end time for the next hour
        end_time = start_time + timedelta(hours=1)

        # Generate future times for each animal within the same hour
        for animal in signals.keys():
            available_times = set()  # Use a set to ensure unique times
            while len(available_times) < num_times:
                # Generate a random number of minutes within the hour
                random_minutes = random.randint(0, 59)
                # Create a new time by adding the random minutes
                signal_time = start_time + timedelta(minutes=random_minutes)
                # Check if the generated time is in the future and not already used
                if (
                    signal_time >= current_time
                    and signal_time < end_time
                    and signal_time.strftime("%H:%M") not in available_times
                ):
                    available_times.add(signal_time.strftime("%H:%M"))

            # Convert the set to a list and sort it
            sorted_times = sorted(available_times)
            signals[animal] = sorted_times

        # Construct the message
        message = """<b>🚨 Jili707 Alerta de Sinais Estratégias: Horário Pagantes ⏰.</b>

<b>⏰ Fuso Horário: Brasil - São Paulo ⏰.</b>

<b>👉🏻 Confira nosso site oficial: <a href='https://app027.jili707.com'>https://app027.jili707.com</a></b>\n\n"""

        for animal, times in signals.items():
            message += f"<b>{animal}\n</b>\n"
            message += "<pre>"  # Use <pre> tag for fixed-width grid
            for time in times:
                message += f"✅ <b>{time}</b>  "
            message += "</pre>\n\n"

        # Calculate the time of the next signal
        next_signal_time = current_time + timedelta(hours=1)
        message += f"<b>⚠️ O próximo sinal será às {next_signal_time.strftime('%H:%M')} ⏰</b>"

        # Send the message with HTML formatting
        context.bot.send_message(
            chat_id=-1001748407396, text=message, parse_mode='HTML', disable_notification=True
        )

    except Exception as e:
        # Handle exceptions gracefully, you can log the error or take other actions
        print(f"An error occurred: {e}")

# Define the main function
def main():
    updater = Updater(token=bot_token, use_context=True)
    job_queue = updater.job_queue

    # Calculate the time remaining until the next hour
    current_time = datetime.now(pytz.timezone('America/Sao_Paulo'))
    time_until_next_hour = (3600 - current_time.minute * 60 - current_time.second) % 3600

    # Schedule the send_signals function to run every hour, starting from the next hour
    job_queue.run_repeating(send_signals, interval=3600, first=time_until_next_hour)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
