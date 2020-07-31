from .position import Position
from .execution import OrderType


class Account:
    def __init__(self, cash=0):
        self._initial_value = cash
        self._cash = cash
        self._positions = {}
        self._executions = []

    @property
    def cash(self):
        return self._cash

    @cash.setter
    def cash(self, cash):
        if self._initial_value == 0:
            self._initial_value = cash

        self._cash = cash

    def get_positions(self):
        return list(self._positions.values())

    def get_executions(self):
        return self._executions

    def get_position(self, symbol):
        if symbol in self._positions:
            return self._positions[symbol]
        else:
            return False

    def update_from_execution(self, execution):
        self._executions.append(execution)

        if execution.symbol in self._positions:
            existing_position = self._positions[execution.symbol]

            if (existing_position.book_value < 0.0 and execution.order_type == OrderType.BUY) or (
                    existing_position.book_value > 0.0 and execution.order_type == OrderType.SELL
            ):
                # Reducing existing position
                if execution.size == existing_position.size:
                    # Existing position closed out
                    if existing_position.book_value > 0.0:
                        # Closing out long position
                        self._cash += execution.get_total_value()
                    else:
                        # Closing out short position
                        self._cash += -existing_position.get_total_book_value() * 2 - execution.get_total_value()

                    del self._positions[existing_position.symbol]
                elif execution.size > existing_position.size:
                    # Existing position type swap
                    new_position = Position.from_execution(execution)
                    new_position.size = execution.size - existing_position.size
                    self._positions[existing_position.symbol] = new_position

                    if execution.order_type == OrderType.BUY:
                        # Previous short position now long

                        # Payment for closing short position
                        self._cash += -existing_position.get_total_book_value() * 2 - existing_position.size * execution.price

                        # Price to open long position
                        self._cash -= new_position.size * execution.price
                    else:
                        # Previous long position now short

                        # Payment for closing long position
                        self._cash += existing_position.size * execution.price

                        # Price to open short position
                        self._cash -= new_position.size * execution.price
            else:
                # Increasing existing position
                existing_position.size += execution.size
                if execution.order_type == OrderType.BUY:
                    existing_position.book_value = (existing_position.book_value + execution.price) / 2.0
                else:
                    existing_position.book_value = (existing_position.book_value + -execution.price) / 2.0

                self._cash -= execution.get_total_value()
        else:
            self._positions[execution.symbol] = Position.from_execution(execution)
            self._cash -= execution.get_total_value()

    def get_percent_cash_pl(self):
        return (self._cash - self._initial_value) / self._initial_value

    def get_market_value(self, broker, quotedate=None):
        return sum(
            map(
                lambda position: + broker.get_market_order_price_for_quote(
                    broker.get_option_quote(symbol=position.symbol, quotedate=quotedate),
                    is_buy=position.book_value < 0.0
                ) * (
                    1.0 if position.book_value >= 0.0 else -1.0
                ) * position.size - (
                    0.0 if position.book_value >= 0.0 else position.get_total_book_value() * 2
                ),
                self.get_positions()
            )
        ) + self._cash

    def get_percent_market_value_pl(self, broker, quotedate=None):
        return (self.get_market_value(broker, quotedate) - self._initial_value) / self._initial_value
