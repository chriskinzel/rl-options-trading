from enum import Enum


class OrderType(Enum):
    BUY = 'buy',
    SELL = 'sell'


class Execution:
    def __init__(self, symbol, price, size, asset, order_type):
        self.symbol = symbol
        self.price = price if price >= 0.0 else -price
        self.size = size
        self.asset = asset
        self.order_type = order_type

    def get_total_value(self):
        return self.price * self.size

    def __str__(self):
        separator = '-' * 100

        return f'{separator}\n' \
               f'Order {self.order_type.name}\tQty: {self.size}\tPrice: {self.price}\n\n' \
               f'{self.asset}\n' \
               f'{separator}\n'
