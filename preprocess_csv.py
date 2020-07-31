#!/usr/bin/env python

import sys
import os

import sqlite3
import pandas

if len(sys.argv) < 2:
    print('Usage preprocess_csv.py <csv_path>')
    exit(0)

csv_path = sys.argv[1]
output_path = os.path.splitext(csv_path)[0] + '.sqlite3'

data = pandas.read_csv(csv_path, parse_dates=['expiration', 'quotedate'], header=0)

db_connection = sqlite3.connect(output_path)
db = db_connection.cursor()

with open('./optionsbacktrader/db.sql', 'r') as fp:
    sql_script = fp.read()
    db.executescript(sql_script)

for row in data.itertuples():
    to_insert = (
        row.underlying,
        row.underlying_last,
        row.optionroot,
        row.type[0].lower(),
        row.expiration.value,
        row.quotedate.value,
        row.strike,
        row.last,
        row.bid,
        row.ask,
        row.impliedvol,
        row.delta,
        row.gamma,
        row.theta,
        row.vega
    )

    db.execute('INSERT INTO historical_data ('
               'underlying,'
               'underlying_last,'
               'optionroot,'
               'type,'
               'expiration,'
               'quotedate,'
               'strike,'
               'last,'
               'bid,'
               'ask,'
               'impliedvol,'
               'delta,'
               'gamma,'
               'theta,'
               'vega'
               ') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);', to_insert)

db_connection.commit()
db_connection.close()
