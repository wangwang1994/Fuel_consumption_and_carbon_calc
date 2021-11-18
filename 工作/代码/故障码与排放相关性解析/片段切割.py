import os
import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt  # 用于画图
import scipy
from scipy.integrate import simps  # 用于计算积分
import seaborn as sns

pd.options.mode.chained_assignment = None


# 下面的3个函数都是对片段进行切割的函数
def group(L):
    '''
    这是一个生成器函数，生成非零片段的区间
    :param L: 传入的是nonzero处理后的字段，类似【1，2，3，4，5，6】
    函数的功能就是将123，456，分开提取出来，形成（1，3），（4，6）这样的效果
    :return: 返回的就是元组的形式
    '''
    first = last = L[0]
    for n in L[1:]:
        if n - 1 == last:
            last = n
        else:
            yield first, last
            first = last = n
    yield first, last


def get_segments(vehicle_speed):
    '''
    采用nonzero函数，来得到全部非零的片段
    :param vehicle_speed:输入dataframe中的车速数据
    :return:返回的是非零的片段
    '''
    test_cycle_array = np.array(vehicle_speed)
    nonzero_index = test_cycle_array.nonzero()
    nonzero_list = list(nonzero_index[0])
    segments_group = list(group(nonzero_list))
    return segments_group


def re_get_segments(segments):
    '''
    通过get_segments函数得到的是不包含怠速片段的速度片段
    接下里需要对这样的segments进行处理，将怠速片段纳入
    :param segments:进行过简单处理的片段列表
    :return:最终的标准的短行程片段
    '''
    new_segments = []
    segments.insert(0, (0, 0))
    for i in range(len(segments)):
        if i != len(segments) - 1:
            new_segments.append((segments[i][-1], segments[i + 1][-1]))
        continue
    new_sequence = [(new_segments[0][0], new_segments[0][1] + 2)]
    for j in range(1, len(new_segments)):
        new_sequence.append((new_segments[j][0] + 1, new_segments[j][1] + 2))
    return new_sequence


def water_temp(segment_tuple):
    # 水温的筛选函数，保留水温大于70度的片段，小于70摄氏度的返回True
    for i in range(segment_tuple[0], segment_tuple[1] - 1):
        if test_data['发动机冷却液温度'][i] < 70:
            return True


def altitude_filter(segment_tuple):
    # 海拔的筛选函数，首先通过气压计算出当前的海拔，然后剔除海拔超过2400的片段
    altitude = []
    for i in range(segment_tuple[0], segment_tuple[1] - 1):
        altitude.append((100.84 - test_data['大气压力'][i]) / 0.0112)
    for alt in altitude:
        if alt > 2400:
            return True


def get_idle_para(segment_tuple):
    length = segment_tuple[1] - segment_tuple[0]
    work_period = get_segments(test_data['车速'][segment_tuple[0]: segment_tuple[1]])
    work_period_time = work_period[0][1] - work_period[0][0]
    idle_time = length - work_period_time
    idle_ratio = idle_time / length
    return idle_time, idle_ratio


def idle_filter(segment_tuple):
    segment_idle_time, segment_idle_ratio = get_idle_para(segment_tuple)
    if segment_idle_time > 600:
        return True
    if segment_idle_ratio > 0.8:
        return True


def filter_segments(segments):
    '''
    对短行程片段进行选取，先进行一次粗筛
    '''
    for segment in segments:
        max_speed = test_data['车速'][segment[0]:segment[1]].max()
        average_speed = test_data['车速'][segment[0]:segment[1]].mean()
        if average_speed > 70:  # 对于M1、N1类车辆 最高车速为90#对于M1、N1类车辆，车辆平均行驶速度＞90 km/h。
            high_list.append(segment)
        if 70 > average_speed > 45:  # 对于M1、N1类车辆 最高车速为70,对于M1、N1类车辆，平均车速60~90 km/h
            sub_list.append(segment)
        if 10 < average_speed < 30:
            urban_list.append(segment)


