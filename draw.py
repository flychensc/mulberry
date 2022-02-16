import akshare as ak
import datetime as dt
import mplfinance as mpf
import pandas as pd

import configparser
import pathlib

#akshare
#baostock

my_color = mpf.make_marketcolors(up='r', down='g', edge='inherit', wick='inherit', volume='inherit')
my_style = mpf.make_mpf_style(marketcolors=my_color)

FOLDER = "img"


def gen_kline(data, fpath):
    data = pd.DataFrame(data)
    data['datetime'] = data['datetime'].map(lambda x: dt.datetime.strptime(str(x), "%Y-%m-%d").date())
    data.index = pd.to_datetime(data.datetime)
    data = data.drop(columns=['datetime'])

    mpf.plot(data, type='candle', volume=True, style=my_style, axisoff=True, tight_layout=True, scale_padding=0, savefig={'fname': fpath})


def bluk():
    config = configparser.ConfigParser()
    config.read('config.ini')

    p = pathlib.Path(FOLDER)
    if not p.exists():
        p.mkdir(parents=True)

    PERIOD = config.getint('CANDLE', 'PERIOD')

    symbol_list = config.get('PROB', 'ID_LIST').split(',')

    day = dt.datetime.strptime(config.get('PROB', 'DAY'), "%Y-%m-%d").date()
    end_date = day.strftime("%Y%m%d")

    day -= dt.timedelta(days=365)
    start_date = day.strftime("%Y%m%d")

    for symbol in symbol_list:
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")

        stock_zh_a_hist_df.rename(columns={'日期': 'datetime', '开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low', '成交量': 'volume'}, inplace=True)
        stock_zh_a_hist_df = stock_zh_a_hist_df[['datetime', 'open','close','high','low','volume']]

        fpath = pathlib.Path().joinpath(FOLDER, '.'.join(['_'.join([end_date, symbol]), 'jpg']))
        if len(stock_zh_a_hist_df) < PERIOD:
            print("length error on ", symbol)
        else:
            gen_kline(stock_zh_a_hist_df[-PERIOD:], fpath)


if __name__ == "__main__":
    bluk()
