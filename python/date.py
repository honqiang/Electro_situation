# xxxx电磁态势分析系统
# hongqiang.lee@gmail.com
# 2018年7月28日
# google map WG-84
# 北纬（lat） 东经（lon），单位：mks
# 瑞丽 24.009181, 97.859101

from math import sin, cos, sqrt, atan2, radians
import numpy as np
import math
import os
import time
import numba
start_time = time.time()

@numba.jit
def get_distanc(lat1, lon1, lat2, lon2):
    "输入两个坐标WG84，计算两点间的地表距离m"
    R = 6373.0  # 地球半径
    lat_1 = radians(lat1)
    lon_1 = radians(lon1)
    lat_2 = radians(lat2)
    lon_2 = radians(lon2)
    dlon = lon_2 - lon_1
    dlat = lat_2 - lat_1
    a = (sin(dlat/2))**2 + cos(lat_1) * cos(lat_2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c*1000
    return distance


def DKE(h, d, omega_post):
    "根据阈值h，两点间的距离，选的参数，计算DKE的值"
    if d >= h:
        fs_dke = 0.0
    else:
        fs_dke = (1/math.pow(h, 2))*omega_post*(3/math.pi) * \
            math.pow((1-math.pow(d/h, 2)), 2)

    return fs_dke


def DKE_negative(h, d, omega_negative):
    "根据阈值h，两点间的距离，选的参数，计算DKE的值,成本型"
    if d >= h:
        fs_dke = 0.0
    else:
        fs_dke = (1/math.pow(h, 2))*(1/omega_negative) * \
            (3/math.pi)*math.pow((1-math.pow(d/h, 2)), 2)

    return fs_dke


def Normalize(data, max):
    "矩阵规范化"
    nor = data/max
    return nor


# 网格划分 输入需要划分的地图对角线坐标
N = 1300
web_begin_lat, web_begin_lon = (24.038639, 97.835673)  # 左上
web_end_lat, web_end_lon = (23.985706, 97.921106)      # 右下

# 将起始坐标转换为网格坐标
web_lat_max = max(web_begin_lat, web_end_lat)
web_lat_min = min(web_begin_lat, web_end_lat)
web_lat = np.linspace(web_lat_max, web_lat_min, N, endpoint=True)
web_lon_max = max(web_begin_lon, web_end_lon)
web_lon_min = min(web_begin_lon, web_end_lon)
web_lon = np.linspace(web_lon_min, web_lon_max, N, endpoint=True)

with open('e:/课题/result/web_lat.txt', 'w') as f1, open('e:/课题/result/web_lon.txt', 'w') as f2:
    np.savetxt('e:/课题/result/web_lat.txt', web_lat)
    np.savetxt('e:/课题/result/web_lon.txt', web_lon)
    web_date_time = time.time()
    print(f"栅格化网络用时:{web_date_time-start_time}s")

# 测试用的点
dot1 = [23.987080, 97.885402, 8.0]
dot2 = [24.010533, 97.871553, 8.0]
dot3 = [24.028241, 97.867378, 8.2]
dot4 = [24.005506, 97.853046, 6]
dot5 = [24.030922, 97.871839, 8]
dot6 = [24.037641, 97.908323, 1]
dot7 = [24.004662, 97.909453, 8]
dot8 = [24.027555, 97.910471, 8]
dot9 = [24.025919, 97.917749, 1]
dot10 = [24.007121, 97.912703, 8]

dot =[dot1, dot2, dot3, dot4, dot5, dot6, dot7, dot8, dot9, dot10]
dot_len = len(dot)

# 划分网格
h = 1500
Rs = np.zeros((N, N))  # 战场热点值矩阵
for i in range(0, N-1):
    for j in range(0, N-1):
        for dot_i in dot:
            distance = get_distanc(web_lat[i], web_lon[j], dot_i[0], dot_i[1])
            if distance < h:
                aa = DKE(h, distance, dot_i[2])
                Rs[i][j] = Rs[i][j]+aa
Rs_time = time.time()
print(f"态势信息用时：{Rs_time-web_date_time}s")


# 矩阵规范化
a = Rs
mx = a.max()
for i in range(0, N-1):
    for j in range(0, N-1):
        Rs[i][j] = Normalize(Rs[i][j], mx)
nor_time = time.time()
print(f"态势信息规范化用时：{nor_time-Rs_time}s")

# 保存数据为txt
with open('e:/课题/result/Rs.txt', 'w'):
    np.savetxt('e:/课题/result/Rs.txt', Rs)
    end_time = time.time()
    print(f"保存数据用时：{end_time-nor_time}s")

print("data  all done")
