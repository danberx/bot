import logging
from requests import request
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
BOT_TOKEN = "6162171453:AAFrLJK5paNLdHqyx45FyUPLkceEbY9_-DI"
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)
f = open("currencies.txt" , encoding="utf8")
s = f.readlines()
LIST_OF_CURRENCIES = []
LIST_OF_CURRENCIES_AND_NAMES = []
for elem in s:
    LIST_OF_CURRENCIES.append(elem[1:4])
    LIST_OF_CURRENCIES_AND_NAMES.append(f"{elem[1:4]}: {elem[8:-3]}")
reply_keyboard1 = [["USD", "EUR"],
                   ["RUB", "GBP"],
                   ["JPY", "CHF"],
                   ["CNY", "KZT"]]
markup = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True)


def latest(cur1, cur2, summ):
    response = request(
        method='GET',
        url='https://openexchangerates.org/api/latest.json',
        params={
            'app_id': '6daf8eb7c7374657a5a06c3c7e3469c8',
        }
    )
    if response.status_code == 200:
        d = {
            "USD": 1,
            **response.json()['rates']
        }
        return f"{(1 / d[cur1] * summ * d[cur2]):.2f}"
    else:
        return "Что-то пошло не так :("


async def start(update, context):
    """Начало работы, высылает приветсвенное сообщение"""
    await update.message.reply_text("Приветствую! Я бот-конвертер валют. \n"
                                    "Чтобы начать, введите команду /convert \n"
                                    "/help - помощь")


async def helper(update, context):
    """Отправляет список команд с пояснениями"""
    await update.message.reply_text("/convert - конвертер валют; \n"
                                    "/help - помощь; \n"
                                    "/list - выведет список возможных валют и их кодов; \n"
                                    "/stop - прервать операцию.")


async def list_send(update, context):
    """Высылает список возиожных валют и их кодов"""
    text = "Список возможных валют и их кодов:\n"
    for elem in LIST_OF_CURRENCIES_AND_NAMES:
        text += elem + "\n"
    await update.message.reply_text(text)


async def convert(update, context):
    """Начало конвертации"""
    await update.message.reply_text("Введите код валюты, которую вы хотите перевести в другую или выберите из выпадающего списка.\n"
                                    "Пример: USD \n"
                                    "Список валют - /list.\n"
                                    "Если вы хотите прервать операцию - /stop", reply_markup=markup)
    return 1


async def first_response(update, context):
    cur1 = update.message.text
    if cur1 in LIST_OF_CURRENCIES:
        context.user_data["cur1"] = cur1
        await update.message.reply_text("Введите код валюты, в которую вы хотите перевести или выберите из выпадающего списка\n"
        "/list - список валют", reply_markup=markup)
        return 2
    else:
        await update.message.reply_text("Я не знаю такого кода :(\n"
                                        "Убедитесь, что вы прислали код, а не название валюты и попробуйте ещё раз.")
        return 1


async def second_response(update, context):
    cur2 = update.message.text
    if cur2 in LIST_OF_CURRENCIES:
        context.user_data["cur2"] = cur2
        await update.message.reply_text(f"Введите количество денег, которое вы хотите перевести из "
                                        f"валюты {context.user_data['cur1']} в валюту {context.user_data['cur2']}:")
        return 3
    else:
        await update.message.reply_text("Я не знаю такого кода :(\n"
                                        "Убедитесь, что вы прислали код, а не название валюты и попробуйте ещё раз.")
        return 2


async def third_response(update, context):
    a = update.message.text
    count = 0
    fl = True
    for elem in a:
        if not elem.isdigit():
            if elem == '.':
                if count == 0:
                    count = 1
                else:
                    fl = False
                    break
            else:
                fl = False
                break
    if a.isdigit() or a.count('.') == 1 and a.index('.') != 0 and a.index('.') != len(a) - 1 and fl:
        context.user_data["summ"] = float(a)
        await update.message.reply_text(f"{context.user_data['summ']} {context.user_data['cur1']}"
                                        f" = {latest(context.user_data['cur1'], context.user_data['cur2'], context.user_data['summ'])}"
                                        f" {context.user_data['cur2']}")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, введите число:")
        return 3


async def stop(update, context):
    await update.message.reply_text("Операция прервана.")
    return ConversationHandler.END


conv_handler = ConversationHandler(
        entry_points=[CommandHandler('convert', convert)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, third_response)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", helper))
    application.add_handler(CommandHandler("list", list_send))
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
#http://t.me/ExchangeConvertBot - ссылка