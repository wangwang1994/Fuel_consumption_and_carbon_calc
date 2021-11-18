import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt


def detect_outliers(data, threshold=3):
    mean_d = np.mean(data)
    std_d = np.std(data)
    outliers = []
    for y in data:
        z_score = (y - mean_d) / std_d
        if np.abs(z_score) > threshold:
            outliers.append(y)
    return outliers


def data_cleaning(col_name):
    data[col_name]=data[col_name].astype(float)
    col_list = data[col_name].tolist()
    col_diff = [int(col_list[i]) - int(col_list[i + 1]) for i in range(len(col_list) - 1)]  # 形成nox差分序列
    col_error_value = detect_outliers(col_diff, threshold=3)  # 开始进行异常点检测
    col_error_index = []  # 找到异常点的坐标位置
    for value in col_error_value:  # 开始对异常点进行更改，现在的原则是改成上一个点的值
        col_error_index.append(col_diff.index(value))
    for index in col_error_index:
        col_list[index] = col_list[index - 1]
    col_pd = pd.DataFrame(col_list)
    col_pd[col_pd < 0] = 0
    col_list = col_pd.values.tolist()
    col_pd = pd.DataFrame(col_list)
    data[col_name] = col_pd
    return None


file_path = input('请输入平台数据文件路径：')
df = pd.read_excel(file_path, sheet_name=None, index_col=None)
data = pd.concat(df.values())
# 找到文件的上级目录和当前文件名
upper_file, filename = os.path.split(file_path)
base_name = os.path.splitext(filename)[0]  # 去除文件后缀
# 无效值填充
data = data.fillna(0)
data = data.replace('无效', 0)

# 首先先按照时间进行排序，避免出现时间倒序的情况
data = data.sort_values(by='时间')
data.reset_index(drop=True, inplace=True)

# 对下面3列进行处理，如果需要的话可以添加更多的列数
data_cleaning('SCR下游NOx传感器输出')
print('------------SCR下游NOx传感器输出处理完成------------')
data_cleaning('SCR上游NOx传感器输出')
print('------------SCR上游NOx传感器输出处理完成------------')
data_cleaning('车速')
print('------------车速处理完成------------')
print('------------数据清洗处理完成------------')

data_after_path = upper_file + '/' + base_name + '---清洗后数据.xlsx'
data.to_excel(data_after_path)
print('------------数据已保存至' + data_after_path + '------------')

