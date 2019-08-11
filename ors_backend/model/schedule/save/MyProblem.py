# -*- coding: utf-8 -*-
"""
作者：李文卓
日期：2019/7/28
功能：对ORS调度的问题进行描述的类class MyProblem
版本：1.0
"""

import numpy as np
import geatpy as ea
from typing import Any


class MyProblem(ea.Problem):
    def __init__(self, Num, n_x, n_y, NIND, list_of_all, morning_time, afternoon_time, dict_for_xunhuan):
        # num - length_sum, n_x, n_y, NIND, list_of_all_1, morning_time, afternoon_time, dict_for_xunhuan
        # n_x表示的是手术室的数量
        # Num表示的是此时一条染色体的数目
        # n_y表示的是复苏室的数量
        self.Num = Num
        self.n_x = n_x
        self.name = 'MyProblem'  # 初始化函数名
        self.M = 1  # 目标维数
        self.maxormins = [1] * self.M  # 所有目标都被要求最小化
        self.Dim = self.Num  # 决策变量维数，病人的个数
        self.varTypes = np.array([1] * self.Dim)  # 初始化varTypes决策变量的类型，离散
        lb = [1] * self.Dim  # 决策变量下界   #决策变量下界是1
        ub = [self.n_x] * self.Dim  # 决策变量上界  #决策变量上界是n_x 手术室数
        self.ranges = np.array([lb, ub])  # 初始化ranges(决策变量范围矩阵)   #决策边界
        lbin = [1] * self.Dim  # 包含决策边界下界
        ubin = [1] * self.Dim  # 包含决策边界上界
        self.borders = np.array([lbin, ubin])  # 初始化borders   #给出被包含的决策边界
        self.list_of_all = list_of_all
        self.NIND = NIND
        self.n_y = n_y
        self.morning = morning_time
        self.afternoon = afternoon_time
        self.dict_for_xunhuan = dict_for_xunhuan

    def simulation_fixed(self ,n_o, n_r, chrom, o_time, c_time, r_time, fixed_o, doctors):
        """n_o为手术室数量，n_r为复苏室数量, chrom为染色体[1,3,2]表示第一台
        手术在1号手术室在1号手术室内做，o_time[30,100,60]表示第一台手术时长30分钟，
        c_time表示清洁时长，r_time表示复苏时长（0或自定义最小复苏时长默认为60min）
        doctors为每台手术室的医生，fixed_o是固定手术室和开始时间的病人，key为手术室房间号，
        value为n*6维的numpy矩阵，一行为一个病人，6列分别为病人id，开始时间（如8：00为0，以分钟记），
        手术时长，复苏时间，清洁时间，主刀医生"""
        flag = True  # 染色体是否符合限制性条件
        r_time_max = r_time.max()  # 最小复苏时长
        o_o_state = np.zeros(n_o, dtype=np.bool)  # 手术室是否进行手术
        o_c_state = np.zeros(n_o, dtype=np.bool)  # 手术室是否进行清洁
        o_r_state = np.zeros(n_o, dtype=np.bool)  # 手术室是否进行复苏
        o_empty_state = np.zeros(n_o, dtype=np.bool)  # 手术室是否在没做完手术时闲置
        o_doctor_conflict = np.zeros(n_o, dtype=np.bool)  # 手术室是否因为医生冲突而闲置
        o_end_state = np.zeros(n_o, dtype=np.bool)  # 手术室是否结束工作
        o_f_state = np.zeros(n_o, dtype=np.bool)  # 手术室是否在做固定的手术
        o_doctor = np.zeros(n_o, dtype='<U3')
        r_state = np.zeros(n_r, dtype=int)  # 复苏室内状态，0表示空置，大于0表示在使用
        o_total_time = np.zeros(n_o, dtype=int)  # 各手术室内工作总时长（直到最后一台手术完成清洁）
        o_total_r_time = np.zeros(n_o, dtype=int)  # 各手术室内复苏总时长
        o_total_empty_time = np.zeros(n_o, dtype=int)  # 各手术室内日常工作时段的闲置总时长（既不做手术，也不清洁，不复苏）
        overtime_work = np.zeros(n_o, dtype=int)
        o_dict = {}  # 一个存放每个手术室室染色体上第几台手术的字典，如{1：[2,4,5]表示第一号手术室按顺序做染色体上第2，4，5台手术
        o_order = np.zeros(n_o, dtype=int)  # 存放目前该手术室正在进行第几台手术
        o_len = np.zeros(n_o, dtype=int)  # 存放每个手术室有几台手术
        o_o_time = np.zeros(n_o, dtype=int)  # 目前手术室内手术还需要多长时间
        o_c_time = np.zeros(n_o, dtype=int)  # 目前手术室内清洁还需要多长时间
        o_r_time = np.zeros(n_o, dtype=int)  # 目前手术室内已复苏了多长时间
        o_empty_time = np.zeros(n_o, dtype=int)  # 手术室内手术没做完闲置的时间
        o_has_fixed = np.zeros(n_o, dtype=np.bool)  # 每个手术室是否有固定的手术
        o_fixed_num = np.zeros(n_o, dtype=int)  # 每个手术室有几台手术被固定
        o_fixed_order = np.zeros(n_o, dtype=int)  # 手术室第几台固定的手术
        work_time = (self.afternoon-self.morning) // 5  # 日常工作时长有多少个5分钟

        for o in range(n_o):  # 初始化
            o_dict[o] = np.where(chrom == o + 1)[0]
            o_len[o] = o_dict[o].shape[0]
            o_has_fixed[o] = o + 1 in fixed_o.keys()
            if o_has_fixed[o]:
                o_fixed_num[o] = fixed_o[o + 1].shape[0]

        for t in range(288):
            # 一天排班最多24小时，每5分钟检查一次
            if not flag:  # 非可行解跳出循环
                break

            if o_end_state.sum() == n_o:  # 如果所有手术室均结束工作，跳出循环
                break

            r_empty_num = r_state[r_state == 0].size  # 更新复苏室空床位数
            if o_r_state[o_r_state].size > 0 and r_empty_num > 0:  # 当复苏室有空床位，又有手术室内复苏
                o_r_time_sort = np.argsort(-o_r_time)  # 早做完手术的优先进入复苏室
                r_state_sort = np.argsort(r_state)

                for r in range(r_empty_num):
                    o_room = o_r_time_sort[r]
                    r_bed = r_state_sort[r]

                    if o_r_time[o_room] == 0:  # 没有还在手术室内复苏的就跳出循环
                        break

                    o_r_state[o_room] = False  # 更改手术室内复苏状态

                    if o_f_state[o_room]:
                        C_time = int(fixed_o[o_room + 1][o_fixed_order[o_room]][4])
                    else:
                        C_time = c_time[o_dict[o_room][o_order[o_room]]]

                    o_total_r_time[o_room] += o_r_time[o_room]
                    o_total_time[o_room] += o_r_time[o_room]
                    r_state[r_bed] = r_time_max - o_r_time[o_room]  # 将剩余的复苏时间填入复苏室
                    o_r_time[o_room] = 0  # 将手术室内复苏时间设为0
                    o_c_state[o_room] = True  # 手术室进入清洁状态
                    o_c_time[o_room] = C_time  # 填入需清洁的时间
                    r_empty_num -= 1  # 复苏室空床位数减一

            r_state[r_state > 0] -= 5  # 更新复苏室床位状态，大于0的就减5

            for o in range(n_o):
                # 对每个手术室状态进行检查

                if o_end_state[o]:  # 如果已结束当天所有工作，进入下一个手术室循环
                    continue

                if o_has_fixed[o] and o_fixed_order[o] < o_fixed_num[o] and int(
                        fixed_o[o + 1][o_fixed_order[o]][1]) == t * 5:
                    # 如果到了固定手术的开始时间，推入固定手术

                    if o_o_state[o] or o_c_state[o] or o_r_state[o]:
                        """已经有一次判断，手术时间加清洁时间小于剩余的时间（到固定手术开始），就推入手术，不然就闲置。
                        如果这次手术要在手术室内复苏，就认为这个是不可行解."""
                        flag = False  # 时间冲突
                        break

                    if (o_doctor == fixed_o[o + 1][o_fixed_order[o]][5]).sum() == 1:
                        flag = False  # 医生冲突
                        break

                    o_empty_state[o] = False
                    o_o_state[o] = True
                    o_f_state[o] = True  # 标记做的是固定手术
                    o_o_time[o] = int(fixed_o[o + 1][o_fixed_order[o]][2])
                    o_doctor[o] = fixed_o[o + 1][o_fixed_order[o]][5]

                if o_len[o] == 0 and not o_has_fixed[o]:  # 考虑手术室一台手术都没排
                    o_total_empty_time[o] += work_time * 5
                    o_end_state[o] = True
                    continue

                if not o_o_state[o] and not o_c_state[o] and not o_r_state[o] and not o_empty_state[o]:
                    if o_len[o] == 0:
                        o_empty_state[o] = True
                        o_empty_time[o] += 5
                        continue
                        # 手术室刚开始是空闲状态
                    if o_fixed_order[o] < o_fixed_num[o]:
                        O_oc_time = o_time[o_dict[o][o_order[o]]] + c_time[o_dict[o][o_order[o]]]
                        # 如果染色体上的手术时间加清洁时间大于进入固定手术的时间，则让手术室进入闲置状态，等待固定手术进入
                        if O_oc_time > int(fixed_o[o + 1][o_fixed_order[o]][1]) - t * 5:
                            o_empty_state[o] = True
                            o_empty_time[o] += 5
                            continue
                            # 否则手术室内进入染色体上排到的手术
                    if (o_doctor == doctors[o_dict[o][o_order[o]]]).sum() == 1:
                        #                    flag = False#医生冲突
                        #                    print(2)
                        #                    break
                        o_empty_state[o] = True  # 如果遇到医生冲突，让这台手术先停，等没有医生冲突再进行
                        o_doctor_conflict[o] = True
                        o_empty_time[o] += 5
                    else:
                        o_o_state[o] = True  # 开始手术
                        o_doctor[o] = doctors[o_dict[o][o_order[o]]]
                        o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 5  # 将第i台的手术时长填入减5

                elif o_o_state[o]:  # 手术室进行手术状态

                    if o_o_time[o] == 0:  # 结束手术
                        o_o_state[o] = False
                        o_doctor[o] = ''

                        if o_f_state[o]:
                            O_time = int(fixed_o[o + 1][o_fixed_order[o]][2])
                            R_time = int(fixed_o[o + 1][o_fixed_order[o]][3])
                            C_time = int(fixed_o[o + 1][o_fixed_order[o]][4])
                        else:
                            O_time = o_time[o_dict[o][o_order[o]]]
                            R_time = r_time[o_dict[o][o_order[o]]]
                            C_time = c_time[o_dict[o][o_order[o]]]

                        o_total_time[o] += O_time  # 将这一台手术时长计入工作总时间

                        if R_time == 0:  # 若不需要复苏
                            o_c_state[o] = True
                            o_c_time[o] = C_time - 5
                        else:
                            if r_empty_num == 0:  # 没复苏室空位
                                o_r_state[o] = True
                                o_r_time[o] += 5
                            else:
                                r_state[np.where(r_state == 0)[0][0]] += r_time_max - 5
                                r_empty_num -= 1
                                o_c_state[o] = True
                                o_c_time[o] = C_time - 5

                    else:
                        o_o_time[o] -= 5


                elif o_c_state[o]:  # 手术室处于清洁状态
                    if o_c_time[o] == 0:  # 结束清洁
                        o_c_state[o] = False
                        if o_f_state[o]:  # 如果进行的是固定的手术，时间从固定手术字典中提取
                            o_total_time[o] += int(fixed_o[o + 1][o_fixed_order[o]][4])
                            o_fixed_order[o] += 1
                            o_f_state[o] = False
                        else:
                            o_total_time[o] += c_time[o_dict[o][o_order[o]]]  # 将这一台手术清洁时间计入手术室工作总时间
                            o_order[o] += 1

                        if o_order[o] < o_len[o] and o_fixed_order[o] < o_fixed_num[o]:  # 推入下一台手术
                            O_oc_time = o_time[o_dict[o][o_order[o]]] + c_time[o_dict[o][o_order[o]]]
                            if O_oc_time > int(fixed_o[o + 1][o_fixed_order[o]][1]) - t * 5:
                                o_empty_state[o] = True
                                o_empty_time[o] += 5
                                continue
                            else:
                                if (o_doctor == doctors[o_dict[o][o_order[o]]]).sum() == 1:
                                    #                                flag = False#医生冲突
                                    #                                print(2)
                                    #                                break
                                    o_empty_state[o] = True  # 如果遇到医生冲突，让这台手术先停，等没有医生冲突再进行
                                    o_doctor_conflict[o] = True
                                    o_empty_time[o] += 5
                                else:
                                    o_o_state[o] = True
                                    o_doctor[o] = doctors[o_dict[o][o_order[o]]]
                                    o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 5
                        elif o_fixed_order[o] < o_fixed_num[o]:
                            o_empty_state[o] = True
                            o_empty_time[o] += 5
                        elif o_order[o] < o_len[o]:
                            if (o_doctor == doctors[o_dict[o][o_order[o]]]).sum() == 1:
                                #                            flag = False#医生冲突
                                #                            print(2)
                                #                            break
                                o_empty_state[o] = True  # 如果遇到医生冲突，让这台手术先停，等没有医生冲突再进行
                                o_doctor_conflict[o] = True
                                o_empty_time[o] += 5
                            else:
                                o_o_state[o] = True
                                o_doctor[o] = doctors[o_dict[o][o_order[o]]]
                                o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 5
                        else:
                            o_end_state[o] = True  # 手术室工作结束
                            o_total_empty_time[o] += o_empty_time[o]
                            o_total_time[o] += o_empty_time[o]
                            if t + 1 < work_time:  # 将闲置时间累加
                                o_total_empty_time[o] += (work_time - t - 1) * 5
                            else:
                                overtime_work[o] += (t + 1 - work_time) * 5

                    else:
                        o_c_time[o] -= 5

                elif o_r_state[o]:  # 手术室处于复苏状态
                    o_r_time[o] += 5
                    if o_r_time[o] == r_time_max:
                        o_total_r_time[o] += r_time_max
                        o_total_time[o] += r_time_max
                        o_r_time[o] = 0
                        o_r_state[o] = False
                        o_c_state[o] = True
                        if o_f_state[o]:
                            C_time = int(fixed_o[o + 1][o_fixed_order[o]][4])
                        else:
                            C_time = c_time[o_dict[o][o_order[o]]]
                        o_c_time[o] = C_time

                elif o_empty_state[o]:
                    if o_doctor_conflict[o] and (o_doctor == doctors[o_dict[o][o_order[o]]]).sum() == 0:
                        if o_fixed_order[o] < o_fixed_num[o]:  # 如果现在没有医生冲突还要再判断一下跟固定手术有没有冲突
                            O_oc_time = o_time[o_dict[o][o_order[o]]] + c_time[o_dict[o][o_order[o]]]
                            if O_oc_time > int(fixed_o[o + 1][o_fixed_order[o]][1]) - t * 5:
                                o_empty_state[o] = True
                                o_empty_time[o] += 5
                                o_doctor_conflict[o] = False  # 现在是因为固定手术而闲置
                                continue
                        else:  # 将下一台手术推入
                            o_o_state[o] = True
                            o_doctor[o] = doctors[o_dict[o][o_order[o]]]
                            o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 10  # 医生在上一个时间循环0时结束手术
                    else:
                        o_empty_time[o] += 5

            if t == 287:  # 工作超过24小时
                if o_end_state.sum() < n_o:
                    flag = False  # 超时冲突
        #    print(flag)
        return o_total_time.sum(), o_total_r_time.sum(), o_total_empty_time.sum(), overtime_work.sum(), flag

    def aimFunc(self, chorm, list_operation_4, list_clean_4, list_sleepy_4, new_fixed_dict, list_doctID_4):
        o_total_time, o_total_r_time, o_total_empty_time, overtime_work, flag = self.simulation_fixed(self.n_x, self.n_y, chorm, list_operation_4, list_clean_4, list_sleepy_4, new_fixed_dict, list_doctID_4)
        f = o_total_r_time+o_total_empty_time+overtime_work
        if flag == False:
            f = 24 * 60 * self.n_x * 10000000
        # print(f, flag)
        return f, flag

    def aim_chuli(self, phen, id, new_fixed_dict):  # 返回当前的染色体函数
        NIND_1 = phen.shape[0]
        f_mubiao = np.zeros((NIND_1, 1))  # 目标函数向量
        CV = np.zeros((NIND_1, 1))  # 限制性向量
        for i in range(NIND_1):
            ARRAY = id[i]    # 种群中的第i个染色体对应的index
            chorm = phen[i]  # 种群中的第i个染色体
            # 对第i个染色体进行修改
         #   print('ARRAY:', ARRAY)
         #   print('chorm:', chorm)
            for index, value in self.dict_for_xunhuan.items():
                chorm[np.where(ARRAY == index)[0][0]] = value[0]
         #   print(chorm)
            sel_data_2 = self.list_of_all[:, list(ARRAY)]  # 当前种群的sel_data
            # list_doctID, list_patientID, list_operation, list_sleepy, list_clean, list_start, list_index_or
            list_doctID_4 = sel_data_2[0]
            list_patientID_4 = sel_data_2[1]
            list_operation_4 = sel_data_2[2]
            list_sleepy_4 = sel_data_2[3]
            list_clean_4 = sel_data_2[4]
            list_start_4 = sel_data_2[5]
            f_mubiao[i], CV[i] = self.aimFunc(chorm, list_operation_4, list_clean_4, list_sleepy_4,new_fixed_dict, list_doctID_4)  # 返回的是目标函数和CV限制矩阵
          #  print('此时的phen：', chorm)
          #  print('第{}次循环的目标函数值：{}'.format(i, f_mubiao[i]))
        # print('此时的CV是：', CV_1.reshape((1, -1)))
        CV = np.where(CV == True, 0, 1)
        return f_mubiao, CV

    def intersect(self, chrom_1, id, mututation):
        """
        作者：zzz
        日期：2019/7/31
        功能：交叉函数
        chrom: 种群//待解码矩阵
        id: 病人id，shape同种群
        mututation: 变异率
        CV: 可行性
        FitV: 适应度
        """
        for i in range(chrom_1.shape[0]):
            if np.round(np.random.uniform(0, 1, 1)) < mututation:
                inter_individual = np.random.randint(1, chrom_1.shape[1], size=2)
                chrom_1[i, [inter_individual[0], inter_individual[1]]] = chrom_1[
                    i, [inter_individual[1], inter_individual[0]]]
                id[i, [inter_individual[0], inter_individual[1]]] = id[i, [inter_individual[0], inter_individual[1]]]
    # for i in range(chrom_1.shape[0]):
        #     d = np.argmax(np.bincount(chrom_1[i]))
        #     e = np.bincount(chrom_1[i])
        #     e = np.delete(e, 0)
        #     x = np.argmin(e)
        #     x = x+1
        #     y = np.where(chrom_1[i] == d)[0]
        #     batch_size = int(y.shape[0]/4)
        #     slice_1 = np.random.choice(y.shape[0], batch_size)
        #     chrom_1[i][y[slice_1]] = x



        return chrom_1, id
