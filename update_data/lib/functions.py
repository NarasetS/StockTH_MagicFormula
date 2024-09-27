import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date


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
        return None