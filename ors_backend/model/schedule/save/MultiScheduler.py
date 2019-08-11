# -*- coding: utf-8 -*-
"""
作者：desklee
日期：2019/8/10
功能：对ORS多人调度问题的前端页面接口
版本：2.0
"""

import json
from model.schedule.save.calculation import calculte
import csv
from model.schedule.save.MyProblem import MyProblem
import geatpy as ea
from model.schedule.save.algorithm import Algorithm
import numpy as np
import pandas as pd
import random
import time

def Scheduler(input_json, input_config):
    """
    调度器
    用法：
    from MultiScheduler import Scheduler
    output_json, output_overall = Scheduler(input_json, input_config)

    输入：
    input_json:患者信息
    input_json = [
        {
            "age": "70",
            "anaesthetic": "全身麻醉",
            "department": "心血管科",
            "doctorName": "李四",
            "gender": "男",
            "id": "1",
            "key": "0",
            "name": "王小舟",
            "operatingName": "心脏搭桥手术",
            "orId": "",
            "predTime": "120",
            "rank": "2",
            "startTime": ""
        },{
            "age": "23",
            "anaesthetic": "全身麻醉",
            "department": "妇产科",
            "doctorName": "王五",
            "gender": "女",
            "id": "1",
            "key": "0",
            "name": "张小臻",
            "operatingName": "剖腹产",
            "orId": "",
            "predTime": "120",
            "rank": "2",
            "startTime": ""
        }
    ]
    input_config:环境变量，手术室数量、复苏室数量等信息
    input_config = {
        "recover_min": 60, #最小恢复时间
        "end_time": "3:30", #下班时间
        "operRoom": 3,  #手术室数目
        "recover": 3,  #恢复室数目
        "start_time": "08:30" #上班时间
    }
    输出：
    output_json:添加手术室号、开始时间等的病人信息
    output_json = [
        {
            "key": "0",
            "id": "1",
            "name": "尹小帆",
            "gender": "男",
            "age": "70",
            "department": "心血管科",
            "operatingName": "心脏搭桥手术",
            "doctorName": "李四",
            "predTime": "120",
            "anaesthetic": "全身麻醉",
            "rank": "2",
            "orId": "10",
            "startTime": "8:00",
            "recoverDuration": 15,
            "cleanDuration": 20
        }, {
            "key": "1",
            "id": "2",
            "name": "司徒",
            "gender": "女",
            "age": "23",
            "department": "妇产科",
            "operatingName": "剖腹产手术",
            "doctorName": "王小二",
            "predTime": "100",
            "anaesthetic": "局部麻醉",
            "rank": "1",
            "orId": "7",
            "startTime": "9:00",
            "recoverDuration": 15,
            "cleanDuration": 20
        }
        ]
    output_overall:手术室利用比例，恢复室利用比例、各手术室超出工作时间和比例
    output_overall = {
    "orRatio": "0.99999",
    "recoverRoomRatio": "0.8",
    "extraHours": [4, 5, 6],
    "extraHourRatio": [0.4, 0.2, 0.9]
    }
    """
    #===================以下为程序部分===================#
    if (not input_json) or (not input_config):  #判断空字符串输入，返回空字符串
        return '',''
    
    data = pd.DataFrame(input_json)
    input_1 = input_config
    
    num = len(data)  # 病人总的数目
    morning_time = int(input_1['start_time'].split(':')[0]) * 60 + int(input_1['start_time'].split(':')[1])
    afternoon_time = int(input_1['end_time'].split(':')[0]) * 60 + int(input_1['end_time'].split(':')[1])
    n_x = int(input_1['operRoom'])   #手术室数目
    n_y = int(input_1['recover'])  #复苏室数目
    t_s = int(input_1['doctor'])   #最小复苏时间
    calculte_r = calculte(data, n_x, n_y, t_s, morning_time, afternoon_time)  # 实例化
    list_doctID, list_patientID, list_operation, list_sleepy, list_clean, list_start, list_index_or, list_of_all= calculte_r._process_data_(num)
    list_of_all_1 = list_of_all[:]                                             # 复制list_of_all为list_of_all_1
    list_start_temple = list_start
    list_index_or_temple = list_index_or
    list_start_3 = np.zeros((num,), dtype=np.int)
    list_index_or_3 = np.zeros((num, 1), dtype=np.int)
    list_clean = list_clean.astype(np.int)
    # print(list_clean)


    temple_for_startime = np.where(list_start_temple != '')[0]
    for value in temple_for_startime:
        neirong = (int((list_start[value].split(':')[0]))) * 60 + int(
            (list_start[value].split(':')[1])) - morning_time
        list_start_3[value] = neirong                      # list_start_3中存入的是有开始时间病人的开始时间

    temple_for_orNum = np.where(list_index_or_temple != '')[0]
    index_index_or_temple_1 = np.array([], dtype=np.int)                        # list_start_3中存储的是转换后的list_start值(分钟)
    for value in temple_for_orNum:
            list_index_or_3[value] = list_index_or[value]      # list_index_or_3中存入的是有手术室号病人的手术室号
            # print(list_index_or_3[value][0])

    set_jiao = set(temple_for_startime) & set(temple_for_orNum)
    list_cha_start_time = list(set(temple_for_startime) - set_jiao)
    list_cha_index_or = list(set(temple_for_orNum) - set_jiao)
    list_jiao = list(set_jiao)

    list_cha_index_or_1 = list_cha_index_or[:]                                  # 复制仅绑定手术室号的值

    dict_for_xunhuan = {}                                                       # 存入需要找到并确定的dict的值
                                                                                # 对仅绑定手术室号的情况进行序列调整, 这一列需要被传递
    for index, value in enumerate(list_cha_index_or):
        a = 0
        for j in temple_for_startime:
            if value > j:
                a -= 1
        list_cha_index_or_1[index] = value+a
        dict_for_xunhuan[value+a] = [list_index_or_3[value][0], value]
                                                                                 # dict_for_xunhuan中存入的是每一个人对应的手术室号0
                                                                                 # 和它实际的位

                                                                                 # ARRAY对应的字典
    dict_for_result = {}                                                         # 存入需要找到并确定的dict的值
    for i in range(num):
        a = 0
        for j in temple_for_startime:
            if i > j:
                a -= 1
        dict_for_result[i] = [i+a]

    for k in temple_for_startime:
        del dict_for_result[k]

    length_sum = len(temple_for_startime)                                       # 绑定了时间的人数
    Encoding = 'RI'                                          # 编码方式为实数                                           # 染色体解码后得到的变量是离散的
    NIND = 50                                              # 种群规模

    problem = MyProblem(num - length_sum, n_x, n_y, NIND, list_of_all_1, morning_time, afternoon_time, dict_for_xunhuan)
    # n_o为手术室数量，n_r为复苏室数量, chrom为染色体[1,3,2]表示第一台
    # 手术在1号手术室在1号手术室内做，o_time[30,100,60]表示第一台手术时长30分钟，
    # c_time表示清洁时长，r_time表示复苏时长（0或自定义最小复苏时长默认为60min）
    # 生成问题对象
    Field = ea.crtfld(Encoding, problem.varTypes, problem.ranges, problem.borders)  # 创建区域描述器
    population = ea.Population(Encoding, Field, NIND)             # 创建种群对象
    x_chuandai = 30
    id_trace = (np.zeros((x_chuandai, num - length_sum)) * np.nan)  # 定义变量记录器，记录决策变量值，初始值为nan
    # problem, population, id_trace, n_x, list_jiao, list_start_3, list_operation, list_sleepy, list_index_or_3, list_doctID, list_clean, list_cha_start_time
    Algorithm_1 = Algorithm(problem, population, id_trace, n_x, list_jiao, list_start_3, list_operation, list_sleepy, list_index_or_3, list_doctID, list_clean, list_cha_start_time)            # 实例化一个算法模板对象

    Algorithm_1.MAXGEN = x_chuandai                                 # 最大遗传代数
    [population, obj_trace, var_trace, id_trace, new_fixed_dict] = Algorithm_1.run()  # 执行算法模板   #如何返回最优解


    best_gen = np.argmin(obj_trace[:, 1])  # 记录最优种群是在哪一代
    best_ObjV = obj_trace[best_gen, 1]  # 目标函数值最优

    # mean_ObjV = obj_trace[best_gen, 0]                      # 均值

    best_paixu = var_trace[best_gen, :]  # 最优解
    ARRAY = id_trace[best_gen, :]

    sel_data = list_of_all_1[:, list(ARRAY.astype(np.int))]
    # list_doctID, list_patientID, list_operation, list_sleepy, list_clean, list_start, list_index_or
    list_doctID_2 = sel_data[0]
    list_patientID_2 = sel_data[1]
    list_operation_2 = sel_data[2]
    list_sleepy_2 = sel_data[3]
    list_clean_2 = sel_data[4]
    list_start_2 = sel_data[5]
    list_index_or_2 = sel_data[6]
    ARRAY_1 = ARRAY.astype(np.int)
    best_paixu_1 = best_paixu.astype(np.int)
    o_total_time, o_total_r_time, o_total_empty_time, overtime_work, result, fixed_result, o_c_time = calculte_r._best_result_(
        best_paixu_1,
        new_fixed_dict,
        list_sleepy_2,
        list_operation_2,
        list_clean_2,
        list_doctID_2)
    # o_total_time是手术室工作的总时长// o_total_r_time是手术室总复苏时长// o_total_empty_time是手术室总空闲时长// overtime_work是手术室总超时工作时长//
    index_or_1, list_clean_1, list_sleepy_1, list_start_1 = calculte_r._get_list_(num, result, fixed_result, ARRAY_1,
                                                                                  list_clean,
                                                                                  list_operation, dict_for_xunhuan,
                                                                                  list_start, dict_for_result)

    data['recoverDuration'] = list_sleepy_1     # 手术室内的复苏时间
    data['cleanDuration'] = list_clean_1        # 手术室内的清洁时间
    data['startTime'] = list_start_1  # 手术室每一台手术的开始时间
    data['orId'] = index_or_1      # 手术室内的手术的编码
    data['predTime'] = list_operation
