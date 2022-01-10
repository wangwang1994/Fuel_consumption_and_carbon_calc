import pandas as pd
import matplotlib.pyplot as plt
import mpl_toolkits.axisartist as axisartist
from matplotlib.ticker import FuncFormatter


def y_update_scale_value(temp, position):
    y = temp // 10000
    return "{}万".format(int(y))


def x_update_scale_value(temp, position):
    x = temp // 10000
    return "{}万".format(int(x))


plt.gca().yaxis.set_major_formatter(FuncFormatter(y_update_scale_value))
plt.gca().xaxis.set_major_formatter(FuncFormatter(x_update_scale_value))
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
data = pd.read_excel("/Users/xuchangmao/Desktop/工作/积分价格计算/2020年数据排序.xlsx")
x = data['平均燃料消耗量积分'].to_list()
y = data['新能源汽车积分'].to_list()
txt = data['企业名称'].to_list()
plt.scatter(x, y)
for i in range(len(x)):
    plt.xlabel('平均燃料消耗量积分', fontsize=40)
    plt.ylabel('新能源汽车积分', fontsize=40)
    plt.xticks(size=25)
    plt.yticks(size=25)
    plt.annotate(txt[i], xy=(x[i], y[i]), xytext=(x[i] - 20, y[i] - 40),fontsize=36)  # 这里xy是需要标记的坐标，xytext是对应的标签坐标
plt.ticklabel_format(style='plain', useOffset=False, axis='both')
plt.show()
