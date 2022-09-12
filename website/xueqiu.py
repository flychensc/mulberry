"""
雪球网接口
"""

import requests
import numpy as np
import pandas as pd

HEADERS = {
    'authority': 'stock.xueqiu.com',
    'method': 'GET',
    # 随代码变化
    'path': '/v5/stock/finance/cn/indicator.json?symbol=SZ002324&type=Q4&is_detail=true&count=5&timestamp=',
    'scheme': 'https',
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    # F12 - [网络] - [标头]
    'cookie': 'device_id=ac924898ea7acf6ab2eff3e83d52a951; s=bk12p3vs9w; remember=1; xq_a_token=6ca8d94c0605ec207b55b89ea3bedaa1c611a8eb; xqat=6ca8d94c0605ec207b55b89ea3bedaa1c611a8eb; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjE2MjI3NDQ5NjIsImlzcyI6InVjIiwiZXhwIjoxNjY0Mzc0Mjg0LCJjdG0iOjE2NjI5NTA3MzM0NTAsImNpZCI6ImQ5ZDBuNEFadXAifQ.ioMyzTAQmGVWjjFcd-xk0lkpO5rrkt4b03RFQrneD12AUgd7UhBadVe1ur9LKiPf8-Fv-0ldi4SxwWsG_9ALdtmqZEx64qej19KolK_ctvOpTfMWacVTOTMAAiMFnCemnHzGX42CBfQ_k7leE2fbgKNpukJtzDNtmjSOzZgd8MQ9U8I26o0JeP40S0T26tXS_8b3I7fRPcAl5lapnuWGIPKhrb2lbBBAabEwktztlWA5eu4z80QP_8Rn8aT30cR_oDVagKvVtm6FIiqBeOeMRlwL6VMOlDq1bJFS-QCtiSoMlr-uLA_TGYBHpy7C9KRdqFZInkAknu0yN47xEXUOKA; xq_r_token=b9a026064ab57811e7e3f2178d2b882415174eef; xq_is_login=1; u=1622744962; Hm_lvt_1db88642e346389874251b5a1eded6e3=1662950720,1662959218,1662961258,1662962805; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1662963183',
    'origin': 'https://xueqiu.com',
    # 随代码变化
    'referer': 'https://xueqiu.com/snowman/S/SZ002324/detail',
    'sec-ch-ua': '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "Windows",
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33',
}


def get_main_financial_indicators(code, annual=True):
    """
        获取个股主要财务指标
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

    # https://stock.xueqiu.com/v5/stock/finance/cn/indicator.json?symbol=SZ002324&type=all&is_detail=true&count=5&timestamp=

    symbol = f"SH{code}" if code.startswith('6') else f"SZ{code}"

    url = r"https://stock.xueqiu.com/v5/stock/finance/cn/indicator.json"
    params = {"symbol": symbol, "type": "all", "is_detail": "true", "count": "5", "timestamp": ""}

    if annual:
        params["type"] = "Q4"
    else:
        raise NotImplementedError

    # update header
    HEADERS['path'] =  f'/v5/stock/finance/cn/indicator.json?symbol={symbol}&type={type}&is_detail=true&count=5&timestamp='
    HEADERS['referer'] = f'https://xueqiu.com/snowman/S/{symbol}/detail'

    session = requests.Session()
    session.headers.update(HEADERS)

    response = session.get(url, params=params, timeout=5)

    session.close()

    # 未实现所有数据
    mf_indicators = pd.DataFrame(index = ['净资产收益率(%)', '销售毛利率(%)'])

    for data in response.json()['data']['list']:
        year = data['report_name'][:4] + "-12-31"

        mf_indicators[year] = np.nan

        mf_indicators.loc['净资产收益率(%)'][year] = data['avg_roe'][0]
        mf_indicators.loc['销售毛利率(%)'][year] = data['gross_selling_rate'][0]

    return mf_indicators
