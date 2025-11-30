import json
import logging
from typing import Optional

import pandas as pd
from pandas import DataFrame

import config
from src.utils import read_excel

pd.options.mode.copy_on_write = True

logger_cash = logging.getLogger("cash")

path_xl = str(config.PATH_TO_OPERATIONS)
operations = read_excel(path_xl)


def get_cash_month(operations: Optional[DataFrame], year: int, month: int) -> str | None:
    """
    Функция принимает файл, год, месяц и возвращает список выгодных категорий повышенного кэшбэка
    """
    logger_cash.info(f"Function run for {month}.{year}")

    if operations is None:
        logger_cash.error("operations is None")
        return None

    operations["Дата операции"] = pd.to_datetime(operations["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    filter_df = operations[
        (operations["Дата операции"].dt.year == year) & (operations["Дата операции"].dt.month == month)
    ]
    if filter_df.empty:
        logger_cash.error(f"No data for this date: {month}.{year}")
        return None

    filter_df = filter_df[filter_df["Кэшбэк"] > 0]
    filter_df = filter_df[filter_df["Статус"] == "OK"]
    filter_df_col = filter_df[["Категория", "Кэшбэк"]].groupby("Категория").sum().reset_index()
    result_dict = filter_df_col.set_index("Категория")["Кэшбэк"].to_dict()

    result_json = json.dumps(result_dict, ensure_ascii=False, indent=4)
    logger_cash.info(f"Data received by month: {len(filter_df)} records found")
    return result_json
