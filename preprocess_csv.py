#!/usr/bin/env python

import sys
import os
import json
import pandas

if len(sys.argv) < 2:
    print('Usage: preprocess_csv.py <csv_path>')
    exit(1)


def convert_dataframe(df):
    result = pandas.DataFrame(columns=['datetime', 'open', 'high', 'low', 'close'])

    prices = df['bid'] * 0.5 + df['ask'] * 0.5

    result['datetime'] = df['quotedate'].copy()
    result['open'] = prices.copy()
    result['high'] = prices.copy()
    result['low'] = prices.copy()
    result['close'] = prices.copy()

    return json.loads(result.to_json())


csv_path = sys.argv[1]

data = pandas.read_csv(csv_path, parse_dates=['expiration', 'quotedate'], header=0)

option_chain = {
    key: convert_dataframe(data.loc[value]) for key, value in data.groupby('optionroot', sort=False).groups.items()
}

with open(os.path.splitext(csv_path)[0]+'.json', 'w') as fp:
    json.dump(option_chain, fp, indent=2)
