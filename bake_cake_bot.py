import os
import telegram
import telegram.ext

from pathlib import Path
from dotenv import load_dotenv


buttons = {}


def help_command(update, _):
    update.message.reply_text("Используйте `/start` для начала или возврата к первому шагу.")


def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Здравствуйте) Рады, что Вы нас посетили!",
    )
    get_permission(update, context)


def get_permission(update: telegram.Update, context: telegram.ext.CallbackContext):
    with open(Path("./Согласие на обработку ПД.pdf"), "rb") as file:
        context.bot.send_document(chat_id=update.effective_chat.id, document=file)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Изучите, пожалуйста, бланк Согласия на обработку персональных данных (далее - ПД), представленный выше.",
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Согласны на обработку Ваших персональных данных?",
    )
    keyboard = [
        [
            telegram.KeyboardButton("Разрешаю обработку моих ПД."),
            telegram.KeyboardButton("Запрещаю обработку моих ПД."),
        ],
        [telegram.KeyboardButton("Для начала, хотел бы взглянуть на торты...")],
    ]
    show_the_keyboard(update, context, keyboard)


def show_the_keyboard(update: telegram.Update, context: telegram.ext.CallbackContext, keyboard):
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Для продолжения выберите один из предложенных вариантов:",
        reply_markup=reply_markup,
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="(нажмите на значок клавиатуры, чтобы развернуть меню, если оно не отображается)",
    )


def launch_next_step(update: telegram.Update, context: telegram.ext.CallbackContext):
    user_answer = update.message.text
    buttons.get(user_answer)(update, context)


def if_allowed(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Благодарим за доверие)",
    )
    show_main_menu(update, context)


def if_forbidden(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="На этапе оформления заказа нам будет не обойтись без Вашего согласия.",
    )
    show_main_menu(update, context)


def show_main_menu(update: telegram.Update, context: telegram.ext.CallbackContext):
    keyboard = [
        [telegram.KeyboardButton("Посмотреть каталог")],
        [
            telegram.KeyboardButton("Создать торт"),
            telegram.KeyboardButton("Удивите меня"),
        ],
        [
            telegram.KeyboardButton("Повторить заказ"),
            telegram.KeyboardButton("Где мой заказ?"),
        ],
        [
            telegram.KeyboardButton("Связаться с нами"),
            telegram.KeyboardButton("Вернуться в начало"),
        ],
    ]
    show_the_keyboard(update, context, keyboard)


def show_catalogue(update: telegram.Update, context: telegram.ext.CallbackContext):
    keyboard = [
        [telegram.KeyboardButton("Создать торт")],
        [telegram.KeyboardButton("Удивите меня")],
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard)


def create_cake(update: telegram.Update, context: telegram.ext.CallbackContext):
    keyboard = [
        [telegram.KeyboardButton("Выбрать форму")],
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard)


def surprise_client(update: telegram.Update, context: telegram.ext.CallbackContext):
    keyboard = [
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard)


def repeat_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    keyboard = [
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard)


def show_current_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Информация о заказе:",
    )
    keyboard = [
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard)


def contact_support(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Контакты:",
    )
    keyboard = [
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard)


def choose_the_form(update: telegram.Update, context: telegram.ext.CallbackContext):
    keyboard = [
        [telegram.KeyboardButton("Посмотреть каталог")],
        [
            telegram.KeyboardButton("Круг"),
            telegram.KeyboardButton("Сердце")
        ],
        [
            telegram.KeyboardButton("Прямоугольник"),
            telegram.KeyboardButton("Квадрат")
        ],
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard)


def main():
    load_dotenv()
    token = os.environ["TG_BOT_KEY"]
    buttons.update({
        "Вернуться в начало": start,
        "Разрешаю обработку моих ПД.": if_allowed,
        "Запрещаю обработку моих ПД.": if_forbidden,
        "Для начала, хотел бы взглянуть на торты...": show_main_menu,
        "Вернуться в основное меню": show_main_menu,
        "Посмотреть каталог": show_catalogue,
        "Создать торт": create_cake,
        "Удивите меня": surprise_client,
        "Повторить заказ": repeat_order,
        "Где мой заказ?": show_current_order,
        "Связаться с нами": contact_support,
        "Выбрать форму": choose_the_form,
    })
    updater = telegram.ext.Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(telegram.ext.CommandHandler('help', help_command))
    dispatcher.add_handler(telegram.ext.CommandHandler('start', start))
    dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, launch_next_step))
    updater.start_polling(1)
    updater.idle()


if __name__ == "__main__":
    main()
