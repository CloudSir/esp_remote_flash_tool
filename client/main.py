'''
Description: 
Author: CloudSir
Date: 2023-10-09 08:20:09
Copyright: Cloudsir
LastEditors: Cloudsir
LastEditTime: 2023-10-16 15:17:19
'''
import requests
import yaml
import os
from termcolor import colored

import argparse  

parser = argparse.ArgumentParser()

parser.add_argument('config', type=str, help='config file path')

args = parser.parse_args()  # 获取所有参数


def print_err(msg):
    print(colored(msg, "red"))

def main():
    config_path = ""
    if(args.config):
        config_path = args.config
    else:
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path) # 设置工作目录
        config_path = "./client_config.yaml"

    with open(config_path, encoding='utf-8') as file_:
        
        data = yaml.load(file_,Loader=yaml.FullLoader)

        bootloader_bin_path = data.get("bootloader_bin_path")
        main_app_bin_path = data.get("main_app_bin_path")
        partitions_bin_path = data.get("partitions_bin_path")

        ota_data_initial_path = data.get("ota_data_initial_path")

        if not os.path.exists(bootloader_bin_path):
            print_err("bootloader.bin is not exist, please check config in 'client_config.yaml'.")
            return

        if not os.path.exists(main_app_bin_path):
            print_err("main_app.bin is not exist, please check config in 'client_config.yaml'.")
            return

        if not os.path.exists(bootloader_bin_path):
            print_err("partitions.bin is not exist, please check config in 'client_config.yaml'.")
            return

        files = {
            'bootloader': open(bootloader_bin_path,'rb'),
            'main_app':   open(main_app_bin_path,'rb'),
            'partitions': open(partitions_bin_path,'rb')
        }

        if ota_data_initial_path and os.path.exists(ota_data_initial_path):
            files["ota_data_initial"] = open(ota_data_initial_path,'rb')

        try:
            requests.get(data["server_url"] + "/", timeout=3)
        except:
            print_err("Server is not running!")
            return

        re = requests.post(data["server_url"] + "/flash", stream=True, files=files)
        for chunk in re.iter_lines():    # 按照一行一行的读取
            if chunk:
                print(chunk.decode("utf-8"))


if __name__ == "__main__":
    main()
    