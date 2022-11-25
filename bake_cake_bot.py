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
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Для продолжения, следуйте нашим подсказкам, выбирая один из предложенных пунктов меню:",
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="(нажмите на значок клавиатуры, в поле ввода текста, чтобы развернуть меню, если оно не отображается)",
    )
    get_permission(update, context)


def get_permission(update: telegram.Update, context: telegram.ext.CallbackContext):
    with open(Path("./Согласие на обработку ПД.pdf"), "rb") as file:
        context.bot.send_document(chat_id=update.effective_chat.id, document=file)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Изучите, пожалуйста, бланк Согласия на обработку персональных данных (далее - ПД), представленный выше.",
    )
    message = "Вы согласны на обработку Ваших персональных данных?"
    keyboard = [
        [
            telegram.KeyboardButton("Разрешаю обработку моих ПД."),
            telegram.KeyboardButton("Запрещаю обработку моих ПД."),
        ],
        [telegram.KeyboardButton("Для начала, хотел бы взглянуть на торты...")],
    ]
    show_the_keyboard(update, context, keyboard, message)


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
    message = "Вы находитесь в основном меню."
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
    show_the_keyboard(update, context, keyboard, message)


def show_catalogue(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Каталог наших тортов:"
    keyboard = [
        [telegram.KeyboardButton("Создать торт")],
        [telegram.KeyboardButton("Удивите меня")],
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def create_cake(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Итак, давайте приступим:"
    keyboard = [
        [telegram.KeyboardButton("Выбрать форму")],
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def surprise_client(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Опа!"
    keyboard = [
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def repeat_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Предыдущие заказы:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def show_current_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Информация по текущему заказу:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def contact_support(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Контакты службы поддержки:"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Контакты:",
    )
    keyboard = [
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_the_form(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Выберите желаемую форму:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к просмотру каталога")],
        [
            telegram.KeyboardButton("Круг           (+400р)"),
            telegram.KeyboardButton("Квадрат        (+600р)"),
            telegram.KeyboardButton("Прямоугольник  (+1000р)"),
        ],
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_levels_number(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Выберите количество уровней:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору формы")],
        [
            telegram.KeyboardButton("1 уровень      (+400р)"),
            telegram.KeyboardButton("2 уровня       (+750р)"),
            telegram.KeyboardButton("3 уровня       (+1100р)")
        ],
        [telegram.KeyboardButton("Вернуться в основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_toppings(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Выберите желаемые топпинги:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору количества уровней")],
        [
            telegram.KeyboardButton("Карамельный сироп      (+180р)"),
            telegram.KeyboardButton("Кленовый сироп         (+200р)"),
        ],
        [
            telegram.KeyboardButton("Белый соус             (+200р)"),
            telegram.KeyboardButton("Молочный шоколад       (+200р)"),
        ],
        [
            telegram.KeyboardButton("Клубничный сироп       (+300р)"),
            telegram.KeyboardButton("Черничный сироп        (+350р)"),
        ],
        [
            telegram.KeyboardButton("Без топпингов"),
            telegram.KeyboardButton("Достаточно топингов"),
        ],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_berries(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Добавьте свежих ягод:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору топпингов")],
        [
            telegram.KeyboardButton("Малина         (+300р)"),
            telegram.KeyboardButton("Ежевика        (+400р)"),
        ],
        [
            telegram.KeyboardButton("Голубика       (+450р)"),
            telegram.KeyboardButton("Клубника       (+500р)"),
        ],
        [telegram.KeyboardButton("Продолжить без ягод")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def show_the_keyboard(update: telegram.Update, context: telegram.ext.CallbackContext, keyboard, message):
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup,
    )


def launch_next_step(update: telegram.Update, context: telegram.ext.CallbackContext):
    user_answer = update.message.text
    for name, _ in buttons.items():
        if name.lower() in user_answer.lower():
            buttons.get(name)(update, context)


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i+n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu




def main():
    load_dotenv()
    token = os.environ["TG_BOT_KEY"]
    buttons.update({
        "Вернуться в начало": get_permission,
        "Разрешаю обработку моих ПД.": if_allowed,
        "Запрещаю обработку моих ПД.": if_forbidden,
        "Для начала, хотел бы взглянуть на торты...": show_main_menu,
        "Вернуться в основное меню": show_main_menu,
        "Посмотреть каталог": show_catalogue,
        "Вернуться к просмотру каталога": show_catalogue,
        "Создать торт": create_cake,
        "Удивите меня": surprise_client,
        "Повторить заказ": repeat_order,
        "Где мой заказ?": show_current_order,
        "Связаться с нами": contact_support,
        "Выбрать форму": choose_the_form,
        "Вернуться к выбору формы": choose_the_form,
        "Круг           (+400р)": choose_levels_number,
        "Квадрат        (+600р)": choose_levels_number,
        "Прямоугольник  (+1000р)": choose_levels_number,
        "1 уровень      (+400р)": choose_toppings,
        "2 уровня       (+750р)": choose_toppings,
        "3 уровня       (+1100р)": choose_toppings,
        "Белый соус             (+200р)": choose_toppings,
        "Молочный шоколад       (+200р)": choose_toppings,
        "Карамельный сироп      (+180р)": choose_toppings,
        "Кленовый сироп         (+200р)": choose_toppings,
        "Клубничный сироп       (+300р)": choose_toppings,
        "Черничный сироп        (+350р)": choose_toppings,
        "Вернуться к выбору топпингов": choose_toppings,
        "Без топпинга": choose_berries,
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
