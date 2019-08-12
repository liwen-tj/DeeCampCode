from catboost import CatBoostClassifier
import catboost
import pandas as pd
pd.options.display.max_columns = None
import os
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.preprocessing import LabelEncoder

d = os.path.dirname(__file__)
modelx_path = os.path.join(d, 'modelx')
lgb_path = os.path.join(d, 'lgbmodel.txt')
parent_path = os.path.dirname(d)
parent_path = os.path.dirname(parent_path)
savepath = os.path.join(parent_path, 'data/190723_HUATUO_OR_data.csv')
ff_path = os.path.join(parent_path, 'data/ff_all_2328_newest.csv')

def yujiazai():
    print("开始预加载")
    data=pd.read_csv(savepath,index_col=0)
    # patch=pd.read_csv('./ff_all_2328_newest.csv',index_col=0)

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

    # patchh=patch[['并发症个数', '手术名长度']]
    # data=pd.concat([data,patchh],axis=1)

    macbook=data.drop(columns=['手术时长(分钟)','术前小结','术后留院时间（天）'])
    target=data['手术时长(分钟)']
    X_train, X_val, y_train, y_val = train_test_split(macbook,target,test_size=0.2 , random_state=12)
    # data[1555:1559]


    # categorical_features_indices = np.where(X_train.dtypes != np.float)[0][:-2]

    hap=catboost.CatBoostRegressor()
    modelx=hap.load_model(modelx_path,format='catboost')


    y_pred1=modelx.predict(macbook)

    import lightgbm as lgb
    from sklearn.metrics import mean_squared_error
    from sklearn.datasets import load_iris
    from sklearn.metrics import mean_absolute_error
    from sklearn.datasets import  make_classification

    macbook=pd.read_csv(ff_path, index_col=0)   
    datax=macbook.drop(columns=['手术时长(分钟)']).values

    IDX_list=np.array(macbook.index.values)
    np.random.seed(1234)
    np.random.shuffle(IDX_list)
    IDX_list_train=IDX_list[:int(len(IDX_list)*0.8)]
    train=macbook.loc[IDX_list_train]
    IDX_list_test=IDX_list[int(len(IDX_list)*0.8):]
    test=macbook.loc[IDX_list_test]
    y_train=train['手术时长(分钟)'].values
    y_test=test['手术时长(分钟)'].values


    X_train=train.drop(columns=['手术时长(分钟)'])
    X_test=test.drop(columns=['手术时长(分钟)'])

    gbm = lgb.Booster(model_file=lgb_path)



    from sklearn.linear_model import LinearRegression, BayesianRidge
    model_Bayes = BayesianRidge()
    model_Bayes.fit(X_train,y_train)

    y_pred3 = model_Bayes.predict(datax)
    y_pred2= gbm.predict(datax, num_iteration=gbm.best_iteration) #如果在训练期间启用了早期停止，可以通过best_iteration方式从最佳迭代中获得预测

    data['猫步']=y_pred1
    data['光步']=y_pred2
    data['贝爷']=y_pred3
    # data['knn']=y_pred5
    global pdd
    pdd=data[['猫步','光步','贝爷']]
    pyy=data[['猫步','光步','贝爷','手术时长(分钟)']]
    pxx=data['手术时长(分钟)']
    X_trainf=pdd.loc[IDX_list_train]
    X_testf=pdd.loc[IDX_list_test]
    y_trainf=pxx.loc[IDX_list_train]
    y_testf=pxx.loc[IDX_list_test]


    X_traink, X_testk, y_traink, y_testk = train_test_split(X_testf, y_testf, test_size=0.1,random_state=0)
    from sklearn.linear_model import LinearRegression
    modely = LinearRegression()
    modely.fit(X_traink, y_traink)
    print('模型预加载完成')
    return modely

def yuce(cssj, modely):
    # cssj=pd.read_csv(pathdataa,index_col=0)
    xcs=cssj._stat_axis.values
    data_X=pdd.loc[xcs].values
    print(data_X)
    y_pred = modely.predict(data_X)
    cssj['手术时长(分钟)']=''
    cssj['手术时长(分钟)']=y_pred
    return cssj
