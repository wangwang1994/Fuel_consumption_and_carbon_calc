import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

filepath = input('请输入平台数据路径：')
data = pd.read_excel(filepath)


def moving_average(interval, window_size):
    window = np.ones(int(window_size)) / float(window_size)
    return np.convolve(interval, window, 'same')  # numpy的卷积函数


x = data['油箱液位'].index.to_list()
y_fuel = data['油箱液位'].to_list()  # 初始的油箱液位数据，list格式
y_fuel_array = np.array(y_fuel)  # 滤波处理之前需要转换为array
# y_new_fuel = moving_average(interval=y_fuel_array, window_size=10000)  # 初始的油箱液位数据进行滤波处理
y_fuel_pd = pd.DataFrame(y_fuel_array)  # 原始的油箱液位，转换为dataframe
y_new_fuel_pd = pd.DataFrame(moving_average(interval=y_fuel_array, window_size=10000))  # 处理后的油箱液位，转换为dataframe

fuel_diff = y_new_fuel_pd - y_new_fuel_pd.shift(7200)  # 处理后的数据进行差分处理，300秒差分
fuel_point = fuel_diff[fuel_diff[0] > 10][0]  # 变化量大于10%的点定位为加油点
fuel_index = fuel_point.index.to_frame()  # 找到加油点的index，也就是时间
fuel_index_diff = fuel_index - fuel_index.shift(1)  # 加油点index的差分，用来寻找端点index
# 如果差分大于半天的秒数，那么就认为发生了加油行为，
fuel_cycle = fuel_index_diff[fuel_index_diff[0] > 3600][0].index.to_list()  # 用这个list来保留周期的信息，list中就是周期端点

dfs = np.split(data, fuel_cycle, axis=0)

for i in range(len(dfs)):
    dfs[i].to_excel(os.path.abspath(os.path.dirname(filepath)) + os.sep + str(i) + '号周期数据.xlsx')

fig, ax = plt.subplots()
ax.plot(y_new_fuel_pd)
ax.set_title('Fuel Cycle Recognition ', fontsize=15)
ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Fuel level', fontsize=12)
for index, xc in enumerate(fuel_cycle):
    plt.axvline(x=xc, color='red')
    ax.text(xc, 100, str(index)+'th cycle', style='italic',fontsize=8)
plt.savefig(os.path.abspath(os.path.dirname(filepath)) + os.sep + '油箱液位变化图.png')
# y_urea = data['反应剂余量'].to_list()  # 初始的尿素液位数据，list格式
# y_urea_array = np.array(y_urea)  # 滤波处理之前需要转换为array
# y_new_urea = moving_average(interval=y_urea_array, window_size=2000)  # 初始的尿素液位数据进行滤波处理
# y_urea_pd = pd.DataFrame(y_urea_array)  # 原始的尿素液位，转换为dataframe
# y_new_urea_pd = pd.DataFrame(y_new_urea)  # 处理后的尿素液位，转换为dataframe

# urea_diff = y_new_urea_pd - y_new_urea_pd.shift(600)  # 处理后的数据进行差分处理，20秒差分
# urea_point = urea_diff[urea_diff[0] > 15][0]  # 变化量大于30%的点定位为加油点
# urea_index = urea_point.index.to_frame()  # 找到加油点的index，也就是时间
# urea_index_diff = urea_index - urea_index.shift(1)  # 加油点index的差分，用来寻找端点index
# # 如果差分大于半天的秒数，那么就认为发生了加油行为，
# urea_cycle = urea_index_diff[urea_index_diff[0] > 13200][0].index.to_list()  # 用这个list来保留周期的信息，list中就是周期端点
