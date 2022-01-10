import pandas as pd
import numpy as np

# 在这里把工况文件路径粘进去
data = pd.read_excel('/Users/xuchangmao/Desktop/工作/油耗行为分析/标准工况/标准模版/wltc工况.xlsx')


# 对原始数据进行处理

def calc_values(df):
    """计算距离、加速度、v*a"""
    # 计算距离
    df['d'] = df['车速'].div(3.6)
    # 计算加速度
    df['v_after'] = df['车速'].shift(-1)
    df['v_before'] = df['车速'].shift(1)
    df['a'] = (df['v_after'] - df['v_before']) / (2 * 3.6)
    df.fillna(0, inplace=True)
    df.drop(['v_after', 'v_before'], axis=1, inplace=True)
    # 计算速度和加速度的乘积
    df['va'] = (df['车速'].multiply(df['a'])) / 3.6
    return df


def time_percent(df):  # 计算动力参数所决定的加减速时间比例
    dec_time_ratio = (df.groupby('Running State').size()['decelerate'] / df.groupby('Running State').size().sum()) * 100
    acc_time_ratio = (df.groupby('Running State').size()['accelerate'] / df.groupby('Running State').size().sum()) * 100
    const_time_ratio = (df.groupby('Running State').size()['constant'] / df.groupby('Running State').size().sum()) * 100
    idle_time_ratio = (df.groupby('Running State').size()['idle'] / df.groupby('Running State').size().sum()) * 100
    return dec_time_ratio, acc_time_ratio, const_time_ratio, idle_time_ratio


def distance_percent(df):  # 计算动力参数所决定的加减速里程比例
    dec_distance_ratio = (df.groupby('Running State').sum()['d']['decelerate'] / df.groupby('Running State').sum()[
        'd'].sum()) * 100
    acc_distance_ratio = (df.groupby('Running State').sum()['d']['accelerate'] / df.groupby('Running State').sum()[
        'd'].sum()) * 100
    const_distance_ratio = (df.groupby('Running State').sum()['d']['constant'] / df.groupby('Running State').sum()[
        'd'].sum()) * 100

    idle_distance_ratio = (df.groupby('Running State').sum()['d']['idle'] / df.groupby('Running State').sum()[
        'd'].sum()) * 100
    return dec_distance_ratio, acc_distance_ratio, const_distance_ratio, idle_distance_ratio


def calc_speed_parameter(df):  # 计算平均车速，巡航平均车速，最高车速
    max_speed = df['车速'].max()
    average_speed = df['车速'].mean()
    cruise_average_speed = df.groupby('Running State').mean().loc['constant']['车速']
    return max_speed, average_speed, cruise_average_speed


def calc_acc_parameter(df):  # 计算加速段平均加速度，减速段平均减速度，最大正向加速度，最大减速度
    pos_average_acc = df.groupby('Running State').mean()['a'].loc['accelerate']
    neg_average_acc = df.groupby('Running State').mean()['a'].loc['decelerate']
    max_pos_acc = df.groupby('Running State').max()['a'].loc['accelerate']
    max_neg_acc = df.groupby('Running State').min()['a'].loc['decelerate']
    return pos_average_acc, neg_average_acc, max_pos_acc, max_neg_acc


def calc_region_parameter(region, df):  # 先将行程分为不同的类型，市区市郊高速，然后对每个单独的区间进行Running state的统计
    total_time = df[df['State'] == region]['Running State'].value_counts().sum()
    region_acc_ratio = df[df['State'] == region]['Running State'].value_counts()['accelerate'] / total_time * 100
    region_dec_ratio = df[df['State'] == region]['Running State'].value_counts()['decelerate'] / total_time * 100
    region_cru_ratio = df[df['State'] == region]['Running State'].value_counts()['constant'] / total_time * 100
    if region == 'urban':
        region_idle_ratio = df[df['State'] == region]['Running State'].value_counts()['idle'] / total_time * 100
    else:
        region_idle_ratio = 0
    return region_acc_ratio, region_dec_ratio, region_cru_ratio, region_idle_ratio


