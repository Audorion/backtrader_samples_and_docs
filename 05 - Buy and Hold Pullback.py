from datetime import datetime
import backtrader as bt
import yfinance as yf


class BuyAndHoldPullback(bt.Strategy):

    def log(self, txt, dt=None):
        """Вывод строки с датой на консоль"""
        dt = bt.num2date(self.datas[0].datetime[0]).date() if dt is None else dt  # Заданная дата или дата текущего бара
        print(f'{dt.strftime("%d.%m.%Y")}, {txt}')  # Выводим дату с заданным текстом на консоль

    def __init__(self):
        """Инициализация торговой системы"""
        self.cheating = self.cerebro.p.cheat_on_open
        self.DataClose = self.datas[0].close
        self.Step = 5
        self.Order1 = None
        self.Order2 = None
        self.StartBalance = cerebro.broker.getvalue()
        self.StopLoss = self.StartBalance - 4000
        self.StopProfit = self.StartBalance + 4000
        self.StatusEnd = False
        self.StatusStop = False

    def notify_order(self, order):
        print('{}: Order ref: {} / Type {} / Status {}'.format(
            self.data.datetime.date(0),
            order.ref, 'Buy' * order.isbuy() or 'Sell',
            order.getstatusname()))
        if order.status == order.Completed:
            if order.isbuy():  # Заявка на покупку
                self.log(f'Bought @{order.executed.price:.2f}')
            elif order.issell():  # Заявка на продажу
                self.log(f'Sold @{order.executed.price:.2f}')
        if order.status == order.Canceled:
            self.log(f'Cancel order')
        if not (self.StopLoss < cerebro.broker.cash < self.StopProfit):
            self.log(f"Stop trading with Loss/Profit: {self.StopLoss} < {cerebro.broker.cash} < {self.StopProfit}")
            self.StatusEnd = True

    def next(self):
        """Получение следующего бара"""
        if self.StatusStop:
            print(3)
            self.env.runstop()
            return
        elif self.StatusEnd:
            self.cancel(self.Order1)
            self.cancel(self.Order2)
            self.close()
            print(2)
            return
        elif (self.Order1 and self.Order1.status == bt.Order.Completed) or (self.Order2 and self.Order2.status == bt.Order.Completed):
            self.cancel(self.Order1)
            self.cancel(self.Order2)
            self.Order1 = None
            self.Order2 = None
        elif self.Order1 or self.Order2:
            return
        else:
            self.log("Oder landing...")
            self.Order1 = self.sell(price=self.DataClose + self.Step, exectype=bt.Order.Limit)
            self.Order2 = self.buy(price=self.DataClose - self.Step, exectype=bt.Order.Limit)

    def next_open(self):
        if self.StatusEnd:
            print(1)
            self.StatusStop = True

    # isSignalBuy = self.DataClose[0] < self.DataClose[-1] < self.DataClose[-2]  # Цена падает 2 сессии подряд
    # if isSignalBuy:  # Если пришла заявка на покупку
    #     self.log('Buy Market')
    #     self.buy()  # Заявка на покупку одной акции по рыночной цене
    def stop(self):
        self.log(self.position)


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    cerebro = bt.Cerebro(cheat_on_open=True)  # Инициируем "движок" BackTrader
    cerebro.addstrategy(BuyAndHoldPullback)  # Привязываем торговую систему
    data = bt.feeds.PandasData(dataname=yf.download('TSLA', '2022-01-22', '2022-01-30', interval="1d"))
    cerebro.adddata(data)  # Привязываем исторические данные
    cerebro.broker.setcash(1000000)  # Стартовый капитал для "бумажной" торговли
    print(f'Старовый капитал: {cerebro.broker.getvalue():.2f}')
    cerebro.run()  # Запуск торговой системы
    print(f'Конечный капитал: {cerebro.broker.getvalue():.2f}')
    cerebro.plot()  # Рисуем график
