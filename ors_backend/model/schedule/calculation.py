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
        list_patientID = np.array(self.data['就诊号'])[:]
        list_doctID = np.array(self.data['医生'])[:]
        list_sleepy = np.array(self.data['麻醉方式'])[:]
        list_operation = np.array(self.data['time'])[:]
        list_clean = np.array(self.data['手术级别'])[:]
        list_start = np.array(self.data['开始时间'])[:]
        list_index_or = np.array(self.data['手术室号'])[:]
#         list_patientID = np.array(self.data[(np.where(self.data == '就诊号')[1][0])])[1:]
#         list_doctID = np.array(self.data[(np.where(self.data == '医生名称')[1][0])])[1:]
#         list_sleepy = np.array(self.data[(np.where(self.data == '麻醉方式')[1][0])])[1:]
#         list_operation = np.array(self.data[(np.where(self.data == '手术时长(分钟)')[1][0])])[1:]
#         list_operation = (np.array(self.data[(np.where(self.data == '手术时长(分钟)')[1][0])])[1:]).astype(np.float64)
        list_operation = (np.ceil(list_operation / 5) * 5).astype(np.int)
        # list_clean = np.array(self.data[(np.where(self.data == '手术级别')[1][0])])[1:]
        list_sleepy.reshape((num, 1))
        for i in range(num):
            b = list_sleepy[i]
            if (b == '全身麻醉' or b == '全身麻醉(喉罩)'):
                tb = 60
            else:
                tb = 0
            list_sleepy[i] = tb
        list_clean.reshape((num, 1))
        for i in range(num):
            a = list_clean[i]
            if a == '1.0':
                tp = 10
            elif a == '2.0' or a == '3.0':
                tp = 20
            else:
                tp = 30
            list_clean[i] = tp
        c = np.vstack((list_doctID, list_patientID, list_operation, list_sleepy, list_clean, list_start, list_index_or))
        key = [i + 1 for i in range(num)]
        e = []   #存储了所有信息的列表，每一个列表的内容是一个字典
        for i in range(num):
            f = dict()
            d = c[:, i]
            f[key[i]] = d
            e.append(f)
        return list_doctID, list_patientID, list_operation, list_sleepy, list_clean, list_start, list_index_or, e

    def _best_result_(self, chrom, Num, t_s, list_doctID, r_time, o_time, c_time):
        """
        Created on Mon Jul 29 09:55:36 2019
        @author: lxw
        """
        """模拟手术室整个工作流程，每5分钟检查一次，得到最终优化目标结果"""
        # import numpy as np
        # n_o = 3
        # n_r = 2
        # chrom = np.array([1, 2, 3, 2, 1, 3])
        # o_time = np.array([60, 40, 35, 30, 45, 50])
        # c_time = np.array([20, 20, 20, 20, 20, 20])
        # r_time = np.array([60, 60, 60, 60, 60, 60])
        # num是病人数量

        # n_o为手术室数量，n_r为复苏室数量, chrom为染色体[1,3,2]表示第一台
        # 手术在1号手术室在1号手术室内做，o_time[30,100,60]表示第一台手术时长30分钟，
        # c_time表示清洁时长，r_time表示复苏时长（0或自定义最小复苏时长默认为60min）
        r_time_max = self.t_s  # 最小复苏时长
        o_o_state = np.zeros(self.n_x, dtype=np.bool)  # 手术室是否进行手术
        o_c_state = np.zeros(self.n_x, dtype=np.bool)  # 手术室是否进行清洁
        o_r_state = np.zeros(self.n_x, dtype=np.bool)  # 手术室是否进行复苏
        o_end_state = np.zeros(self.n_x, dtype=np.bool)  # 手术室是否结束工作
        r_state = np.zeros(self.n_y, dtype=int)  # 复苏室内状态，0表示空置，大于0表示在使用
