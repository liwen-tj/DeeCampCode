import lightgbm as lgb
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.datasets import  make_classification
from collections import Counter
import lime
import lime.lime_tabular
import os

d = os.path.dirname(__file__)
parent_path = os.path.dirname(d) 
parent_path = os.path.dirname(parent_path) 
savepath = os.path.join(parent_path, 'data/ff_all_2328.csv')
macbook=pd.read_csv(savepath,index_col=0)
#pathdataa="../../data/190723_HUATUO_OR_data.csv"
#ef yuce(pathdataa):
#cssj=pd.read_csv(pathdataa,index_col=0).drop(columns=['手术时长(分钟)'])[1:30]
# cssj
def jieshi(cssj):
    xcs=cssj._stat_axis.values
    #print(xcs)
    data_X=macbook.drop(columns=['手术时长(分钟)']).values
    data_label=macbook['手术时长(分钟)'].values
    #hyj=macbook.drop(columns=['手术时长(分钟)'])
    #sss=hyj.hkc[xcs]

    #ata_X=macbook.drop(columns=['手术时长(分钟)']).loc[xcs].values
    X_train,X_test,y_train,y_test =train_test_split(data_X,data_label,test_size=0.2, random_state=0)
    # hkllc=macbook['手术时长(分钟)'].loc[xcs].values
    #data_label=cssj['手术时长(分钟)'].values
    #data_X
    li=[]
    hsc=macbook.drop(columns=['手术时长(分钟)'])._stat_axis.values
    for i in range(len(data_X)):
        if (hsc[i] in xcs):
            li.append(i)

    lgb_train = lgb.Dataset(X_train, y_train) # 将数据保存到LightGBM二进制文件将使加载更快
    lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)  # 创建验证数据

    params = {
        'max_depth':6,
        'task': 'train',
        'boosting_type': 'dart',  # 设置提升类型
        'objective': 'regression', # 目标函数
        'metric': {'l2'},  # 评估函数
        'num_leaves':127,   # 叶子节点数
        'learning_rate': 0.03,  # 学习速率
        'feature_fraction': 0.9, # 建树的特征选择比例
        'bagging_fraction': 0.8, # 建树的样本采样比例
        'bagging_freq': 5,  # k 意味着每 k 次迭代执行bagging
        'verbose': 1 # <0 显示致命的, =0 显示错误 (警告), >0 显示信息

    }

    #print('Start training...'),num_boost_round=200,valid_sets=lgb_eval,early_stopping_rounds=50
    # 训练 cv and train
    gbm = lgb.train(params,lgb_train,num_boost_round=2400,valid_sets=lgb_eval) # 训练数据需要参数列表和数据集
    # print('Save model...') 
    # gbm.save_model('model.txt')   # 训练后保存模型到文件

    # 预测数据集
    #y_pred = gbm.predict(X_test, num_iteration=gbm.best_iteration)


# cssj['手术时长(分钟)']=''
# cssj['手术时长(分钟)']=y_pred


    categorical_features = np.argwhere(np.array([len(set(data_X[:,x])) for x in range(data_X.shape[1])]) <10).flatten()
    data_feat=macbook.columns.values
    explainer = lime.lime_tabular.LimeTabularExplainer(data_X, feature_names=data_feat, categorical_features=categorical_features, verbose=True, mode='regression')

    lo=[]
    for i in range(len(li)):
        exp = explainer.explain_instance( data_X[li[i]],gbm.predict, num_features=5 )
        print(exp.as_list())
        lo.append(lo)
    return lo