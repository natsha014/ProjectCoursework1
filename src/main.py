from src.services import get_cash_month
from src.services import operations
from src.views import str_main

if __name__ == "__main__":
    print(str_main("2020-05-20 15:30:00"))
    print(get_cash_month(operations, 2020, 5))
