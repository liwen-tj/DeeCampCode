from catboost import CatBoostClassifier
import catboost
import pandas as pd
pd.options.display.max_columns = None
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.preprocessing import LabelEncoder
#data=pd.read_csv('../../data/190723_HUATUO_OR_data.csv',index_col=0)

def xunlian(data):#此处data为最早的40+mb的那个原始csv
    data=data.drop(index=[100946646, 100428578, 100410820,100654350,100271127,100380152])
    mask1 = ~(data['手术时长(分钟)'] == 0)
    mask2 = ~(data['手术时长(分钟)'] > 480)
    data = data[mask1]
    data = data[mask2]
    data.loc[data['手术时长(分钟)'] < 10,'手术时长(分钟)']=10
    data=data.fillna(999999999)
    data['他']=''
    data['他'][data['血清丙氨酸氨基转移酶定量测定（谷丙）']!=999999999]=data['血清天门冬氨酸氨基转移酶定量测定（谷草）'][data['血清天门冬氨酸氨基转移酶定量测定（谷草）']!=999999999]/data['血清丙氨酸氨基转移酶定量测定（谷丙）'][data['血清丙氨酸氨基转移酶定量测定（谷丙）']!=999999999]
    data=data.fillna(999999999)
    macbook=data.drop(columns=['手术时长(分钟)','术前小结','术后留院时间（天）'])
    target=data['手术时长(分钟)']
    X_train, X_val, y_train, y_val = train_test_split(macbook,target,test_size=0.2 , random_state=12)


    categorical_features_indices = np.where(X_train.dtypes != np.float)[0][:-1]
    #param:task_type = "GPU",
    modelx = catboost.CatBoostRegressor(iterations=100, depth=5,cat_features=categorical_features_indices,learning_rate=1, loss_function='MAE',
                                logging_level='Verbose')#如果gpu在本地不能用，删掉task_type参数并调整iterations到100，意思意思
    modelx.fit(X_train,y_train,eval_set=(X_val, y_val),plot=True)
    modelx.save_model('modelxs.cb')#保存模型，但不建议后续调用，因为这个模型轮数不够。
    strr='已建立模型'
    return strr