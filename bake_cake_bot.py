import os

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler


def build_menu(
        buttons,
        n_columns,
        header_buttons=None,
        footer_buttons=None
    ):
    menu = [buttons[i:i+n_columns] for i in range(0, len(buttons), n_columns)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def start(update: Update, context: CallbackContext):
    pd_buttons = [
        InlineKeyboardButton("Подтверждаю)", callback_data="True"),
        InlineKeyboardButton("Нет, нет и нет!", callback_data="False"),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(pd_buttons, n_columns=2))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Здравствуйте. Подтвердите, пожалуйста, своё согласие на обработку персональных данных:", reply_markup=reply_markup)


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
