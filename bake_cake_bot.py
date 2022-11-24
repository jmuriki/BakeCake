import os
import telegram
import telegram.ext

from pathlib import Path
from dotenv import load_dotenv


def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    with open(Path("./Согласие на обработку ПД.pdf"), "rb") as file:
        context.bot.send_document(chat_id=update.effective_chat.id, document=file)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Здравствуйте. Изучите, пожалуйста, бланк согласия на обработку персональных данных (далее - ПД), представленный выше.",
    )
    start_keyboard = [
        [
            telegram.KeyboardButton("Разрешаю обработку моих ПД."),
            telegram.KeyboardButton("Запрещаю обработку моих ПД."),
        ],
        [telegram.KeyboardButton("Для начала, хотел бы взглянуть на торты...")],
    ]
    reply_markup = telegram.ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы согласны на обработку персональных данных? Для продолжения выберите один из предложенных вариантов:",
        reply_markup=reply_markup,
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
    updater.start_polling(1)
    updater.idle()


if __name__ == "__main__":
    main()
