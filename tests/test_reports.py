from unittest.mock import mock_open
from unittest.mock import patch

from src.reports import spending_by_category


def test_spending_by_category_input_none_log_error():
    expected_log_content = None

    with patch("builtins.open", mock_open()) as mock_file:
        result = spending_by_category(operations=None, category="Еда")

        assert result is None

        mock_file.assert_called_with("log.log", "w", encoding="utf-8")
        handle = mock_file()
        handle.write.assert_called_once_with(expected_log_content)
