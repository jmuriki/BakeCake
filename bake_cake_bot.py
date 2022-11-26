import os
import telegram
import telegram.ext

from pathlib import Path
from dotenv import load_dotenv


def help_command(update, _):
    update.message.reply_text("Используйте `/start` для начала или возврата к первому шагу.")


def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Здравствуйте) Рады, что Вы нас посетили!",
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Cледуйте нашим подсказкам, выбирая за раз один из предложенных пунктов меню.",
    )
    message = "(нажмите на значок в поле ввода текста, чтобы развернуть меню, если оно не отображается)"
    keyboard = [
        [telegram.KeyboardButton("Согласие на обработку ПД")],
        [telegram.KeyboardButton("Срочно покажите мне торты!")],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


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
            telegram.KeyboardButton("Запрещаю обработку моих ПД."),
            telegram.KeyboardButton("Разрешаю обработку моих ПД."),
        ]
    ]
    show_the_keyboard(update, context, keyboard, message)


def if_allowed(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Благодарим за доверие)",
    )
    show_menu(update, context)


def if_forbidden(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="На этапе оформления заказа нам будет не обойтись без Вашего согласия.",
    )
    show_menu(update, context)


def show_menu(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Вы находитесь в основном меню."
    keyboard = [
        [telegram.KeyboardButton("Каталог тортов")],
        [
            telegram.KeyboardButton("Создать торт"),
            telegram.KeyboardButton("Текуший заказ"),
        ],
        [
            telegram.KeyboardButton("Повторить заказ"),
            telegram.KeyboardButton("Удивите меня"),
        ],
        [
            telegram.KeyboardButton("Связаться с нами"),
            telegram.KeyboardButton("Согласие на обработку ПД"),
        ],
    ]
    show_the_keyboard(update, context, keyboard, message)


def repeat_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы можете отправить нам сообщением номер прошлого заказа и сразу перейти к его оформлению.",
    )
    message = "Список Ваших прошлых заказов:"
    keyboard = [
        [telegram.KeyboardButton("Каталог тортов")],
        [
            telegram.KeyboardButton("Связаться с нами"),
            telegram.KeyboardButton("Оформить заказ"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def show_current_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Информация по текущему заказу:"
    keyboard = [
        [
            telegram.KeyboardButton("Связаться с нами"),
            telegram.KeyboardButton("Оформить заказ"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def contact_support(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Контакты службы поддержки:"
    keyboard = [
        [
            telegram.KeyboardButton("Текуший заказ"),
            telegram.KeyboardButton("Оформить заказ"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def show_catalogue(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Каталог наших тортов:"
    keyboard = [
        [
            telegram.KeyboardButton("Создать торт"),
            telegram.KeyboardButton("Удивите меня"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def surprise_client(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Ооооп! Вот Ваш торт)"
    keyboard = [
        [
            telegram.KeyboardButton("Оформить заказ"),
            telegram.KeyboardButton("Собрать ещё один торт"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_size(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Выберите количество уровней торта:"
    keyboard = [
        [telegram.KeyboardButton("Посмотреть каталог тортов")],
        [
            telegram.KeyboardButton("1 уровень\n(+400р)"),
            telegram.KeyboardButton("2 уровня\n(+750р)"),
            telegram.KeyboardButton("3 уровня\n(+1100р)")
        ],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_form(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Выберите желаемую форму:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору количества уровней")],
        [
            telegram.KeyboardButton("Круг\n(+400р)"),
            telegram.KeyboardButton("Квадрат\n(+600р)"),
            telegram.KeyboardButton("Прямоугольник\n(+1000р)"),
        ],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_toppings(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Добавьте топпинги по вкусу:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору формы")],
        [
            telegram.KeyboardButton("Карамельный сироп\n(+180р)"),
            telegram.KeyboardButton("Кленовый сироп\n(+200р)"),
        ],
        [
            telegram.KeyboardButton("Белый соус\n(+200р)"),
            telegram.KeyboardButton("Молочный шоколад\n(+200р)"),
        ],
        [
            telegram.KeyboardButton("Клубничный сироп\n(+300р)"),
            telegram.KeyboardButton("Черничный сироп\n(+350р)"),
        ],
        [
            telegram.KeyboardButton("Без топпингов"),
            telegram.KeyboardButton("Достаточно топпингов"),
        ],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_berries(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Добавьте свежих ягод:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору топпингов")],
        [
            telegram.KeyboardButton("Малина\n(+300р)"),
            telegram.KeyboardButton("Ежевика\n(+400р)"),
        ],
        [
            telegram.KeyboardButton("Голубика\n(+450р)"),
            telegram.KeyboardButton("Клубника\n(+500р)"),
        ],
        [
            telegram.KeyboardButton("Без ягод"),
            telegram.KeyboardButton("Ягод уже достаточно"),
        ],
        [
            telegram.KeyboardButton("Оформить заказ"),
            telegram.KeyboardButton("Собрать ещё один торт"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_decor(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Добавьте съедобных украшений:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору ягод")],
        [
            telegram.KeyboardButton("Маршмеллоу\n(+200р)"),
            telegram.KeyboardButton("Марципан\n(+280р)"),
        ],
        [
            telegram.KeyboardButton("Фисташки\n(+300р)"),
            telegram.KeyboardButton("Пекан\n(+300р)"),
        ],
        [
            telegram.KeyboardButton("Фундук\n(+350р)"),
            telegram.KeyboardButton("Безе\n(+400р)"),
        ],
        [
            telegram.KeyboardButton("Без декора"),
            telegram.KeyboardButton("Уже достаточно декора"),
        ],
        [
            telegram.KeyboardButton("Оформить заказ"),
            telegram.KeyboardButton("Собрать ещё один торт"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def specify_label(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Мы можем разместить на торте любую надпись, например: «С днем рождения!»"
    )
    message = "Если у Вас есть желание сделать надпись, пришлите сначала её текст ответным сообщением, а потом нажмите соответствующую кнопку меню."
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору декора")],
        [
            telegram.KeyboardButton("Без надписи"),
            telegram.KeyboardButton("Хочу надпись!\n(+500)"),
        ],
        [
            telegram.KeyboardButton("Оформить заказ"),
            telegram.KeyboardButton("Собрать ещё один торт"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def specify_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Почти всё! Осталось уточнить детали доставки или же... можно собрать ещё один торт)"
    keyboard = [
        [
            telegram.KeyboardButton("Изменить детали торта"),
            telegram.KeyboardButton("Собрать ещё один торт"),
        ],
        [
            telegram.KeyboardButton("Адрес доставки"),
            telegram.KeyboardButton("Дата доставки"),
            telegram.KeyboardButton("Время доставки"),
        ],
        [
            telegram.KeyboardButton("Оставить комментарий"),
            telegram.KeyboardButton("Оплатить заказ"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def verify_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Спецификация заказа:"
    keyboard = [
        [telegram.KeyboardButton("Подтвердить и оплатить")],
        [telegram.KeyboardButton("Основное меню")],
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
    triggers = {
        "Согласие на обработку ПД": get_permission,
        "Срочно покажите мне торты!": show_catalogue,
        "Основное меню": show_menu,
        "Разрешаю обработку моих ПД.": if_allowed,
        "Запрещаю обработку моих ПД.": if_forbidden,
        "Каталог тортов": show_catalogue,
        "Создать торт": choose_size,
        "Текуший заказ": show_current_order,
        "Повторить заказ": repeat_order,
        "Удивите меня": surprise_client,
        "Связаться с нами": contact_support,
        "Оформить заказ": specify_order,
        "Собрать ещё один торт": choose_size,
        "Посмотреть каталог тортов": show_catalogue,
        "1 уровень\n(+400р)": choose_form,
        "2 уровня\n(+750р)": choose_form,
        "3 уровня\n(+1100р)": choose_form,
        "Вернуться к выбору количества уровней": choose_size,
        "Круг\n(+400р)": choose_toppings,
        "Квадрат\n(+600р)": choose_toppings,
        "Прямоугольник\n(+1000р)": choose_toppings,
        "Вернуться к выбору формы": choose_form,
        "Карамельный сироп\n(+180р)": choose_toppings,
        "Кленовый сироп\n(+200р)": choose_toppings,
        "Белый соус\n(+200р)": choose_toppings,
        "Молочный шоколад\n(+200р)": choose_toppings,
        "Клубничный сироп\n(+300р)": choose_toppings,
        "Черничный сироп\n(+350р)": choose_toppings,
        "Без топпингов": choose_berries,
        "Достаточно топпингов": choose_berries,
        "Вернуться к выбору топпингов": choose_toppings,
        "Малина\n(+300р)": choose_berries,
        "Ежевика\n(+400р)": choose_berries,
        "Голубика\n(+450р)": choose_berries,
        "Клубника\n(+500р)": choose_berries,
        "Без ягод": choose_decor,
        "Ягод уже достаточно": choose_decor,
        "Вернуться к выбору ягод": choose_berries,
        "Маршмеллоу\n(+200р)": choose_decor,
        "Марципан\n(+280р)": choose_decor,
        "Фисташки\n(+300р)": choose_decor,
        "Пекан\n(+300р)": choose_decor,
        "Фундук\n(+350р)": choose_decor,
        "Безе\n(+400р)": choose_decor,
        "Без декора": specify_label,
        "Уже достаточно декора": specify_label,
        "Вернуться к выбору декора": choose_decor,
        "Без надписи": specify_order,
        "Хочу надпись!\n(+500)": specify_order,
        "Изменить детали торта": specify_label,
        "Адрес доставки": specify_order,
        "Дата доставки": specify_order,
        "Время доставки": specify_order,
        "Оставить комментарий": specify_order,
        "Оплатить заказ": verify_order,
        "Подтвердить и оплатить": get_permission,
    }
    for name, _ in triggers.items():
        if name.lower() in user_answer.lower():
            triggers.get(name)(update, context)


def main():
    load_dotenv()
    token = os.environ["TG_BOT_KEY"]
    updater = telegram.ext.Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(telegram.ext.CommandHandler('help', help_command))
    dispatcher.add_handler(telegram.ext.CommandHandler('start', start))
    dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, launch_next_step))
    updater.start_polling(1)
    updater.idle()


if __name__ == "__main__":
    main()
