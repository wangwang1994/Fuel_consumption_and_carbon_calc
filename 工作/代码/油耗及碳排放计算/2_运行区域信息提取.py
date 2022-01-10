import pandas as pd
import requests
import json
import os

file_path=input('输入文件路径：')
vin=input('输入车辆信息：')
data = pd.read_excel(file_path)
AK = 'HI7l93gtaQPgYKLh58rej8iP5FDRFImP'


def get_address(latitude, longtitude):
    latitude = str(latitude)  # 纬度
    longtitude = str(longtitude)  # 经度
    url = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak={}&output=json&coordtype=wgs84ll&location={},{}'.format(AK,
                                                                                                                     latitude,
                                                                                                                     longtitude)
    res = requests.get(url)
    location = json.loads(res.text)['result']['formatted_address']
    return location


def get_day_location(df):
    # 输入一个dataframe，输出当前数据的，第一行对应的经纬度坐标的位置，作为当天的位置
    address = get_address(df['纬度'].iloc[0], df['经度'].iloc[0])
    return address


def get_date(df):
    # 输入一个dataframe,根据最开始第一行数据，提取出他的日期，形成datelist
    date = df['日期'].iloc[0].strftime('%Y-%m-%d')
    return date


day_location_list = []  # 用来存储每天的位置信息
day_list = []  # 用来存储每天的具体日期
data['日期'] = pd.to_datetime(data['时间']).dt.date
date_list = [x for _, x in data.groupby(data['日期'])]

for item in date_list:
    day_location_list.append(get_day_location(item))
    day_list.append(get_date(item))

result=pd.DataFrame(
    {
        '日期':day_list,
        '位置':day_location_list
    }
                    )
result.to_excel((os.path.dirname(file_path))+os.sep+vin+'位置信息数据.xlsx')
