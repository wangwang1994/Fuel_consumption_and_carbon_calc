import os

path = '/Users/xuchangmao/Desktop/工作/油耗行为分析/1四地车辆数据对比'
file_list = os.listdir(path)
n = 0
for file in file_list:
    oldname = path + os.sep + file_list[n]
    newname = path + os.sep + file.split('_')[1]
    os.rename(oldname, newname)
    print(oldname, '======>', newname)
    n += 1
