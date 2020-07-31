from optionsbacktrader import OptionsBroker, Trader


class TestTrader(Trader):
    def __init__(self):
        self._day = 0

    def step(self, current_date, the_broker, account):
        quote = broker.get_option_quote(symbol='SPX151016C00400000')

        if self._day == 0:
            print(f'Cash: {broker.account.cash}\tMarket Value: {broker.account.get_market_value(broker)}')
            print(f'Cash PL %: {broker.account.get_percent_cash_pl()}\tMarket PL %: {broker.account.get_percent_market_value_pl(broker)}\n')

            long_leg_order = broker.buy(symbol='SPX151016P01870000', size=1)
            short_leg_order = broker.sell(symbol='SPX151016P01880000', size=1)

            print(f'Got {long_leg_order.symbol} for {long_leg_order.price}')
            print(f'Sold {short_leg_order.symbol} for {short_leg_order.price}\n')
        elif self._day == 5:
            long_leg_close_order = broker.sell(symbol='SPX151016P01870000', size=1)
            short_leg_close_order = broker.buy(symbol='SPX151016P01880000', size=1)

            print(f'Sold {long_leg_close_order.symbol} for {long_leg_close_order.price}')
            print(f'Bought back {short_leg_close_order.symbol} for {short_leg_close_order.price}\n')

        print(f'Cash: {broker.account.cash}\tMarket Value: {broker.account.get_market_value(broker)}')
        print(f'Cash PL %: {broker.account.get_percent_cash_pl()}\tMarket PL %: {broker.account.get_percent_market_value_pl(broker)}\n')

        self._day += 1


broker = OptionsBroker()

broker.load_historical_data('./Sample_SPX_20151001_to_20151030.sqlite3', fidelity='day')

broker.set_trader(TestTrader())
broker.account.cash = 1000000

broker.start()