def speed_filter_urban(segments):
    """
    通过上面的平均车速筛选后，形成了3个库，但是库中片段只满足了平均车速要求，法规中对
    最高车速仍然有一定的要求，因此对市区段进行判断，如果最高车速大于75或55，则将其放入高速和市郊片段中
    """
    new_segments = copy.deepcopy(segments)
    for segment in segments:
        if test_data['车速'][segment[0]:segment[1]].max() > 75:
            new_segments.remove(segment)
            high_list.append(segment)
        if 75 > test_data['车速'][segment[0]:segment[1]].max() > 55:
            new_segments.remove(segment)
            sub_list.append(segment)
    return new_segments


def speed_filter_sub(segments):
    """
    对市郊段进行判断，如果最高车速大于75，则将其放入高速片段中
    """
    new_segments = copy.deepcopy(segments)
    for segment in segments:
        if test_data['车速'][segment[0]:segment[1]].max() > 75:
            new_segments.remove(segment)
            high_list.append(segment)
    return new_segments


def calc_values(one_new_sequence):
    """计算距离、加速度、v*a"""
    # 计算距离
    one_new_sequence['d'] = one_new_sequence['车速'].div(3.6)
    # 计算加速度
    one_new_sequence['v_after'] = one_new_sequence['车速'].shift(-1)
    one_new_sequence['v_before'] = one_new_sequence['车速'].shift(1)
    one_new_sequence['a'] = (one_new_sequence['v_after'] - one_new_sequence['v_before']) / (2 * 3.6)
    one_new_sequence.fillna(0, inplace=True)
    one_new_sequence.drop(['v_after', 'v_before'], axis=1, inplace=True)
    # 计算速度和加速度的乘积
    one_new_sequence['va'] = (one_new_sequence['车速'].multiply(one_new_sequence['a'])) / 3.6
    return one_new_sequence


file_path = input('请输入原始文件路径：')
max_torque = int(input('请输入基准扭矩：'))
upper_file, filename = os.path.split(file_path)
base_name = os.path.splitext(filename)[0]
file_name = base_name  # 车辆名称

# 将程序切换到原始文件上层目录中运行，构建出3个文件夹，分别用来存储市区市郊和高速段工况数据
os.chdir(upper_file)
os.makedirs(file_name + '片段库/市区片段库')
os.makedirs(file_name + '片段库/市郊片段库')
os.makedirs(file_name + '片段库/高速片段库')

raw_test_data = pd.read_excel(file_path)
# 使用前100小时数据进行分析
test_data = raw_test_data[:]
test_data.fillna(0, inplace=True)
test_data = calc_values(test_data)
# 增加海拔列
test_data['海拔'] = (100.84 - test_data['大气压力']) / 0.0112
# 3个列表用来存储切割后的片段
urban_list = []
sub_list = []
high_list = []
# 开始通过车速进行选择，形成的segments是最初始的所有原始片段
raw_segments = get_segments(test_data['车速'])
segments = re_get_segments(raw_segments)
# 形成的segments是所有的短行程片段，但是尚未对其进行怠速车速等条件判断
print('-----------形成的原始短行程片段有：' + str(len(segments)) + '个')
# 通过水温开始进行判断，如果小于70摄氏度，返回True，那就就不会筛选出来
segments = [x for x in segments if not water_temp(x)]
print('-----------水温筛选后短行程片段有：' + str(len(segments)) + '个')
# 通过气压进行海拔判断，如果大于2400，返回True，那就就不会筛选出来
segments = [x for x in segments if not altitude_filter(x)]
print('-----------海拔筛选后短行程片段有：' + str(len(segments)) + '个')
# 通过怠速时间与比例进行判断
segments = [x for x in segments if not idle_filter(x)]
print('-----------怠速筛选后短行程片段有：' + str(len(segments)) + '个')

# 然后通过最高速度进行筛选，分别存储到不同的列表中去
filter_segments(segments)
print('-----------进行第一次筛选(按照最高车速)-----------')
print('-----------市区片段有：' + str(len(urban_list)) + '个')
print('-----------市郊片段有：' + str(len(sub_list)) + '个')
print('-----------高速片段有：' + str(len(high_list)) + '个')
print('-----------进行第二次筛选(按照平均车速)-----------')

