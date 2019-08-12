from catboost import CatBoostClassifier, CatBoostRegressor, Pool
import os
import shap
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier
import catboost
import pandas as pd
pd.options.display.max_columns = None
d = os.path.dirname(__file__)
parent_path = os.path.dirname(d)
parent_path = os.path.dirname(parent_path)
savepath = os.path.join(parent_path, 'data/190723_HUATUO_OR_data.csv')
macbook = pd.read_csv(savepath, index_col=0)
model_path = os.path.join(d, 'modelx')

def jieshi(yssj):

    # yssj=pd.read_csv('../../data/yssj_2.csv',index_col=0)
    data = pd.read_csv(savepath, index_col=0)
    yssj = yssj.fillna(999999999)
    yssj = yssj.drop(columns=['术前小结', '医生'])
    yssj['AST:ALT'] = ''
    yssj['AST:ALT'][yssj['血清丙氨酸氨基转移酶定量测定（谷丙）'] != 999999999] = yssj['血清天门冬氨酸氨基转移酶定量测定（谷草）'][yssj['血清天门冬氨酸氨基转移酶定量测定（谷草）']
                                                                                            != 999999999]/yssj['血清丙氨酸氨基转移酶定量测定（谷丙）'][yssj['血清丙氨酸氨基转移酶定量测定（谷丙）'] != 999999999]
    yssj = yssj.fillna(999999999)
    # yssj.drop(columns=['Unnamed: 33', 'Unnamed: 34'])
    inf = yssj.columns.tolist()
    ind = yssj.index.tolist()
    # print(yssj)
    print(inf)
    X_test = yssj.values
    y_test = data.loc[ind]['手术时长(分钟)'].values
    hap = CatBoostRegressor()
    modelx = hap.load_model(model_path, format='catboost')
    shap_values = modelx.get_feature_importance(Pool(X_test, label=y_test, cat_features=[0, 1, 2, 3, 4, 5, 8, 9, 10, 12, 13, 14]),
                                                type="ShapValues")

    # print(len(inf))
    lp = []
    for j in range(len(yssj)):
        li = []
        for i in range(0, 30):
            lpo = []
            lpo.append(inf[i]+'='+str(data[inf[i]].loc[ind[j]]))
            lpo.append(shap_values[j][i])
            li.append(lpo)
        lp.append(li)
    return lp
