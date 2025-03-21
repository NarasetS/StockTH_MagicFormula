import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import sys
import os
# print(os.getcwd()+"\\update_data\\self_lib")
sys.path.append(os.getcwd()+"\\update_data\\self_lib")
sys.path.append(os.getcwd()+"/update_data/self_lib")
import rankingclustering

df = pd.read_csv('data_stock_us.csv')
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

columns_todrop = [
    'date_pulling',
    'totalCashPerShare',
    'currentRatio',
    'Total Non Current Assets',
    'Working Capital',
    'Operating Income',
    'ttm_latest',
    'Free Cash Flow'
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
def func_clustertoshow(dataf,listclusterno):
    dataf = dataf.loc[dataf['clusterno_kmeans'].isin(listclusterno)]
    return dataf

################## Calculation Part ###################################################

################## main ###########################################################
st.header("Ranking based on the Magic Formula")
sectortoshow = st.multiselect(
    "Select sector to show", df_output['sector'].unique() , default = df_output['sector'].unique()
)

clustertoshow = st.multiselect(
    "Select cluster to show", df['clusterno_kmeans'].unique() , default =  df['clusterno_kmeans'].unique() 
)

df_output = func_sectortoshow(df_output,sectortoshow)
df_output = func_clustertoshow(df_output,clustertoshow)

numstocks = st.slider('Number of top ranking stocks', 0, len(df_output), len(df_output))
df_output = df_output[:numstocks]

sortby = st.selectbox(
    "Sort by ?",options = df_output.columns, index = len(df_output.columns) - 2  
)
df_output = df_output.sort_values(by = sortby,ascending = False)


st.header("Scatter Plot Clustered using Kmeans with features MF_Ranking, FCF_Yield and percentage_FCFtosharedprice")

scatterx = st.selectbox(
    "X Axis",options = df_output.columns, index = len(df_output.columns) - 1  
)
scattery = st.selectbox(
    "Y Axis",options = df_output.columns, index = len(df_output.columns) - 6  
)
st.scatter_chart(
    df_output,
    x=scatterx,
    y=scattery,
    color="clusterno_kmeans",
)

st.write(df_output)
st.markdown("You can then modify the result by sorting the result regarding your own interested attributes")
st.markdown("It's a must to verify this ranking by reviewing individual stock and choosing to invest ""by yourself"" ")

################# main ###########################################################
