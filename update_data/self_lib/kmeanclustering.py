import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def __init__() :
    pass

def kmeanclustering(stockmarket):
    filename = 'data_stock_'+stockmarket+'.csv'
    data = pd.read_csv(filename)
    data = data.loc[(data['MF_EarningYield'] > 0) & (data['current_MF_ROC'] > 0)]
    data['MF_Rank_EY'] = (data['MF_EarningYield'].rank(method='max'))
    data['MF_Rank_ROC'] = ((data['avg_MF_ROC'] + data['current_MF_ROC'])/2).rank(method='max')
    data['MF_Rank'] = data['MF_Rank_EY'] + data['MF_Rank_ROC']

    data = data.set_index('ticker')

    data_features = data[
        [
        'MF_Rank',
        # 'PriceIndex_6m',
        'FCF_Yield',
        # 'percenFCFpersharetoprice'
        ]
    ]
    # Feature scaling
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data_features)


    # Convert back to a DataFrame
    scaled_df = pd.DataFrame(scaled_data, columns=data_features.columns)

    # K-means clustering
    n_clusters = 4
    kmeans = KMeans(n_clusters=n_clusters,random_state = 1)
    kmeans_labels = kmeans.fit_predict(scaled_data)
    data['clusterno_kmeans'] = kmeans_labels
    # data.to_csv('clustered_'+filename,index= True)
    data.to_csv(filename,index= True)
    return None

