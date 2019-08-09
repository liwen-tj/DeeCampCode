"""
作者：李文卓
日期：2019/7/29
用途：主程序
版本：2.0
"""
import json
from calculation import calculte
import csv
from MyProblem import MyProblem
import geatpy as ea
from algorithm import Algorithm
import numpy as np
import pandas as pd
import random

def _get_json_(filepath):
    with open(filepath, mode='r', encoding='utf-8') as f:
        number = json.load(f)
    return number


def main_1(filepath_1):
    filepath_1 = 'input_1.json'
    input_1 = _get_json_(filepath_1)
    filepath_2 = input_1['filePath']   #读入csv路径
    data = pd.read_csv(filepath_2)
    # 必须添加header=None，否则默认把第一行数据处理成列名导致缺失
    data_1 = pd.DataFrame(data)
    
    num = len(data_1)  # 病人总的数目
    morning_time = int(input_1['startTime'].split(':')[0]) * 60 + int(input_1['startTime'].split(':')[1])
    afternoon_time = int(input_1['endTime'].split(':')[0]) * 60 + int(input_1['endTime'].split(':')[1])
    n_x = int(input_1['orNum'])   #手术室数目
    n_y = int(input_1['recoverNum'])  #复苏室数目
    t_s = int(input_1['minRecoverTime'])   #最小复苏时间

    calculte_r = calculte(data, n_x, n_y, t_s, morning_time, afternoon_time)  # 实例化
    list_doctID, list_patientID, list_operation, list_sleepy, list_clean, list_start, list_index_or, list_of_all= calculte_r._process_data_(num)
 #   print(list_doctID, list_sleepy, list_operation, list_clean, list_patientID, list_start, list_index_or)

    Encoding = 'RI'                                          # 编码方式为实数
    conordis = 1                                            # 染色体解码后得到的变量是离散的
    NIND = 50                                              # 种群规模

    problem = MyProblem(num, n_x, n_y, NIND, list_of_all, morning_time, afternoon_time)
    # n_o为手术室数量，n_r为复苏室数量, chrom为染色体[1,3,2]表示第一台
    # 手术在1号手术室在1号手术室内做，o_time[30,100,60]表示第一台手术时长30分钟，
    # c_time表示清洁时长，r_time表示复苏时长（0或自定义最小复苏时长默认为60min）
    # 生成问题对象
    Field = ea.crtfld(Encoding, problem.varTypes, problem.ranges, problem.borders)  # 创建区域描述器
    population = ea.Population(Encoding, Field, NIND)             # 创建种群对象
    x_chuandai = 20
    id_trace = (np.zeros((x_chuandai, num)) * np.nan)     # 定义变量记录器，记录决策变量值，初始值为nan
    Algorithm_1 = Algorithm(problem, population, id_trace)            # 实例化一个算法模板对象

    Algorithm_1.MAXGEN = x_chuandai                                 # 最大遗传代数
    [population, obj_trace, var_trace, id_trace] = Algorithm_1.run()  # 执行算法模板   #如何返回最优解


    best_gen = np.argmin(obj_trace[:, 1])                   # 记录最优种群是在哪一代
    best_ObjV = obj_trace[best_gen, 1]                      # 目标函数值最优

    #mean_ObjV = obj_trace[best_gen, 0]                      # 均值

    best_paixu = var_trace[best_gen, :]                      # 最优解
    ARRAY = id_trace[best_gen, :]
    print('最优的目标函数值为：%s' % (best_ObjV))
    print('有效进化代数：%s' % (obj_trace.shape[0]))
    print('最优的一代是第 %s 代' % (best_gen + 1))
    print('时间已过 %s 秒' % (Algorithm_1.passTime))

   # id_trace = (np.zeros((self.MAXGEN, NVAR)) * np.nan)  # 定义变量记录器，记录决策变量值，初始值为nan

    #返回一个ARRAY将list调整并传给best_result函数
    sel_data = list_of_all[:, list(ARRAY.astype(np.int))]
    #list_doctID, list_patientID, list_operation, list_sleepy, list_clean, list_start, list_index_or
    list_doctID_2 = sel_data[0]
    list_patientID_2 = sel_data[1]
    list_operation_2 = sel_data[2]
    list_sleepy_2 = sel_data[3]
    list_clean_2 = sel_data[4]
    list_start_2 = sel_data[5]
    list_index_or_2 = sel_data[6]
    ARRAY_1 = ARRAY.astype(np.int)
    best_paixu_1 = best_paixu.astype(np.int)
    print('最优解的index:', ARRAY_1)
    print('最优解的手术室号:',best_paixu_1)
    o_total_time, o_total_r_time, o_total_empty_time, overtime_work, result = calculte_r._best_result_(best_paixu_1, num, list_sleepy_2, list_operation_2, list_clean_2)
# o_total_time是手术室工作的总时长// o_total_r_time是手术室总复苏时长// o_total_empty_time是手术室总空闲时长// overtime_work是手术室总超时工作时长//

    index_or_1, list_clean_1, list_sleepy_1, list_start_1 = calculte_r._get_list_(num, result, ARRAY_1, list_clean, list_operation)
#用于返回数据
    data['复苏时间'] = list_sleepy_1     # 手术室内的复苏时间
    data['清洁时间'] = list_clean_1        # 手术室内的清洁时间
    data['手术开始时间'] = list_start_1  # 手术室每一台手术的开始时间
    data['手术室编码'] = index_or_1      # 手术室内的手术的编码
#存入csv
    data.to_csv('output.csv', sep=',', header=True)
#json输出内容
    orRatio = str((o_total_time-o_total_r_time-list_clean_1.sum())/(o_total_time+o_total_empty_time))
    cleanRatio = str(list_clean_1.sum()/(o_total_time+o_total_empty_time))
    recoverRoomratio = str(o_total_r_time/(o_total_time+o_total_empty_time))
    emptyRatio = str(o_total_empty_time/(o_total_time+o_total_empty_time))
    extraHours = overtime_work
    extraHoursRatio = (extraHours/o_total_time)
    overtimeRatio = str(overtime_work.sum()/o_total_time)
    dict_2 = {}
    dict_2["filePath"] = "output.csv"
    dict_2["orRatio"] = orRatio                   # 手术室利用率
    dict_2["recoverRatio"] = recoverRoomratio     # 复苏室利用率
    dict_2["cleanRatio"] = cleanRatio             # 用于清洁的时间
    dict_2["emptyRatio"] = emptyRatio             # 闲置时间比例
    dict_2["extraHours"] = extraHours.tolist()             # 加班总时间(分钟)
    dict_2["extraHoursRatio"] = extraHoursRatio.tolist()   # 每一个元素
    dict_2["overtimeRatio"] = overtimeRatio       # 额外加班时间

# 用于饼图展示的比例：



    return dict_2






#    calculte_r._output_date_(output_1)  #对输出进行返回
                                #运行主程序
if __name__ == '__main__':
    dict_2 = main_1('input_1.json')
    print('手术室工作比例：', dict_2["orRatio"])
    print('手术室用于复苏的比例:', dict_2["recoverRatio"])
    print('手术室清洁时间比例：', dict_2["cleanRatio"])
    print('手术室空闲时间比例：', dict_2["emptyRatio"])
    print('手术室额外加班时间比例：', dict_2["overtimeRatio"])
    print('总利用比例：', float(dict_2["orRatio"])+float(dict_2["recoverRatio"])+float(dict_2["cleanRatio"])+float(dict_2["emptyRatio"]))