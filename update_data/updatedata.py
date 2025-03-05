# import magicformula_th_stock
# import magicformula_sandp500_stock
# import magicformula_us_stock
###############################

import pandas as pd
from lib import etl
from lib import kmeanclustering

## Firstly, let me build up a list of tickers ####
list_stock_th = pd.read_excel('update_data/stock_info_th.xlsx', sheet_name='listedCompanies_th_TH',skiprows=1)
df_list_stock_th = pd.DataFrame(list_stock_th['หลักทรัพย์'].astype('str') + '.bk')
df_list_stock_th['market'] = list_stock_th['ตลาด']
df_list_stock_th = df_list_stock_th.rename(columns={'หลักทรัพย์' : 'ticker'})
df_list_stock_th = df_list_stock_th.reset_index(drop=True)

list_stock_sp500 = pd.read_csv('update_data/stock_info_s&p500.csv')
df_list_stock_sp500 = pd.DataFrame(list_stock_sp500['Symbol'].astype('str'))
df_list_stock_sp500 = df_list_stock_sp500.rename(columns={'Symbol' : 'ticker'})
df_list_stock_sp500 = df_list_stock_sp500.drop_duplicates()
df_list_stock_sp500['market'] = 's&p500'

list_stock_us1 = pd.read_csv('update_data/stock_info_us_1.csv')
list_stock_us2 = pd.read_csv('update_data/stock_info_us_2.csv')

df_list_stock_us1 = pd.DataFrame(list_stock_us1['Symbol'].astype('str'))
df_list_stock_us = pd.concat([df_list_stock_us1,list_stock_us2['Symbol'].astype('str')])
df_list_stock_us = df_list_stock_us.rename(columns={'Symbol' : 'ticker'})
df_list_stock_us = df_list_stock_us.drop_duplicates()
df_list_stock_us['market'] = 'us'

df_list_stock_us_all = pd.concat([df_list_stock_sp500,df_list_stock_us])
df_list_stock_us_all = df_list_stock_us_all.drop_duplicates('ticker')
df_list_stock_us_all = df_list_stock_us_all.reset_index(drop=True)

df_list_stock = pd.concat([df_list_stock_th,df_list_stock_us_all])
df_list_stock = df_list_stock.reset_index(drop=True)

print(df_list_stock)

etl.etl(df_list_stock,'s&p500')
# kmeanclustering.kmeanclustering('s&p500')
etl.etl(df_list_stock,'SET')
kmeanclustering.kmeanclustering('SET')
etl.etl(df_list_stock,'us')
kmeanclustering.kmeanclustering('us')


