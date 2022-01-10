import pandas as pd
import os

filepath = input('输入文件路径：')
file_list = os.listdir(filepath)
dfs = []
for file in file_list:
    dfs.append(pd.read_excel(filepath + os.sep + file))
data = pd.concat(dfs, ignore_index=True)
data = data.sort_values(by='日期')
