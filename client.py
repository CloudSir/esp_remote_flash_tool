'''
Author: CloudSir
@Github: https://github.com/CloudSir
Date: 2023-10-08 21:48:26
LastEditTime: 2023-10-08 22:02:57
LastEditors: CloudSir
Description: 
'''
import requests
import yaml
import os

current_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(current_path) # 设置工作目录

with open('./_config.yaml',encoding='utf-8') as file_:
    data = yaml.load(file_,Loader=yaml.FullLoader)
    re = requests.get(data["server_url"], stream=True)
    for chunk in re.iter_lines():    # 按照一行一行的读取
        if chunk:
            print(chunk.decode("utf-8"))
