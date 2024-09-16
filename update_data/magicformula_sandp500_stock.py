import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date


## To acquire stock list in S&P500 ###
ex1 = pd.read_csv('update_data/stock_info_s&p500.csv')
df = pd.DataFrame(ex1['Symbol'].astype('str'))
df = df.rename(columns={'Symbol' : 'ticker'})
df = df.drop_duplicates()
df = df.reset_index(drop=True)

# 1st pulling date for this data #
df['date_pulling'] = date.today()

# 2nd acquiring information from .info #
info_attribute_list = [
    'industry',
    'sector',
    'enterpriseValue',
    'totalCashPerShare',
    'profitMargins',
    'trailingPE',
    'currentPrice',
    'fiftyTwoWeekLow',
    'fiftyTwoWeekHigh'
]
# 3rd acquiring information from .quarterly_balance_sheet #
balancesheet_list = [
    'Total Assets',
    'Current Liabilities',
    'Invested Capital'
]

# 4th acquiring information from .quarterly_financials #
ttm = 4
financials_list = [
    'EBIT',
    'Operating Income'
]

info_attribute_list_buffer = []
balancesheet_list_buffer = []
financials_list_buffer = []
for i in range(len(df)):
    print(i, "/", len(df)-1 , df['ticker'][i])
    yfticker = yf.Ticker(df['ticker'][i])

    # 2nd acquiring information from .info #
    info_attribute_list_buffer_r = []
    for j in range(len(info_attribute_list)):
        try:
            info_attribute_list_buffer_r.append(yfticker.info[info_attribute_list[j]])
        except:
            info_attribute_list_buffer_r.append(None)
    info_attribute_list_buffer.append(info_attribute_list_buffer_r)

    # 3rd acquiring information from .balancesheet #
    balancesheet_list_buffer_r = []
    for j in range(len(balancesheet_list)):
        try:
            balancesheet_list_buffer_r.append(yfticker.quarterly_balance_sheet.loc[yfticker.quarterly_balance_sheet.index == balancesheet_list[j]].values[0][0])
        except:
            balancesheet_list_buffer_r.append(None)
    balancesheet_list_buffer.append(balancesheet_list_buffer_r)

    # 4th acquiring information from .quarterly_financials #
    financials_list_buffer_r = []
    for j in range(len(financials_list)):
        try:
            financials_list_buffer_r.append(np.array([yfticker.quarterly_financials.loc[yfticker.quarterly_financials.index == financials_list[j]].values[0][i] for i in range(ttm)]).sum())
        except:
            financials_list_buffer_r.append(None)
    try:
        financials_list_buffer_r.append(yfticker.quarterly_financials.columns[0])
    except:
        financials_list_buffer_r.append(None)
    financials_list_buffer.append(financials_list_buffer_r)

financials_list.append('ttm_latest')
df = df.join(pd.DataFrame(info_attribute_list_buffer, columns=info_attribute_list))
df = df.join(pd.DataFrame(balancesheet_list_buffer, columns=balancesheet_list))
df = df.join(pd.DataFrame(financials_list_buffer, columns=financials_list))

########### Calculate % diff from 52 week high and low
try: 
    df['percento52weekhigh'] = np.round(((df['currentPrice'] - df['fiftyTwoWeekHigh']) * 100 / df['currentPrice']),2)
except:
    None
try: 
    df['percento52weeklow'] = np.round(((df['currentPrice'] - df['fiftyTwoWeekLow']) * 100 / df['currentPrice']),2)
except:
    None
########### Calculate % diff from 52 week high and low

#### Drop NAN #############
df = df.dropna()
##### Drop where marketcap and EBIT < 0#############
df = df.loc[df['enterpriseValue'] >0]
df = df.loc[df['EBIT'] >0]
df = df.loc[df['Operating Income'] >0]
df = df.reset_index(drop=True)

df.to_csv('data_stock_s&p500.csv',index= False)