def cal_rpa(df):  # 计算rpa的函数，通过输入一个dataframe来对这个dataframe所包含的数据进行计算
    pos_info = df[df['a'] > 0.1]
    rpa = pos_info['va'].sum() / (pos_info['d'].sum())
    return rpa


def calc_region_rpa(region, df):  # 按照市区市郊高速的情况进行rpa的计算
    region_rpa = cal_rpa(df[df['State'] == region])
    return region_rpa


def calc_region_distance(region, df):  # 按照市区市郊高速的情况进行里程的计算
    region_distance = df[df['State'] == region]['d'].sum()
    return region_distance


# 平台数据用这个条件进行区分
# conditions = [
#     (data['车速'] == 0) & (data['发动机转速'] == 0),  # 停车状态  stop
#     (data['车速'] == 0) & (data['发动机转速'] != 0),  # 怠速状态  idle
#     (data['车速'] > 0) & (data['车速'] < 30) & (data['发动机转速'] != 0),  # 市区状态  urban
#     (data['车速'] > 30) & (data['车速'] < 70) & (data['发动机转速'] != 0),  # 市郊状态  sub
#     (data['车速'] > 70) & (data['车速'] < 120) & (data['发动机转速'] != 0),  # 高速状态  motor
# ]
# 标准工况数据用下面这个条件
conditions = [
    (data['车速'] >= 0) & (data['车速'] < 30) & (data['发动机转速'] != 0),  # 市区状态  urban
    (data['车速'] > 30) & (data['车速'] < 70) & (data['发动机转速'] != 0),  # 市郊状态  sub
    (data['车速'] > 70) & (data['车速'] < 120) & (data['发动机转速'] != 0),  # 高速状态  motor
]

values = ['urban', 'sub', 'motor']
data['State'] = np.select(conditions, values)
data = calc_values(data)
# 接下来需要对运行状态进行一个划分，上一个condition是将市区市郊高速怠速等车辆运行状态进行了划分
# 下一个condition是对动力参数，也就是加减速状态上对工况进行区分，按照v，a的情况
condition2 = [
    (data['a'] < -0.15) & (data['车速'] != 0),  # 减速状态  decelerate
    (data['a'] > 0.15) & (data['车速'] != 0),  # 加速状态  accelerate
    (data['a'].abs() < 0.15) & (data['车速'] >= 0.5),  # 匀速状态  constant
    (data['a'].abs() < 0.15) & (data['车速'] <= 0.5)  # 怠速状态  idle
]
values2 = ['decelerate', 'accelerate', 'constant', 'idle']
data['Running State'] = np.select(condition2, values2)

