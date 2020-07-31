from enum import Enum


class OptionType(Enum):
    CALL = 'c'
    PUT = 'p'


class Option:
    def __init__(self,
                 symbol,
                 underlying_symbol,
                 option_type,
                 strike,
                 expiry_date,
                 implied_volatility,
                 delta,
                 theta,
                 gamma,
                 vega):
        self.symbol = symbol
        self.underlying_symbol = underlying_symbol
        self.option_type = OptionType.CALL if option_type == 'c' else OptionType.PUT
        self.strike = strike
        self.expiry_date = expiry_date
        self.implied_volatility = implied_volatility
        self.delta = delta
        self.theta = theta
        self.gamma = gamma
        self.vega = vega

    def __str__(self):
        return f'Asset: {self.symbol}\tType: Option\tUnderlying: {self.underlying_symbol}\n\n' \
               f'Type\tStrike\tExpiry\t\tImp. Vol.\tDelta\t\tTheta\t\tGamma\t\tVega\n' \
               f'{"Call" if self.option_type == OptionType.CALL else "Put"}\t{self.strike}\t{self.expiry_date.strftime("%m/%d/%Y")}\t{self.implied_volatility}\t\t{self.delta}\t\t{self.theta}\t\t{self.gamma}\t\t{self.vega}\n'
