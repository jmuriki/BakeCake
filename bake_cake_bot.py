import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Стартовое сообщение.")


def main():
    load_dotenv()
    token = os.environ["TG_BOT_KEY"]
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    updater.start_polling(1)
    updater.idle()


if __name__ == "__main__":
    main()
