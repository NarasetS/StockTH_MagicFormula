import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date
import datetime
import calendar

def etl(df_list_stock,stockmarket):
    
    df_list_stock = df_list_stock.loc[df_list_stock['market'] == stockmarket]
    df_list_stock = df_list_stock.reset_index(drop=True)

    # 1st pulling date for this data #
    df_list_stock['date_pulling'] = date.today()
    # 2nd acquiring information from .info #
    info_attribute_list = [
        'industry',
        'sector',
        'enterpriseValue',
        'totalCashPerShare',
        'profitMargins',
        # 'trailingPE',
        # 'beta',
        # 'sharesOutstanding',
        'priceToBook',
        'debtToEquity',
        'returnOnEquity',
        'currentRatio',
        # 'trailingPegRatio',
        # 'currentPrice',
        'trailingEps'
    ]
    # 3rd acquiring information from .quarterly_balance_sheet #
    balancesheet_list = [
        'Total Non Current Assets',
        'Working Capital'
    ]
    # 4th acquiring information from .quarterly_financials #
    ttm = 4
    financials_list = [
        # 'EBIT',
        'Operating Income'
    ]

    # 5th acquiring information from .quarterly_cash_flow #
    ttm_c = 4
    cashflow_list = [
        'Free Cash Flow'
    ]

    info_attribute_list_buffer = []
    balancesheet_list_buffer = []
    financials_list_buffer = []
    cashflow_list_buffer = []
    normalised_OI_index_list_buffer = []
    average_MF_ROC_list_buffer = []
    pricerelated_list_bugger = []

    # 1st pulling date for this data #
    df_list_stock['date_pulling'] = date.today()

    for i in range(len(df_list_stock)) :
        print(i, "/", len(df_list_stock)-1 ,df_list_stock['ticker'][i])
        
        yfticker = yf.Ticker(df_list_stock['ticker'][i])
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

        # 5th acquiring information from .quarterly_cashflow #
        cashflow_list_buffer_r = []
        for j in range(len(cashflow_list)):
            try:
                cashflow_list_buffer_r.append(np.array([yfticker.quarterly_cashflow.loc[yfticker.quarterly_cashflow.index == cashflow_list[j]].values[0][i] for i in range(ttm_c)]).sum())
            except:
                cashflow_list_buffer_r.append(None)

        cashflow_list_buffer.append(cashflow_list_buffer_r)
        
        ### get average_MF_ROC_list_buffer ####
        average_MF_ROC_list_r = []
        try:
            avg_mf_roc = yfinance_average_ROI(df_list_stock['ticker'][i],'Operating Income')
            average_MF_ROC_list_r.append(avg_mf_roc)
        except:
            average_MF_ROC_list_r.append(None)

        average_MF_ROC_list_buffer.append(average_MF_ROC_list_r)
        

        #### Get indicators based on price #####
        if (df_list_stock['market'][i] == 'SET'):
            market = "^SET.bk"
        elif (df_list_stock['market'][i] == 'mai') :
            market = "^SET.bk"
        elif (df_list_stock['market'][i] == 'US') :
            market = "^GSPC"      
        else : market = "^GSPC" 
        pricerelated_list_bugger_r = []
        try:
            date_end = date.today()
            month_backward = -6
            date_start = add_months(date_end, month_backward)
            beta, price_current, price_past = finding_beta(market,df_list_stock['ticker'][i],date_start,date_end)

            pricerelated_list_bugger_r.append(beta)
            pricerelated_list_bugger_r.append(price_current)
            pricerelated_list_bugger_r.append(price_past)
        except:
            pricerelated_list_bugger_r.append(None)
            pricerelated_list_bugger_r.append(None)
            pricerelated_list_bugger_r.append(None)
        pricerelated_list_bugger.append(pricerelated_list_bugger_r)


    financials_list.append('ttm_latest')
    df_list_stock = df_list_stock.join(pd.DataFrame(info_attribute_list_buffer, columns=info_attribute_list))
    df_list_stock = df_list_stock.join(pd.DataFrame(balancesheet_list_buffer, columns=balancesheet_list))
    df_list_stock = df_list_stock.join(pd.DataFrame(financials_list_buffer, columns=financials_list))
    df_list_stock = df_list_stock.join(pd.DataFrame(cashflow_list_buffer, columns=cashflow_list))
    df_list_stock = df_list_stock.join(pd.DataFrame(average_MF_ROC_list_buffer, columns=['avg_MF_ROC']))
    df_list_stock = df_list_stock.join(pd.DataFrame(pricerelated_list_bugger, columns=['beta','price_current','price_past']))

    #### Drop NAN #############
    df_list_stock = df_list_stock.dropna()
    ## we could notice that bakning/financial stocks would be filtered out since there accounting method is not the same as others 

    df_list_stock = df_list_stock.reset_index(drop=True)


    #### Now, we begin task2 ####
    df_list_stock = df_list_stock.loc[df_list_stock['enterpriseValue'] != 0]
    df_list_stock['MF_EarningYield'] = df_list_stock['Operating Income'] / df_list_stock['enterpriseValue']

    df_list_stock['current_MF_ROC'] = df_list_stock['Operating Income'] / (df_list_stock['Working Capital'] + df_list_stock['Total Non Current Assets'])

    df_list_stock['FCF_Yield'] = df_list_stock['Free Cash Flow'] / df_list_stock['enterpriseValue']

    df_list_stock['PE_offset_Cash'] = (df_list_stock['price_current'] - df_list_stock['totalCashPerShare']) / df_list_stock['trailingEps']

    df_list_stock['PE'] = (df_list_stock['price_current']) / df_list_stock['trailingEps']

    df_list_stock['PriceIndex_6m'] = df_list_stock['price_current']/df_list_stock['price_past']
    df_list_stock['percenFCFpersharetoprice'] = (df_list_stock['totalCashPerShare'])/df_list_stock['price_current']



    #### Unrelated columns #### 
    # df_list_stock = df_list_stock.drop(columns=['enterpriseValue','Total Non Current Assets','Working Capital','Operating Income','Free Cash Flow','totalCashPerShare','ttm_latest','price_current','price_past'])

    df_list_stock.to_csv('data_stock_' + stockmarket +'.csv',index= False)
    return print("ETL for",stockmarket,"is complete")