urban_list = speed_filter_urban(urban_list)
sub_list = speed_filter_sub(sub_list)

print('-----------第二次筛选后-----------')
print('-----------市区片段有：' + str(len(urban_list)) + '个')
print('-----------市郊片段有：' + str(len(sub_list)) + '个')
print('-----------高速片段有：' + str(len(high_list)) + '个')
print('-----------片段切割筛选完成-----------')


def get_average_speed(segments):
    average_speed_list = []
    for segment in segments:
        average_speed_list.append(test_data['车速'][segment[0]:segment[1]].mean())
    return average_speed_list


def get_alt_info(segments):
    max_alt = []
    min_alt = []
    pos_sum_alt = []
    for segment in segments:
        max_alt.append(test_data['海拔'][segment[0]:segment[1]].max())
    for segment in segments:
        min_alt.append(test_data['海拔'][segment[0]:segment[1]].min())
    for segment in segments:
        pos_sum_alt.append(get_alt_sum(test_data['海拔'][segment[0]:segment[1]].to_list()))
    return max_alt, min_alt, pos_sum_alt


def get_alt_sum(seq):
    sum_list = []
    ascending_lists = get_ascending_seq(seq)
    for i in range(len(ascending_lists)):
        sum_list.append(ascending_lists[i][-1] - ascending_lists[i][0])
    alt_sum = sum(sum_list)
    return alt_sum


def get_ascending_seq(seq):
    lists = []  # 用来记录每一次seq_list清空前的状态
    seq_list = []  # 用这个栈来记录数据状况
    for i in range(len(seq) - 1):
        seq_list.append(seq[i])
        if seq_list[-1] < seq[i + 1]:
            seq_list.append(seq[i + 1])
            seq_list.pop()
        else:
            if len(seq_list) == 1:
                seq_list = []
                continue
            lists.append(seq_list)
            seq_list = []
    return lists


def get_date(segments):
    date_time_list = []
    for segment in segments:
        date_time_list.append(test_data['时间'][segment[0]:segment[1]].iloc[0:1].values.tolist()[0].split(" ")[0])
    return date_time_list


def cal_nox_emission(one_new_sequence):
    nox_emission = one_new_sequence['SCR下游NOx传感器输出'].sum() / (one_new_sequence['d'] / 1000).sum()
    return nox_emission


def get_nox_emission(segments):
    '''
    通过传入区间起止数字，计算当前片段的nox排放量
    '''
    emission_list = []
    for segment in segments:
        test_data['发动机燃料流量'].iloc[segment[0]:segment[1]] = test_data['发动机燃料流量'].iloc[segment[0]:segment[1]].replace(
            '无效', 0)
        test_data['发动机燃料流量'].iloc[segment[0]:segment[1]] = test_data['发动机燃料流量'].iloc[segment[0]:segment[1]].astype(
            float)
        fuel_mass_flow = test_data['发动机燃料流量'].iloc[segment[0]:segment[1]]
        fuel_mass_flow = 0.84 * fuel_mass_flow / 3600
        air_mass_flow = test_data['进气量'].iloc[segment[0]:segment[1]]
        air_mass_flow = air_mass_flow / 3600
        total_mass_flow = air_mass_flow + fuel_mass_flow
        test_data['SCR下游NOx传感器输出'].iloc[segment[0]:segment[1]] = test_data['SCR下游NOx传感器输出'].iloc[
                                                                 segment[0]:segment[1]].replace('无效', 0)
        nox_conc = test_data['SCR下游NOx传感器输出'].iloc[segment[0]:segment[1]]
        nox_conc = nox_conc.astype(float)
        nox_flow = 0.001587 * nox_conc * total_mass_flow
        y = nox_flow
        index = nox_flow.index.tolist()
        index = np.array(index)
        x = index
        nox_integrals = []
        for i in range(len(y)):
            nox_integrals.append(scipy.integrate.trapz(y[:i + 1], x[:i + 1]))
        emission_list.append(nox_integrals[-1])
    return emission_list


