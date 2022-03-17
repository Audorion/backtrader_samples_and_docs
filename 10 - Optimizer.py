from datetime import datetime
import backtrader as bt


class PriceMACross(bt.Strategy):
    """Пересечение цены и SMA"""
    params = (  # Параметры торговой системы
        ('SMAPeriod', 26),  # Период SMA
        ('PrintLog', False),  # Выводить лог на консоль
    )

    def log(self, txt, dt=None, doprint=False):
        """Вывод строки с датой на консоль"""
        if self.params.PrintLog or doprint:  # Если на уровне ТС или тестера нужно сделать вывод на консоль
            dt = dt or self.datas[0].datetime.date(0)  # Заданная дата или дата текущего бара
            print(f'{dt.isoformat()}, {txt}')  # Выводим дату в формате ISO с заданным текстом на консоль 

    def __init__(self):
        """Инициализация торговой системы"""
        self.DataClose = self.datas[0].close
        self.Order = None  # Заявка
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.SMAPeriod)  # SMA

    def notify_order(self, order):
        """Изменение статуса заявки"""
        if order.status in [order.Submitted, order.Accepted]:  # Если заявка не исполнена (отправлена брокеру или принята брокером)
            return  # то статус заявки не изменился, выходим, дальше не продолжаем

        if order.status in [order.Completed]:  # Если заявка исполнена
            if order.isbuy():  # Заявка на покупку
                self.log(f'Bought @{order.executed.price:.2f}, Cost={order.executed.value:.2f}, Comm={order.executed.comm:.2f}')
            elif order.issell():  # Заявка на продажу
                self.log(f'Sold @{order.executed.price:.2f}, Cost={order.executed.value:.2f}, Comm={order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:  # Заявка отменена, нет средств, отклонена брокером
            self.log('Canceled/Margin/Rejected')
        self.Order = None  # Этой заявки больше нет

    def notify_trade(self, trade):
        """Изменение статуса позиции"""
        if not trade.isclosed:  # Если позиция не закрыта
            return  # то статус позиции не изменился, выходим, дальше не продолжаем

        self.log(f'Trade Profit, Gross={trade.pnl:.2f}, NET={trade.pnlcomm:.2f}')
    
    def next(self):
        """Получение следующего бара"""
        self.log(f'Close={self.DataClose[0]:.2f}')
        if self.Order:  # Если есть неисполненная заявка
            return  # то выходим, дальше не продолжаем
        
        if not self.position:  # Если позиции нет
            isSignalBuy = self.DataClose[0] > self.sma[0]  # Цена закрылась выше скользящцей
            if isSignalBuy:  # Если пришла заявка на покупку
                self.log('Buy Market')
                self.Order = self.buy()  # Заявка на покупку одной акции по рыночной цене
        else:  # Если позиция есть
            isSignalSell = self.DataClose[0] < self.sma[0]  # Цена закрылась ниже скользящей
            if isSignalSell:  # Если пришла заявка на продажу
                self.log('Sell Market')
                self.Order = self.sell()  # Заявка на продажу одной акции по рыночной цене

    def stop(self):
        """Окончание запуска торговой системы"""
        self.log(f'SMA({self.params.SMAPeriod}), Конечный капитал: {self.broker.getvalue():.2f}', doprint=True)


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    cerebro = bt.Cerebro()  # Инициируем "движок" BackTrader
    cerebro.optstrategy(PriceMACross, SMAPeriod=range(8, 65))  # Торговая система на оптимизацию с параметрами. Первое значение входит, последнее - нет
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
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)  # Кол-во акций для покупки/продажи
    cerebro.broker.setcommission(commission=0.001)  # Комиссия брокера 0.1% от суммы каждой исполненной заявки
    cerebro.run()  # Запуск торговой системы. Можно указать кол-во ядер процессора, которые будут загружены. Например, maxcpus=2
