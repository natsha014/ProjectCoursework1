import json
from unittest.mock import mock_open
from unittest.mock import patch

import pandas as pd
import pytest

from src.reports import spending_by_category


def test_spending_by_category_input_none_log_error():
    expected_log_content = None

    with patch("builtins.open", mock_open()) as mock_file:
        result = spending_by_category(operations=None, category="Еда")

        assert result is None

        mock_file.assert_called_with("log.log", "w", encoding="utf-8")
        handle = mock_file()
        handle.write.assert_called_once_with(expected_log_content)


@pytest.fixture
def operations_df():
    data = {
        "Дата операции": [
            "14.01.2025",
            "16.01.2025",
            "01.04.2025",
            "16.04.2025",
            "01.03.2025",
            "20.03.2025",
            "20.03.2025",
        ],
        "Категория": ["Еда", "Еда", "Еда", "Еда", "Транспорт", "Еда", "Еда"],
        "Сумма операции с округлением": [10.0, 20.0, 5.0, 50.0, 100.0, 15.0, 5.0],
        "Статус": ["OK", "OK", "OK", "OK", "FAIL", "OK", "OK"],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    return df


@pytest.mark.parametrize(
    "date_r, category, expected_json",
    [
        ("2025-04-15", "Еда", json.dumps({"Еда": 45.0}, ensure_ascii=False, indent=4)),
        ("2025-04-15", "Транспорт", json.dumps({})),
        ("2025-04-15", "Канцтовары", json.dumps({})),
    ],
)
def test_spending_by_category_parametrized(date_r, category, expected_json, operations_df):
    result = spending_by_category(operations=operations_df, category=category, date_r=date_r)

    assert result == expected_json
