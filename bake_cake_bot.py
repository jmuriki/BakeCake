import logging
import datetime

import os
import telegram
import telegram.ext

from pathlib import Path
from dotenv import load_dotenv


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,
                    filename="bake_cake_bot_log.log",
                    filemode="w",
)
logging.debug("LOGGING DEBUG")
logging.info("LOGGING INFO")
logging.warning("LOGGING WARNING")
logging.error("LOGGING ERROR")
logging.critical("LOGGING CRITICAL")


db = {}


def help_command(update, _):
    update.message.reply_text("Используйте `/start` для начала или возврата к первому шагу.")


def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    if not db.get(update.effective_chat.id):
        db[update.effective_chat.id] = {
            "user": {},
            "orders": {},
            "cakes": {},
            "n_cakes": 0,
            "surprise": False,
            "actual_cake_id": 0,
            "previous_user_choice": "",
        }
    db[update.effective_chat.id]["user"]["first_name"] = update.effective_chat.first_name
    db[update.effective_chat.id]["user"]["last_name"] = update.effective_chat.last_name
    db[update.effective_chat.id]["user"]["username"] = update.effective_chat.username
    db[update.effective_chat.id]["user"]["id"] = update.effective_chat.id
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
        [telegram.KeyboardButton("Каталог тортов")],
        [telegram.KeyboardButton("Согласие на обработку ПД")],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def get_pd_permission(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    if not db[update.effective_chat.id]["user"].get("permission"):
        db[update.effective_chat.id]["user"]["permission"] = False
    with open(Path("./Согласие на обработку ПД.pdf"), "rb") as file:
        context.bot.send_document(chat_id=update.effective_chat.id, document=file)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Изучите, пожалуйста, бланк Согласия на обработку персональных данных (далее - ПД), представленный выше.",
    )
    message = "Вы согласны на обработку Ваших персональных данных?"
    keyboard = [
        [
            telegram.KeyboardButton("Не разрешаю обработку моих ПД."),
            telegram.KeyboardButton("Разрешаю обработку моих ПД."),
        ]
    ]
    show_the_keyboard(update, context, keyboard, message)


def if_allowed(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    db[update.effective_chat.id]["user"]["permission"] = True
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Благодарим за доверие)",
    )
    show_menu(update, context, arg, save_to)


def if_forbidden(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    db[update.effective_chat.id]["user"]["permission"] = False
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="На этапе оформления заказа нам будет не обойтись без Вашего согласия.",
    )
    show_menu(update, context, arg, save_to)


