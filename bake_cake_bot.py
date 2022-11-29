import logging
import datetime

import os
import telegram
import telegram.ext

from pathlib import Path
from dotenv import load_dotenv

from pprint import pprint


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


DB = {}
db = None


def help_command(update, _):
    update.message.reply_text("Используйте `/start` для начала или возврата к первому шагу.")


def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    if not DB.get(update.effective_chat.id):
        DB[update.effective_chat.id] = {
            "user": {},
            "orders": {},
            "current_order": {},
            "temp": {
                "last_choice": "",
                "last_mssg": "",
                "n_cakes": 0,
                "actual_cake_id": 0,
                "new_cake_flag": True,
                "surprise_flag": False,
                "specify_order_flag": False,
                "ready_to_pay": False,
            },
        }
    global db
    db = DB[update.effective_chat.id]
    db["user"]["first_name"] = update.effective_chat.first_name
    db["user"]["last_name"] = update.effective_chat.last_name
    db["user"]["username"] = update.effective_chat.username
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Здравствуйте, {db["user"]["username"]}! Рады, что Вы нас посетили)',
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


def get_pd_permission(update: telegram.Update, context: telegram.ext.CallbackContext):
    if not db["user"].get("permission"):
        db["user"]["permission"] = False
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


def if_allowed(update: telegram.Update, context: telegram.ext.CallbackContext):
    db["user"]["permission"] = True
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Благодарим за доверие)",
    )
    if db["temp"]["ready_to_pay"]:
        return get_payment(update, context)
    show_menu(update, context)


def if_forbidden(update: telegram.Update, context: telegram.ext.CallbackContext):
    db["user"]["permission"] = False
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="На этапе оформления заказа нам будет не обойтись без Вашего согласия.",
    )
    show_menu(update, context)


