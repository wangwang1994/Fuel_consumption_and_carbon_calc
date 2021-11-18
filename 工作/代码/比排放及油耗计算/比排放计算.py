import numpy as np
import scipy
from scipy.integrate import simps  # 用于计算积分
import pandas as pd

data = pd.read_excel('/Users/xuchangmao/Desktop/工作/排放模型/比排放及油耗计算/原始数据/高排放车原始数据/8月15-8月16日数据---清洗后数据.xlsx')
data['日期'] = pd.to_datetime(data['时间']).dt.date  # 通过先转换为datetime类型，然后再提取出date参数，保留日期
date_list = [x for _, x in data.groupby(data['日期'])]  # 通过一个list来保留划分为不同日期数据的dataframe
max_torque = 1000


def get_nox_curve(test_data):
    nox_integrals = []
    test_data['发动机燃料流量'] = test_data['发动机燃料流量'].replace('无效', 0)
    test_data['发动机燃料流量'] = test_data['发动机燃料流量'].astype(float)
    fuel_mass_flow = test_data['发动机燃料流量']

    fuel_mass_flow = 0.84 * fuel_mass_flow / 3600

    air_mass_flow = test_data['进气量']

    air_mass_flow = air_mass_flow / 3600
    total_mass_flow = air_mass_flow + fuel_mass_flow

    test_data['SCR下游NOx传感器输出'] = test_data['SCR下游NOx传感器输出'].replace('无效', 0)
    nox_conc = test_data['SCR下游NOx传感器输出']

    nox_conc = nox_conc.astype(float)
    nox_flow = 0.001587 * nox_conc * total_mass_flow

    y = nox_flow
    index = nox_flow.index.tolist()
    index = np.array(index)
    x = index
    nox_integrals = []
    for i in range(len(y)):
        nox_integrals.append(scipy.integrate.trapz(y[:i + 1], x[:i + 1]))
    return nox_integrals[-1] * 1000  # 单位是mg，最后的排放量


def get_work_curve(test_data):
    '''
    :param test_data:传入需要计算的dataframe
    :return: 输出一个累积功曲线的integrals
    '''
    torque_data = test_data['发动机净输出扭矩']

    friction_data = test_data['摩擦扭矩']

    zhuansu_data = test_data['发动机转速']

    torque_percent = torque_data - friction_data
    torque_percent[torque_percent < 0] = 0
    cal_w = torque_percent * max_torque * 0.01 * zhuansu_data / 9550
    # 计算发动机的实时功率，数据中的输出扭矩减去摩擦扭矩才是实际扭矩百分比，对不同的车要乘以其标称扭矩，得到N*m单位的实际扭矩
    index = cal_w.index.tolist()
    index = np.array(index)
    # index相当于是时间序列，下面要转换为小时h
    cal_w_np = np.array(cal_w)
    y = cal_w_np
    x = index / 3600  # 构造一个等差数列数组，作为横轴取值，单位为h，小时
    integrals = []
    for i in range(len(y)):  # 计算梯形的面积，面积其实就是所作的功，由于是累加，所以是切片"i+1"
        integrals.append(scipy.integrate.trapz(y[:i + 1], x[:i + 1]))
    return integrals[-1]  # integrals是累积功，而后面的是每秒的功率


def get_distance(test_data):
    v_distance = []  # 用一个list来记录每秒的距离增量
    for i in range(test_data.shape[0] - 1):
        v_distance.append(
            ((test_data['车速'].iloc[i] + test_data['车速'].iloc[i + 1]) / 2) / 3.6)  # 每秒的距离增量是由该秒的前后速度平均进行计算，单位是m
    return sum(v_distance) / 1000  # 最后返回的结果是km的单位


# 构建3个list用来分别存储时间，比排放信息，最后组合形成一个总的dataframe
list1 = []
list2 = []
list3 = []
list4 = []
list5 = []
list6 = []
for df in date_list:
    # 通过对每个df进行计算，datelist中存储的是按照日期进行分类以后的
    df_emission = get_nox_curve(df)
    df_distance = get_distance(df)
    df_work = get_work_curve(df)
    list1.append(str(df['日期'].iloc[0]))
    list2.append(df_emission / df_work)
    list3.append(df_emission / df_distance)
    list4.append(df_emission)
    list5.append(df_distance)
    list6.append(df_work)
    print('完成' + str(df['日期'].iloc[0]) + '日的数据计算')

info_pd = pd.DataFrame(
    {'日期': list1,
     '比排放（mg/kw*h）': list2,
     '比排放（mg/km）': list3,
     '排放量（mg）': list4,
     '行驶里程（km）': list5,
     '累积功（kw*h）': list6,
     })
