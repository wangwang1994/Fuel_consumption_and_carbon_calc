import pandas as pd

data = pd.read_excel('/Users/xuchangmao/Desktop/工作/排放模型/故障分析/LFNA4LJB3LTB12607故障码（3个月）.xlsx')
time_list = data['故障时间'].to_list()  # 将时间提取出来，分离出具体的日期，而不要具体的时间点，精确到天就可以
new_time_list = []
for item in time_list:
    new_time_list.append(item[:10])
data['故障日期'] = pd.DataFrame(new_time_list)
# 以上重新在数据中设定了新的列，也就只显示日期
error_list = []  # 用一个list来存储所有的不同故障的情况
error_index = data['故障内容'].unique().tolist()  # 需要统计出出现的故障类型
for item in error_index:
    error_list.append(pd.DataFrame(data[data['故障内容'] == item]))
# 当前形成的error——list中，就汇总了所有的故障码所出现的情况，每一个元素都是一个dataframe，可以通过查看每个小元素来了解当前故障码的情况
error_pd_list = []  # 创建一个空的列表用来存储故障发生日期及频次的dataframe
for i in range(len(error_list)):
    error_pd_list.append(pd.DataFrame(error_list[i]['故障日期'].value_counts().sort_index()))
    error_pd_list[i].rename(columns={'故障日期': '频次'}, inplace=True)
    error_pd_list[i]['故障类型'] = error_index[i]
writer = pd.ExcelWriter('故障频次统计.xlsx')
for i in range(len(error_pd_list)):
    error_pd_list[i].to_excel(writer, str(i))
writer.save()