def show_catalogue(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Каталог наших тортов:"
    keyboard = [
        [
            telegram.KeyboardButton("Собрать торт"),
            telegram.KeyboardButton("Удивите меня"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def show_menu(update: telegram.Update, context: telegram.ext.CallbackContext):
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
            telegram.KeyboardButton("Где мой заказ?"),
        ],
    ]
    show_the_keyboard(update, context, keyboard, message)


def repeat_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы можете отправить нам сообщением номер прошлого заказа и сразу перейти к его оформлению.",
    )
    message = f'Список Ваших прошлых заказов: {db["orders"]}'
    keyboard = [
        [
            telegram.KeyboardButton("Связаться с нами"),
            telegram.KeyboardButton("Оформить заказ"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def show_current_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    if not db.get("current_order"):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ваш текущий заказ пуст, но это легко исправить!",
        )
        customise_cake(update, context)
    else:
        cake = db["current_order"][db["temp"]["actual_cake_id"]]
        pprint(cake)
        cake["Итоговая стоимость"] = cake["Комплектация"].items()
        pprint(cake["Итоговая стоимость"])
        message = f'Информация по текущему заказу: {db["current_order"]}'
        keyboard = [
            [
                telegram.KeyboardButton("Связаться с нами"),
                telegram.KeyboardButton("Оформить заказ"),
            ],
            [telegram.KeyboardButton("Основное меню")],
        ]
        show_the_keyboard(update, context, keyboard, message)


def find_my_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    if db["temp"].get("waiting_for_delivery"):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Ваш заказ передадут в службу доставки сразу же, как только он будет готов. {db["orders"]}',
        )
        return contact_support(update, context)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="У Вас нет недоставленых заказов.",
    )
    return show_menu(update, context)


def contact_support(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Контакты службы поддержки:"
    keyboard = [
        [
            telegram.KeyboardButton("Посмотреть текуший заказ"),
            telegram.KeyboardButton("Оформить заказ"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def add_new_cake(update: telegram.Update, context: telegram.ext.CallbackContext):
    db["temp"]["new_cake_flag"] = True
    customise_cake(update, context)


def surprise_client(update: telegram.Update, context: telegram.ext.CallbackContext):
    if db["temp"].get("surprise_flag"):
        db["temp"]["surprise_flag"] = False
        message = f'Ооооп! Вот Ваш торт) {db["current_order"][db["temp"]["n_cakes"]]}'
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
        db["temp"]["surprise_flag"] = True
        customise_cake(update, context)


def customise_cake(update: telegram.Update, context: telegram.ext.CallbackContext):
    if not db.get("current_order"):
        db["temp"]["new_cake_flag"] = False
        db["current_order"][1] = {
                "Заказчик №": update.effective_chat.id,
                "Дата / Время": datetime.datetime.now(),
                "Комплектация": {
                },
                "Итоговая стоимость": 0,
        }
        db["temp"]["actual_cake_id"] = 1
        db["temp"]["n_cakes"] = 1
    elif db.get("current_order") and db["temp"]["new_cake_flag"]:
        db["temp"]["new_cake_flag"] = False
        n_cake = db["temp"]["n_cakes"] + 1
        db["current_order"][n_cake] = {
                "Заказчик №": update.effective_chat.id,
                "Дата / Время": datetime.datetime.now(),
                "Комплектация": {
                },
                "Итоговая стоимость": 0,
        }
        db["temp"]["actual_cake_id"] = n_cake
        db["temp"]["n_cakes"] = n_cake
    if db["temp"].get("surprise_flag"):
        surprise_client(update, context)
    else:
        choose_size(update, context)


def choose_size(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Выберите количество уровней торта:"
    keyboard = [
        [
            telegram.KeyboardButton("Каталог тортов"),
            telegram.KeyboardButton("Удивите меня"),
        ],
        [
            telegram.KeyboardButton("1 уровень\n(+400р)"),
            telegram.KeyboardButton("2 уровня\n(+750р)"),
            telegram.KeyboardButton("3 уровня\n(+1100р)")
        ],
        [telegram.KeyboardButton("Основное меню")],
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
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_topping(update: telegram.Update, context: telegram.ext.CallbackContext):
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
        [telegram.KeyboardButton("Без топпингов\n(+0р)")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_berries(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = "Добавьте свежих ягод:"
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору топпинга")],
        [
            telegram.KeyboardButton("Малина\n(+300р)"),
            telegram.KeyboardButton("Ежевика\n(+400р)"),
            telegram.KeyboardButton("Голубика\n(+450р)"),
            telegram.KeyboardButton("Клубника\n(+500р)"),
        ],
        [telegram.KeyboardButton("Без ягод\n(+0р)")],
        [
            telegram.KeyboardButton("Оформить заказ"),
            telegram.KeyboardButton("Собрать ещё один торт"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def choose_decor(update: telegram.Update, context: telegram.ext.CallbackContext):
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
        [telegram.KeyboardButton("Без декора\n(+0р)")],
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
    message = "Если у Вас есть желание сделать надпись, пришлите сначала её текст ответным сообщением, а потом нажмите кнопку 'Хочу надпись!'."
    keyboard = [
        [telegram.KeyboardButton("Вернуться к выбору декора")],
        [
            telegram.KeyboardButton("Без надписи\n(+0р)"),
            telegram.KeyboardButton("Хочу надпись!\n(+500р)"),
        ],
        [
            telegram.KeyboardButton("Оформить заказ"),
            telegram.KeyboardButton("Собрать ещё один торт"),
        ],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def get_label(update: telegram.Update, context: telegram.ext.CallbackContext):
    db["temp"]["label_flag"] = True
    specify_order(update, context)


def specify_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    if not db["temp"]["specify_order_flag"]:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Почти всё! Осталось уточнить детали доставки или же... можно собрать ещё один торт)"
        )
        db["temp"]["specify_order_flag"] = True
    message = "Чтобы уточнить детали, выберите соответствующий пункт меню, а затем отправьте информацию сообщением."
    keyboard = [
        [
            telegram.KeyboardButton("Изменить детали торта"),
            telegram.KeyboardButton("Собрать ещё один торт"),
        ],
        [
            telegram.KeyboardButton("Адрес доставки"),
            telegram.KeyboardButton("Дата доставки"),
            telegram.KeyboardButton("Время доставки"),
            telegram.KeyboardButton("Коммент"),
        ],
        [
            telegram.KeyboardButton("Основное меню"),
            telegram.KeyboardButton("Оплатить заказ"),
        ],
    ]
    show_the_keyboard(update, context, keyboard, message)


def verify_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    message = f'Спецификация заказа: {db["current_order"]}'
    keyboard = [
        [telegram.KeyboardButton("Уточнить детали доставки")],
        [telegram.KeyboardButton("Подтвердить и оплатить")],
        [telegram.KeyboardButton("Основное меню")],
    ]
    show_the_keyboard(update, context, keyboard, message)


def get_payment(update: telegram.Update, context: telegram.ext.CallbackContext):
    db["temp"]["ready_to_pay"] = True
    if not db["user"].get("permission"):
        get_pd_permission(update, context)
    else:
        message = "Здесь должны быть данные для оплаты заказа."
        keyboard = [
            [telegram.KeyboardButton("Уточнить детали доставки")],
            [telegram.KeyboardButton("Оплата")],
            [telegram.KeyboardButton("Основное меню")],
        ]
        show_the_keyboard(update, context, keyboard, message)


def archive_the_order(update: telegram.Update, context: telegram.ext.CallbackContext):
    for order, details in db["current_order"].items():
        db["orders"][order] = details
    db["current_order"] = {}
    db["temp"] = {
        "last_choice": "",
        "last_mssg": "",
        "n_cakes": 0,
        "actual_cake_id": 0,
        "new_cake_flag": True,
        "surprise_flag": False,
        "specify_order_flag": False,
        "ready_to_pay": False,
        "waiting_for_delivery": True,
    }
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Ваш заказ оформлен. Ожидайте доставки."
    )
    pprint(db)
    return show_menu(update, context)


def save_choise(update: telegram.Update, context: telegram.ext.CallbackContext, price, save_to):
    db["current_order"][db["temp"]["actual_cake_id"]]["Комплектация"][save_to] = price
    pprint(db)


def save_mssg(update: telegram.Update, context: telegram.ext.CallbackContext, save_to):
    db["current_order"][save_to] = db["temp"]["last_mssg"]
    db["temp"]["last_mssg"] = ""
    db["temp"]["last_choice"] = ""
    db["temp"]["label_flag"] = False
    pprint(db)


def show_the_keyboard(update: telegram.Update, context: telegram.ext.CallbackContext, keyboard, message):
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup,
    )


def launch_next_step(update: telegram.Update, context: telegram.ext.CallbackContext):
    if not DB:
        return start(update, context)
    last_input = update.message.text
    triggers = {
        "Согласие на обработку ПД": {
            "next_func": get_pd_permission,
        },
        "Каталог тортов": {
            "next_func": show_catalogue,
        },
        "Основное меню": {
            "next_func": show_menu,
        },
        "Разрешаю обработку моих ПД.": {
            "next_func": if_allowed,
        },
        "Не разрешаю обработку моих ПД.": {
            "next_func": if_forbidden,
        },
        "Собрать торт": {
            "next_func": customise_cake,
        },
        "Посмотреть текуший заказ": {
            "next_func": show_current_order,
        },
        "Повторить прошлый заказ": {
            "next_func": repeat_order,
        },
        "Удивите меня": {
            "next_func": surprise_client,
        },
        "Связаться с нами": {
            "next_func": contact_support,
        },
        "Оформить заказ": {
            "next_func": specify_order,
        },
        "Собрать ещё один торт": {
            "next_func": add_new_cake,
        },
        "1 уровень\n(+400р)": {
            "next_func": choose_form,
            "price": 400,
            "save_to": "Количество уровней",
        },
        "2 уровня\n(+750р)": {
            "next_func": choose_form,
            "price": 750,
            "save_to": "Количество уровней",
        },
        "3 уровня\n(+1100р)": {
            "next_func": choose_form,
            "price": 1100,
            "save_to": "Количество уровней",
        },
        "Вернуться к выбору количества уровней": {
            "next_func": choose_size,
        },
        "Круг\n(+400р)": {
            "next_func": choose_topping,
            "price": 400,
            "save_to": "Форма",
        },
        "Квадрат\n(+600р)": {
            "next_func": choose_topping,
            "price": 600,
            "save_to": "Форма",
        },
        "Прямоугольник\n(+1000р)": {
            "next_func": choose_topping,
            "price": 1000,
            "save_to": "Форма",
        },
        "Вернуться к выбору формы": {
            "next_func": choose_form,
        },
        "Карамельный сироп\n(+180р)": {
            "next_func": choose_berries,
            "price": 180,
            "save_to": "Топпинг",
        },
        "Кленовый сироп\n(+200р)": {
            "next_func": choose_berries,
            "price": 200,
            "save_to": "Топпинг",
        },
        "Белый соус\n(+200р)": {
            "next_func": choose_berries,
            "price": 200,
            "save_to": "Топпинг",
        },
        "Молочный шоколад\n(+200р)": {
            "next_func": choose_berries,
            "price": 200,
            "save_to": "Топпинг",
        },
        "Клубничный сироп\n(+300р)": {
            "next_func": choose_berries,
            "price": 300,
            "save_to": "Топпинг",
        },
        "Черничный сироп\n(+350р)": {
            "next_func": choose_berries,
            "price": 350,
            "save_to": "Топпинг",
        },
        "Без топпингов\n(+0р)": {
            "next_func": choose_berries,
            "price": 0,
            "save_to": "Топпинг",
        },
        "Вернуться к выбору топпинга": {
            "next_func": choose_topping,
        },
        "Малина\n(+300р)": {
            "next_func": choose_decor,
            "price": 300,
            "save_to": "Ягоды",
        },
        "Ежевика\n(+400р)": {
            "next_func": choose_decor,
            "price": 400,
            "save_to": "Ягоды",
        },
        "Голубика\n(+450р)": {
            "next_func": choose_decor,
            "price": 450,
            "save_to": "Ягоды",
        },
        "Клубника\n(+500р)": {
            "next_func": choose_decor,
            "price": 500,
            "save_to": "Ягоды",
        },
        "Без ягод\n(+0р)": {
            "next_func": choose_decor,
            "price": 0,
            "save_to": "Ягоды",
        },
        "Вернуться к выбору ягод": {
            "next_func": choose_berries,
        },
        "Маршмеллоу\n(+200р)": {
            "next_func": specify_label,
            "price": 200,
            "save_to": "Декор",
        },
        "Марципан\n(+280р)": {
            "next_func": specify_label,
            "price": 280,
            "save_to": "Декор",
        },
        "Фисташки\n(+300р)": {
            "next_func": specify_label,
            "price": 300,
            "save_to": "Декор",
        },
        "Пекан\n(+300р)": {
            "next_func": specify_label,
            "price": 300,
            "save_to": "Декор",
        },
        "Фундук\n(+350р)": {
            "next_func": specify_label,
            "price": 350,
            "save_to": "Декор",
        },
        "Безе\n(+400р)": {
            "next_func": specify_label,
            "price": 400,
            "save_to": "Декор",
        },
        "Без декора\n(+0р)": {
            "next_func": specify_label,
            "price": 0,
            "save_to": "Декор",
        },
        "Вернуться к выбору декора": {
            "next_func": choose_decor,
        },
        "Без надписи\n(+0р)": {
            "next_func": specify_order,
            "price": 0,
            "save_to": "Надпись",
        },
        "Хочу надпись!\n(+500р)": {
            "next_func": get_label,
            "price": 500,
            "save_to": "Надпись",
        },
        "Изменить детали торта": {
            "next_func": specify_label,
        },
        "Адрес доставки": {
            "next_func": specify_order,
            "save_to": "Адрес доставки",
        },
        "Дата доставки": {
            "next_func": specify_order,
            "save_to": "Дата доставки",
        },
        "Время доставки": {
            "next_func": specify_order,
            "save_to": "Время доставки",
        },
        "Коммент": {
            "next_func": specify_order,
            "save_to": "Комментарий",
        },
        "Уточнить детали доставки": {
            "next_func": specify_order,
        },
        "Оплатить заказ": {
            "next_func": verify_order,
        },
        "Подтвердить и оплатить": {
            "next_func": get_payment,
        },
        "Оплата": {
            "next_func": archive_the_order,
        },
        "Где мой заказ?": {
            "next_func": find_my_order,
        }
    }
    if triggers.get(last_input):
        price = triggers[last_input].get("price")
        save_to = triggers[last_input].get("save_to")
        if triggers[last_input].get("price") and triggers[last_input].get("save_to"):
            save_choise(update, context, price, save_to)
        elif triggers[last_input].get("save_to"):
            db["temp"]["last_choice"] = last_input
        else:
            db["temp"]["last_choice"] = ""
        triggers[last_input]["next_func"](update, context)
    else:
        if db["temp"].get("label_flag"):
            db["temp"]["last_mssg"] = last_input
            save_to = "Текст надписи"
            save_mssg(update, context, save_to)
        elif db["temp"].get("last_choice"):
            db["temp"]["last_mssg"] = last_input
            save_to = triggers[db["temp"]["last_choice"]].get("save_to")
            save_mssg(update, context, save_to)
        

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
