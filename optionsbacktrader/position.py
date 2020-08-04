from .execution import OrderType

class Position:
    def __init__(self, symbol, book_value, size, asset):
        if symbol is None:
            raise ValueError()

        self.symbol = symbol
        self.book_value = book_value
        self.size = size
        self.asset = asset

    @classmethod
    def from_execution(cls, execution):
        return Position(symbol=execution.symbol,
                        book_value=execution.price if execution.order_type == OrderType.BUY else -execution.price,
                        size=execution.size,
                        asset=execution.asset)

    def get_total_book_value(self):
        return self.book_value * self.size

    def __str__(self):
        separator = '-' * 100

        return f'{separator}\n' \
               f'Qty: {self.size}\tBook Value: {self.book_value}\n\n' \
               f'{self.asset}\n' \
               f'{separator}\n'
