import sqlite3

from datetime import datetime, timezone
from .account import Account
from .trader import Trader
from .option import Option
from .quote import Quote
from .execution import Execution, OrderType


def datetime_to_db(date):
    return int(date.replace(tzinfo=timezone.utc).timestamp() * 10 ** 9)

def datetime_from_db(timestamp):
    return datetime.fromtimestamp(timestamp / 10 ** 9, timezone.utc)


class OptionsBroker:
    def __init__(self, liquidity_risk=0.5, commission=0, account=Account()):
        self._liquidity_risk = liquidity_risk
        self._commission = commission
        self._current_date = None
        self._fidelity = None
        self._isRunning = False

        self._db_connection = None
        self._db = None

        self.data_start_date = None
        self.data_end_date = None

        self.account = account
        self.trader = Trader()

    @property
    def fidelity(self):
        return self._fidelity

    @property
    def liquidity_risk(self):
        return self._liquidity_risk

    @liquidity_risk.setter
    def liquidity_risk(self, value):
        if value < 0.0 or value > 1.0:
            raise ValueError

        self._liquidity_risk = value

    @property
    def commission(self):
        return self._commission

    @commission.setter
    def commission(self, value):
        if value < 0.0:
            raise ValueError

        self._commission = value

    def load_historical_data(self, db_path, fidelity=None, in_memory=False):
        if not fidelity:
            fidelity = self._fidelity

        self._fidelity = fidelity

        self._db_connection = sqlite3.connect(db_path)
        if in_memory:
            memory_db_connection = sqlite3.connect(':memory:')
            self._db_connection.backup(memory_db_connection)
            self._db_connection.close()

            self._db_connection = memory_db_connection

        self._db = self._db_connection.cursor()

        self.data_start_date = datetime_from_db(
            self._db.execute('SELECT MIN(quotedate) FROM historical_data').fetchall()[0][0]
        )
        self.data_end_date = datetime_from_db(
            self._db.execute('SELECT MAX(quotedate) FROM historical_data').fetchall()[0][0]
        )

    def set_trader(self, trader):
        self.trader = trader

    def start(self, start_date=None, end_date=None):
        if start_date is None:
            start_date = self.data_start_date

        if end_date is None:
            end_date = self.data_end_date

        self._current_date = start_date

        simulation_days = map(lambda row: datetime.fromtimestamp(row[0] / 10**9, timezone.utc),
                              self._db
                              .execute(
                                  'SELECT DISTINCT quotedate FROM historical_data WHERE quotedate >= ? AND quotedate <= ? ORDER BY quotedate ASC',
                                  (datetime_to_db(start_date), datetime_to_db(end_date))
                              )
                              .fetchall())

        self._isRunning = True

        for trading_date in simulation_days:
            if not self._isRunning:
                break

            self._current_date = trading_date
            self.trader.step(trading_date, self, self.account)

        self._isRunning = False

    def stop(self):
        self._isRunning = False

    def shutdown(self):
        self._db_connection.close()

    def buy(self, symbol, quote=None, size=1):
        if quote is None:
            quote = self.get_option_quote(symbol)

        order_price = self.get_market_order_price_for_quote(quote, is_buy=True)
        order = Execution(symbol=symbol,
                          price=order_price,
                          size=size * 100,
                          asset=quote.asset,
                          order_type=OrderType.BUY)

        self.account.update_from_execution(order)
        self.account.cash -= self._commission

        return order

    def sell(self, symbol, quote=None, size=1):
        if quote is None:
            quote = self.get_option_quote(symbol)

        order_price = -self.get_market_order_price_for_quote(quote, is_buy=False)
        order = Execution(symbol=symbol,
                          price=order_price,
                          size=size * 100,
                          asset=quote.asset,
                          order_type=OrderType.SELL)

        self.account.update_from_execution(order)
        self.account.cash -= self._commission

        return order

    def close(self, position):
        if self.account.get_position(position.symbol):
            if position.book_value >= 0.0:
                return self.sell(symbol=position.symbol, size=position.size)
            else:
                return self.buy(symbol=position.symbol, size=position.size)

    def get_option_quote(self, symbol, quotedate=None):
        if quotedate is None:
            quotedate = self._current_date

        result = self._db.execute(
            'SELECT optionroot, underlying, type, strike, expiration, bid, ask, impliedvol, delta, gamma, theta, vega FROM historical_data WHERE optionroot = ? AND quotedate = ?',
            (symbol, datetime_to_db(quotedate))
        ).fetchall()

        if result:
            result = result[0]
            return Quote(
                quotedate=quotedate,
                asset=Option(
                    symbol=result[0],
                    underlying_symbol=result[1],
                    option_type=result[2],
                    strike=result[3],
                    expiry_date=datetime_from_db(result[4]),
                    implied_volatility=result[7],
                    delta=result[8],
                    gamma=result[9],
                    theta=result[10],
                    vega=result[11]
                ), bid=result[5], ask=result[6])
        else:
            return Quote(quotedate=quotedate, asset=symbol, bid=0, ask=0)

    def get_options_chain(self, quotedate=None, expiry_min=None, expiry_max=None):
        if quotedate is None:
            quotedate = self._current_date

        if expiry_min is None:
            expiry_min = quotedate

        if expiry_max is None:
            expiry_max = self.data_end_date

        return list(map(
            lambda row: Quote(
                quotedate=quotedate,
                asset=Option(
                    symbol=row[0],
                    underlying_symbol=row[1],
                    option_type=row[2],
                    strike=row[3],
                    expiry_date=datetime_from_db(row[4]),
                    implied_volatility=row[7],
                    delta=row[8],
                    gamma=row[9],
                    theta=row[10],
                    vega=row[11]
                ), bid=row[5], ask=row[6]),
            self._db.execute(
                'SELECT optionroot, underlying, type, strike, expiration, bid, ask, impliedvol, delta, gamma, theta, vega FROM historical_data WHERE expiration >= ? AND expiration <= ? AND quotedate = ? ORDER BY expiration ASC',
                (datetime_to_db(expiry_min), datetime_to_db(expiry_max), datetime_to_db(quotedate))
            ).fetchall()))

    def get_history_for_option(self, symbol, from_date=None, to_date=None):
        if from_date is None:
            from_date = self._current_date

        if to_date is None:
            to_date = self.data_start_date

        start_date = to_date if to_date < from_date else from_date
        end_date = from_date if to_date < from_date else to_date

        return list(map(
            lambda row: Quote(
                quotedate=datetime_from_db(row[0]),
                asset=Option(
                    symbol=row[1],
                    underlying_symbol=row[2],
                    option_type=row[3],
                    strike=row[4],
                    expiry_date=datetime_from_db(row[5]),
                    implied_volatility=row[8],
                    delta=row[9],
                    gamma=row[10],
                    theta=row[11],
                    vega=row[12]
                ), bid=row[6], ask=row[7]),
            self._db.execute(
                'SELECT quotedate, optionroot, underlying, type, strike, expiration, bid, ask, impliedvol, delta, gamma, theta, vega FROM historical_data WHERE optionroot = ? AND quotedate >= ? AND quotedate <= ? ORDER BY quotedate ASC',
                (symbol, datetime_to_db(start_date), datetime_to_db(end_date))
            ).fetchall()))

    def get_market_order_price_for_quote(self, quote, is_buy):
        if is_buy:
            return quote.bid * (1.0 - self._liquidity_risk) + quote.ask * self._liquidity_risk
        else:
            return quote.bid * self._liquidity_risk + quote.ask * (1.0 - self._liquidity_risk)
