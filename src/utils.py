import json
import logging
import os
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

import config

pd.options.mode.copy_on_write = True
load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename=config.PATH_TO_LOGGER / "utils.log",
    filemode="w",
    encoding="utf-8",
    format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",
)

logger_greeting = logging.getLogger("greeting")
logger_excel = logging.getLogger("excel")
logger_filter_date = logging.getLogger("filter_date")
logger_cards = logging.getLogger("cards")
logger_top = logging.getLogger("top")
logger_json = logging.getLogger("load_json")
logger_currency = logging.getLogger("currency")
logger_stock = logging.getLogger("stock")

url_c = os.getenv("url_c")
api_key_c = os.getenv("my_apikey_c")

url_s = os.getenv("url_s")
api_key_s = os.getenv("my_apikey_s")


def get_time_greeting() -> str:
    """
    Функция возвращает «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени
    """
    logger_greeting.info("Run function")

    try:
        user_time = datetime.now().hour
        if 5 <= user_time < 12:
            return "Доброе утро"
        elif 12 < user_time <= 18:
            return "Добрый день"
        elif 18 < user_time <= 22:
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    except Exception as e:
        logger_greeting.error(f"Error: {e}")
        return ""


def read_exel(path_xlsx: str) -> DataFrame | None:
    """
    Чтение Exel файла
    """
    logger_excel.info("Run function")

    if not os.path.exists(path_xlsx) or os.path.getsize(path_xlsx) == 0:
        logger_excel.error("Path_xlsx does not exist or is empty")
        return None
    else:
        df = pd.read_excel(path_xlsx)
        logger_excel.info("Data received")

    return df


def get_filter_date_df(operations: Optional[DataFrame], date: str) -> DataFrame | None:
    """
    Функция принимает файл, входящую дату и возвращает данные с начала месяца,
    на который выпадает входящая дата, по входящую дату
    """
    logger_filter_date.info("Run function")

    if operations is None:
        logger_filter_date.error("operations is None")
        return None

    date_start = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-1 00:00:00")
    operations["Дата операции"] = pd.to_datetime(operations["Дата операции"], dayfirst=True)
    filter_df = operations[operations["Дата операции"].between(date_start, date)]
    logger_filter_date.info(f"Data received from {date_start} to {date} {len(filter_df)} records found")
    return filter_df


def get_cards(df_filter_date: Optional[DataFrame]) -> list[dict] | None:
    """
    Функция принимает отфильтрованную по дате таблицу и возвращает
    информацию по каждой карте: последние 4 цифры карты; общая сумма расходов; кешбэк.
    """
    logger_cards.info("Run function")

    if df_filter_date is None:
        logger_cards.error("Input DataFrame is None")
        return None

    try:
        df_filter_date = df_filter_date[df_filter_date["Сумма платежа"] < 0]
        df_filter_date = df_filter_date[df_filter_date["Статус"] == "OK"]
        df_filter_col = (
            df_filter_date[["Номер карты", "Сумма операции с округлением", "Кэшбэк"]]
            .groupby("Номер карты")
            .sum()
            .reset_index()
        )

        df_filter_col.rename(
            columns={
                "Номер карты": "last_digits",
                "Сумма операции с округлением": "total_spent",
                "Кэшбэк": "cashback",
            },
            inplace=True,
        )

        dict_cards = df_filter_col.to_dict("records")

        result = []
        for i in dict_cards:
            new_i = {
                "last_digits": i["last_digits"].replace("*", ""),
                "total_spent": round(i["total_spent"], 2),
                "cashback": i["cashback"],
            }

            result.append(new_i)

        logger_cards.info("Result received")
        return result

    except Exception as e:
        logger_cards.error(f"Error: {e}")
        return None


def get_top(df_filter_date: Optional[DataFrame], top: int = 5) -> list[dict] | None:
    """
    Функция принимает отфильтрованную по дате таблицу
    и возвращает топ-5 транзакций по сумме платежа
    """
    logger_top.info("Run function")

    if df_filter_date is None:
        logger_top.error("Input DataFrame is None. Cannot process.")
        return None

    try:
        df_filter_date = df_filter_date[df_filter_date["Статус"] == "OK"]
        df_sorted = df_filter_date.sort_values(by="Сумма операции с округлением", ascending=False)
        df_top_total = df_sorted[:top]
        df_top = df_top_total[["Дата операции", "Сумма платежа", "Категория", "Описание"]]
        df_top["Дата операции"] = df_top["Дата операции"].apply(lambda x: x.strftime("%d.%m.%Y"))

        df_top.rename(
            columns={
                "Дата операции": "date",
                "Сумма платежа": "amount",
                "Категория": "category",
                "Описание": "description",
            },
            inplace=True,
        )

        dict_top = df_top.to_dict("records")

        logger_top.info("Result received")
        return dict_top

    except Exception as e:
        logger_cards.error(f"Error: {e}")
        return None


def load_json(path_json: str) -> Optional[Dict[str, Any]]:
    """
    Чтение json файла
    """
    logger_json.info("Run function")

    if not os.path.exists(path_json) or os.path.getsize(path_json) == 0:
        logger_json.error("Path_json does not exist or is empty")
        return None
    else:
        with open(path_json, "r", encoding="utf-8") as f:
            file = json.load(f)
            logger_json.info("Data received")
        return dict(file)


def get_currency(user_settings: Optional[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    """
    Функция принимает файл настроек и возвращает курс валют
    """
    logger_currency.info("Run function")

    if user_settings is None:
        logger_currency.error("user_settings is None")
        return None

    currency_rate = []

    currencies = user_settings["user_currencies"]
    for currency in currencies:
        payload = {"amount": 1, "from": currency, "to": "RUB"}
        headers = {"apikey": api_key_c}

        if url_c is not None:
            response = requests.get(url_c, headers=headers, params=payload)

            status_code = response.status_code
            if status_code == 200:
                resp = response.json()
                logger_currency.info("Request received")
                cur_resp = resp.get("query", {}).get("from")
                cur_rate = round(float(resp.get("result")), 2)
                currency_rate.append({"currency": cur_resp, "rate": cur_rate})
                logger_currency.info("Currencies received")
            else:
                logger_currency.error(f"Status_code: {status_code}")
                return None
        else:
            logger_currency.error("URL not found, request skipped")
            return None
    return currency_rate


def get_stock(user_settings: Optional[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    """
    Функция принимает файл настроек и возвращает стоимость акций
    """
    logger_stock.info("Run function")

    if user_settings is None:
        logger_currency.error("user_settings is None.")
        return None

    stocks_price = []

    stocks = user_settings["user_stocks"]
    for stock in stocks:
        params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": api_key_s}
        if url_s is not None:
            r = requests.get(url_s, params=params)

            status_code = r.status_code

            if status_code == 200:
                data = r.json()
                logger_stock.info("Request received")
                stock_r = data.get("Global Quote", {}).get("01. symbol")
                stock_price = round(float(data.get("Global Quote", {}).get("05. price")), 2)
                stocks_price.append({"stock": stock_r, "price": stock_price})
                logger_stock.info("Stocks received")
            else:
                logger_stock.error(f"Status_code: {status_code}")
                return None
        else:
            logger_stock.error("URL not found, request skipped")
            return None
    return stocks_price
