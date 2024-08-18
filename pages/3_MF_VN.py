import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date


df = pd.read_csv('data_stock_vn.csv')

################## sidebar ###########################################################
st.sidebar.markdown("Options")
market = st.sidebar.number_input(
    "Market Cap in Million VND", value= (100*25060), placeholder="Type a number..."
)

sectortoexclude = st.sidebar.multiselect(
    "Select sector to exclude", df['sector'].unique() , default=['Utilities','Energy','Financial Services','Real Estate']
)
industrytoexclude = st.sidebar.multiselect(
    "Select industry to exclude", df['industry'].unique() , default= ['Engineering & Construction']
)
earningrepresentative = st.sidebar.selectbox(
    "Do you prefer EBIT or Operating Income to represent earning?",
    ("Operating Income","EBIT"),
)
numstocks = st.slider('Number of top ranking stocks', 0, 50, 30)
st.markdown("Price update : "+str(df['date_pulling'][0]))
################## sidebar ###########################################################

################## Calculation Part ###################################################
df['MF_ROC'] = df[earningrepresentative]/(df['Total Assets'] - df['Current Liabilities'])
df['MF_EY'] = df[earningrepresentative]/df['enterpriseValue']


df = df.loc[df['enterpriseValue'] >= (market  *(1000000))]
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

df['Ranking_MF_ROC'] = df['MF_ROC'].rank()
df['Ranking_MF_EY'] = df['MF_EY'].rank()
df['Ranking_MF'] = df['Ranking_MF_ROC'] + df['Ranking_MF_EY']
df = df.sort_values(by=['Ranking_MF'],ascending=False)
df = df.reset_index(drop=True)
df = df[:numstocks]

df_bytotalcashpershare = df.sort_values(by=['totalCashPerShare'],ascending=False).copy()
df_bytotalcashpershare = df_bytotalcashpershare.reset_index(drop=True)
################## Calculation Part ###################################################

################## main ###########################################################
st.header("Ranking based on the Magic Formula")
st.write(df)

st.markdown("You can then modify the result by sorting the result regarding your own interested attributes")
st.markdown("It's a must to verify this ranking by reviewing indivual stock and choosing to invest ""by yourself"" ")

################## main ###########################################################

