import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# 更详细的路线坐标、城市、国家和访问日期（示意版本）
detailed_route = [
    {"city": "New York", "country": "USA", "date": "1999.01", "coords": (-74.006, 40.7128)},
    {"city": "Reykjavik", "country": "Iceland", "date": "1999.02", "coords": (-21.8277, 64.1265)},
    {"city": "London", "country": "UK", "date": "1999.03", "coords": (-0.1276, 51.5074)},
    {"city": "Paris", "country": "France", "date": "1999.04", "coords": (2.3522, 48.8566)},
    {"city": "Berlin", "country": "Germany", "date": "1999.05", "coords": (13.4050, 52.5200)},
    {"city": "Rome", "country": "Italy", "date": "1999.06", "coords": (12.4964, 41.9028)},
    {"city": "Istanbul", "country": "Turkey", "date": "1999.07", "coords": (28.9784, 41.0082)},
    {"city": "Moscow", "country": "Russia", "date": "1999.09", "coords": (37.6173, 55.7558)},
    {"city": "Ulaanbaatar", "country": "Mongolia", "date": "2000.03", "coords": (106.9057, 47.9212)},
    {"city": "Beijing", "country": "China", "date": "2000.05", "coords": (116.4074, 39.9042)},
    {"city": "Bangkok", "country": "Thailand", "date": "2000.10", "coords": (100.5018, 13.7563)},
    {"city": "Delhi", "country": "India", "date": "2001.01", "coords": (77.2090, 28.6139)},
    {"city": "Tehran", "country": "Iran", "date": "2001.03", "coords": (51.3890, 35.6892)},
    {"city": "Cairo", "country": "Egypt", "date": "2001.05", "coords": (31.2357, 30.0444)},
    {"city": "Nairobi", "country": "Kenya", "date": "2001.08", "coords": (36.8219, -1.2921)},
    {"city": "Cape Town", "country": "South Africa", "date": "2001.11", "coords": (18.4241, -33.9249)},
    {"city": "Buenos Aires", "country": "Argentina", "date": "2002.03", "coords": (-58.3816, -34.6037)},
    {"city": "Santiago", "country": "Chile", "date": "2002.05", "coords": (-70.6693, -33.4489)},
    {"city": "Mexico City", "country": "Mexico", "date": "2002.09", "coords": (-99.1332, 19.4326)},
    {"city": "New York", "country": "USA", "date": "2002.12", "coords": (-74.006, 40.7128)},
]

# 经纬度坐标
lons, lats = zip(*[entry["coords"] for entry in detailed_route])

# 创建地图
fig = plt.figure(figsize=(22, 11))
m = Basemap(projection='robin', lon_0=0, resolution='c')
m.drawcoastlines()
m.drawcountries()
m.fillcontinents(color='lightgray', lake_color='lightblue')
m.drawmapboundary(fill_color='lightblue')

# 坐标转换
x, y = m(lons, lats)

# 绘制红线路径
m.plot(x, y, color='red', linewidth=2, marker='o', markersize=6)

# 标注详细说明（含路线编号、城市、国家、时间）
for i, entry in enumerate(detailed_route):
    lon, lat = entry["coords"]
    px, py = m(lon, lat)
    label = f"{i+1}. {entry['city']}, {entry['country']}\n{entry['date']}"
    plt.text(px + 400000, py, label, fontsize=8, ha='left', va='center', color='darkblue')

# 图标题
plt.title("吉姆·罗杰斯《旷野人生》环球旅行路线图（1999–2002）- 详细版", fontsize=18)

plt.show()

