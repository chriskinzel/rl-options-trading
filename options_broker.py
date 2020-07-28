import backtrader as bt
import json
import pandas


class OptionsBroker(bt.Cerebro):
    def __init__(self, options_data_path):
        super().__init__()

        with open(options_data_path, 'r') as fp:
            options_data = json.load(fp)
            self._option_chains = {
                key: self._convert_date(pandas.DataFrame.from_dict(value)) for key, value in options_data.items()
            }
            print(self._option_chains['SPX151016C00400000'])

        for key, data in self._option_chains.items():
            self.adddata(bt.feeds.PandasData(dataname=data, datetime=-1), name=key)

        self.addsizer(bt.sizers.SizerFix, stake=100)

    def _convert_date(self, df):
        df['datetime'] = pandas.to_datetime(df['datetime'], unit='ms')
        return df
