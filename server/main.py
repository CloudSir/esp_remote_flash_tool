'''
Description: 
Author: CloudSir
Date: 2023-10-09 08:20:09
Copyright: Cloudsir
LastEditors: Cloudsir
LastEditTime: 2023-11-03 09:54:02
'''

"""python ./esptool/esptool.py \
           --chip {chip} \
           --port {ComName} \
           --baud 921600 \
           --before default_reset \
           --after {after_flash} \
           write_flash -z \
           --flash_mode dio \
           --flash_freq 40m \
           --flash_size 2MB \
           0x0000  ./bin/bootloader.bin \
           0x10000 ./bin/main_app.bin \
           0x8000  ./bin/partitions.bin \ 
"""

import os
from flask import Flask,request
from flask import Response
from serial.tools import list_ports

import subprocess
import sys

from termcolor import colored

import argparse  

parser = argparse.ArgumentParser()

parser.add_argument('--port', type=int, required=False, default=9969, help='htpp server port')

args = parser.parse_args()  # 获取所有参数

def err_msg(msg):
    return colored(msg, "red")

def success_msg(msg):
    return colored(msg, "green")

if __name__ == "__main__":

    app = Flask('app')

    @app.route("/clear")
    def clear():
        os.system("cls")
        return "Clear server console OK."

    @app.route("/")
    def root():
        return "Flask is running."

    @app.route('/flash', methods=['GET', 'POST'])
    def flash():
        if(len(request.files) == 0):
            return err_msg("No bin file posted!")
        
        prefix_cmd = "python ./esptool/esptool.py  "
        suffix_cmd = "  write_flash -z  "
        firmware_bin_cmd = ""

        for item_name in request.files:

            if item_name == "basic_options":
                prefix_cmd += request.files.get(item_name).read().decode("utf-8")
                continue

            if item_name == "flash_options":
                suffix_cmd += request.files.get(item_name).read().decode("utf-8")
                continue

            if item_name == "com_port":
                com_port = request.files.get(item_name).read().decode("utf-8")
                port_list = list(list_ports.comports())

                # 如果是自动选择COM
                if com_port == "auto":
                    num = len(port_list)
                    if num <= 0:
                        msg = err_msg("COM is Null!!!")
                        print(msg)
                        return msg
                    elif num > 1:
                        msg = err_msg("You have connected more than one COM ports, please set a COM port!!!")
                        print(msg)
                        return msg
                    
                    com_port = list(port_list[-1]) [0]
                
                else:  # 手动选择的COM
                    
                    port_name_list = []
                    for port_name in port_list:
                        port_name_list.append(port_name[0])

                    # 检查选择的是否存在COM
                    if com_port not in port_name_list:
                        msg = err_msg(f"{com_port} is not connecting!!!")
                        print(msg)
                        return msg

                prefix_cmd += f"  --port {com_port}  "
                continue


            file = request.files.get(item_name)
            file.save(f"./bin/{file.filename}")
            bin_addr_name = item_name
            firmware_bin_cmd += f"  {bin_addr_name}  ./bin/{file.filename}"

        cmd_str = prefix_cmd + suffix_cmd + firmware_bin_cmd

        def generate():
            command_str = cmd_str
            print(command_str)

            # 执行外部命令
            p = subprocess.Popen(command_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # 获取实时输出并处理
            for line in iter(p.stdout.readline, b''):
                tmp_line = line.decode('utf-8')
                sys.stdout.write(tmp_line)
                yield tmp_line
                sys.stdout.flush()
            
            # 输出的异常检查
            err_code = p.wait()
            if err_code:  # 异常情况
                msg = err_msg( str(p.stderr.read(), "gbk") )
                print(msg)
                yield msg
            else:    # 正常情况
                msg = success_msg("Flash finish, success!!!")
                print(msg)
                yield msg
            
            print("---------------------------------------------------\n")

        return Response(generate(), mimetype='text/plain')

    app.run(debug=True, port=args.port, host="0.0.0.0")

