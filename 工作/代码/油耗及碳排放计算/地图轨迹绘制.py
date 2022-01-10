import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame

df = pd.read_excel('/Users/xuchangmao/Desktop/工作/排放模型/燃油周期/周期验证（加油点与尿素添加点）/7月29日-8月15原始数据.xlsx')

geometry = [Point(xy) for xy in zip(df['经度'], df['纬度'])]
gdf = GeoDataFrame(df, geometry=geometry)


world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gdf.plot(ax=world.plot(figsize=(10, 6)), marker='o', color='red', markersize=15)