import website
import numpy as np
import pandas as pd

import configparser


DEBUG = False

RP_COLUMNS = [
    "排除ROE(净利润/净资产)<15%的企业",
    "排除上市未满5年的企业",
    "检查“重要提示”",
    "轻重资产. 生产资产: 固定资产, 在建工程, 工程物资, 土地. 当年税前利润总额/生产资产, 是否显著高于社会平均资本回报率.",
    "营业总收入/(固定资产+无形资产)",
    "毛利率保持40%以上有持续竞争力",
    "费用(销售、管理、正数的财务费用)在毛利润30%以内, 不大于70%也勉强可以",
'''          经现流净额   投现流净额   筹现流净额
老母鸡型:     +           +           -
蛮牛型:       +           -           +
奶牛型:       +           -           -''',
    "经营活动产生的现金流量净额>净利润>0",
    "销售商品、提供劳务收到的现金>=营业收入",
    "投资活动产生的现金流量净额<0, 且主要是投入新项目, 而非用于维持原有生产能力",
    "现金及现金等价物净额增加额>0(可放宽为排除分红因素), 该科目>0",
    "期末现金及现金等价物>=有息负债(可放宽为期末现金及现金等价物+应收票据中的银行承兑汇票>有息负债)",
]


def report(symbol_list, filename="FinancialReportAnalysis.xls"):
    df_report = pd.DataFrame(columns=RP_COLUMNS)

    for symbol in symbol_list:
        df_report.loc[symbol] = [np.nan for i in RP_COLUMNS]

        profitabilit = website.get_profitability(symbol)
        main_financial_indicators = website.get_main_financial_indicators(symbol)
        balance_sheet = website.get_balance_sheet(symbol).fillna(0)
        income_statement = website.get_income_statement(symbol).fillna(0)
        cash_flow_statement = website.get_cash_flow_statement(symbol).fillna(0)

        year = profitabilit.columns[0]
        if DEBUG:
            print(f"{year.year}年{year.month}月:")

            print("{0:<20}: {1}".format('净资产收益率(%)', profitabilit.loc['净资产收益率(%)'][year]))
            print("{0:<20}: {1}".format('销售毛利率(%)', profitabilit.loc['销售毛利率(%)'][year]))

            print("{0:<20}: {1}".format('净资产收益率(%)', main_financial_indicators.loc['净资产收益率(%)'][year]))
            print("{0:<20}: {1}".format('销售毛利率(%)', main_financial_indicators.loc['销售毛利率(%)'][year]))

            print("{0:<20}: {1}".format('货币资金(万元)', balance_sheet.loc['货币资金(万元)'][year]))
            print("{0:<20}: {1}".format('交易性金融资产(万元)', balance_sheet.loc['交易性金融资产(万元)'][year]))
            print("{0:<20}: {1}".format('应收票据(万元)', balance_sheet.loc['应收票据(万元)'][year]))
            print("{0:<20}: {1}".format('投资性房地产(万元)', balance_sheet.loc['投资性房地产(万元)'][year]))
            print("{0:<20}: {1}".format('固定资产(万元)', balance_sheet.loc['固定资产(万元)'][year]))
            print("{0:<20}: {1}".format('在建工程(万元)', balance_sheet.loc['在建工程(万元)'][year]))
            print("{0:<20}: {1}".format('工程物资(万元)', balance_sheet.loc['工程物资(万元)'][year]))
            print("{0:<20}: {1}".format('无形资产(万元)', balance_sheet.loc['无形资产(万元)'][year]))
            print("{0:<20}: {1}".format('短期借款(万元)', balance_sheet.loc['短期借款(万元)'][year]))
            print("{0:<20}: {1}".format('交易性金融负债(万元)', balance_sheet.loc['交易性金融负债(万元)'][year]))
            print("{0:<20}: {1}".format('衍生金融负债(万元)', balance_sheet.loc['衍生金融负债(万元)'][year]))
            print("{0:<20}: {1}".format('一年内到期的非流动负债(万元)', balance_sheet.loc['一年内到期的非流动负债(万元)'][year]))

            print("{0:<20}: {1}".format('营业总收入(万元)', income_statement.loc['营业总收入(万元)'][year]))
            print("{0:<20}: {1}".format('销售费用(万元)', income_statement.loc['销售费用(万元)'][year]))
            print("{0:<20}: {1}".format('管理费用(万元)', income_statement.loc['管理费用(万元)'][year]))
            print("{0:<20}: {1}".format('财务费用(万元)', income_statement.loc['财务费用(万元)'][year]))
            print("{0:<20}: {1}".format('利润总额(万元)', income_statement.loc['利润总额(万元)'][year]))

            print("{0:<20}: {1}".format('销售商品、提供劳务收到的现金(万元)', cash_flow_statement.loc['销售商品、提供劳务收到的现金(万元)'][year]))
            print("{0:<20}: {1}".format('经营活动产生的现金流量净额(万元)', cash_flow_statement.loc['经营活动产生的现金流量净额(万元)'][year]))
            print("{0:<20}: {1}".format('投资活动产生的现金流量净额(万元)', cash_flow_statement.loc['投资活动产生的现金流量净额(万元)'][year]))
            print("{0:<20}: {1}".format('筹资活动产生的现金流量净额(万元)', cash_flow_statement.loc['筹资活动产生的现金流量净额(万元)'][year]))


        # 排除ROE（净利润/净资产）<15%的企业
        df_report.loc[symbol][RP_COLUMNS[0]] = "OK" if profitabilit.loc['净资产收益率(%)'][year] >= 15 else "NG"

        # 排除上市未满5年的企业
        df_report.loc[symbol][RP_COLUMNS[1]] = "OK" if len(profitabilit.columns) >= 5 else "NG"

        # 检查“重要提示”
        # df_report.loc[symbol][RP_COLUMNS[2]]

        # 轻重资产。生产资产：固定资产，在建工程，工程物资，土地。当年税前利润总额/生产资产，是否显著高于社会平均资本回报率。
        df_report.loc[symbol][RP_COLUMNS[3]] = income_statement.loc['利润总额(万元)'][year] / (balance_sheet.loc['投资性房地产(万元)'][year] + balance_sheet.loc['固定资产(万元)'][year] + balance_sheet.loc['在建工程(万元)'][year] + balance_sheet.loc['工程物资(万元)'][year])

        #
        df_report.loc[symbol][RP_COLUMNS[4]] = income_statement.loc['营业总收入(万元)'][year] / (balance_sheet.loc['固定资产(万元)'][year] + balance_sheet.loc['无形资产(万元)'][year])

        # 毛利率保持40%以上有持续竞争力
        df_report.loc[symbol][RP_COLUMNS[5]] = main_financial_indicators.loc['销售毛利率(%)'][year]

        # 费用（销售、管理、正数的财务费用）在毛利润30%以内，不大于70%也勉强可以
        df_report.loc[symbol][RP_COLUMNS[6]] = (income_statement.loc['销售费用(万元)'][year] + income_statement.loc['管理费用(万元)'][year] + (income_statement.loc['财务费用(万元)'][year] if income_statement.loc['财务费用(万元)'][year] > 0 else 0)) / income_statement.loc['利润总额(万元)'][year]

        #           经现流净额      投现流净额       筹现流净额
        # 老母鸡型：    +               +               -
        # 蛮牛型：      +               -               +
        # 奶牛型：      +               -               -
        if cash_flow_statement.loc['经营活动产生的现金流量净额(万元)'][year] > 0 and cash_flow_statement.loc['投资活动产生的现金流量净额(万元)'][year] > 0 and cash_flow_statement.loc['筹资活动产生的现金流量净额(万元)'][year] < 0:
            df_report.loc[symbol][RP_COLUMNS[7]] = "老母鸡型"
        elif cash_flow_statement.loc['经营活动产生的现金流量净额(万元)'][year] > 0 and cash_flow_statement.loc['投资活动产生的现金流量净额(万元)'][year] < 0 and cash_flow_statement.loc['筹资活动产生的现金流量净额(万元)'][year] > 0:
            df_report.loc[symbol][RP_COLUMNS[7]] = "蛮牛型"
        elif cash_flow_statement.loc['经营活动产生的现金流量净额(万元)'][year] > 0 and cash_flow_statement.loc['投资活动产生的现金流量净额(万元)'][year] < 0 and cash_flow_statement.loc['筹资活动产生的现金流量净额(万元)'][year] < 0:
            df_report.loc[symbol][RP_COLUMNS[7]] = "奶牛型"
        else:
            df_report.loc[symbol][RP_COLUMNS[7]] = "NG"

        # 经营活动产生的现金流量净额>净利润>0
        df_report.loc[symbol][RP_COLUMNS[8]] = "OK" if cash_flow_statement.loc['经营活动产生的现金流量净额(万元)'][year] > income_statement.loc['利润总额(万元)'][year] > 0 else "NG"

        # 销售商品、提供劳务收到的现金>=营业收入
        df_report.loc[symbol][RP_COLUMNS[9]] = "OK" if cash_flow_statement.loc['销售商品、提供劳务收到的现金(万元)'][year] > income_statement.loc['营业总收入(万元)'][year] else "NG"

        # 投资活动产生的现金流量净额<0，且主要是投入新项目，而非用于维持原有生产能力
        df_report.loc[symbol][RP_COLUMNS[10]] = "OK" if cash_flow_statement.loc['投资活动产生的现金流量净额(万元)'][year] < 0 else "NG"

        # 现金及现金等价物净额增加额>0（可放宽为排除分红因素），该科目>0
        if profitabilit.columns.size > 1:
            last_year = profitabilit.columns[1]
            df_report.loc[symbol][RP_COLUMNS[11]] = "OK" if (balance_sheet.loc['货币资金(万元)'][year] + balance_sheet.loc['交易性金融资产(万元)'][year]) - (balance_sheet.loc['货币资金(万元)'][last_year] + balance_sheet.loc['交易性金融资产(万元)'][last_year]) > 0 else "NG"

        # 期末现金及现金等价物>=有息负债（可放宽为期末现金及现金等价物+应收票据中的银行承兑汇票>有息负债）
        df_report.loc[symbol][RP_COLUMNS[12]] = "OK" if (balance_sheet.loc['货币资金(万元)'][year] + balance_sheet.loc['交易性金融资产(万元)'][year] + balance_sheet.loc['应收票据(万元)'][year]) >= (balance_sheet.loc['短期借款(万元)'][year] + balance_sheet.loc['交易性金融负债(万元)'][year] + balance_sheet.loc['衍生金融负债(万元)'][year] + balance_sheet.loc['一年内到期的非流动负债(万元)'][year]) else "NG"


    if DEBUG:
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.precision', 2)
        print("财报分析:")
        print(df_report)

    # FutureWarning: As the xlwt package is no longer maintained, the xlwt engine will be removed in a future version of pandas. This is the only engine in pandas that supports writing in the xls format. Install openpyxl and write to an xlsx file instead. You can set the option io.excel.xls.writer to 'xlwt' to silence this warning. While this option is deprecated and will also raise a warning, it can be globally set and the warning suppressed.
    df_report.to_excel(filename, index=True)


def do_report():
    config = configparser.ConfigParser()
    config.read('config.ini')

    symbol_list = config.get('PROB', 'ID_LIST').split(',')
    if DEBUG:
        symbol_list = ['002324']

    report(symbol_list)


if __name__ == "__main__":
    do_report()
