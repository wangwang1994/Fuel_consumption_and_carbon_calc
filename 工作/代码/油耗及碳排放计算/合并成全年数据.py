import pandas as pd
data=pd.read_excel('/Users/xuchangmao/Desktop/工作/油耗行为分析/1四地车辆数据对比/车辆运行特征/青海车辆数据/总运行数据.xlsx')

data=data.set_index('日期')
data.index = pd.DatetimeIndex(data.index)
data = data[~data.index.duplicated(keep='first')]
idx = pd.date_range('2021-1-1', '2021-12-15')
data = data.reindex(idx, fill_value=0)