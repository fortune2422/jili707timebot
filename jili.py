# jilibot.py （把你原来的文件替换为这个）
import os
import pytz
import logging
import asyncio
from datetime import datetime, time, timedelta
from fastapi import FastAPI, Request
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("请在 Render 环境变量中设置 BOT_TOKEN")

# 自动回退 WEBHOOK_URL（如果你没有在 env 里手动写 WEBHOOK_URL，就使用 Render 提供的域名）
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "-1001748407396"))  # 允许通过 env 覆盖

# 巴西圣保罗时区
TZ = pytz.timezone("America/Sao_Paulo")

signals = {
    "🐯 Fortuna do Tigre 🐯": ["Sinal 1", "Sinal 2"],
    "🐇 Fortuna do Coelho 🐇": ["Sinal A", "Sinal B"],
    "🐁 Fortuna do Rato 🐁": ["Sinal X", "Sinal Y"],
    "🐂 Fortuna do Boi 🐂": ["Sinal M", "Sinal N"],
    "🐲 Fortuna do Dragão 🐲": ["Sinal P", "Sinal Q"],
}

app = FastAPI()
bot = Bot(token=BOT_TOKEN)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

async def send_signals(context: ContextTypes.DEFAULT_TYPE = None):
    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    message = f"📢 信号更新 ({now})\n\n"
    for name, sigs in signals.items():
        message += f"{name}\n" + "\n".join(sigs) + "\n\n"
    try:
        await bot.send_message(chat_id=TARGET_CHAT_ID, text=message)
        logger.info(f"✅ 已发送信号到群 ({now})")
    except Exception as e:
        logger.exception("发送信号失败: %s", e)

async def start_cmd(update, context):
    await update.message.reply_text("Bot 正在运行，每小时会自动发送 signals 到群。")

# 在 FastAPI 的 startup 钩子里初始化并启动 telegram Application
@app.on_event("startup")
async def on_startup():
    logger.info("FastAPI startup: 初始化 Telegram Application ...")
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .updater(None)  # 使用 webhook（不启用 polling/updater）
        .build()
    )

    # 保存到 app.state 以便 webhook handler 使用
    app.state.telegram_app = application

    # 注册命令
    application.add_handler(CommandHandler("start", start_cmd))

    # 计算第一次整点的延迟（秒）
    now = datetime.now(TZ)
    next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
    first_delay_seconds = (next_hour - now).total_seconds()
    if first_delay_seconds < 0:
        first_delay_seconds = 0

    # 在启动时立即发送一条（用于测试）
    asyncio.create_task(send_signals())

    # 安排 JobQueue：first 参数为延迟秒数
    application.job_queue.run_repeating(send_signals, interval=3600, first=first_delay_seconds)

    # 设置 webhook（确保 WEBHOOK_URL 以 https:// 开头）
    webhook_full = f"{WEBHOOK_URL}/webhook"
    await application.bot.set_webhook(webhook_full)
    logger.info("✅ 已设置 webhook: %s", webhook_full)

    # 将 FastAPI 的 /webhook 请求投递到 telegram application 的 update_queue
    @app.post("/webhook")
    async def webhook_handler(request: Request):
        data = await request.json()
        try:
            await application.update_queue.put(data)
        except Exception:
            # fallback: put_nowait
            application.update_queue.put_nowait(data)
        return {"status": "ok"}

    # 启动 telegram application（非阻塞）
    await application.initialize()
    await application.start()
    logger.info("🚀 Telegram Application 已启动 (webhook 模式)")

# 在 FastAPI shutdown 时停止 telegram application
@app.on_event("shutdown")
async def on_shutdown():
    application = getattr(app.state, "telegram_app", None)
    if application:
        logger.info("Shutting down Telegram Application ...")
        try:
            await application.stop()
            await application.shutdown()
        except Exception:
            logger.exception("Shutdown Telegram Application 时出错")

if __name__ == "__main__":
    # 绑定 Render 提供的 PORT（默认 8000）
    port = int(os.environ.get("PORT", 8000))
    # 运行 uvicorn（这会马上绑定端口，Render 扫描就能检测到）
    uvicorn.run("jilibot:app" if __name__ == "__main__" else "jilibot:app",
                host="0.0.0.0", port=port, log_level="info")
