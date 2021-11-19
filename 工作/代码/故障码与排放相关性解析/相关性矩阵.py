import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_excel('/Users/xuchangmao/Desktop/工作/排放模型/故障分析/故障与排放相关性分析/故障码数据/相关性分析原始数据.xlsx')
corr = df.corr()
