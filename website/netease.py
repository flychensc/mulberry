"""
网易财经接口
"""

import datetime
import requests
import pandas as pd
import numpy as np

from io import StringIO

HEADERS = {
    "Accept":
    "text/html, application/xhtml+xml, image/jxr, */*",
    "Accept-Language":
    "zh-CN",
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063",
    "Accept-Encoding":
    "gzip, deflate",
    "Host":
    "quotes.money.163.com",
    "Connection":
    "Keep-Alive"
}


def get_main_financial_indicators(code, part=None, annual=True):
    """
        获取个股主要财务指标
    Parameters
    ------
        code:string
                股票代码 e.g. 002356
        part:string
                None: 主要财务指标
                "ylnl": 盈利能力
        annual:bool, 默认 true
                报表类型，默认年报
    return
    ------
        DataFrame
    """

    # http://quotes.money.163.com/service/zycwzb_002356.html
    url = r"http://quotes.money.163.com/service/zycwzb_%s.html" % code

    session = requests.Session()
    session.headers.update(HEADERS)

    params = {}
    if annual:
        params["type"] = "year"
    if part:
        params["part"] = part

    response = session.get(url, params=params, timeout=5)

    response.encoding = "gbk"
    session.close()

    balance_sheet = pd.read_csv(
        StringIO(response.text),
        index_col=0,
        na_values=np.NaN,
        skipinitialspace=True)
    # pylint: disable=E1101
    # drop unnamed column
    balance_sheet.drop(balance_sheet.columns[-1], axis=1, inplace=True)
    # convert type
    balance_sheet.columns = pd.to_datetime(balance_sheet.columns)
    return balance_sheet.replace("--", np.NaN).astype(float)


def get_profitability(code, annual=True):
    """
        获取个股主要财务指标[盈利能力]
    Parameters
    ------
        code:string
                股票代码 e.g. 002356
        annual:bool, 默认 true
                报表类型，默认年报
    return
    ------
        DataFrame
    """

    return get_main_financial_indicators(code, "ylnl", annual)


def get_balance_sheet(code, annual=True):
    """
        获取个股资产负债表
    Parameters
    ------
        code:string
                股票代码 e.g. 002356
        annual:bool, 默认 true
                报表类型，默认年报
    return
    ------
        DataFrame
    """

    # http://quotes.money.163.com/service/zcfzb_002356.html
    url = r"http://quotes.money.163.com/service/zcfzb_%s.html" % code

    session = requests.Session()
    session.headers.update(HEADERS)

    if annual:
        response = session.get(url, params={"type": "year"}, timeout=5)
    else:
        response = session.get(url, timeout=5)

    response.encoding = "gbk"
    session.close()

    balance_sheet = pd.read_csv(
        StringIO(response.text),
        index_col=0,
        na_values=np.NaN,
        skipinitialspace=True)
    # pylint: disable=E1101
    # drop unnamed column
    balance_sheet.drop(balance_sheet.columns[-1], axis=1, inplace=True)
    # convert type
    balance_sheet.columns = pd.to_datetime(balance_sheet.columns)
    return balance_sheet.replace("--", np.NaN).astype(float)


def get_income_statement(code, annual=True):
    """
        获取个股利润表
    Parameters
    ------
        code:string
                股票代码 e.g. 002356
        annual:bool, 默认 true
                报表类型，默认年报
    return
    ------
        DataFrame
    """

    #http://quotes.money.163.com/service/lrb_002356.html
    url = r"http://quotes.money.163.com/service/lrb_%s.html" % code

    session = requests.Session()
    session.headers.update(HEADERS)

    if annual:
        response = session.get(url, params={"type": "year"}, timeout=5)
    else:
        response = session.get(url)

    response.encoding = "gbk"
    session.close()

    profit_statement = pd.read_csv(
        StringIO(response.text),
        index_col=0,
        na_values=np.NaN,
        skipinitialspace=True)
    # pylint: disable=E1101
    # drop unnamed column
    profit_statement.drop(profit_statement.columns[-1], axis=1, inplace=True)
    # convert type
    profit_statement.columns = pd.to_datetime(profit_statement.columns)
    return profit_statement.replace("--", np.NaN).astype(float)


def get_cash_flow_statement(code, annual=True):
    """
        获取个股现金流量表
    Parameters
    ------
        code:string
                股票代码 e.g. 002356
        annual:bool, 默认 true
                报表类型，默认年报
    return
    ------
        DataFrame
    """

    #http://quotes.money.163.com/service/xjllb_002356.html
    url = r"http://quotes.money.163.com/service/xjllb_%s.html" % code

    session = requests.Session()
    session.headers.update(HEADERS)

    if annual:
        response = session.get(url, params={"type": "year"}, timeout=5)
    else:
        response = session.get(url)

    response.encoding = "gbk"
    session.close()

    profit_statement = pd.read_csv(
        StringIO(response.text),
        index_col=0,
        na_values=np.NaN,
        skipinitialspace=True)
    # pylint: disable=E1101
    # drop unnamed column
    profit_statement.drop(profit_statement.columns[-1], axis=1, inplace=True)
    # convert type
    profit_statement.columns = pd.to_datetime(profit_statement.columns)
    return profit_statement.replace("--", np.NaN).astype(float)


def get_k_data(code, start=''):
    if start is None or start == '':
        start_day = (datetime.date.today()-datetime.timedelta(days=30*6))
    else:
        start_day = datetime.datetime.strptime(str(start)[:10], "%Y-%m-%d")

    params = {
        "code": "0" + code if code.startswith('6') else '1' + code,
        'start': datetime.datetime.strftime(start_day, "%Y%m%d"),
        'end': datetime.datetime.strftime(datetime.datetime.today(), "%Y%m%d"),
        'fields': 'TCLOSE;HIGH;LOW;TOPEN;VOTURNOVER',
    }
    headers = {
        'Host': 'quotes.money.163.com',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'http://quotes.money.163.com/trade/lsjysj_' + code + '.html',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    url = r"http://quotes.money.163.com/service/chddata.html"

    session = requests.Session()
    session.headers.update(headers)

    response = session.get(url, params=params, timeout=5)

    response.encoding = "gbk"
    session.close()

    historys = pd.read_csv(
        StringIO(response.text),
        na_values=np.NaN,
        converters={
            '股票代码': lambda x:x[1:]
        })

    return historys.rename(columns={
            '日期': 'date',
            "股票代码": "code",
            "名称": "name",
            "开盘价": "open",
            "收盘价": "close",
            "最高价": "high",
            "最低价": "low",
            "成交量": "volume"
        })
