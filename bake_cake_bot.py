import os
import telegram
import telegram.ext

from pathlib import Path
from dotenv import load_dotenv


def button(update, _):
    query = update.callback_query
    variant = query.data
    query.answer()
    query.edit_message_text(text=variant)
    return variant


def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    start_keyboard = [
        [
            telegram.InlineKeyboardButton("Подтверждаю)", callback_data="Вы согласились на обработку ПД."),
            telegram.InlineKeyboardButton("Нет, нет и нет!", callback_data="Вы отказались от обработки ПД."),
        ],
        [telegram.InlineKeyboardButton("Для начала, хотел бы взглянуть на торты...", callback_data="Сейчас покажем наш ассортимент:")],
    ]
    reply_markup = telegram.InlineKeyboardMarkup(start_keyboard)
    with open(Path("./Согласие на обработку ПД.pdf"), "rb") as file:
        context.bot.send_document(chat_id=update.effective_chat.id, document=file)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Здравствуйте. Изучите, пожалуйста, бланк согласия на обработку персональных данных (далее - ПД), представленный выше.",
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы согласны на обработку персональных данных? Для продолжения выберите один из вариантов:",
        reply_markup=reply_markup
    )


def help_command(update, _):
    update.message.reply_text("Используйте `/start` для начала или возврата к первому шагу.")


def main():
    load_dotenv()
    token = os.environ["TG_BOT_KEY"]
    updater = telegram.ext.Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(telegram.ext.CommandHandler('help', help_command))
    dispatcher.add_handler(telegram.ext.CommandHandler('start', start))
    variant = dispatcher.add_handler(telegram.ext.CallbackQueryHandler(button))
    updater.start_polling(1)
    updater.idle()


if __name__ == "__main__":
    main()
