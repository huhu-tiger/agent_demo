

# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Thu Mar 13 14:07:57 2025
"""


# http://山河API接口地址?city=成都

# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 10:53:54 2025

@author: jinho
"""



import requests

def get_weather_info(city):

    url = f"http://山河API接口地址?city={city}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
     
        if data.get("code") == 1: # 检查是否成功获取数据
            weather =  data["data"] 
            current_weather = weather.get("current", {})
            print(f"城市: {current_weather.get('city')}")
            print(f"温度: {current_weather.get('temp')}°C")
            print(f"天气状况: {current_weather.get('weather')}")
            print(f"湿度: {current_weather.get('humidity')}")
            print(f"风速: {current_weather.get('windSpeed')}")
            print(f"能见度: {current_weather.get('visibility')}km")
            print(f"空气质量指数: {current_weather.get('air')}")
            print(f"PM2.5浓度: {current_weather.get('air_pm25')}")
            print(f"获取时间: {current_weather.get('time')}")
        else:
            print("未能成功获取数据：", data.get("text"))
    else:
        print(f"请求失败，状态码：{response.status_code}")
if __name__ == "__main__":
# 调用函数
    get_weather_info(city = "北京")


