import json
import sys
from unittest.mock import MagicMock
from unittest.mock import patch

import pandas as pd

mock_config_object = MagicMock()
mock_config_object.PATH_TO_OPERATIONS = "fake_ops_path.xlsx"
mock_config_object.PATH_TO_USER_SETTINGS = "fake_settings_path.json"


@patch("src.utils.get_stock")
@patch("src.utils.get_currency")
@patch("src.utils.load_json")
@patch("src.utils.get_top")
@patch("src.utils.get_cards")
@patch("src.utils.get_filter_date_df")
@patch("src.utils.read_excel")
@patch("src.utils.get_time_greeting")
def test_main_function_success(
    mock_get_time_greeting,
    mock_read_excel,
    mock_get_filter_date_df,
    mock_get_cards,
    mock_get_top,
    mock_load_json,
    mock_get_currency,
    mock_get_stock,
):
    with patch.dict(sys.modules, {"config": mock_config_object}):
        from src.views import logger_views
        from src.views import str_main

        with patch.object(logger_views, "info") as mock_logger_info, patch.object(
            logger_views, "error"
        ) as mock_logger_error:
            mock_get_time_greeting.return_value = "Добрый день"
            mock_excel_df = MagicMock(spec=pd.DataFrame)
            mock_filtered_df = MagicMock(spec=pd.DataFrame)
            mock_read_excel.return_value = mock_excel_df
            mock_get_filter_date_df.return_value = mock_filtered_df
            mock_get_cards.return_value = [{"last_digits": "1234", "total_spent": -1500.0, "cashback": 45.0}]
            mock_get_top.return_value = [
                {"date": "20.05.2020", "amount": 200.0, "category": "Еда", "description": "Обед"}
            ]
            mock_user_settings = MagicMock(spec=dict)
            mock_load_json.return_value = mock_user_settings
            mock_get_currency.return_value = [{"currency": "USD", "rate": 90.0}]
            mock_get_stock.return_value = [{"stock": "AAPL", "price": 150.0}]

            test_date = "2020-05-20 15:30:00"
            result_json = str_main(date=test_date)

            mock_logger_info.assert_called_once_with(f"Function run for {test_date}")
            mock_get_time_greeting.assert_called_once()
            mock_read_excel.assert_called_once_with("fake_ops_path.xlsx")
            mock_get_filter_date_df.assert_called_once_with(mock_excel_df, test_date)
            mock_get_cards.assert_called_once_with(mock_filtered_df)
            mock_get_top.assert_called_once_with(mock_filtered_df)
            mock_load_json.assert_called_once_with("fake_settings_path.json")
            mock_get_currency.assert_called_once_with(mock_user_settings)
            mock_get_stock.assert_called_once_with(mock_user_settings)

            expected_result_dict = {
                "greeting": "Добрый день",
                "cards": [{"last_digits": "1234", "total_spent": -1500.0, "cashback": 45.0}],
                "top_transactions": [
                    {"date": "20.05.2020", "amount": 200.0, "category": "Еда", "description": "Обед"}
                ],
                "currency_rates": [{"currency": "USD", "rate": 90.0}],
                "stock_prices": [{"stock": "AAPL", "price": 150.0}],
            }
            assert json.loads(result_json) == expected_result_dict
