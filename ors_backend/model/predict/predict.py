import pandas as pd
import numpy as np
import datetime

def predict(filepath):
    data = pd.read_csv(filepath, index_col=0)
    data['time'] = (np.random.randn(data.shape[0]) * 10 + 50)//1
    savepath = '../../data/predict/predicted.csv'
    data.to_csv(savepath)
    return savepath
