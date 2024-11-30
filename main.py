import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import pandas as pd
import sqlite3
from datetime import datetime
from corev2 import rag_chain,llm 
from store import handle_message
from dotenv import load_dotenv
import os
load_dotenv()
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I can resolve your doubts related to the Indian Constitution!")

async def main_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_message(update,context)
    # result = rag_chain.invoke({"input": update.effective_message.text})
    result = llm.invoke(f'You are a assistant specialized on the Indian Constitution. Give concise answer to the following question(40-50 words)-{update.effective_message.text}')
    # print(result)
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=str(result['answer']))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(result.content))


async def handle_non_text(update, context):
    """Handle any non-text messages"""
    await update.message.reply_text("Only text queries expected")

if __name__ == '__main__':
    main_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), main_func)
    application = ApplicationBuilder().token(os.environ.get('TOKEN')).build()
    start_handler = CommandHandler('start', start)

    application.add_handler(
        MessageHandler(
            ~filters.TEXT,
            handle_non_text
        )
    )
    application.add_handler(main_handler)
    application.add_handler(start_handler)
    application.run_polling()