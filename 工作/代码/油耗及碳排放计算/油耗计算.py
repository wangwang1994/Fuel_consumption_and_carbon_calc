import pandas as pd
import scipy
from scipy.integrate import simps  # 用于计算积分
import numpy as np
import os

file_path = '/Users/xuchangmao/Desktop/工作/排放模型/油耗分析/周期数据'
file_list = os.listdir(file_path)  # 读取文件路径下的所有文件
file_list = sorted(file_list, key=lambda string: string[0])  # 按照周期的先后对list内的文件名进行排序，按首字母0，1，2

data_list = []
# for file in range():
#
#     data = pd.read_excel(file_path)
for file_name in file_list:
    data_list.append(pd.read_excel(file_path + '/' + file_name))


def get_distance(test_data):
    v_distance = []  # 用一个list来记录每秒的距离增量
    for i in range(test_data.shape[0] - 1):
        v_distance.append(
            ((test_data['车速'].iloc[i] + test_data['车速'].iloc[i + 1]) / 2) / 3.6)  # 每秒的距离增量是由该秒的前后速度平均进行计算，单位是m
    return sum(v_distance) / 1000  # 最后返回的结果是km的单位


def get_fuel_cons(test_data):
    """
    :param test_data:传入需要计算的dataframe
    :return: 输出一个油耗的integrals
    """
    fuel_rate = test_data['发动机燃料流量'] / 3600  # 将发动机燃料流量转换为l/s的单位，进行后面的积分
    index = fuel_rate.index.tolist()
    index = np.array(index)
    # index相当于是时间序列，下面要转换为小时h
    fuel_rate_np = np.array(fuel_rate)
    y = fuel_rate_np
    x = index
    integrals = []
    for i in range(len(y)):  # 计算梯形的面积，面积其实就是所消耗的燃油量
        integrals.append(scipy.integrate.trapz(y[:i + 1], x[:i + 1]))
    return integrals[-1]  # integrals是累积的燃油消耗量


# data['日期'] = pd.to_datetime(data['时间']).dt.date
# date_list = [x for _, x in data.groupby(data['日期'])]
#
fuel_list = []
#
for df in data_list:
    df_distance = get_distance(df)
    df_fuel_cons = get_fuel_cons(df)
    fuel_list.append(df_fuel_cons / (df_distance / 100))
#
# fuel_list = []
# df = data
# df_distance = get_distance(df)
# df_fuel_cons = get_fuel_cons(df)
# fuel_list.append(df_fuel_cons / (df_distance / 100))
