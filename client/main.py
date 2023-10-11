'''
Description: 
Author: CloudSir
Date: 2023-10-09 08:20:09
Copyright: Cloudsir
LastEditors: Cloudsir
LastEditTime: 2023-10-11 10:13:16
'''
import requests
import yaml
import os



def main():

    current_path = os.path.dirname(os.path.abspath(__file__))

    os.chdir(current_path) # 设置工作目录

    with open('./_config.yaml',encoding='utf-8') as file_:
        
        data = yaml.load(file_,Loader=yaml.FullLoader)

        bootloader_bin_path = data["bootloader_bin_path"]
        main_app_bin_path = data["main_app_bin_path"]
        partitions_bin_path = data["partitions_bin_path"]

        files = {
            'bootloader': open(bootloader_bin_path,'rb'),
            'main_app':   open(main_app_bin_path,'rb'),
            'partitions': open(partitions_bin_path,'rb')
        }

        try:
            requests.get(data["server_url"] + "/", timeout=3)
        except:
            print("Server is not running!")
            return

        re = requests.post(data["server_url"] + "/flash", stream=True, files=files)
        for chunk in re.iter_lines():    # 按照一行一行的读取
            if chunk:
                print(chunk.decode("utf-8"))


main()