#### Calculate ROIC #####
def yfinance_average_ROI(ticker,property) :
    try:
        netfixedcapital = yf.Ticker(ticker).balance_sheet.dropna(axis = 1, how = 'all')
        netfixedcapital = netfixedcapital.T
        netfixedcapital = netfixedcapital['Working Capital'] + netfixedcapital['Total Non Current Assets']

        earninngs = yf.Ticker(ticker).financials.dropna(axis = 1, how = 'all')
        earninngs = earninngs.T
        earninngs = earninngs[property]


        data = pd.DataFrame()
        data['Invested Capital'] = netfixedcapital
        data[property] = earninngs
        data = data.dropna()
        data['avg_MF_ROC'] = data[property]/data['Invested Capital']
        avg_MF_ROC = data['avg_MF_ROC'].mean()
        avg_MF_ROC = np.round(avg_MF_ROC,4)

        return avg_MF_ROC
    except:
        return None
    
    
def yfinance_normalised_OI_index(ticker,property):
    ### Get data from .financials and .quaterly_financials ####
    try:
        data_financials = yf.Ticker(ticker).financials.loc[yf.Ticker(ticker).financials.index == property].dropna(axis = 1, how = 'all')
        data_financials = data_financials.T
        # print(data_financials)
        
        data_quaterly_financials = yf.Ticker(ticker).quarterly_financials.loc[yf.Ticker(ticker).quarterly_financials.index == property].dropna(axis = 1, how = 'all')
        list_col = data_quaterly_financials.columns
        data_quaterly_financials = data_quaterly_financials.reset_index()
        data_quaterly_financials['ttm'] = 0
        if len(list_col) >=4 :
            ttm_period = 4
        else : ttm_period = len(list_col)
        for i in range(ttm_period): 
            data_quaterly_financials['ttm'] = data_quaterly_financials['ttm'] + data_quaterly_financials[list_col[i]]
        data_quaterly_financials = data_quaterly_financials.set_index('index')
        data_quaterly_financials = data_quaterly_financials.T
        # print(data_quaterly_financials.loc[data_quaterly_financials.index == 'ttm'])
        # print(data_quaterly_financials)
              
        data = pd.concat([data_quaterly_financials.loc[data_quaterly_financials.index == 'ttm'],data_financials])

        minval = data[property].astype('float64').min()
        maxval = data[property].astype('float64').max()
        numofyear = len(data[property])
        data[property] = ( data[property] - minval ) / (maxval - minval)
        
        
        #### Calculate beta ###
        data.reset_index(inplace=True)
        data = data.rename(columns = {'index':'time'})
        data.reset_index(inplace=True)
        data = data.sort_values('index',ascending=False)
        data = data.drop(columns = 'index')
        data.reset_index(inplace=True,drop = True)
        beta, alpha = np.polyfit(np.array(data[property]).astype('float64'), np.array(data.index).astype('float64'),1)
        # data[property].plot()
        beta = np.round(beta,4)
        return beta , numofyear
    except: 
        return
    
def normalize(df):
  x = df.copy()
  for i in x.columns[0:]:
    x[i] = x[i]/x[i][0]
  return x

def daily_return(df):
    df_daily_return = df.copy()
    for i in df.columns[0:]:
        for j in range(1, len(df)):
            # df_daily_return.iloc[j][i] = ((df.iloc[j][i] - df.iloc[j-1][i])/df.iloc[j-1][i]) * 100
            df_daily_return.loc[j,i] = ((df.loc[j,i] - df.loc[j-1,i])/df.loc[j-1,i]) * 100
        # df_daily_return.iloc[0][i] = 0
        df_daily_return.loc[0,i] = 0
    return df_daily_return

def finding_beta(market,ticker,date_start,date_end):
    try:
        m = yf.Ticker(market).history(start=date_start, end=date_end, interval="1d")
        s = yf.Ticker(ticker).history(start=date_start, end=date_end, interval="1d")
        price_current = s.iloc[-1]['Close']
        price_past = s.iloc[0]['Close']
        # print(price_past)
        # print(price_current)
        # print(s)

        m.reset_index(inplace=True)
        s.reset_index(inplace=True)
        m['1d'] = m['Date'].dt.date
        s['1d'] = s['Date'].dt.date
        m = m.drop(columns=['Date'])
        s = s.drop(columns=['Date'])
        m = m.set_index('1d')
        s = s.set_index('1d')

        data = pd.DataFrame()
        data['market'] = m['Close']
        data['ticker'] = s['Close']
        
        data = data.loc[~(data['market'].isna() | data['ticker'].isna())]
        data.reset_index(inplace=True,drop=True)

        data = normalize(data)
        # data.plot()
        data_daily_return = daily_return(data)
        # data_daily_return.plot.scatter(x='market',
        #               y='ticker',
        #               c='DarkBlue',)
        beta, alpha = np.polyfit(data_daily_return['market'], data_daily_return['ticker'], 1)
        return beta, price_current, price_past
    except:
        return None
    
def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)
