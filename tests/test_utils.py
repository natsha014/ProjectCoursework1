import json
from unittest.mock import Mock
from unittest.mock import patch

import pandas as pd
from freezegun import freeze_time

from src.utils import get_cards
from src.utils import get_currency
from src.utils import get_filter_date_df
from src.utils import get_stock
from src.utils import get_time_greeting
from src.utils import get_top
from src.utils import load_json
from src.utils import read_excel


def test_get_time_greeting():
    with freeze_time("2020-03-25 05:00:00"):
        assert get_time_greeting() == "Доброе утро"
    with freeze_time("2020-03-25 12:00:00"):
        assert get_time_greeting() == "Добрый день"
    with freeze_time("2020-03-25 18:00:00"):
        assert get_time_greeting() == "Добрый вечер"
    with freeze_time("2020-03-25 22:00:00"):
        assert get_time_greeting() == "Доброй ночи"


@patch("src.utils.os.path.exists")
@patch("src.utils.os.path.getsize")
@patch("src.utils.pd.read_excel")
def test_read_excel_success(mock_read_excel, mock_getsize, mock_exists):
    mock_exists.return_value = True
    mock_getsize.return_value = 1
    expected_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    mock_read_excel.return_value = expected_df

    result = read_excel("valid_path.xlsx")

    assert result.equals(expected_df)
    mock_read_excel.assert_called_once_with("valid_path.xlsx")


@patch("src.utils.os.path.exists")
@patch("src.utils.os.path.getsize")
def test_read_excel_file_not_exists_or_empty(mock_getsize, mock_exists):
    mock_exists.return_value = False
    result = read_excel("invalid_path.xlsx")
    assert result is None

    mock_exists.return_value = True
    mock_getsize.return_value = 0
    result = read_excel("empty_file.xlsx")
    assert result is None


def test_filter_date_successful_filtering():
    data = {
        "Дата операции": ["01.01.2025 10:00:00", "15.01.2025 12:00:00", "31.01.2025 14:00:00", "01.02.2025 09:00:00"],
        "Сумма": [100, 200, 300, 400],
    }
    input_df = pd.DataFrame(data)
    target_date = "2025-01-20 23:59:59"

    expected_data = {
        "Дата операции": pd.to_datetime(["01.01.2025 10:00:00", "15.01.2025 12:00:00"], dayfirst=True),
        "Сумма": [100, 200],
    }
    expected_df = pd.DataFrame(expected_data)
    result_df = get_filter_date_df(input_df.copy(), target_date)
    assert result_df is not None
    assert expected_df.equals(result_df)


def test_filter_date_none_input():
    input_df = None
    target_date = "2025-01-20 23:59:59"
    result = get_filter_date_df(input_df, target_date)
    assert result is None


def test_get_cards_successful_processing():
    data = {
        "Номер карты": ["*1111", "*1111", "*2222", "*2222", "*3333"],
        "Сумма платежа": [-50.0, -100.0, -20.0, 50.0, -30.0],
        "Сумма операции с округлением": [-50.0, -100.0, -20.0, 50.0, -30.0],
        "Кэшбэк": [1.5, 3.0, 0.5, 0.0, 1.0],
        "Статус": ["OK", "OK", "OK", "OK", "FAIL"],
    }
    input_df = pd.DataFrame(data)

    expected_result = [
        {"last_digits": "1111", "total_spent": -150.0, "cashback": 4.5},
        {"last_digits": "2222", "total_spent": -20.0, "cashback": 0.5},
    ]

    result = get_cards(input_df.copy())

    assert result is not None
    assert result == expected_result


def test_get_cards_none_input():
    input_df = None
    result = get_cards(input_df)

    assert result is None


def test_get_cards_empty_filtered_df():
    data = {
        "Номер карты": ["*1111", "*2222"],
        "Сумма платежа": [50.0, 100.0],
        "Сумма операции с округлением": [50.0, 100.0],
        "Кэшбэк": [1.5, 3.0],
        "Статус": ["OK", "OK"],
    }
    input_df = pd.DataFrame(data)
    expected_result = []
    result = get_cards(input_df.copy())
    assert result is not None
    assert result == expected_result


def test_get_top_successful_processing():
    data = {
        "Дата операции": pd.to_datetime(
            ["2025-01-05", "2025-01-01", "2025-01-03", "2025-01-06", "2025-01-02", "2025-01-04"]
        ),
        "Сумма платежа": [10.0, 50.0, 20.0, 60.0, 30.0, 999.0],
        "Сумма операции с округлением": [10.0, 50.0, 20.0, 60.0, 30.0, 999.0],
        "Категория": ["Еда", "Транспорт", "Развлечения", "Покупки", "Счета", "Зарплата"],
        "Описание": ["Обед", "Метро", "Кино", "Кроссовки", "Свет", "Аванс"],
        "Статус": ["OK", "OK", "OK", "OK", "OK", "FAIL"],
    }
    input_df = pd.DataFrame(data)

    expected_result = [
        {"date": "06.01.2025", "amount": 60.0, "category": "Покупки", "description": "Кроссовки"},
        {"date": "01.01.2025", "amount": 50.0, "category": "Транспорт", "description": "Метро"},
        {"date": "02.01.2025", "amount": 30.0, "category": "Счета", "description": "Свет"},
        {"date": "03.01.2025", "amount": 20.0, "category": "Развлечения", "description": "Кино"},
        {"date": "05.01.2025", "amount": 10.0, "category": "Еда", "description": "Обед"},
    ]

    result = get_top(input_df.copy(), top=5)
    assert result is not None
    assert len(result) == 5
    assert result == expected_result


