
import os
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
MODEL = os.getenv("OPENAI_MODEL", "gpt-5")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

conversations = {}

SYSTEM_PROMPT = """
أنت GPT-5 العراقي 🇮🇶.
تحدث باللهجة العراقية الطبيعية عند مخاطبة العراقيين.
افهم العربية والإنجليزية.
ساعد المستخدم في البرمجة والدراسة والألعاب
والتحليل والكتابة والمعلومات العامة.
كن ذكياً ودقيقاً وودوداً.
لا تخترع المعلومات إذا لم تكن متأكداً.
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "هلا بيك حبيبي 🇮🇶\n"
        "أنا GPT-5 العراقي 🤖\n\n"
        "اسألني أي سؤال حتى أساعدك!\n"
        "اكتب /reset لمسح المحادثة."
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conversations.pop(update.effective_user.id, None)
    await update.message.reply_text(
        "تم مسح المحادثة 🧹\nنبدأ من جديد!"
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text

    history = conversations.setdefault(user_id, [])
    history.append({
        "role": "user",
        "content": message
    })

    try:
        response = await client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=history
        )

        answer = response.output_text or "ما قدرت أجهز جواب."

        history.append({
            "role": "assistant",
            "content": answer
        })

        conversations[user_id] = history[-10:]

        for i in range(0, len(answer), 4000):
            await update.message.reply_text(answer[i:i + 4000])

    except Exception:
        logger.exception("AI request failed")

        if history and history[-1]["role"] == "user":
            history.pop()

        await update.message.reply_text(
            "صار خطأ بالاتصال 🤖\n"
            "حاول مرة ثانية بعد قليل."
        )


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    logger.info("GPT-5 Iraqi is running!")

    app.run_polling()


if __name__ == "__main__":
    main()
