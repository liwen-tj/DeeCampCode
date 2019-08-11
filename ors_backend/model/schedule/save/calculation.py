"""
作者：desklee
日期：2019/7/29
功能：计算对象
版本：2.0
"""
import json
import numpy as np


class calculte():
    def __init__(self, data, n_x, n_y, t_s, morning_time, afternoon_time):
        self.data = data
        self.n_x = n_x
        self.n_y = n_y
        self.t_s = t_s
        self.morning_time = morning_time
        self.afternoon_time = afternoon_time

    def _process_data_(self, num):
        list_patientID = np.array(self.data['id'])[:] # 就诊号
        list_doctID = np.array(self.data['doctorName'])[:] #医生
        list_sleepy = np.array(self.data['anaesthetic'])[:] #麻醉方式
        list_operation = (np.array(self.data['predTime'])[:]).astype(np.int) #手术时间
        list_clean = (np.array(self.data['rank'])[:]) #手术级别
        list_start = np.array(self.data['startTime'])[:] #开始时间
        list_index_or = (np.array(self.data['orId'])[:]) #手术室号
        list_operation = (np.ceil(list_operation / 5) * 5).astype(np.int)
        list_sleepy.reshape((num, 1))
        for i in range(num):
            b = list_sleepy[i]
            if b == '全身麻醉' or b == '全身麻醉(喉罩)':
                tb = self.t_s
            else:
                tb = 0
            list_sleepy[i] = tb
        list_clean.reshape((num, 1))
        for i in range(num):
            a = list_clean[i]
            if a == 1.0:
                tp = 10
            elif a == 2.0 or a == 3.0:
                tp = 20
            elif a == 4.0:
                tp = 30
            else:
                tp = 20
            list_clean[i] = tp
        c = np.vstack((list_doctID, list_patientID, list_operation, list_sleepy, list_clean, list_start, list_index_or))
        return list_doctID, list_patientID, list_operation, list_sleepy, list_clean, list_start, list_index_or, c
    def _best_result_(self, chrom, dict_chaxun, r_time, o_time, c_time, doctors):
        """
        calculte_r._best_result_(best_paixu_1,dict_chaxun,num,list_sleepy_2,list_operation_2,list_clean_2)
        Created on Mon Jul 29 09:55:36 2019
        @author: lxw
        功能：模拟手术室整个工作流程，每5分钟检查一次，得到最终优化目标结果
        """
        r_time_max = r_time.max()  # 最小复苏时长
        o_o_state = np.zeros(self.n_x, dtype=np.bool)  # 手术室是否进行手术
        o_c_state = np.zeros(self.n_x, dtype=np.bool)  # 手术室是否进行清洁
        o_r_state = np.zeros(self.n_x, dtype=np.bool)  # 手术室是否进行复苏
        o_empty_state = np.zeros(self.n_x, dtype=np.bool)  # 手术室是否在没做完手术时闲置
        o_end_state = np.zeros(self.n_x, dtype=np.bool)  # 手术室是否结束工作
        o_f_state = np.zeros(self.n_x, dtype=np.bool)  # 手术室是否在做固定的手术
        o_doctor_conflict = np.zeros(self.n_x, dtype=np.bool)  # 手术室是否因为医生冲突而闲置
        o_doctor = np.zeros(self.n_x, dtype='<U3')
        r_state = np.zeros(self.n_y, dtype=int)  # 复苏室内状态，0表示空置，大于0表示在使用
        o_total_time = np.zeros(self.n_x, dtype=int)  # 各手术室内工作总时长（直到最后一台手术完成清洁）
        o_total_r_time = np.zeros(self.n_x, dtype=int)  # 各手术室内复苏总时长
        o_total_empty_time = np.zeros(self.n_x, dtype=int)  # 各手术室内日常工作时段的闲置总时长（既不做手术，也不清洁，不复苏）
        overtime_work = np.zeros(self.n_x, dtype=int)
        o_dict = {}  # 一个存放每个手术室室染色体上第几台手术的字典，如{1：[2,4,5]表示第一号手术室按顺序做染色体上第2，4，5台手术
        o_order = np.zeros(self.n_x, dtype=int)  # 存放目前该手术室正在进行第几台手术
        o_len = np.zeros(self.n_x, dtype=int)  # 存放每个手术室有几台手术
        o_o_time = np.zeros(self.n_x, dtype=int)  # 目前手术室内手术还需要多长时间
        o_c_time = np.zeros(self.n_x, dtype=int)  # 目前手术室内清洁还需要多长时间
        o_r_time = np.zeros(self.n_x, dtype=int)  # 目前手术室内已复苏了多长时间
        o_c_time = np.zeros(self.n_x, dtype=int)  # 目前手术室内已清洁了多长时间
        o_empty_time = np.zeros(self.n_x, dtype=int)  # 手术室内手术没做完闲置的时间
        o_has_fixed = np.zeros(self.n_x, dtype=np.bool)  # 每个手术室是否有固定的手术
        o_fixed_num = np.zeros(self.n_x, dtype=int)  # 每个手术室有几台手术被固定
        o_fixed_order = np.zeros(self.n_x, dtype=int)  # 手术室第几台固定的手术
        work_time = (self.afternoon_time - self.morning_time) // 5  # 日常工作时长有多少个5分钟
        result = {}
        fixed_result = {}
        for o in range(self.n_x):
            o_dict[o] = np.where(chrom == o + 1)[0]
            o_len[o] = o_dict[o].shape[0]
            o_has_fixed[o] = o + 1 in dict_chaxun.keys()
            result[o] = []
            fixed_result[o] = []
            if o_has_fixed[o]:
                o_fixed_num[o] = dict_chaxun[o + 1].shape[0]

        for t in range(288):
            # 一天排班最多24小时，每5分钟检查一次
            if o_end_state.sum() == self.n_x:  # 如果所有手术室均结束工作，跳出循环
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
                        C_time = int(dict_chaxun[o_room + 1][o_fixed_order[o_room]][4])
                        fixed_result[o_room][o_fixed_order[o_room]].append(o_r_time[o_room])
                    else:
                        result[o_room][o_order[o_room]].append(o_r_time[o_room])
                        C_time = c_time[o_dict[o_room][o_order[o_room]]]
                    o_total_r_time[o_room] += o_r_time[o_room]
                    o_total_time[o_room] += o_r_time[o_room]
                    r_state[r_bed] = r_time_max - o_r_time[o_room]  # 将剩余的复苏时间填入复苏室
                    o_r_time[o_room] = 0  # 将手术室内复苏时间设为0
                    o_c_state[o_room] = True  # 手术室进入清洁状态
                    o_c_time[o_room] = C_time  # 填入需清洁的时间
                    r_empty_num -= 1  # 复苏室空床位数减一
            r_state[r_state > 0] -= 5  # 更新复苏室床位状态，大于0的就减5

            for o in range(self.n_x):
                # 对每个手术室状态进行检查

                if o_end_state[o]:  # 如果已结束当天所有工作，进入下一个手术室循环
                    continue

                if o_has_fixed[o] and o_fixed_order[o] < o_fixed_num[o] and int(
                        dict_chaxun[o + 1][o_fixed_order[o]][1]) == t * 5:
                    # 如果到了固定手术的开始时间，推入固定手术

                    o_empty_state[o] = False
                    o_o_state[o] = True
                    o_f_state[o] = True  # 标记做的是固定手术
                    o_o_time[o] = int(dict_chaxun[o + 1][o_fixed_order[o]][2])
                    o_doctor[o] = dict_chaxun[o + 1][o_fixed_order[o]][5]

                if o_len[o] == 0 and not o_has_fixed[o]:  # 考虑手术室一台手术都没排
                    o_total_empty_time[o] += work_time * 5
                    o_end_state[o] = True
                    continue

                if not o_o_state[o] and not o_c_state[o] and not o_r_state[o] and not o_empty_state[o]:  # 手术室刚开始是空闲状态
                    if o_len[o] == 0:
                        o_empty_state[o] = True
                        o_empty_time[o] += 5
                        continue
                    if o_fixed_order[o] < o_fixed_num[o]:
                        O_oc_time = o_time[o_dict[o][o_order[o]]] + c_time[o_dict[o][o_order[o]]]
                        if O_oc_time > int(dict_chaxun[o + 1][o_fixed_order[o]][1]) - t * 5:
                            o_empty_state[o] = True
                            o_empty_time[o] += 5
                            continue
                    if (o_doctor == doctors[o_dict[o][o_order[o]]]).sum() == 1:
                        o_empty_state[o] = True  # 如果遇到医生冲突，让这台手术先停，等没有医生冲突再进行
                        o_doctor_conflict[o] = True
                        o_empty_time[o] += 5
                    else:
                        o_o_state[o] = True  # 开始手术
                        o_doctor[o] = doctors[o_dict[o][o_order[o]]]
                        o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 5  # 将第i台的手术时长填入减5
                #                o_o_state[o] = True#开始手术
                #                o_doctor[o] = doctors[o_dict[o][o_order[o]]]
                #                o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 5#将第i台的手术时长填入减5

                elif o_o_state[o]:  # 手术室进行手术状态
                    if o_o_time[o] == 0:
                        o_o_state[o] = False
                        o_doctor[o] = ''
                        if o_f_state[o]:
                            O_time = int(dict_chaxun[o + 1][o_fixed_order[o]][2])
                            o_total_time[o] += O_time
                            fixed_result[o].append(
                                [int(dict_chaxun[o + 1][o_fixed_order[o]][0]), t * 5 - O_time, O_time])
                            R_time = int(dict_chaxun[o + 1][o_fixed_order[o]][3])
                            C_time = int(dict_chaxun[o + 1][o_fixed_order[o]][4])
                        else:
                            O_time = o_time[o_dict[o][o_order[o]]]
                            result[o].append([o_dict[o][o_order[o]], t * 5 - O_time, O_time])
                            o_total_time[o] += O_time  # 将这一台手术时长计入工作总时间
                            R_time = r_time[o_dict[o][o_order[o]]]
                            C_time = c_time[o_dict[o][o_order[o]]]
                        if R_time == 0:  # 若不需要复苏
                            if not o_f_state[o]:
                                result[o][o_order[o]].append(0)
                            else:
                                fixed_result[o][o_fixed_order[o]].append(0)
                            o_c_state[o] = True
                            o_c_time[o] = C_time - 5
                        else:
                            if r_empty_num == 0:
                                o_r_state[o] = True
                                o_r_time[o] += 5
                            else:
                                r_state[np.where(r_state == 0)[0][0]] += r_time_max - 5
                                r_empty_num -= 1
                                if not o_f_state[o]:
                                    result[o][o_order[o]].append(0)
                                else:
                                    fixed_result[o][o_fixed_order[o]].append(0)
                                o_c_state[o] = True
                                o_c_time[o] = C_time - 5
                    else:
                        o_o_time[o] -= 5


                elif o_c_state[o]:  # 手术室处于清洁状态
                    if o_c_time[o] == 0:
                        o_c_state[o] = False
                        if o_f_state[o]:  # 如果进行的是固定的手术，时间从固定手术字典中提取
                            o_total_time[o] += int(dict_chaxun[o + 1][o_fixed_order[o]][4])
                            fixed_result[o][o_fixed_order[o]].append(int(dict_chaxun[o + 1][o_fixed_order[o]][4]))
                            o_c_time[o] += int(dict_chaxun[o + 1][o_fixed_order[o]][4])
                            o_fixed_order[o] += 1
                            o_f_state[o] = False
                        else:
                            result[o][o_order[o]].append(c_time[o_dict[o][o_order[o]]])
                            o_c_time[o] += c_time[o_dict[o][o_order[o]]]
                            o_total_time[o] += c_time[o_dict[o][o_order[o]]]  # 将这一台手术清洁时间计入手术室工作总时间
                            o_order[o] += 1

                        if o_order[o] < o_len[o] and o_fixed_order[o] < o_fixed_num[o]:  # 推入下一台手术
                            O_oc_time = o_time[o_dict[o][o_order[o]]] + c_time[o_dict[o][o_order[o]]]
                            if O_oc_time > int(dict_chaxun[o + 1][o_fixed_order[o]][1]) - t * 5:
                                o_empty_state[o] = True
                                o_empty_time[o] += 5
                                continue
                            else:
                                if (o_doctor == doctors[o_dict[o][o_order[o]]]).sum() == 1:
                                    o_empty_state[o] = True  # 如果遇到医生冲突，让这台手术先停，等没有医生冲突再进行
                                    o_doctor_conflict[o] = True
                                    o_empty_time[o] += 5
                                else:
                                    o_o_state[o] = True
                                    o_doctor[o] = doctors[o_dict[o][o_order[o]]]
                                    o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 5
                        #                            o_o_state[o] = True
                        #                            o_doctor[o] = doctors[o_dict[o][o_order[o]]]
                        #                            o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 5
                        elif o_fixed_order[o] < o_fixed_num[o]:
                            o_empty_state[o] = True
                            o_empty_time[o] += 5
                        elif o_order[o] < o_len[o]:
                            if (o_doctor == doctors[o_dict[o][o_order[o]]]).sum() == 1:
                                o_empty_state[o] = True  # 如果遇到医生冲突，让这台手术先停，等没有医生冲突再进行
                                o_doctor_conflict[o] = True
                                o_empty_time[o] += 5
                            else:
                                o_o_state[o] = True
                                o_doctor[o] = doctors[o_dict[o][o_order[o]]]
                                o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 5
                        #                        o_o_state[o] = True
                        #                        o_doctor[o] = doctors[o_dict[o][o_order[o]]]
                        #                        o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 5
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
                            fixed_result[o][o_fixed_order[o]].append(r_time_max)
                            C_time = int(dict_chaxun[o + 1][o_fixed_order[o]][4])
                        else:
                            result[o][o_order[o]].append(r_time_max)
                            C_time = c_time[o_dict[o][o_order[o]]]
                        o_c_time[o] = C_time

                elif o_empty_state[o]:
                    if o_doctor_conflict[o] and (o_doctor == doctors[o_dict[o][o_order[o]]]).sum() == 0:
                        if o_fixed_order[o] < o_fixed_num[o]:  # 如果现在没有医生冲突还要再判断一下跟固定手术有没有冲突
                            O_oc_time = o_time[o_dict[o][o_order[o]]] + c_time[o_dict[o][o_order[o]]]
                            if O_oc_time > int(dict_chaxun[o + 1][o_fixed_order[o]][1]) - t * 5:
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
        #                o_empty_time[o] += 5

        return o_total_time, o_total_r_time, o_total_empty_time, overtime_work, result, fixed_result, o_c_time

    def _get_list_(self, num, result, fixed_result, ARRAY, list_clean, list_operation, dict_for_xunhuan, list_start,
                   dict_for_result):
        # 分析传回数据
        # result--dict, e.g.
        # {1: [[0, 0,  60, 35, 20], [4, 600, 45, 0, 20]], 1: [[1, 40, 0, 20], [3, 30, 10, 20]]}
        #        data['复苏时间'] = pd.Series(index_sleepy)
        #        data['清洁时间'] = list_clean
        #        data['手术开始时间'] = cunchu
        #        data['手术室编码'] = index_or
        # temple_index_or = np.zeros((num, 1))
        index_or = np.zeros((num, 1), dtype=np.int)
        #        list_clean = np.zeros((num, 1))
        list_sleepy_1 = np.zeros((num, 1))
        #        list_operation = np.zeros((num, 1))
        list_start_1 = np.array(['10:00'] * num)  # print(cunchu)输出cunchu值
        # for index_1, value_1 in dict_for_xunhuan.items():
        #     print('index_1, value_1:', index_1, value_1)
        for i in range(len(result)):
            a = result[i]            # 取第一个手术室
            pu = len(a)              # 该手术室有几台手术
            for j in range(pu):      # 对第一台手术进行判断
            #    print('a[j][0]:', a[j][0])
                bp = ARRAY[a[j][0]]  # 默认ARRAY是一个list,bp是此时次级的真实index
            #    print('bp:', bp)
                for index, value in dict_for_result.items():
            #        print('index,value:', index, value)
                    flag = 1
                    if bp == value:
                        bp = index
            #            print('bp:', bp)
                        for index_1, value_1 in dict_for_xunhuan.items():
                            if bp == value_1[1]:
                                index_or[bp] = value_1[0]
                                flag = 0
                                break
                        if flag == 1:
                            index_or[bp] = (i + 1)
            #            print(bp, index_or[bp])
                        list_sleepy_1[bp] = a[j][3]  # 存入复苏时间
                        list_operation[bp] = a[j][2]  # 存入手术时间
                        list_clean[bp] = a[j][4]  # 存入清洁时间
                        sum_1 = a[j][1]
                        hour = int((sum_1+self.morning_time) / 60)  # 对它进行求和
                        min = int((sum_1+self.morning_time) % 60)  # 转为hour和min
                        if (min < 10):  # 转为hour:min
                            true_sum_1 = ("{}:0{}").format(hour, min)
                        else:
                            true_sum_1 = ("{}:{}").format(hour, min)
                        list_start_1[bp] = true_sum_1  # cunchu中放的是time//cunchu是一个列表
                        break
        for index, value in fixed_result.items():
            b = fixed_result[index]  # 取第一个手术室
            px = len(b)
            for j in range(px):
                bp = b[j][0]
                index_or[bp] = (index + 1)  # 存入手术室编码
                list_sleepy_1[bp] = b[j][3]  # 存入复苏时间
                list_operation[bp] = b[j][2]  # 存入手术时间
                list_clean[bp] = b[j][4]  # 存入清洁时间
                list_start_1[bp] = list_start[bp]  # cunchu中放的是time//cunchu是一个列表
        return index_or, list_clean, list_sleepy_1, list_start_1