def get_work(segments):
    '''
    :param segment:传入需要计算的segment
    :return: 输出一个累积功曲线的integrals
    '''
    work_list = []
    for segment in segments:
        torque_data = test_data['发动机净输出扭矩'].iloc[segment[0]:segment[1]].replace('无效', 0)
        friction_data = test_data['摩擦扭矩'].iloc[segment[0]:segment[1]].replace('无效', 0)
        zhuansu_data = test_data['发动机转速'].iloc[segment[0]:segment[1]].replace('无效', 0)
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
        work_integrals = []
        for i in range(len(y)):  # 计算梯形的面积，面积其实就是所作的功，由于是累加，所以是切片"i+1"
            work_integrals.append(scipy.integrate.trapz(y[:i + 1], x[:i + 1]))
        work_list.append(work_integrals[-1])
    return work_list


def get_spec_emission(segments):
    work_list = get_work(segments)
    emission_list = get_nox_emission(segments)
    spec_emission = [i / j for i, j in zip(emission_list, work_list)]
    return spec_emission


urban_pd = pd.DataFrame(urban_list)
sub_pd = pd.DataFrame(sub_list)
high_pd = pd.DataFrame(high_list)

urban_pd['区间代号'] = urban_pd[[0, 1]].apply(tuple, axis=1)
urban_pd['时长'] = pd.DataFrame(urban_pd[1] - urban_pd[0])
urban_average_list = get_average_speed(urban_list)
urban_pd['平均车速'] = pd.DataFrame(urban_average_list)
urban_pd['最低海拔'] = pd.DataFrame(get_alt_info(urban_list)[0])
urban_pd['最高海拔'] = pd.DataFrame(get_alt_info(urban_list)[1])
urban_pd['海拔增量'] = pd.DataFrame(get_alt_info(urban_list)[2])
urban_pd['日期'] = pd.DataFrame(get_date(urban_list))
urban_pd['比排放g/kw*h']=pd.DataFrame(get_spec_emission(urban_list))
urban_pd['累积功'] = pd.DataFrame(get_work(urban_list))
urban_pd['排放量g'] = pd.DataFrame(get_nox_emission(urban_list))

sub_pd['区间代号'] = sub_pd[[0, 1]].apply(tuple, axis=1)
sub_pd['时长'] = pd.DataFrame(sub_pd[1] - sub_pd[0])
sub_average_list = get_average_speed(sub_list)
sub_pd['平均车速'] = pd.DataFrame(sub_average_list)
sub_pd['最低海拔'] = pd.DataFrame(get_alt_info(sub_list)[0])
sub_pd['最高海拔'] = pd.DataFrame(get_alt_info(sub_list)[1])
sub_pd['海拔增量'] = pd.DataFrame(get_alt_info(sub_list)[2])
sub_pd['日期'] = pd.DataFrame(get_date(sub_list))
sub_pd['比排放g/kw*h']=pd.DataFrame(get_spec_emission(sub_list))

sub_pd['累积功'] = pd.DataFrame(get_work(sub_list))
sub_pd['排放量g'] = pd.DataFrame(get_nox_emission(sub_list))

high_pd['区间代号'] = high_pd[[0, 1]].apply(tuple, axis=1)
high_pd['时长'] = pd.DataFrame(high_pd[1] - high_pd[0])
high_average_list = get_average_speed(high_list)
high_pd['平均车速'] = pd.DataFrame(high_average_list)
high_pd['最低海拔'] = pd.DataFrame(get_alt_info(high_list)[0])
high_pd['最高海拔'] = pd.DataFrame(get_alt_info(high_list)[1])
high_pd['海拔增量'] = pd.DataFrame(get_alt_info(high_list)[2])
high_pd['日期'] = pd.DataFrame(get_date(high_list))
high_pd['比排放g/kw*h']=pd.DataFrame(get_spec_emission(high_list))
high_pd['累积功'] = pd.DataFrame(get_work(high_list))
high_pd['排放量g'] = pd.DataFrame(get_nox_emission(high_list))