def show_menu(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    message = "Вы находитесь в основном меню."
    keyboard = [
        [telegram.KeyboardButton("Каталог тортов")],
        [
            telegram.KeyboardButton("Собрать торт"),
            telegram.KeyboardButton("Удивите меня"),
        ],
        [
            telegram.KeyboardButton("Повторить прошлый заказ"),
            telegram.KeyboardButton("Посмотреть текуший заказ"),
        ],
        [
            telegram.KeyboardButton("Согласие на обработку ПД"),
            telegram.KeyboardButton("Связаться с нами"),
        ],
    ]
    show_the_keyboard(update, context, keyboard, message)


def repeat_order(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы можете отправить нам сообщением номер прошлого заказа и сразу перейти к его оформлению.",
    )
    message = f'Список Ваших прошлых заказов: {db[update.effective_chat.id]["orders"]}'
    keyboard = [
        [
            telegram.KeyboardButton("Связаться с нами"),
            telegram.KeyboardButton("Оформить заказ"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def show_current_order(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    if not db[update.effective_chat.id].get("cakes"):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ваш текущий заказ пуст, но это легко исправить!",
        )
        add_cake(update, context)
    else:
        message = f'Информация по текущему заказу: {db[update.effective_chat.id]["cakes"]}'
        keyboard = [
            [
                telegram.KeyboardButton("Связаться с нами"),
                telegram.KeyboardButton("Оформить заказ"),
            ],
            [telegram.KeyboardButton("Основное меню")],
        ]
        show_the_keyboard(update, context, keyboard, message)


def contact_support(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    message = "Контакты службы поддержки:"
    keyboard = [
        [
            telegram.KeyboardButton("Посмотреть текуший заказ"),
            telegram.KeyboardButton("Оформить заказ"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def show_catalogue(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    print("show_catalogue")
    message = "Каталог наших тортов:"
    keyboard = [
        [
            telegram.KeyboardButton("Собрать торт"),
            telegram.KeyboardButton("Удивите меня"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def surprise_client(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    if db[update.effective_chat.id].get("surprise"):
        db[update.effective_chat.id]["surprise"] = False
        message = f'Ооооп! Вот Ваш торт) {db[update.effective_chat.id]["cakes"][db[update.effective_chat.id]["n_cakes"]]}'
        keyboard = [
            [telegram.KeyboardButton("Каталог тортов")],
            [
                telegram.KeyboardButton("Собрать ещё один торт"),
                telegram.KeyboardButton("Оформить заказ"),
            ],
            [telegram.KeyboardButton("Основное меню")],
        ]
        show_the_keyboard(update, context, keyboard, message)
    else:
        db[update.effective_chat.id]["surprise"] = True
        if db[update.effective_chat.id].get("surprise"):
            add_cake(update, context, arg, save_to)


def add_cake(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    if not db[update.effective_chat.id].get("cakes"):
        db[update.effective_chat.id]["cakes"][1] = {
                "Заказ №": db[update.effective_chat.id],
                "Торт №": 1,
                "Дата": datetime.datetime.date,
                "Время": datetime.datetime.time,
                "Количество уровней": {},
                "Форма": {},
                "Топпинг": {},
                "Ягоды": {},
                "Декор": {},
                "Надпись": {},
                "Итоговая стоимость": 0,
        }
        db[update.effective_chat.id]["actual_cake_id"] = 1
        db[update.effective_chat.id]["n_cakes"] = 1
    elif db[update.effective_chat.id].get("cakes"):
        n_cake = db[update.effective_chat.id]["n_cakes"] + 1
        db[update.effective_chat.id]["cakes"][n_cake] = {
                "Заказ №": db[update.effective_chat.id],
                "Торт №": n_cake,
                "Дата": datetime.datetime.date,
                "Время": datetime.datetime.time,
                "Количество уровней": {},
                "Форма": {},
                "Топпинг": {},
                "Ягоды": {},
                "Декор": {},
                "Надпись": {},
                "Итоговая стоимость": 0,
        }
        db[update.effective_chat.id]["actual_cake_id"] = n_cake
        db[update.effective_chat.id]["n_cakes"] = n_cake
    if db[update.effective_chat.id].get("surprise"):
        surprise_client(update, context, arg, save_to)
    else:
        choose_size(update, context, arg, save_to)


def choose_size(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    message = "Выберите количество уровней торта:"
    keyboard = [
        [telegram.KeyboardButton("Каталог тортов")],
        [
            telegram.KeyboardButton("1 уровень\n(+400р)"),
            telegram.KeyboardButton("2 уровня\n(+750р)"),
            telegram.KeyboardButton("3 уровня\n(+1100р)")
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_form(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    message = "Выберите желаемую форму:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору количества уровней")],
        [
            telegram.KeyboardButton("Круг\n(+400р)"),
            telegram.KeyboardButton("Квадрат\n(+600р)"),
            telegram.KeyboardButton("Прямоугольник\n(+1000р)"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_topping(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    message = "Добавьте топпинг по вкусу:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору формы")],
        [
            telegram.KeyboardButton("Карамельный сироп\n(+180р)"),
            telegram.KeyboardButton("Кленовый сироп\n(+200р)"),
            telegram.KeyboardButton("Белый соус\n(+200р)"),
        ],
        [
            telegram.KeyboardButton("Молочный шоколад\n(+200р)"),
            telegram.KeyboardButton("Клубничный сироп\n(+300р)"),
            telegram.KeyboardButton("Черничный сироп\n(+350р)"),
        ],
        [telegram.KeyboardButton("Без топпингов")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_berries(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    message = "Добавьте свежих ягод:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору топпинга")],
        [
            telegram.KeyboardButton("Малина\n(+300р)"),
            telegram.KeyboardButton("Ежевика\n(+400р)"),
            telegram.KeyboardButton("Голубика\n(+450р)"),
            telegram.KeyboardButton("Клубника\n(+500р)"),
        ],
        [telegram.KeyboardButton("Без ягод")],
        [
            telegram.KeyboardButton("Оформить заказ"),
            telegram.KeyboardButton("Собрать ещё один торт"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_decor(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    message = "Добавьте съедобное украшение:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору ягод")],
        [
            telegram.KeyboardButton("Маршмеллоу\n(+200р)"),
            telegram.KeyboardButton("Марципан\n(+280р)"),
            telegram.KeyboardButton("Фисташки\n(+300р)"),
        ],
        [
            
            telegram.KeyboardButton("Пекан\n(+300р)"),
            telegram.KeyboardButton("Фундук\n(+350р)"),
            telegram.KeyboardButton("Безе\n(+400р)"),
        ],
        [telegram.KeyboardButton("Без декора")],
        [
            telegram.KeyboardButton("Оформить заказ"),
            telegram.KeyboardButton("Собрать ещё один торт"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def specify_label(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Мы можем разместить на торте любую надпись, например: «С днем рождения!»"
    )
    message = "Если у Вас есть желание сделать надпись, пришлите сначала её текст ответным сообщением, а потом нажмите кнопку 'Хочу надпись!'."
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


def specify_order(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    if not arg:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Почти всё! Осталось уточнить детали доставки или же... можно собрать ещё один торт)"
        )
    message = "Чтобы уточнить детали, нажмите кнопку, а затем отправьте сообщением соответствующую информацию."
    keyboard = [
        [
            telegram.KeyboardButton("Изменить детали торта"),
            telegram.KeyboardButton("Собрать ещё один торт"),
        ],
        [
            telegram.KeyboardButton("Адрес доставки"),
            telegram.KeyboardButton("Дата доставки"),
            telegram.KeyboardButton("Время доставки"),
            telegram.KeyboardButton("Оставить коммент"),
        ],
        [
            telegram.KeyboardButton("Основное меню"),
            telegram.KeyboardButton("Оплатить заказ"),
        ],
    ]
    show_the_keyboard(update, context, keyboard, message)


def verify_order(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    message = f'Спецификация заказа: {db[update.effective_chat.id]["cakes"]}'
    keyboard = [
        [telegram.KeyboardButton("Подтвердить и оплатить")],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def get_payment(update: telegram.Update, context: telegram.ext.CallbackContext, arg, save_to):
    if not db[update.effective_chat.id]["user"].get("permission"):
        get_pd_permission(update, context, arg, save_to)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Здесь должны быть данные для оплаты заказа."
        )


def show_the_keyboard(update: telegram.Update, context: telegram.ext.CallbackContext, keyboard, message):
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup,
    )


def launch_next_step(update: telegram.Update, context: telegram.ext.CallbackContext):
    user_choice = update.message.text
    print("user_choise", user_choice)
    triggers = {
        "Согласие на обработку ПД": {
                "next_func": get_pd_permission,
                "arg": None,
                "save_to": None
        },
        "Каталог тортов": {
                "next_func": show_catalogue,
                "arg": None,
                "save_to": None,
        },
        "Основное меню": {
                "next_func": show_menu,
                "arg": None,
                "save_to": None,
        },
        "Разрешаю обработку моих ПД.": {
                "next_func": if_allowed,
                "arg": None,
                "save_to": None,
        },
        "Не разрешаю обработку моих ПД.": {
                "next_func": if_forbidden,
                "arg": None,
                "save_to": None,
        },
        "Собрать торт": {
                "next_func": add_cake,
                "arg": None,
                "save_to": None,
        },
        "Посмотреть текуший заказ": {
                "next_func": show_current_order,
                "arg": None,
                "save_to": None,
        },
        "Повторить прошлый заказ": {
                "next_func": repeat_order,
                "arg": None,
                "save_to": None,
        },
        "Удивите меня": {
                "next_func": surprise_client,
                "arg": None,
                "save_to": None,
        },
        "Связаться с нами": {
                "next_func": contact_support,
                "arg": None,
                "save_to": None,
        },
        "Оформить заказ": {
                "next_func": specify_order,
                "arg": None,
                "save_to": None,
        },
        "Собрать ещё один торт": {
                "next_func": add_cake,
                "arg": None,
                "save_to": None,
        },
        "1 уровень\n(+400р)": {
                "next_func": choose_form,
                "arg": 400,
                "save_to": "Количество уровней",
        },
        "2 уровня\n(+750р)": {
                "next_func": choose_form,
                "arg": 750,
                "save_to": "Количество уровней",
        },
        "3 уровня\n(+1100р)": {
                "next_func": choose_form,
                "arg": 1100,
                "save_to": "Количество уровней",
        },
        "Вернуться к выбору количества уровней": {
                "next_func": choose_size,
                "arg": None,
                "save_to": None,
        },
        "Круг\n(+400р)": {
                "next_func": choose_topping,
                "arg": 400,
                "save_to": "Форма",
        },
        "Квадрат\n(+600р)": {
                "next_func": choose_topping,
                "arg": 600,
                "save_to": "Форма",
        },
        "Прямоугольник\n(+1000р)": {
                "next_func": choose_topping,
                "arg": 1000,
                "save_to": "Форма",
        },
        "Вернуться к выбору формы": {
                "next_func": choose_form,
                "arg": None,
                "save_to": None,
        },
        "Карамельный сироп\n(+180р)": {
                "next_func": choose_berries,
                "arg": 180,
                "save_to": "Топпинг",
        },
        "Кленовый сироп\n(+200р)": {
                "next_func": choose_berries,
                "arg": 200,
                "save_to": "Топпинг",
        },
        "Белый соус\n(+200р)": {
                "next_func": choose_berries,
                "arg": 200,
                "save_to": "Топпинг",
        },
        "Молочный шоколад\n(+200р)": {
                "next_func": choose_berries,
                "arg": 200,
                "save_to": "Топпинг",
        },
        "Клубничный сироп\n(+300р)": {
                "next_func": choose_berries,
                "arg": 300,
                "save_to": "Топпинг",
        },
        "Черничный сироп\n(+350р)": {
                "next_func": choose_berries,
                "arg": 350,
                "save_to": "Топпинг",
        },
        "Без топпингов": {
                "next_func": choose_berries,
                "arg": 0,
                "save_to": "Топпинг",
        },
        "Вернуться к выбору топпинга": {
                "next_func": choose_topping,
                "arg": None,
                "save_to": None,
        },
        "Малина\n(+300р)": {
                "next_func": choose_decor,
                "arg": 300,
                "save_to": "Ягоды",
        },
        "Ежевика\n(+400р)": {
                "next_func": choose_decor,
                "arg": 400,
                "save_to": "Ягоды",
        },
        "Голубика\n(+450р)": {
                "next_func": choose_decor,
                "arg": 450,
                "save_to": "Ягоды",
        },
        "Клубника\n(+500р)": {
                "next_func": choose_decor,
                "arg": 500,
                "save_to": "Ягоды",
        },
        "Без ягод": {
                "next_func": choose_decor,
                "arg": 0,
                "save_to": "Ягоды",
        },
        "Вернуться к выбору ягод": {
                "next_func": choose_berries,
                "arg": None,
                "save_to": None,
        },
        "Маршмеллоу\n(+200р)": {
                "next_func": specify_label,
                "arg": 200,
                "save_to": "Декор",
        },
        "Марципан\n(+280р)": {
                "next_func": specify_label,
                "arg": 280,
                "save_to": "Декор",
        },
        "Фисташки\n(+300р)": {
                "next_func": specify_label,
                "arg": 300,
                "save_to": "Декор",
        },
        "Пекан\n(+300р)": {
                "next_func": specify_label,
                "arg": 300,
                "save_to": "Декор",
        },
        "Фундук\n(+350р)": {
                "next_func": specify_label,
                "arg": 350,
                "save_to": "Декор",
        },
        "Безе\n(+400р)": {
                "next_func": specify_label,
                "arg": 400,
                "save_to": "Декор",
        },
        "Без декора": {
                "next_func": specify_label,
                "arg": 0,
                "save_to": "Декор",
        },
        "Вернуться к выбору декора": {
                "next_func": choose_decor,
                "arg": None,
                "save_to": None,
        },
        "Без надписи": {
                "next_func": specify_order,
                "arg": 0,
                "save_to": "Надпись",
        },
        "Хочу надпись!\n(+500)": {
                "next_func": specify_order,
                "arg": 500,
                "save_to": "Надпись",
        },
        "Изменить детали торта": {
                "next_func": specify_label,
                "arg": None,
                "save_to": None,
        },
        "Адрес доставки": {
                "next_func": specify_order,
                "arg": db[update.effective_chat.id]["previous_user_choice"],
                "save_to": "Адрес доставки",
        },
        "Дата доставки": {
                "next_func": specify_order,
                "arg": db[update.effective_chat.id]["previous_user_choice"],
                "save_to": "Дата доставки",
        },
        "Время доставки": {
                "next_func": specify_order,
                "arg": db[update.effective_chat.id]["previous_user_choice"],
                "save_to": "Время доставки",
        },
        "Оставить комментарий": {
                "next_func": specify_order,
                "arg": db[update.effective_chat.id]["previous_user_choice"],
                "save_to": "Комментарий",
        },
        "Оплатить заказ": {
                "next_func": verify_order,
                "arg": None,
                "save_to": None,
        },
        "Подтвердить и оплатить": {
                "next_func": get_payment,
                "arg": None,
                "save_to": None,
        },
    }
    if triggers.get(user_choice):
        print("000")
        if not db:
            print("111")
            start(update, context)
        else:
            print("222")
            db[update.effective_chat.id]["previous_user_choice"] = user_choice
            arg = triggers[user_choice]["arg"]
            save_to = triggers[user_choice]["save_to"]
            triggers[user_choice]["next_func"](update, context, arg, save_to)
    else:
        print("333")
        if db:
            print("444")
            db[update.effective_chat.id]["cakes"][triggers["user_choice"]['save_to']] = user_choice
            print(db[update.effective_chat.id]["cakes"][triggers["user_choice"]['save_to']])


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
