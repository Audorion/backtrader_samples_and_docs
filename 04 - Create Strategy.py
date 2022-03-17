from datetime import datetime
import backtrader as bt


class ShowBarPriceVolume(bt.Strategy):
    """Простейшая система без торговли. При приходе нового бара отображает его цены/объем"""

    def log(self, txt, dt=None):
        """Вывод строки с датой на консоль"""
        dt = bt.num2date(self.datas[0].datetime[0]).date() if dt is None else dt  # Заданная дата или дата текущего бара
        print(f'{dt.strftime("%d.%m.%Y")}, {txt}')  # Выводим дату с заданным текстом на консоль

    def __init__(self):
        """Инициализация торговой системы"""
        self.DataOpen = self.datas[0].open
        self.DataHigh = self.datas[0].high
        self.DataLow = self.datas[0].low
        self.DataClose = self.datas[0].close
        self.DataVolume = self.datas[0].volume

    def next(self):
        """Получение следующего бара"""
        self.log(f'Open={self.DataOpen[0]:.2f}, High={self.DataHigh[0]:.2f}, Low={self.DataLow[0]:.2f}, Close={self.DataClose[0]:.2f}, Volume={self.DataVolume[0]:.0f}')


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    cerebro = bt.Cerebro()  # Инициируем "движок" BackTrader
    cerebro.addstrategy(ShowBarPriceVolume)  # Привязываем торговую систему
    data = bt.feeds.GenericCSVData(
        # Можно принимать любые CSV файлы с разделителем десятичных знаков в виде точки https://backtrader.com/docu/datafeed-develop-csv/
        dataname='..\\..\\..\\Data\\TQBR.SBER_D1.txt',  # Файл для импорта
        separator='\t',  # Колонки разделены табуляцией
        dtformat='%d.%m.%Y %H:%M',  # Формат даты/времени DD.MM.YYYY HH:MI
        openinterest=-1,  # Открытого интереса в файле нет
        fromdate=datetime(2019, 1, 1),  # Начальная дата приема исторических данных (Входит)
        todate=datetime(2021, 1, 1))  # Конечная дата приема исторических данных (Не входит)
    cerebro.adddata(data)  # Привязываем исторические данные
    cerebro.broker.setcash(1000000)  # Стартовый капитал для "бумажной" торговли
    print(f'Старовый капитал: {cerebro.broker.getvalue():.2f}')
    cerebro.run()  # Запуск торговой системы
    print(f'Конечный капитал: {cerebro.broker.getvalue():.2f}')
    # cerebro.plot()  # Рисуем график
