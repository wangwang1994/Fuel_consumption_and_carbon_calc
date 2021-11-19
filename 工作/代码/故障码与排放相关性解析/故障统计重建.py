import pandas as pd

data = pd.read_excel('/Users/xuchangmao/Desktop/工作/排放模型/故障分析/故障与排放相关性分析/故障码数据/故障频次统计.xlsx', sheet_name=None)
start = input('输入开始日期(20210828类似格式)：')  # 20210828
end = input('输入结束日期（20211103类似格式）：')  # 20211103
# 创建一个基础的dataframe,然后利用故障的dataframe进行拼接后，去除具有相同时间的行，那么留下来的就是所有的行
# 然后再进行一定的处理就可以得到包含从起点到终点日期的所有天中，故障是否发生的dataframe
time_list = [d.strftime('%Y-%m-%d') for d in pd.date_range(start, end)]
df = pd.DataFrame({'频次': [0],
                   '故障类型': [0],
                   '是否发生故障': [0],
                   '日期': time_list
                   }, index=time_list)
# 使用这个list来存储进行处理以后的dataframe
new_df_list = []
#接下来用这个新的空白的dataframe和每一个小的故障frame合并，合并以后按照日期去重，这样就只留下了有故障的行
for small_df in data.values(): #data是一个字典，key是读取的excel的表名，而value是该表的内容
    small_df.rename(columns={'Unnamed: 0': '日期'}, inplace=True)  # 修改初始的第一列为日期
    small_df['是否发生故障'] = 1                                 #新增一列为是否发生故障，因为是导出的故障dataframe，所以都设置为1
    small_df.index = list(small_df['日期'])                    #修改故障dataframe的index为日期
    pd2 = pd.concat([small_df, df], join='inner')              #将基准dataframe和故障dataframe合并
    pd2 = pd2.drop_duplicates(subset=['日期'])    # 将合并后的dataframe去重，按照日期列
    pd2['日期'] = pd2.index.to_list()
    pd2 = pd2.reindex(time_list)
    pd2['故障类型']=small_df['故障类型'][0]
    new_df_list.append(pd2)
writer = pd.ExcelWriter('/Users/xuchangmao/Desktop/工作/排放模型/故障分析/故障与排放相关性分析/故障码数据/故障频次统计更新版.xlsx')
for i in range(len(new_df_list)):
    new_df_list[i].to_excel(writer, str(i))
writer.save()