"""
作者：lwz
日期：2019/7/29
功能：算法函数//重要函数//AG算法核心
"""
# -*- coding: utf-8 -*-
import time
import numpy as np
import geatpy as ea            # 导入geatpy库

class Algorithm(ea.Algorithm):
    def __init__(self, problem, population, id_trace, n_x):
        self.name = 'fxxk'         # 算法名称
        self.problem = problem
        self.population = population
        self.selFunc = 'tour'  # 锦标赛选择算子
        self.n_x = n_x
        if population.Encoding == 'P':
            self.recFunc = 'xovpmx' # 部分匹配交叉
            self.mutFunc = 'mutinv' # 染色体片段互换变异
        else:
            self.recFunc = 'xovdp' # 两点交叉
            if population.Encoding == 'BG':
                self.mutFunc = 'mutbin' # 二进制变异
            elif population.Encoding == 'RI':
                self.mutFunc = 'mutbga' # breeder GA中的变异算子
            else:
                raise RuntimeError('编码方式必须为''BG''、''RI''或''P''.')

        self.pc = 0.8                 # 重组概率
        self.pm = 0.8                 # 变异概率
        self.drawing = 0          # 绘图
        self.ax = None              # 存储上一桢动画
        self.passTime = 0           # 记录用时
        self.id_trace = id_trace    #记录id_trace的值

    def stat(self, population, id_1):     # 用于分析记录
        # 进行进化记录
        feasible = np.where(np.all(population.CV <= 0, 1))[0]  # 找到可行解的下标 np.all返回T/F,对T的下标进行记录
        if len(feasible) > 0:
            # 若可行解的个数超过0的话，那么
            # 将可行解取出来，是tempPop
            tempPop = population[feasible]
            id_1_1 = id_1[feasible]
            bestIdx = np.argmax(tempPop.FitnV)  # 获取最优个体的下标
            # 可行解的适应度的下标
            self.obj_trace[self.currentGen, 0] = np.sum(tempPop.ObjV) / tempPop.sizes  # 记录种群个体平均目标函数值
            # print('obj_trace:', self.obj_trace)
            self.obj_trace[self.currentGen, 1] = tempPop.ObjV[bestIdx]                 # 记录当代目标函数的最优值
            self.var_trace[self.currentGen, :] = tempPop.Phen[bestIdx, :]              # 记录当代最优的决策变量值
            self.id_trace[self.currentGen, :] = id_1_1[bestIdx, :]              # 记录当代最优的决策变量值
            self.forgetCount = 0  # “遗忘策略”计数器清零
            self.passTime += time.time() - self.timeSlot  # 更新用时记录
            if self.drawing == 2:
                self.ax = ea.soeaplot(self.obj_trace[:, [1]], '种群最优个体目标函数值', False, self.ax,
                                      self.currentGen)  # 绘制动态图
            self.timeSlot = time.time()  # 更新时间戳
        else:
            self.currentGen -= 1   # 忽略这一代
            self.forgetCount += 1  # “遗忘策略”计数器加1

    def terminated(self, population, id_1): # 判断是否终止进化
        if self.currentGen < self.MAXGEN or self.forgetCount >= 10 * self.MAXGEN:  # 如果有当前子代小于总迭代次数
            # 或者有遗忘次数大于等于总迭代次数的10倍，那么就对当前种群进行分析。
            self.stat(population, id_1)         # 分析记录当代种群的数据
            self.currentGen += 1          # 进化代数+1  进化代数+1
            return False                  # 返回F
        else:
            return True                   # 返回T，表示终止进化
    # 提取出list列表

    def run(self):
        # ==========================初始化配置===========================
        population = self.population      # population是传入的初始化种群
        NIND = population.sizes           # NIND表示的是种群数目
        NVAR = self.problem.Dim           # 得到决策变量的个数
        self.obj_trace = (np.zeros((self.MAXGEN, 2)) * np.nan)       # 定义目标函数值记录器，初始值为nan
        # 目标函数记录器(2列)
        self.var_trace = (np.zeros((self.MAXGEN, NVAR)) * np.nan)    # 定义变量记录器，记录决策变量值，初始值为nan
        # id_trace用于记录每一代训练得出的最佳子种群的ARRAY
        self.forgetCount = 0    # “遗忘策略”计数器，用于记录连续出现最优个体不是可行个体的代数/"遗忘策略"

        x_hang = np.arange(0, NVAR)
        id_1 = np.array([x_hang] * NIND)
        for i in range(NIND):
            np.random.shuffle(id_1[i])
        #id_1 = np.random.randint(0, NVAR, (NIND, NVAR))              # 对index记录的矩阵进行初始化
        # ===========================准备进化============================
        self.timeSlot = time.time()                                  # 开始计时
        if population.Chrom is None:
            # 如果Chrom是空的话，那么就初始化//Chrom为待解码矩阵
            # population.ObjV = None
            # population.FitnV = np.ones((self.sizes,1))
            # population.CV = np.zeros((self.sizes,1))
            # population.Phen =
            A = int(NVAR/self.n_x)
            e = np.zeros((NIND, NVAR), dtype=np.int)
            for i in range(NIND):
                c = np.arange(0, NVAR)
                batch_size = A
                for j in range(self.n_x):
                    slice_1 = np.random.choice(c.shape[0], batch_size)
                    d = c[slice_1]
                    e[i][d] = (j + 1)
                    c = np.delete(c, slice_1)
                e[i][c] = np.random.randint(1, self.n_x)
            population.Chrom = e
            population.Phen = e
            population.FitnV = np.ones((NVAR, 1))
            population.CV = np.zeros((NVAR, 1))
            population.ObjV = None

            # population.initChrom(NIND)     # 初始化种群染色体矩阵（内含染色体解码，详见Population类的源码）
            # print('初始化Chorm矩阵：', population.Chrom)
            # print('初始化Phen矩阵：', population.Phen)
