import os

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler


def button(update, _):
    query = update.callback_query
    variant = query.data
    query.answer()
    query.edit_message_text(text=f"Вы {variant}")


def start(update: Update, context: CallbackContext):
    start_keyboard = [
        [
            InlineKeyboardButton("Подтверждаю)", callback_data="согласились на обработку ПД."),
            InlineKeyboardButton("Нет, нет и нет!", callback_data="отказались от обработки ПД."),
        ],
        [InlineKeyboardButton("Хотел бы для начала взглянуть на торты.", callback_data="захотели изучить ассортимент.")],
    ]
    reply_markup = InlineKeyboardMarkup(start_keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Здравствуйте. Подтвердите, пожалуйста, своё согласие на обработку персональных данных (далее - ПД):",
        reply_markup=reply_markup
    )


def help_command(update, _):
    update.message.reply_text("Используйте `/start` для начала / возврата к первому шагу.")


def main():
    load_dotenv()
    token = os.environ["TG_BOT_KEY"]
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    updater.start_polling(1)
    updater.idle()


if __name__ == "__main__":
    main()
