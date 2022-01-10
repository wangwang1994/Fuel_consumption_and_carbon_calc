import numpy as np;

np.random.seed(sum(map(ord, 'calmap')))
import pandas as pd
import calmap

filepath = input('输入文件路径：')
data = pd.read_excel(filepath)

# all_days = pd.date_range('1/15/2014', periods=6, freq='D')
# '/Users/xuchangmao/Desktop/工作/油耗行为分析/1四地车辆数据对比/1位置信息提取/湖南车辆/每日运行情况统计.xlsx'
# days = np.random.choice(all_days, 6)

days = pd.to_datetime(data['日期'].values)
days = pd.to_datetime(data['日期'].values)
distance = data['运行里程(km)'].to_list()
events = pd.Series(distance, index=days)
calmap.yearplot(events, year=2021)
calmap.calendarplot(events)