#
# data.fillna(0, inplace=True)
# data = data[2:]
# data = data.reset_index(drop=True)
# # 重新命名
# data.rename(columns={'OBD_Ch4': 'vehicle speed'}, inplace=True)
# data.rename(columns={'OBD_Ch4.2': 'distance per sec'}, inplace=True)
# data.rename(columns={'Tailpipe_NOx_Conc.1': 'nox conc'}, inplace=True)
# data.rename(columns={'PN_Concentration': 'pn conc'}, inplace=True)
# data.rename(columns={'ExhaustVolumeFlowRate_1': 'flowrate'}, inplace=True)
# data.rename(columns={'Tailpipe_CO2_Conc.1': 'co2'}, inplace=True)
# # 数据类型转换为浮点数
# data['vehicle speed'] = data['vehicle speed'].astype(float)
# data['distance per sec'] = data['distance per sec'].astype(float)
# data['nox conc'] = data['nox conc'].astype(float)
# data['pn conc'] = data['pn conc'].astype(float)
# data['flowrate'] = data['flowrate'].astype(float)
# data['co2'] = data['co2'].astype(float)
#
#
# # 下面的3个函数都是对片段进行切割的函数
# def group(L):
#     '''
#     这是一个生成器函数，生成非零片段的区间
#     :param L: 传入的是nonzero处理后的字段，类似【1，2，3，4，5，6】
#     函数的功能就是将123，456，分开提取出来，形成（1，3），（4，6）这样的效果
#     :return: 返回的就是元组的形式
#     '''
#     first = last = L[0]
#     for n in L[1:]:
#         if n - 1 == last:
#             last = n
#         else:
#             yield first, last
#             first = last = n
#     yield first, last
#
#
# def get_segments(vehicle_speed):
#     '''
#     采用nonzero函数，来得到全部非零的片段
#     :param vehicle_speed:输入dataframe中的车速数据
#     :return:返回的是非零的片段
#     '''
#     test_cycle_array = np.array(vehicle_speed)
#     nonzero_index = test_cycle_array.nonzero()
#     nonzero_list = list(nonzero_index[0])
#     segments_group = list(group(nonzero_list))
#     return segments_group
#
#
# def re_get_segments(raw_segments):
#     '''
#     通过get_segments函数得到的是不包含怠速片段的速度片段
#     接下里需要对这样的raw_segments进行处理，将怠速片段纳入
#     :param raw_segments:进行过简单处理的片段列表
#     :return:最终的标准的短行程片段
#     '''
#     new_segments = []
#     raw_segments.insert(0, (0, 0))
#     for i in range(len(raw_segments)):
#         if i != len(raw_segments) - 1:
#             new_segments.append((raw_segments[i][-1], raw_segments[i + 1][-1]))
#         continue
#     new_sequence = []
#     new_sequence.append((new_segments[0][0], new_segments[0][1] + 2))
#     for j in range(1, len(new_segments)):
#         new_sequence.append((new_segments[j][0] + 1, new_segments[j][1] + 2))
#     return new_sequence
#
#
# # 做出3个list用来保存分割好的段行程片段
# urban_list = []
# sub_list = []
# high_list = []
#
#
# def filter_segments(segments):
#     # 按照平均车速进行分类
#     for segment in segments:
#         if (segment[1] - segment[0]) > 10:
#             max_speed = data['vehicle speed'][segment[0]:segment[1]].max()
#             if max_speed > 90:
#                 high_list.append(segment)
#             if 60 < max_speed < 90:
#                 sub_list.append(segment)
#             if max_speed < 60:
#                 urban_list.append(segment)
#
#
# def calc_values(df):
#     """计算距离、加速度、v*a"""
#     # 计算距离
#     df['d'] = df['车速'].div(3.6)
#     # 计算加速度
#     df['v_after'] = df['车速'].shift(-1)
#     df['v_before'] = df['车速'].shift(1)
#     df['a'] = (df['v_after'] - df['v_before']) / (2 * 3.6)
#     df.fillna(0, inplace=True)
#     df.drop(['v_after', 'v_before'], axis=1, inplace=True)
#     # 计算速度和加速度的乘积
#     df['va'] = (df['车速'].multiply(df['a'])) / 3.6
#     return df
#
#
# def cal_rpa(df):  # 计算rpa的函数，通过输入一个dataframe来对这个dataframe所包含的数据进行计算
#     pos_info = df[df['a'] > 0.1]
#     rpa = pos_info['va'].sum() / (pos_info['d'].sum())
#     return rpa
#
#
# def cal_va95(df):  # 计算va95的函数，通过输入一个dataframe来对这个dataframe所包含的数据进行计算
#     pos_info = df[df['a'] > 0.1]
#     vapos95 = np.percentile(pos_info['va'], 95)
#     return vapos95
#
#
# pailiang = input('请输入发动机排量：')
#
#
# # 计算每个点的负荷
# def cal_rl_mess(one_new_sequence):
#     intake_flow = (one_new_sequence['flowrate'] - one_new_sequence['co2']) * 3.6
#     umsrln = one_new_sequence['vehicle speed'] * float(pailiang) / 2578
#     one_new_sequence['engine_load'] = intake_flow / umsrln
#     return one_new_sequence
#
#
# # 通过两个函数进行参数的计算，包括没个点的di,a,va
# data = calc_values(data)
# data = cal_rl_mess(data)
# # 下面是分割行程
# raw_segments = get_segments(data['vehicle speed'])
# segments = re_get_segments(raw_segments)
# filter_segments(segments)
#
#
# # rpa计算函数
# def cal_rpa(one_new_sequence):
#     pos_info = one_new_sequence[one_new_sequence['a'] > 0.1]
#     rpa = pos_info['va'].sum() / (pos_info['d'].sum())
#     return rpa
#
#
# # va95计算函数
# def cal_va95(one_new_sequence):
#     pos_info = one_new_sequence[one_new_sequence['a'] > 0.1]
#     vapos95 = np.percentile(pos_info['va'], 95)
#     return vapos95
#
#
# # nox比排放计算函数
# def cal_nox_emission(one_new_sequence):
#     nox_emission = one_new_sequence['nox conc'].sum() / (one_new_sequence['d'] / 1000).sum()
#     return nox_emission
#
#
# # pn比排放计算函数
# def cal_pn_emission(one_new_sequence):
#     pn_emission = one_new_sequence['pn conc'].sum() / one_new_sequence['d'].sum()
#     return pn_emission
#
#
# # 形成每个片段的信息列表
# urban_segment_rpa_list = []
# urban_segment_va95_list = []
# urban_segment_nox_list = []
# urban_segment_pn_list = []
# urban_segment_index = []
#
# sub_segment_rpa_list = []
# sub_segment_va95_list = []
# sub_segment_nox_list = []
# sub_segment_pn_list = []
# sub_segment_index = []
#
# high_segment_rpa_list = []
# high_segment_va95_list = []
# high_segment_nox_list = []
# high_segment_pn_list = []
# high_segment_index = []
#
# print('有' + str(len(urban_list)) + '个市区片段')
# print('有' + str(len(sub_list)) + '个市郊片段')
# print('有' + str(len(high_list)) + '个高速片段')
#
# for i in range(len(urban_list)):
#     print('第' + str(i) + '个市区片段处理完成')
#     urban_segment = data[urban_list[i][0]:urban_list[i][1]]
#     urban_segment_rpa_list.append(cal_rpa(urban_segment))
#     urban_segment_va95_list.append(cal_va95(urban_segment))
#     urban_segment_nox_list.append(cal_nox_emission(urban_segment))
#     urban_segment_pn_list.append(cal_pn_emission(urban_segment))
#     urban_segment_index.append(urban_list[i])
#     urban_info_data = {
#         '区间序号': urban_segment_index,
#         '相对正加速度': urban_segment_rpa_list,
#         'va95': urban_segment_va95_list,
#         'NOx平均排放': urban_segment_nox_list,
#         'PN平均排放': urban_segment_pn_list
#     }
#     urban_info_data_pd = pd.DataFrame(urban_info_data)
#     urban_info_data_pd.to_excel('市区片段数据.xlsx')
#     urban_segment.to_excel('市区短行程片段-' + str(i) + '.xlsx')
#
# for i in range(len(sub_list)):
#     print('第' + str(i) + '个市郊片段处理完成')
#     sub_segment = data[sub_list[i][0]:sub_list[i][1]]
#     sub_segment_rpa_list.append(cal_rpa(sub_segment))
#     sub_segment_va95_list.append(cal_va95(sub_segment))
#     sub_segment_nox_list.append(cal_nox_emission(sub_segment))
#     sub_segment_pn_list.append(cal_pn_emission(sub_segment))
#     sub_segment_index.append(sub_list[i])
#     sub_info_data = {
#         '区间序号': sub_segment_index,
#         '相对正加速度': sub_segment_rpa_list,
#         'va95': sub_segment_va95_list,
#         'NOx平均排放': sub_segment_nox_list,
#         'PN平均排放': sub_segment_pn_list
#     }
#     sub_info_data_pd = pd.DataFrame(sub_info_data)
#     sub_info_data_pd.to_excel('市郊片段数据.xlsx')
#     sub_segment.to_excel('市郊短行程片段-' + str(i) + '.xlsx')
#
# for i in range(len(high_list)):
#     print('第' + str(i) + '个高速片段处理完成')
#     high_segment = data[high_list[i][0]:high_list[i][1]]
#     high_segment_rpa_list.append(cal_rpa(high_segment))
#     high_segment_va95_list.append(cal_va95(high_segment))
#     high_segment_nox_list.append(cal_nox_emission(high_segment))
#     high_segment_pn_list.append(cal_pn_emission(high_segment))
#     high_segment_index.append(high_list[i])
#     high_info_data = {
#         '区间序号': high_segment_index,
#         '相对正加速度': high_segment_rpa_list,
#         'va95': high_segment_va95_list,
#         'NOx平均排放': high_segment_nox_list,
#         'PN平均排放': high_segment_pn_list
#     }
#     high_info_data_pd = pd.DataFrame(high_info_data)
#     high_info_data_pd.to_excel('高速片段数据.xlsx')
#     high_segment.to_excel('高速短行程片段-' + str(i) + '.xlsx')
#
# data.to_excel('博世计算负荷后数据.xlsx')
# '''
#  以下是新增排放选择部分代码
#  先对上面的片段分割后进行一个统计总结
# 薛工请你将以下的代码片段复制到你的代码中，需要对下面的转速和负荷进行数值的调整
# '''
# # 以下是新增排放选择部分代码
# # 先对上面的片段分割后进行一个统计总结
# print('共有' + str(len(segments)) + '个片段')
# print('市区片段：' + str(len(urban_list)) + '个')
# print('市郊片段：' + str(len(sub_list)) + '个')
# print('高速片段：' + str(len(high_list)) + '个')
#
# print('-------------以下是对高排放片段进行选取-------------')
# # 将需要用到的列，进行数据格式转换，其中OBD_Ch3是转速列
# data['OBD_Ch3'] = data['OBD_Ch3'].astype(float)
# data['engine_load'] = data['engine_load'].astype(float)
# # 一开始初始化一个空的列表，用来保存高排放的片段
# emission_urban_list = []
#
#
# def urban_select(segment_list):
#     for SEGMENT in segment_list:
#         for point in range(SEGMENT[0], SEGMENT[1]):
#             # 这里的2500是指转速，而1.2是指负荷，其中的point是循环每一个工况点，只要其中出现了
#             # 高排放的工况点，就将其提取到emission_urban_list中
#             if (data['OBD_Ch3'][point] > 2500) & (data['engine_load'][point] > 1.2):
#                 emission_urban_list.append(segment)
#         return emission_urban_list
#
#
# emission_sub_list = []
#
#
# def sub_select(segment_list):
#     for SEGMENT in segment_list:
#         for point in range(SEGMENT[0], SEGMENT[1]):
#             if (data['OBD_Ch3'][point] > 2500) & (data['engine_load'][point] > 1.2):
#                 emission_sub_list.append(SEGMENT)
#         return emission_sub_list
#
#
# emission_high_list = []
#
#
# def high_select(segment_list):
#     for SEGMENT in segment_list:
#         for point in range(SEGMENT[0], SEGMENT[1]):
#             if (data['OBD_Ch3'][point] > 2500) & (data['engine_load'][point] > 1.4):
#                 emission_high_list.append(SEGMENT)
#         return emission_high_list
#
#
# '''
# #以下是为了方便对应的找到高排放片段的编号
# #因为上面的过程，最后提取出来的3个列表，其中存储的都是排放区间的时间序号
# #如市区高排放列表，存储的是[(0,100),(390,800)],因此需要找到对应的(0,100)是第几段市区片段
# 就需要下面的结构，通过形成对应的编号映射来提取
# '''
#
# urban_segments_dict = {}
# for index, value in enumerate(urban_list):
#     urban_segments_dict[value] = index
#
# sub_segments_dict = {}
# for index, value in enumerate(sub_list):
#     sub_segments_dict[value] = index
#
# high_segments_dict = {}
# for index, value in enumerate(high_list):
#     high_segments_dict[value] = index
#
# emission_urban_list = urban_select(urban_list)
# emission_sub_list = sub_select(sub_list)
# emission_high_list = high_select(high_list)
#
# '''
# 由于形成的搞排放片段有可能为空，因此需要增加一个if判断逻辑，如果是空值
# 那么就需要显示没有高排放片段
# '''
# if emission_urban_list is None:
#     print('没有市区段高排放片段')
# else:
#     for i in emission_urban_list:
#         if i in urban_segments_dict:
#             print('市区段高排放片段为第' + str(urban_segments_dict[i]) + '个片段')
# if emission_sub_list is None:
#     print('没有市郊段高排放片段')
# else:
#     for i in emission_sub_list:
#         if i in sub_segments_dict:
#             print('市郊段高排放片段为第' + str(sub_segments_dict[i]) + '个片段')
# if emission_high_list is None:
#     print('没有高速段高排放片段')
# else:
#     for i in emission_high_list:
#         if i in high_segments_dict:
#             print('高速段高排放片段为第' + str(high_segments_dict[i]) + '个片段')
# print('-------------高排放片段选择完成-------------')

