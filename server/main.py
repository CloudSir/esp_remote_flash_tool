'''
Author: CloudSir
@Github: https://github.com/CloudSir
Date: 2023-10-08 21:09:13
LastEditTime: 2023-10-08 22:14:18
LastEditors: CloudSir
Description: 
'''
import os
from flask import Flask,request
from flask import Response
from serial.tools import list_ports
import yaml

import subprocess
import sys

# params
baud = 961200
chip = "esp8266"
after_flash = "soft_reset"
# params end

def update_config():
    global baud
    global chip
    global after_flash
    global com_tool_path

    with open('_config.yaml',encoding='utf-8') as file_:
        data = yaml.load(file_,Loader=yaml.FullLoader)


        baud = data["baud"]
        chip = data["chip"]
        after_flash = data["after_flash"]
        com_tool_path = data["com_tool_path"]


def get_last_portName():
    port_list = list(list_ports.comports())
    num = len(port_list)
    if num <= 0:
        print("COM is Null!!!")
        return "null"
    else:
        return list(port_list[-1]) [0]

def get_command(ComName):
    update_config()
    return f"""python ./esptool/esptool.py \
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


if __name__ == "__main__":

    app = Flask('app')

    @app.route('/flash_old_interface')
    def main():
        command_str = get_command(get_last_portName())
        print(command_str)
        os.system(command_str)

        os.system(f"\"{com_tool_path}\"")
        return "OK"

    @app.route("/clear")
    def clear():
        os.system("cls")
        return "Clear server console OK."

    @app.route("/")
    def root():
        return "Flask is running."

        
    @app.route('/flash')
    def test():
        def generate():
            # 拼接命令
            com_num = get_last_portName()
            if (com_num == "null"):
                yield "\nCOM is Null"

            command_str = get_command(com_num)
            print(command_str)

            # 执行外部命令
            p = subprocess.Popen(command_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # 获取实时输出并处理
            for line in iter(p.stdout.readline, b''):
                tmp_line = line.decode('utf-8')
                sys.stdout.write(tmp_line)
                yield tmp_line
                sys.stdout.flush()
            
            print("write flash OK, open COM_TOOL...")
            yield "write flash OK, open COM_TOOL...\n"

            os.system(f"\"{com_tool_path}\"")
            print("Finish.")
            yield "Finish.\n"
            print("---------------------------------------------------\n")

        return Response(generate(), mimetype='text/plain')

    app.run(debug=True, port=9989, host="0.0.0.0")

