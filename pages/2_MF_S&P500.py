import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date
import sys
import os
# print(os.getcwd()+"\\update_data\\self_lib")
sys.path.append(os.getcwd()+"\\update_data\\self_lib")
sys.path.append(os.getcwd()+"/update_data/self_lib")
import rankingclustering

df = pd.read_csv('data_stock_s&p500.csv')
################## sidebar ###########################################################
st.sidebar.markdown("Options")
market = st.sidebar.number_input(
    "Enterprise Value in Million USD", value=0, placeholder="Type a number..."
)

sectortoexclude = st.sidebar.multiselect(
    "Select sector to exclude", df['sector'].unique()
)
industrytoexclude = st.sidebar.multiselect(
    "Select industry to exclude", df['industry'].unique() 
)
numstocks = st.slider('Number of top ranking stocks', 0, len(df), 30)
st.markdown("Price update >> "+str(df['date_pulling'][0]))
################## sidebar ###########################################################

df = df.loc[df['enterpriseValue'] >= (market*(1000000))]
for i in sectortoexclude:
    try:
        df = df.loc[df['sector'] != i]
    except:
        None
for i in industrytoexclude:
    try:
        df = df.loc[df['industry'] != i]
    except:
        None
df = df.reset_index(drop=True)

df = rankingclustering.rankingclustering(df,'s&p500')
df = df[:numstocks]

columns_todrop = [
    'date_pulling',
    'totalCashPerShare',
    'currentRatio',
    'Total Non Current Assets',
    'Working Capital',
    'Operating Income',
    'ttm_latest',
    'Free Cash Flow,'
]
for i in range(len(columns_todrop)):
    try:
       df = df.drop(columns = columns_todrop[i])
    except:
        None

df_output = df.copy()
def func_sectortoshow(dataf,listsector):
    dataf = dataf.loc[dataf['sector'].isin(listsector)]
    return dataf

################## Calculation Part ###################################################

################## main ###########################################################
st.header("Ranking based on the Magic Formula")
sectortoshow = st.multiselect(
    "Select sector to show", df_output['sector'].unique() , default = df_output['sector'].unique()
)
df_output = func_sectortoshow(df_output,sectortoshow)
st.write(df_output)

st.markdown("You can then modify the result by sorting the result regarding your own interested attributes")
st.markdown("It's a must to verify this ranking by reviewing individual stock and choosing to invest ""by yourself"" ")

################# main ###########################################################