urban_pd.rename(columns={0: '片段起点', 1: '片段终点'}, inplace=True)
sub_pd.rename(columns={0: '片段起点', 1: '片段终点'}, inplace=True)
high_pd.rename(columns={0: '片段起点', 1: '片段终点'}, inplace=True)

urban_pd.to_excel(upper_file + '/' + file_name + '片段库/市区片段库/' + '市区片段数据.xlsx')
sub_pd.to_excel(upper_file + '/' + file_name + '片段库/市郊片段库/' + '市郊片段数据.xlsx')
high_pd.to_excel(upper_file + '/' + file_name + '片段库/高速片段库/' + '高速片段数据.xlsx')

urban_pd = urban_pd[['日期', '片段起点', '片段终点', '区间代号', '时长', '平均车速', '最高海拔', '最低海拔', '海拔增量', '比排放g/kw*h']]
sub_pd = sub_pd[['日期', '片段起点', '片段终点', '区间代号', '时长', '平均车速', '最高海拔', '最低海拔', '海拔增量', '比排放g/kw*h']]
high_pd = high_pd[['日期', '片段起点', '片段终点', '区间代号', '时长', '平均车速', '最高海拔', '最低海拔', '海拔增量', '比排放g/kw*h']]

for i in range(len(urban_list)):
    plt.plot(test_data['车速'][urban_list[i][0]:urban_list[i][1]])
    plt.xlabel('time')
    plt.ylabel('vehicle speed')
    plt.title('Urban ' + str(i) + 'th segment')
    filename1 = str(i) + 'th segment' + '.png'
    filepath1 = upper_file + '/' + file_name + '片段库/市区片段库'
    plt.savefig(filepath1 + '/' + filename1)
    plt.close()
    test_data[urban_list[i][0]:urban_list[i][1]].to_excel(file_name + '片段库/市区片段库/' + '市区-' + str(i) + '片段.xlsx')

for i in range(len(sub_list)):
    plt.plot(test_data['车速'][sub_list[i][0]:sub_list[i][1]])
    plt.xlabel('time')
    plt.ylabel('vehicle speed')
    plt.title('Sub ' + str(i) + 'th segment')
    filename2 = str(i) + 'th segment' + '.png'
    filepath2 = upper_file + '/' + file_name + '片段库/市郊片段库'
    plt.savefig(filepath2 + '/' + filename2)
    plt.close()
    test_data[sub_list[i][0]:sub_list[i][1]].to_excel(file_name + '片段库/市郊片段库/' + '市郊-' + str(i) + '片段.xlsx')

for i in range(len(high_list)):
    plt.plot(test_data['车速'][high_list[i][0]:high_list[i][1]])
    plt.xlabel('time')
    plt.ylabel('vehicle speed')
    plt.title('High ' + str(i) + 'th segment')
    filename3 = str(i) + 'th segment' + '.png'
    filepath3 = upper_file + '/' + file_name + '片段库/高速片段库'
    plt.savefig(filepath3 + '/' + filename3)
    plt.close()
    test_data[high_list[i][0]:high_list[i][1]].to_excel(file_name + '片段库/高速片段库/' + '高速-' + str(i) + '片段.xlsx')

# 接下来绘制不同片段库中片段时长与平均车速的分布情况
urban_info = pd.read_excel(upper_file + '/' + file_name + '片段库/市区片段库/' + '市区片段数据.xlsx')
plt.bar(range(len(urban_info['时长'].sort_values().to_list())), urban_info['时长'].sort_values().to_list())
plt.xlabel('different segments')
plt.ylabel('duration (s)')
plt.savefig(upper_file + '/' + file_name + '片段库/市区片段库/市区片段时长分布情况.png')
plt.close()

sub_info = pd.read_excel(upper_file + '/' + file_name + '片段库/市郊片段库/' + '市郊片段数据.xlsx')
plt.bar(range(len(sub_info['时长'].sort_values().to_list())), sub_info['时长'].sort_values().to_list())
plt.xlabel('different segments')
plt.ylabel('duration (s)')
plt.savefig(upper_file + '/' + file_name + '片段库/市郊片段库/市郊片段时长分布情况.png')
plt.close()

