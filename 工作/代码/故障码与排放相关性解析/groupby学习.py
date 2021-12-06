import pandas as pd

df = pd.read_csv('/Users/xuchangmao/Downloads/nba.csv')
df1 = pd.DataFrame(
    {
        '消费金额': [1, 2, 3, 4],
        '小费': [3, 2, 3, 4],
        '性别': ['男', '男', '女', '女'],
        '是否吸烟': ['是', '是', '否', '是'],
        '星期': [5, 6, 5, 6],
        '就餐时间': [3, 3, 2, 2],
        '就餐人数': [2, 3, 2, 4]
    },
    index=[0, 1, 2, 3]
)

df2=pd.read_csv('/Users/xuchangmao/joyful-pandas/data/learn_pandas.csv')
def get_weight_class(data):
    if data
    return 'high'