def test_get_top_custom_top_size():
    data = {
        "Дата операции": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
        "Сумма платежа": [100.0, 50.0, 200.0],
        "Сумма операции с округлением": [100.0, 50.0, 200.0],
        "Категория": ["A", "B", "C"],
        "Описание": ["Op A", "Op B", "Op C"],
        "Статус": ["OK", "OK", "OK"],
    }
    input_df = pd.DataFrame(data)

    expected_result = [
        {"date": "03.01.2025", "amount": 200.0, "category": "C", "description": "Op C"},
        {"date": "01.01.2025", "amount": 100.0, "category": "A", "description": "Op A"},
    ]

    result = get_top(input_df.copy(), top=2)

    assert result is not None
    assert len(result) == 2
    assert result == expected_result


def test_get_top_none_input():
    result = get_top(None)
    assert result is None


def test_load_json_with_tmp(tmp_path):
    test_file = tmp_path / "test_file_json"

    data = [{"key_1": "value_1", "number": 123}, {"key_2": "value_2", "number": 456}]
    with open(test_file, "w") as f:
        json.dump(data, f)

    result = load_json(str(test_file))
    assert result == data


@patch("os.path.exists")
def test_file_path_not_exists(mock_exists):
    mock_exists.return_value = False
    assert load_json("non_exists_file_json") is None
    mock_exists.assert_called_with("non_exists_file_json")


@patch("os.path.exists")
@patch("os.path.getsize")
def test_file_not_empty(mock_exists, mock_getsize):
    mock_exists.return_value = True
    mock_getsize.return_value = 0
    assert load_json("empty_file_json") is None
    mock_getsize.assert_called_with("empty_file_json")


def test_get_currency_success():
    input_settings = {"user_currencies": ["USD", "EUR"]}

    mock_resp_usd = Mock()
    mock_resp_usd.status_code = 200
    mock_resp_usd.json.return_value = {"query": {"from": "USD"}, "result": 90.12345}

    mock_resp_eur = Mock()
    mock_resp_eur.status_code = 200
    mock_resp_eur.json.return_value = {"query": {"from": "EUR"}, "result": 100.45678}

    expected_result = [
        {"currency": "USD", "rate": 90.12},  # Округлено до 2 знаков
        {"currency": "EUR", "rate": 100.46},
    ]

    with patch("requests.get") as mock_get:
        mock_get.side_effect = [mock_resp_usd, mock_resp_eur]

        result = get_currency(input_settings)
        assert result == expected_result
        assert mock_get.call_count == 2


def test_get_currency_none_input():
    result = get_currency(None)

    assert result is None


def test_get_currency_url_none():
    input_settings = {"user_currencies": ["USD"]}

    with patch("src.utils.url_c", None):
        result = get_currency(input_settings)

        assert result is None


def test_get_currency_api_error_status():
    input_settings = {"user_currencies": ["USD"]}

    mock_resp_error = Mock()
    mock_resp_error.status_code = 403

    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_resp_error

        result = get_currency(input_settings)

        assert result is None


def test_get_stock_success():
    input_settings = {"user_stocks": ["AAPL", "GOOG"]}

    mock_resp_aapl = Mock()
    mock_resp_aapl.status_code = 200
    mock_resp_aapl.json.return_value = {"Global Quote": {"01. symbol": "AAPL", "05. price": "175.5567"}}

    mock_resp_goog = Mock()
    mock_resp_goog.status_code = 200
    mock_resp_goog.json.return_value = {"Global Quote": {"01. symbol": "GOOG", "05. price": "140.1234"}}

    expected_result = [{"stock": "AAPL", "price": 175.56}, {"stock": "GOOG", "price": 140.12}]

    with patch("requests.get") as mock_get:
        mock_get.side_effect = [mock_resp_aapl, mock_resp_goog]

        result = get_stock(input_settings)
        assert result == expected_result
        assert mock_get.call_count == 2


def test_get_stock_none_input():
    result = get_stock(None)

    assert result is None


def test_get_stock_url_none():
    input_settings = {"user_stocks": ["AAPL"]}

    with patch("src.utils.url_s", None):
        result = get_stock(input_settings)

        assert result is None


def test_get_stock_api_error_status():
    input_settings = {"user_stocks": ["AAPL"]}

    mock_resp_error = Mock()
    mock_resp_error.status_code = 500

    with patch("requests.get") as _:
        result = get_stock(input_settings)

        assert result is None