high_info = pd.read_excel(upper_file + '/' + file_name + '片段库/高速片段库/' + '高速片段数据.xlsx')
plt.bar(range(len(high_info['时长'].sort_values().to_list())), high_info['时长'].sort_values().to_list())
plt.xlabel('different segments')
plt.ylabel('duration (s)')
plt.savefig(upper_file + '/' + file_name + '片段库/高速片段库/高速片段时长分布情况.png')
plt.close()
# 开始绘制平均车速分布情况
urban_info = pd.read_excel(upper_file + '/' + file_name + '片段库/市区片段库/' + '市区片段数据.xlsx')
plt.bar(range(len(urban_info['平均车速'].sort_values().to_list())), urban_info['平均车速'].sort_values().to_list())
plt.xlabel('different segments')
plt.ylabel('average speed (km/h)')
plt.savefig(upper_file + '/' + file_name + '片段库/市区片段库/市区片段平均车速分布情况.png')
plt.close()

sub_info = pd.read_excel(upper_file + '/' + file_name + '片段库/市郊片段库/' + '市郊片段数据.xlsx')
plt.bar(range(len(sub_info['平均车速'].sort_values().to_list())), sub_info['平均车速'].sort_values().to_list())
plt.xlabel('different segments')
plt.ylabel('average speed (km/h)')
plt.savefig(upper_file + '/' + file_name + '片段库/市郊片段库/市郊片段平均车速分布情况.png')
plt.close()

high_info = pd.read_excel(upper_file + '/' + file_name + '片段库/高速片段库/' + '高速片段数据.xlsx')
plt.bar(range(len(high_info['平均车速'].sort_values().to_list())), high_info['平均车速'].sort_values().to_list())
plt.xlabel('different segments')
plt.ylabel('average speed (km/h)')
plt.savefig(upper_file + '/' + file_name + '片段库/高速片段库/高速片段平均车速分布情况.png')
plt.close()
# 开始绘制排放的分布情况
plt.bar(range(len(urban_info['比排放g/kw*h'].sort_values().to_list())), urban_info['比排放g/kw*h'].sort_values().to_list())
plt.xlabel('different segments')
plt.ylabel('specific emission (g/kw*h)')
plt.savefig(upper_file + '/' + file_name + '片段库/市区片段库/市区片段平均排放分布情况.png')
plt.close()

plt.bar(range(len(sub_info['比排放g/kw*h'].sort_values().to_list())), sub_info['比排放g/kw*h'].sort_values().to_list())
plt.xlabel('different segments')
plt.ylabel('specific emission (g/kw*h)')
plt.savefig(upper_file + '/' + file_name + '片段库/市郊片段库/市郊片段平均排放分布情况.png')
plt.close()

plt.bar(range(len(high_info['比排放g/kw*h'].sort_values().to_list())), high_info['比排放g/kw*h'].sort_values().to_list())
plt.xlabel('different segments')
plt.ylabel('specific emission (g/kw*h)')
plt.savefig(upper_file + '/' + file_name + '片段库/高速片段库/高速片段平均排放分布情况.png')
plt.close()

urban_info=urban_info.rename(columns={'比排放g/kw*h':'emission(g/kw*h)'})
ax = sns.displot(urban_info['emission(g/kw*h)'],bins=20,kde=True)
ax.savefig(upper_file + '/' + file_name + '片段库/市区片段库/市区片段平均排放分布热力图.png')

sub_info=sub_info.rename(columns={'比排放g/kw*h':'emission(g/kw*h)'})
ax = sns.displot(sub_info['emission(g/kw*h)'],bins=20,kde=True)
ax.savefig(upper_file + '/' + file_name + '片段库/市郊片段库/市郊片段平均排放分布热力图.png')

high_info=high_info.rename(columns={'比排放g/kw*h':'emission(g/kw*h)'})
ax = sns.displot(high_info['emission(g/kw*h)'],bins=20,kde=True)
ax.savefig(upper_file + '/' + file_name + '片段库/高速片段库/高速片段平均排放分布热力图.png')
