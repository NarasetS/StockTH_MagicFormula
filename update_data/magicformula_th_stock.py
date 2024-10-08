import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date
from lib import functions

## To acquire stock list in thailand ###
ex = pd.read_excel('update_data/stock_info_th.xlsx', sheet_name='listedCompanies_th_TH',skiprows=1)
df = pd.DataFrame(ex['หลักทรัพย์'].astype('str') + '.bk')
df['market'] = ex['ตลาด']
df = df.rename(columns={'หลักทรัพย์' : 'ticker'})
df = df.reset_index(drop=True)
# df = df[:30]

# 1st pulling date for this data #
df['date_pulling'] = date.today()

# 2nd acquiring information from .info #
info_attribute_list = [
    'industry',
    'sector',
    'marketCap',
    'enterpriseValue',
    'currentPrice',
    'totalCashPerShare',
    'profitMargins',
    'trailingPE',
]
# 3rd acquiring information from .quarterly_balance_sheet #
balancesheet_list = [
    'Total Non Current Assets',
    'Working Capital'
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
normalised_OI_index_list_buffer = []
average_MF_ROC_list_buffer = []
for i in range(len(df)):
    print(i, "/", len(df)-1 ,df['ticker'][i])
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

    ### get normalised_OI_index_list_buffer ####
    normalised_OI_index_list_r = []
    try:
        beta , numofyear = functions.yfinance_normalised_OI_index(df['ticker'][i],'Operating Income')
        normalised_OI_index_list_r.append(beta)
        normalised_OI_index_list_r.append(numofyear)
    except:
        normalised_OI_index_list_r.append(None)
        normalised_OI_index_list_r.append(None)       
    normalised_OI_index_list_buffer.append(normalised_OI_index_list_r)
    
    ### get average_MF_ROC_list_buffer ####
    average_MF_ROC_list_r = []
    try:
        avg_mf_roc = functions.yfinance_average_ROI(df['ticker'][i],'Operating Income')
        average_MF_ROC_list_r.append(avg_mf_roc)
    except:
        average_MF_ROC_list_r.append(None)
    average_MF_ROC_list_buffer.append(average_MF_ROC_list_r)

financials_list.append('ttm_latest')
df = df.join(pd.DataFrame(info_attribute_list_buffer, columns=info_attribute_list))
df = df.join(pd.DataFrame(balancesheet_list_buffer, columns=balancesheet_list))
df = df.join(pd.DataFrame(financials_list_buffer, columns=financials_list))
df = df.join(pd.DataFrame(normalised_OI_index_list_buffer, columns=['beta_earnings','numofyear']))
df = df.join(pd.DataFrame(average_MF_ROC_list_buffer, columns=['avg_MF_ROC']))


##### Drop NAN #############
df = df.dropna()
##### Drop where marketcap and EBIT < 0#############
df = df.loc[df['marketCap'] >0]
df = df.loc[df['EBIT'] >0]
df = df.loc[df['Operating Income'] >0]

sectortoexclude =['Financial Services','Utilities','Energy']
for i in sectortoexclude:
    try:
        df = df.loc[df['sector'] != i]
    except:
        None
df = df.reset_index(drop=True)

df.to_csv('data_stock_th.csv',index= False)