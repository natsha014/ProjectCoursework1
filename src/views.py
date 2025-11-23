import json

import config
from src.utils import get_cards
from src.utils import get_currency
from src.utils import get_filter_date_df
from src.utils import get_stock
from src.utils import get_time_greeting
from src.utils import get_top
from src.utils import load_json
from src.utils import read_exel


def str_main(date: str) -> str:
    """
    Функция принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращает JSON-ответ со следующими данными:
    - Приветствие в формате «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени
    - По каждой карте: последние 4 цифры карты; общая сумма расходов; кешбэк (1 рубль на каждые 100 рублей)
    - Топ-5 транзакций по сумме платежа
    - Курс валют
    - Стоимость акций из S&P500
    """
    path_xl = str(config.PATH_TO_OPERATIONS)
    path_j = str(config.PATH_TO_USER_SETTINGS)

    greeting = get_time_greeting()
    operations = read_exel(path_xl)
    df_filter_date = get_filter_date_df(operations, date)
    cards = get_cards(df_filter_date)
    top_transactions = get_top(df_filter_date)
    user_settings = load_json(path_j)
    currency_rates = get_currency(user_settings)
    stock_prices = get_stock(user_settings)

    result = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    result_json = json.dumps(result, ensure_ascii=False, indent=4)

    return result_json