whole_speed_list = list(calc_speed_parameter(data))  # 整体的速度参数信息
urban_speed_list = list(calc_speed_parameter(data[data['State'] == 'urban']))  # 市区的速度参数信息
sub_speed_list = list(calc_speed_parameter(data[data['State'] == 'sub']))  # 市郊的速度参数信息
motor_speed_list = list(calc_speed_parameter(data[data['State'] == 'motor']))  # 高速的速度参数信息

speed_info_pd = pd.DataFrame({'整体': whole_speed_list,
                              '市区': urban_speed_list,
                              '市郊': sub_speed_list,
                              '高速': motor_speed_list}, index=['最高车速', '平均车速', '巡航平均车速'])

distance_ratio = list(distance_percent(data))  # 整体中，加减速段的里程分配
# urban_distance_ratio=list(distance_percent(data[data['State']=='urban']))
# sub_distance_ratio=list(distance_percent(data[data['State']=='sub']))
# motor_distance_ratio=list(distance_percent(data[data['State']=='motor']))

time_ratio = list(time_percent(data))  # 整体中，加减速段的时间分配

acc_info = calc_acc_parameter(data)  # 整体中，加速度的信息
urban_acc_info = calc_acc_parameter(data[data['State'] == 'urban'])  # 整体中，加速度的信息
sub_acc_info = calc_acc_parameter(data[data['State'] == 'sub'])  # 整体中，加速度的信息
motor_acc_info = calc_acc_parameter(data[data['State'] == 'motor'])  # 整体中，加速度的信息

