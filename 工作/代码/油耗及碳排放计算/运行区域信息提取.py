import pandas as pd
import requests
import json
import re

data = pd.read_excel('/Users/xuchangmao/Desktop/工作/代码/油耗及碳排放计算/1号周期数据.xlsx')
AK = 'HI7l93gtaQPgYKLh58rej8iP5FDRFImP'


def get_address(latitude, longtitude):
    latitude = str(latitude)
    longtitude = str(longtitude)
    url = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak={}&output=json&coordtype=wgs84ll&location={},{}'.format(AK,
                                                                                                                     latitude,
                                                                                                                     longtitude)
    res = requests.get(url)
    location = json.loads(res.text)['result']['formatted_address']
    return location