#        r_empty_num = self.n_y  # 有几个复苏室空床位
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
        work_time = (self.afternoon_time - self.morning_time) * 60 // 5  # 日常工作时长有多少个5分钟
        result = {}
        for o in range(self.n_x):
            o_dict[o] = np.where(chrom == o + 1)[0]
            o_len[o] = o_dict[o].shape[0]
            result[o] = []

        for t in range(288):
            # 一天排班最多24小时，每5分钟检查一次
            if o_end_state.sum() == self.n_x:  # 如果所有手术室均结束工作，跳出循环
                break

            r_empty_num = r_state[r_state == 0].size  # 更新复苏室空床位数
            if o_r_state[o_r_state == True].size > 0 and r_empty_num > 0:  # 当复苏室有空床位，又有手术室内复苏
                o_r_time_sort = np.argsort(-o_r_time)  # 早做完手术的优先进入复苏室
                r_state_sort = np.argsort(r_state)
                for r in range(r_empty_num):
                    o_room = o_r_time_sort[r]
                    r_bed = r_state_sort[r]
                    if o_r_time[o_room] == 0:  # 没有还在手术室内复苏的就跳出循环
                        break
                    o_r_state[o_room] = False  # 更改手术室内复苏状态
                    o_total_r_time[o_room] += o_r_time[o_room]
                    o_total_time[o_room] += o_r_time[o_room]
                    result[o_room][o_order[o_room]].append(o_r_time[o_room])
                    r_state[r_bed] = r_time_max - o_r_time[o_room]  # 将剩余的复苏时间填入复苏室
                    o_r_time[o_room] = 0  # 将手术室内复苏时间设为0
                    o_c_state[o_room] = True  # 手术室进入清洁状态
                    o_c_time[o_room] = c_time[o_dict[o_room][o_order[o_room]]]  # 填入需清洁的时间
                    r_empty_num -= 1  # 复苏室空床位数减一
            r_state[r_state > 0] -= 5  # 更新复苏室床位状态，大于0的就减5

            for o in range(self.n_x):
                # 对每个手术室状态进行检查

                if o_end_state[o] == True:  # 如果已结束当天所有工作，进入下一个手术室循环
                    continue

                if o_len[o] == 0:  # 考虑手术室一台手术都没排
                    o_total_empty_time[o] += work_time * 5
                    o_end_state[o] = True
                    continue

                if o_o_state[o] == False and o_c_state[o] == False and o_r_state[o] == False:  # 手术室空闲状态
                    o_o_state[o] = True  # 开始手术
                    o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 5  # 将第i台的手术时长填入减5


                elif o_o_state[o] == True:  # 手术室进行手术状态
                    if o_o_time[o] == 0:
                        o_o_state[o] = False
                        result[o].append([o_dict[o][o_order[o]], o_time[o_dict[o][o_order[o]]]])
                        o_total_time[o] += o_time[o_dict[o][o_order[o]]]  # 将这一台手术时长计入工作总时间
                        if r_time[o_dict[o][o_order[o]]] == 0:  # 若不需要复苏
                            result[o][o_order[o]].append(0)
                            o_c_state[o] = True
                            o_c_time[o] = c_time[o_dict[o][o_order[o]]] - 5
                        else:
                            if r_empty_num == 0:
                                o_r_state[o] = True
                                o_r_time[o] += 5
                            else:
                                result[o][o_order[o]].append(0)
                                r_state[np.where(r_state == 0)[0][0]] += r_time_max - 5
                                r_empty_num -= 1
                                o_c_state[o] = True
                                o_c_time[o] = c_time[o_dict[o][o_order[o]]] - 5
                    else:
                        o_o_time[o] -= 5


                elif o_c_state[o] == True:  # 手术室处于清洁状态
                    if o_c_time[o] == 0:
                        o_total_time[o] += c_time[o_dict[o][o_order[o]]]  # 将这一台手术清洁时间计入手术室工作总时间
                        o_c_state[o] = False
                        result[o][o_order[o]].append(c_time[o_dict[o][o_order[o]]])

                        o_order[o] += 1
                        if o_order[o] < o_len[o]:  # 推入下一台手术
                            o_o_state[o] = True
                            o_o_time[o] = o_time[o_dict[o][o_order[o]]] - 5
                        else:
                            o_end_state[o] = True  # 手术室工作结束
                            if t + 1 < work_time:  # 将闲置时间累加
                                o_total_empty_time[o] += (work_time - t) * 5
                            else:
                                overtime_work[o] += (t - work_time) * 5
                    else:
                        o_c_time[o] -= 5

                elif o_r_state[o] == True:  # 手术室处于复苏状态
                    o_r_time[o] += 5
                    if o_r_time[o] == r_time_max:
                        result[o][o_order[o]].append(r_time_max)
                        o_total_r_time[o] += r_time_max
                        o_total_time[o] += r_time_max
                        o_r_time[o] = 0
                        o_r_state[o] = False
                        o_c_state[o] = True
                        o_c_time[o] = c_time[o_dict[o][o_order[o]]]

        return o_total_time.sum(), o_total_r_time.sum(), o_total_empty_time.sum(), overtime_work.sum(), result

    def _get_list_(self,a):
        key = []
        dic = {}
        key_2 = ['time_of_operation', 'time_of_sleep', 'time_of_clean']
        for i in range(self.n_x):
            c = a[i]
            key.append('手术室{}'.format(i+1))
            x = []
            for j in range(int(len(c) / 3)):
                e = 3 * j
                d = c[e:e + 3]
                f = dict(zip(key_2, d))
                x.append(f)
            dic[key[i]] = x
        return dic

    def _output_date_(self,output_1):
        f = open('output.json', 'w', encoding='utf-8')
        json.dump(output_1, f, ensure_ascii=False, indent=4)
        f.close()




#  def output(self,):
#       return
