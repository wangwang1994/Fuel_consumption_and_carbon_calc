import folium
import pandas as pd
import os

file_path=input('输入平台数据文件：')
vin=input('输入车辆信息：')
data = pd.read_excel(file_path, skiprows=lambda x: x > 0 and (x - 1) % 600 != 0)

place_lat = data['纬度'].to_list()
place_lng = data['经度'].to_list()
m = folium.Map(location=[place_lat[0], place_lng[-1]],
               zoom_start=15)
points = []
for i in range(len(place_lat)):
    points.append([place_lat[i], place_lng[i]])

for index, lat in enumerate(place_lat):
    folium.Marker([lat,
                   place_lng[index]],
                  popup=('patient{} \n 74contacts'.format(index)),
                  icon=folium.Icon(color='green', icon='plus')).add_to(m)
folium.PolyLine(points, color='red').add_to(m)
m.save((os.path.dirname(file_path))+os.sep+vin+"运行轨迹分布.html")
