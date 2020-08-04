class Quote:
    def __init__(self, quotedate, asset, bid, ask, underlying_last):
        self.quotedate = quotedate
        self.asset = asset
        self.bid = bid
        self.ask = ask
        self.underlying_last = underlying_last

    def __str__(self):
        separator = '-' * 100

        return f'{separator}\n' \
               f'Quotedate\t\t\tBid\tAsk\n' \
               f'{self.quotedate}\t{self.bid}\t{self.ask}\n\n' \
               f'{self.asset}\n' \
               f'{separator}\n'
