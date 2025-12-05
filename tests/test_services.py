import json

import pandas as pd

from src.services import get_cash_month


def test_get_cash_month_success():
    data = {
        "Дата операции": [
            "01.01.2025 10:00:00",
            "15.01.2025 12:00:00",
            "31.01.2025 14:00:00",
            "01.02.2025 09:00:00",
            "10.01.2025 09:00:00",
            "10.01.2025 09:00:00",
        ],
        "Категория": ["Еда", "Транспорт", "Еда", "Транспорт", "Еда", "Развлечения"],
        "Кэшбэк": [10.0, 5.0, 0.0, 20.0, 15.0, 2.0],
        "Статус": ["OK", "OK", "OK", "OK", "OK", "FAIL"],
    }
    input_df = pd.DataFrame(data)
    target_year = 2025
    target_month = 1

    expected_dict = {"Еда": 25.0, "Транспорт": 5.0}
    expected_result_json = json.dumps(expected_dict, ensure_ascii=False, indent=4)

    result = get_cash_month(input_df.copy(), target_year, target_month)

    assert result is not None
    assert result == expected_result_json


def test_get_cash_month_none_input():
    result = get_cash_month(None, 2025, 1)

    assert result is None


def test_get_cash_month_empty_filter():
    data = {
        "Дата операции": ["01.02.2025 10:00:00", "15.02.2025 12:00:00"],
        "Категория": ["Еда", "Транспорт"],
        "Кэшбэк": [10.0, 5.0],
        "Статус": ["OK", "OK"],
    }
    input_df = pd.DataFrame(data)
    target_year = 2025
    target_month = 1

    result = get_cash_month(input_df.copy(), target_year, target_month)

    assert result is None
