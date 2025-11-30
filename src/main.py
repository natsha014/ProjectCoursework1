import logging

from src.reports import spending_by_category
from src.services import get_cash_month
from src.services import operations
from src.views import str_main

logger_main = logging.getLogger("main")


def main() -> None:  # pragma: no cover
    """Функция отвечает за основную логику проекта и связывает функциональности между собой"""
    try:
        date = input("Введите дату в формате YYYY-MM-DD HH:MM:SS, чтобы получить данные с начала месяца    ")
        print(str_main(date))

        print("Чтобы получить список выгодных категорий повышенного кэшбэка за месяц")
        year = int(input("введите год    "))
        month = int(input("Введите месяц    "))
        print(get_cash_month(operations, year, month))

        print("Чтобы получить траты по заданной категории за последние три месяца")
        category = input("Введите категорию    ").capitalize()
        date_r = input("Ведите дату (необязательно)    ")
        print(spending_by_category(operations, category, date_r))

    except Exception as e:
        logger_main.error(f"Error: {e}")


# if __name__ == "__main__":
#     main()