acc_info_pd = pd.DataFrame({'整体': acc_info,
                            '市区': urban_acc_info,
                            '市郊': sub_acc_info,
                            '高速': motor_acc_info}, index=['加速段平均加速度', '减速段平均减速度', '最大正向加速度', '最大减速度'])

urban_region_info = calc_region_parameter('urban', data)  # 整体中，加速度的信息
sub_region_info = calc_region_parameter('sub', data)  # 整体中，加速度的信息
motor_region_info = calc_region_parameter('motor', data)  # 整体中，加速度的信息
region_info_pd = pd.DataFrame({'市区': urban_region_info,
                               '市郊': sub_region_info,
                               '高速': motor_region_info}, index=['加速占比', '减速占比', '巡航占比', '怠速占比'])

rpa_list = [calc_region_rpa('urban', data), calc_region_rpa('sub', data), calc_region_rpa('motor', data)]
distance_list = [calc_region_distance('urban', data), calc_region_distance('sub', data),
                 calc_region_distance('motor', data)]
average_speed_list = [urban_speed_list[1], sub_speed_list[1], motor_speed_list[1]]
rpa_info_pd = pd.DataFrame({'平均车速': average_speed_list,
                            'rpa': rpa_list,
                            '里程': distance_list}, index=['市区', '市郊', '高速'])
