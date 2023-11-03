'''
Description: 
Author: CloudSir
Date: 2023-10-09 08:20:09
Copyright: Cloudsir
LastEditors: Cloudsir
LastEditTime: 2023-11-03 09:58:10
'''
import requests
import yaml
import os
from termcolor import colored
import argparse  

parser = argparse.ArgumentParser()

parser.add_argument('--config', type=str, required=False, help='config file path')

args = parser.parse_args()  # 获取所有参数


def print_err(msg):
    print(colored(msg, "red"))

def print_ok(msg):
    print(colored(msg, "green"))

def main():
    config_path = ""
    if(args.config):
        config_path = args.config
    else:  # 使用默认配置文件
        current_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_path) # 设置工作目录为当前程序文件所在目录
        config_path = "./config.yaml" 

    with open(config_path, encoding='utf-8') as file_:
        
        data = yaml.load(file_,Loader=yaml.FullLoader)

        firmware_list = data.get("firmware_list")
        com_port = data.get("com_port")
        flash_options = data.get("flash_options")
        basic_options = data.get("basic_options")

        for firmware_burn_address in firmware_list:
            firmware_bin = firmware_list.get(firmware_burn_address)
            
            
        print_ok("Start uploading firmware...")

        post_tables = {}

        for firmware_burn_address in firmware_list:
            firmware_bin = firmware_list.get(firmware_burn_address)

            if not os.path.exists(firmware_bin):
                print_err(f"\"{firmware_bin}\" is not exist, please check \"firmware_list\" in config file.")
                return

            firmware_burn_address = hex(firmware_burn_address)
            post_tables[firmware_burn_address] = open(firmware_bin,'rb')
            
        post_tables["com_port"] = com_port
        post_tables["flash_options"] = flash_options
        post_tables["basic_options"] = basic_options

        try:
            requests.get(data["server_url"] + "/", timeout=3)
        except:
            print_err("Server is not running!")
            return

        re = requests.post(data["server_url"] + "/flash", stream=True, files=post_tables)

        if re.status_code != 200:
            print_err("Server error!")
            return
        
        print_ok("Upload firmware success!")
        print("-----------------------------------------------------------")
        print_ok("Starting Flash firmwares...\n")
        
        
        for chunk in re.iter_lines():    # 按照一行一行的读取
            if chunk:
                print(chunk.decode("utf-8"))


if __name__ == "__main__":
    main()
