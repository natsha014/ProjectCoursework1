import json
import logging
from functools import wraps
from typing import Any
from typing import Callable
from typing import Optional

import pandas as pd
from pandas import DataFrame

import config
from src.utils import read_exel

pd.options.mode.copy_on_write = True

logger_reports = logging.getLogger("reports")

path_xl = str(config.PATH_TO_OPERATIONS)
operations = read_exel(path_xl)


def log(filename: str) -> Callable:
    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            try:
                result = func(*args, **kwargs)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(result)
                return result
            except Exception as e:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"{func.__name__} error: {e}. Inputs: {args}, {kwargs}\n")

        return inner

    return wrapper


@log("log.log")
def spending_by_category(operations: Optional[DataFrame], category: str, date_r: Optional[str] = None) -> str | None:
    """
    Функция возвращает траты по заданной категории за последние
    три месяца (от переданной даты)
    """
    logger_reports.info("Function run")
    if operations is None:
        logger_reports.error("operations is None")
        return None

    if category is None:
        logger_reports.error("Category is None")
        return None

    if date_r is None:
        user_date = pd.to_datetime("today").normalize()
    else:
        user_date = pd.to_datetime(date_r)

    try:
        start_date = user_date - pd.DateOffset(months=3)
        operations["Дата операции"] = pd.to_datetime(operations["Дата операции"], dayfirst=True)
        filter_total = operations[
            (operations["Дата операции"].between(start_date, user_date)) & (operations["Категория"] == category)
        ]
        filter_total = filter_total[filter_total["Статус"] == "OK"]

        if filter_total.empty:
            logger_reports.info(f"No data found for category '{category}' from {start_date} to {user_date}.")
            return json.dumps({})

        result_df = (
            filter_total[["Категория", "Сумма операции с округлением"]].groupby("Категория").sum().reset_index()
        )

        result_dict = result_df.set_index("Категория")["Сумма операции с округлением"].to_dict()
        result_json = json.dumps(result_dict, ensure_ascii=False, indent=4)
        logger_reports.info(f"Data received from {start_date} to {user_date}")
        return result_json
    except Exception as e:
        logger_reports.error(f"Error: {e}")
        return None
