import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date


df = pd.read_csv('data_stock_us.csv')

################## sidebar ###########################################################
st.sidebar.markdown("Options")
market = st.sidebar.number_input(
    "Enterprise Value in Million USD", value=50, placeholder="Type a number..."
)

sectortoexclude = st.sidebar.multiselect(
    "Select sector to exclude", df['sector'].unique() , default=['Financial Services','Utilities']
)
industrytoexclude = st.sidebar.multiselect(
    "Select industry to exclude", df['industry'].unique()
)
earningrepresentative = st.sidebar.selectbox(
    "Do you prefer EBIT or Operating Income to represent earning?",
    ("Operating Income","EBIT"),
)
numstocks = st.slider('Number of top ranking stocks', 0, len(df), 30)
st.markdown("Price update : "+str(df['date_pulling'][0]))
################## sidebar ###########################################################

################## Calculation Part ###################################################
# df['MF_ROC'] = df[earningrepresentative]/(df['Total Assets'] - df['Current Liabilities'])
df['MF_EY'] = df[earningrepresentative]/df['enterpriseValue']
df['MF_ROC'] = df[earningrepresentative]/df['Invested Capital']


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

df['Ranking_MF_ROC'] = df['MF_ROC'].rank()
df['Ranking_MF_EY'] = df['MF_EY'].rank()
df['Ranking_MF'] = df['Ranking_MF_ROC'] + df['Ranking_MF_EY']
df = df.sort_values(by=['Ranking_MF'],ascending=False)
df = df.reset_index(drop=True)
df = df[:numstocks]

columns_todrop = [
    'Total Assets',
    'enterpriseValue',
    'Current Liabilities',
    'Operating Income',
    'EBIT',
    'fiftyTwoWeekLow',
    'fiftyTwoWeekHigh',
    'Invested Capital'
]
for i in range(len(columns_todrop)):
    try:
       df = df.drop(columns = columns_todrop[i])
    except:
        None
df_output = df.copy()
def func_sectortoshow(dataf,listsector):
    dataf = dataf.loc[dataf['sector'].isin(listsector)]
    dataf = dataf.reset_index(drop=True)
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

################## main ###########################################################

