import backtrader as bt  # Библиотека BackTrader (pip install backtrader)


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    cerebro = bt.Cerebro()  # Инициируем "движок" BackTrader (Cerebro = Мозг на испанском)
    print(f'Старовый капитал: {cerebro.broker.getvalue()}')  # По умолчанию получаем "бумажную" торговлю с начальным размером счета в 10000
    cerebro.run()  # Запуск ТС. Пока ее у нас нет
    print(f'Конечный капитал: {cerebro.broker.getvalue()}')  # Поэтому, размер капитала не должен измениться
