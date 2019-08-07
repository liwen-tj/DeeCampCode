import lightgbm as lgb
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from collections import Counter
import os

d = os.path.dirname(__file__)
parent_path = os.path.dirname(d)
parent_path = os.path.dirname(parent_path)
savepath = os.path.join(parent_path, 'data/ff_all_2328.csv')
macbook = pd.read_csv(savepath, index_col=0)


def yuce(cssj):
    # cssj=pd.read_csv(pathdataa,index_col=0).drop(columns=['手术时长(分钟)'])
    xcs = cssj._stat_axis.values
    data_X = macbook.drop(columns=['手术时长(分钟)']).loc[xcs].values
    gbm = lgb.Booster(model_file=os.path.join(d, 'model.txt'))
    y_pred = gbm.predict(data_X, num_iteration=gbm.best_iteration)
    cssj['手术时长(分钟)'] = ''
    cssj['手术时长(分钟)'] = y_pred
    return cssj