#        population.ObjV, population.CV = self.problem.aim_chuli(population.Phen, , population.CV) # 计算种群的目标函数值
        population.ObjV, population.CV = self.problem.aim_chuli(population.Phen, id_1)            # 计算种群的目标函数值

        # id_1是保留shape的形状
        # 计算种群的目标函数，输入的是CV和Phen表现矩阵
        population.FitnV = ea.scaling(self.problem.maxormins * population.ObjV, population.CV)  # 计算适应度
        # 自动计算适应度
        #print('种群初始化-2时的适应度:', population.FitnV)
        self.evalsNum = population.sizes     # 记录评价次数
        # 记录评价次数
        # ===========================开始进化============================
        self.currentGen = 0
        # 开始进化，设置currentGen为0
        while self.terminated(population, id_1) == False:
            # 若需要继续进化，那么有
            bestIdx = np.argmax(population.FitnV, axis = 0)        # 得到当代的最优个体的索引, 设置axis=0可使得返回一个向量
            studPop = population[np.tile(bestIdx, (NIND//2))]      # 复制最优个体NIND//2份，组成一个“种马种群”
            restPop = population[np.where(np.array(range(NIND)) != bestIdx)[0]]                   # 得到除去精英个体外其它个体组成的种群
            # 选择个体，以便后面与种马种群进行交配
            tempPop = restPop[ea.selecting(self.selFunc, restPop.FitnV, (NIND - studPop.sizes))]
            # 将种马种群与选择出来的个体进行合并
            population = studPop + tempPop
            # 进行进化操作
            population.Chrom = ea.recombin(self.recFunc, population.Chrom, self.pc)                  # 重组
            population.Chrom, id_1 = self.problem.intersect(population.Chrom, id_1, self.pc)         # 重组
            # population.Chrom = ea.mutate(self.mutFunc, population.Encoding, population.Chrom, population.Field, self.pm)
            # 求进化后个体的目标函数值//变异
            # print('进化中的Chorm矩阵：', population.Chrom)
            # print('进化中的Phen矩阵：', population.Phen)
            population.Phen = population.decoding()                                  # 染色体解码
            # population.ObjV, population.CV = self.problem.aimFuc(population.Phen, population.CV)
            population.ObjV, population.CV = self.problem.aim_chuli(population.Phen, id_1)                   # 计算种群的目标函数值
            # population.ObjV, population.CV = self.problem.aim_chuli(population.Chrom, id_1)
            self.evalsNum += population.sizes                                        # 更新评价次数
            population.FitnV = ea.scaling(self.problem.maxormins * population.ObjV, population.CV)           # 计算适应度
        # 处理进化记录器
        delIdx = np.where(np.isnan(self.obj_trace))[0]
        self.obj_trace = np.delete(self.obj_trace, delIdx, 0)
        self.var_trace = np.delete(self.var_trace, delIdx, 0)
        # 对id的trace进行记录
        self.id_trace = np.delete(self.id_trace, delIdx, 0)

       # self.var_trace = np.delete(self.var_trace, delIdx, 0)                       #记录trace
        if self.obj_trace.shape[0] == 0:
            raise RuntimeError('error: No feasible solution. (有效进化代数为0，没找到可行解。)')
        self.passTime += time.time() - self.timeSlot # 更新用时记录
        # 绘图
        if self.drawing != 0:
            ea.trcplot(self.obj_trace, [['种群个体平均目标函数值', '种群最优个体目标函数值']])
        # 返回最后一代种群、进化记录器、变量记录器以及执行时间

        return [population, self.obj_trace, self.var_trace, self.id_trace]
# 返回最后一代种群/进化记录器/执行时间
