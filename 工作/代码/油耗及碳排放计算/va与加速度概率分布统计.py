import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 在这里把工况文件路径粘进去
data1 = pd.read_excel('/Users/xuchangmao/Desktop/工作/油耗行为分析/标准工况/标准模版/wltc工况.xlsx')
data2 = pd.read_excel('/Users/xuchangmao/Desktop/工作/油耗行为分析/标准工况/标准模版/CLTC工况.xlsx')
data3= pd.read_excel('/Users/xuchangmao/Desktop/工作/油耗行为分析/标准工况/标准模版/NEDC工况.xlsx')

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


data1 = calc_values(data1)
data2 = calc_values(data2)
data3 = calc_values(data3)
# Make a separate list for each airline
x1 = list(data1[data1['a'] > 0]['va'])
x2 = list(data2[data2['a'] > 0]['va'])
x3 = list(data3[data3['a'] > 0]['va'])


# Assign colors for each airline and the names, '#56B4E9', '#F0E442', '#009E73', '#D55E00'
colors = ['#E69F00','#F0E442','#56B4E9']
names = ['wltc','cltc','nedc']

# Make the histogram using a list of lists
# Normalize the flights and assign colors and names
plt.hist([x1,x2,x3], bins=int(20),
         color=colors, label=names)

# Plot formatting
plt.legend()
plt.xlabel('va值')
plt.ylabel('样本数')
plt.title('va分布')
plt.show()
