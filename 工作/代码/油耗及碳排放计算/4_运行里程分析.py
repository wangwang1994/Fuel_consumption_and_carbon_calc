import pandas as pd
import numpy as np


def get_distance(test_data):
    v_distance = []  # 用一个list来记录每秒的距离增量
    for i in range(test_data.shape[0] - 1):
        v_distance.append(
            ((test_data['车速'].iloc[i] + test_data['车速'].iloc[i + 1]) / 2) / 3.6)  # 每秒的距离增量是由该秒的前后速度平均进行计算，单位是m
    return sum(v_distance) / 1000  # 最后返回的结果是km的单位


filepath=input('输入数据路径：')
upperfile=input('输入数据上层文件路径：')
month=input('输入月份：')
df = pd.read_excel(filepath,sheet_name=None)
data = pd.concat(df.values())
data['日期'] = pd.to_datetime(data['时间']).dt.date
data['是否处于怠速'] = np.where((data['车速'] == 0) & (data['发动机转速'] != 0), 1, 0)
data['是否运行'] = np.where(data['发动机转速'] != 0, 1, 0)
data['是否市区'] = np.where((data['车速'] <= 30) & (data['发动机转速'] != 0), 1, 0)
data['是否市郊'] = np.where((data['车速'] > 30) & (data['车速'] <= 70) & (data['发动机转速'] != 0), 1, 0)
data['是否高速'] = np.where((data['车速'] > 70) & (data['车速'] <= 120) & (data['发动机转速'] != 0), 1, 0)
data['是否超速'] = np.where((data['车速'] > 120) & (data['发动机转速'] != 0), 1, 0)

# conditions = [
#     (data['车速'] <= 30) & (data['发动机转速'] != 0),
#     (data['车速'] > 30) & (data['车速'] <= 70) & (data['发动机转速'] != 0),
#     (data['车速'] > 70) & (data['车速'] <= 120) & (data['发动机转速'] != 0),
#     (data['车速'] > 120) & (data['发动机转速'] != 0)
# ]
#
# values = ['市区', '市郊', '高速', '超速']
# data['速度区间'] = np.select(conditions, values)

date_list = [x for _, x in data.groupby(data['日期'])]
list1 = []  # 日期信息
list2 = []  # 运行时间
list3 = []  # 运行里程
list4 = []  # 怠速比例
list5 = []  # 市区比例
list6 = []  # 市郊比例
list7 = []  # 高速比例
list8 = []  # 超速比例
for df in date_list:
    # 通过对每个df进行计算，datelist中存储的是按照日期进行分类以后的
    list1.append(str(df['日期'].iloc[0]))  # 日期信息增加入列表中
    if 1 not in df['是否运行'].value_counts().index.to_list():
        df_working_time=0
    else:
        df_working_time = round(df['是否运行'].value_counts().loc[1] / 3600, 2)

    list2.append(df_working_time)  # 运行时间增加入列表
    df_distance = get_distance(df)

    list3.append(round(df_distance,2))  # 运行里程增加入列表中
    # 怠速比例计算
    list4.append(round(df['是否处于怠速'].sum() / df['是否处于怠速'].value_counts().sum() * 100, 2))  # 怠速比例计算,百分比
    # 市区比例计算
    if 1 not in df['是否运行'].value_counts().index.to_list() or 1 not in df['是否市区'].value_counts().index.to_list():
        list5.append(0)
    else:
        list5.append(round(df['是否市区'].value_counts().loc[1] / df['是否运行'].value_counts().loc[1] * 100, 2))
    # 市郊比例计算
    if 1 not in df['是否运行'].value_counts().index.to_list() or 1 not in df['是否市郊'].value_counts().index.to_list():
        list6.append(0)
    else:
        list6.append(round(df['是否市郊'].value_counts().loc[1] / df['是否运行'].value_counts().loc[1] * 100, 2))
    # 高速比例计算
    if 1 not in df['是否高速'].value_counts().index.to_list() or 1 not in df['是否运行'].value_counts().index.to_list():
        list7.append(0)
    else:
        list7.append(round(df['是否高速'].value_counts().loc[1] / df['是否运行'].value_counts().loc[1] * 100, 2))
    # 超速比例计算
    if 1 not in df['是否超速'].value_counts().index.to_list() or 1 not in df['是否运行'].value_counts().index.to_list():
        list8.append(0)
    else:
        list8.append(round(df['是否超速'].value_counts().loc[1] / df['是否运行'].value_counts().loc[1] * 100, 2))

    print('完成' + str(df['日期'].iloc[0]) + '日的数据计算')
info_pd = pd.DataFrame(
    {'日期': list1,
     '运行时间(h)': list2,
     '运行里程(km)': list3,
     '怠速比例(%)': list4,
     '市区比例(%)': list5,
     '市郊比例(%)': list6,
     '高速比例(%)': list7,
     '超速比例(%)': list8
     })

info_pd.to_excel(upperfile+'/'+str(month)+'月信息.xlsx')




