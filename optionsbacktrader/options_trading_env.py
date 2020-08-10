import gym
from gym import spaces

import numpy as np

from datetime import timedelta


def clamp(n, smallest, largest): return max(smallest, min(n, largest))


class OptionsTradingEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, broker, max_chain_length=2602):
        super(OptionsTradingEnvironment, self).__init__()

        self._max_chain_length = max_chain_length
        self.broker = broker

        # delta, spread delta, dte, buy, sell, ignore
        self.action_space = spaces.Box(
            low=np.array([-1, 0, 0, 0, 0, 0]), high=np.array([1, 1, 31, 1, 1, 1]), dtype=np.float32)

        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(max_chain_length, 5 * 8 + 2), dtype=np.float32)

    def reset(self):
        self.broker.account.reset()
        self.broker.start(step_mode=True)

        return self._next_observation()

    def _next_observation(self):
        self.broker.step()

        options_chain = self.broker.get_options_chain()

        return self._vectorize_options_chain(options_chain)

    def step(self, action):
        self._take_action(action)

        for position in self.broker.account.get_positions():
            if position.book_value < 0.0 and position.asset.expiry_date == self.broker.current_date:
                self.broker.close(position)

        obs = self._next_observation()

        reward = self.broker.account.get_percent_spent_pl(self.broker) * 100
        if not self.broker.account.get_positions():
            reward -= 0.01

        done = not self.broker.isRunning

        return obs, reward, done, {}

    def _take_action(self, action):
        action_type = np.argmax([action[-3], action[-2], action[-1]])
        if action_type != 2:
            ntm_leg_delta = action[0]
            otm_leg_delta = clamp(ntm_leg_delta + (action[1] if ntm_leg_delta >= 0.0 else -action[1]), -1.0, 1.0)
            dte = round(action[2])

            expiry_date = self.broker.current_date + timedelta(days=dte)

            ntm_leg_option = self.broker.find_option(delta=ntm_leg_delta, expiry=expiry_date)
            otm_leg_option = self.broker.find_option(delta=otm_leg_delta, expiry=expiry_date)

            if ntm_leg_option is None or otm_leg_option is None:
                return

            if ntm_leg_option.asset.symbol == otm_leg_option.asset.symbol:
                return

            if action_type == 0:
                self.broker.buy(quote=ntm_leg_option)
                self.broker.sell(quote=otm_leg_option)
            else:
                self.broker.sell(quote=ntm_leg_option)
                self.broker.buy(quote=otm_leg_option)

    def render(self, mode='human', close=False):
        print('-' * 100, end='\n\n')

        print(f'Date: {self.broker.current_date.strftime("%m/%d/%Y")}')
        print(f'Total Return: {self.broker.account.get_percent_spent_pl(self.broker) * 100:.3f}%', end='\n\n')

        print('Positions:', end='\n\n')
        for position in self.broker.account.get_positions():
            market_value = self.broker.get_market_order_price_for_quote(
                self.broker.get_option_quote(symbol=position.symbol),
                is_buy=position.book_value < 0.0
            ) * (
                1.0 if position.book_value >= 0.0 else -1.0
            ) * position.size - (
                0.0 if position.book_value >= 0.0 else position.get_total_book_value() * 2
            )

            print(f'{position.symbol} Strike: {position.asset.strike} Qty: {position.size // 100} Price: {position.book_value} Market Value: {market_value}', end='\n\n')

        print('-' * 100, end='\n\n')

    def _vectorize_options_chain(self, options_chain):
        vec = np.array(
            list(map(lambda quote: self._quote_to_vec(quote), options_chain))[:self._max_chain_length]
        )

        if vec.shape[0] < self._max_chain_length:
            vec = np.append(vec, [[0] * (8 * 5 + 2)] * (self._max_chain_length - vec.shape[0]), axis=0)

        return vec

    def _quote_to_vec(self, input_quote):
        history = self.broker.get_history_for_option(symbol=input_quote.asset.symbol,
                                                     from_date=self.broker.current_date,
                                                     to_date=self.broker.current_date - timedelta(days=5))

        vec = list(map(lambda quote: [
            quote.bid / input_quote.underlying_last,
            quote.ask / input_quote.underlying_last,
            quote.asset.implied_volatility,
            quote.asset.delta,
            quote.asset.theta,
            quote.asset.gamma,
            quote.asset.vega,
            quote.underlying_last / input_quote.underlying_last,
        ], history))

        if len(history) < 5:
            for i in range(5 - len(history)):
                vec.insert(i, [0.0] * 8)

        vec = [item for sublist in vec for item in sublist] + [
            input_quote.asset.strike / input_quote.underlying_last
        ] + [
                  # TODO: -1 if short position
                  1.0 if self.broker.account.get_position(symbol=input_quote.asset.symbol) else 0.0
              ]

        return vec