#存入csv
#json输出内容
    orRatio = str((o_total_time.sum()-o_total_r_time.sum()-list_clean_1.sum())/(o_total_time.sum()+o_total_empty_time.sum()))
    everyorRatio = (o_total_time-o_total_r_time-o_c_time)/(o_total_time+o_total_empty_time)
    cleanRatio = str(list_clean_1.sum()/(o_total_time.sum()+o_total_empty_time.sum()))
    recoverRoomratio = str(o_total_r_time.sum()/(o_total_time.sum()+o_total_empty_time.sum()))
    emptyRatio = o_total_empty_time/(o_total_time+o_total_empty_time)
    extraHours = overtime_work
    extraHoursRatio = (extraHours/o_total_time)
    overtimeRatio = str(overtime_work.sum()/o_total_time.sum())
    # dict_2 = {}
    # dict_2["filePath"] = "output.csv"
    # dict_2["orRatio"] = orRatio                   # 手术室利用率
    # dict_2["recoverRatio"] = recoverRoomratio     # 复苏室利用率
    # dict_2["cleanRatio"] = cleanRatio             # 用于清洁的时间
    # dict_2["emptyRatio"] = emptyRatio             # 闲置时间比例
    # dict_2["extraHours"] = extraHours.tolist()             # 加班总时间(分钟)
    # dict_2["extraHoursRatio"] = extraHoursRatio.tolist()   # 每一个元素
    # dict_2["overtimeRatio"] = overtimeRatio       # 额外加班时间

# 用于饼图展示的比例：
    data.to_csv('output.csv', sep=',', header=True)
    output_json = data.to_json(orient='records',force_ascii = False)
    output_overall = {
    "orRatio": orRatio,
    "everyorRatio": everyorRatio.tolist(),
    "recoverRoomRatio": recoverRoomratio,
    "emptyRatio": emptyRatio.tolist(),
    "cleanRatio": cleanRatio,
    "extraHours": extraHours.tolist(),
    "extraHourRatio": extraHoursRatio.tolist(),
    "overtimeRatio": overtimeRatio
    }

    
    return output_json, output_overall

if __name__ == '__main__':
    with open('data.json', 'r') as f:
        input_json = json.load(f)
    input_config = {
        "recover_min": 60,  # 最小恢复时间
        "end_time": "16:00",  # 下班时间
        "operRoom": 8,  # 手术室数目
        "recover": 4,  # 恢复室数目
        "start_time": "08:00"  # 上班时间
    }
    t1 = time.time()
    output_json, output_overall = Scheduler(input_json, input_config)
    t2 = time.time()
    print('output_json:', output_json)
    print('out_overall', output_overall)
    print('所用时间', t2-t1)
