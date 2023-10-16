'''
Description: 
Author: CloudSir
Date: 2023-10-09 08:20:09
Copyright: Cloudsir
LastEditors: Cloudsir
LastEditTime: 2023-10-16 15:21:04
'''

import os
from flask import Flask,request
from flask import Response
from serial.tools import list_ports
import yaml

import subprocess
import sys

from termcolor import colored

# params
baud = 961200
chip = "esp8266"
after_flash = "soft_reset"
# params end


def err_msg(msg):
    return colored(msg, "red")

def success_msg(msg):
    return colored(msg, "green")

def update_config():
    global baud
    global chip
    global after_flash
    global com_tool_path

    with open('server_config.yaml',encoding='utf-8') as file_:
        data = yaml.load(file_,Loader=yaml.FullLoader)

        baud = data["baud"]
        chip = data["chip"]
        after_flash = data["after_flash"]
        com_tool_path = data["com_tool_path"]


def get_last_portName():
    port_list = list(list_ports.comports())
    num = len(port_list)
    if num <= 0:
        print(err_msg("COM is Null!!!"))
        return "null"
    else:
        return list(port_list[-1]) [0]

def get_command(ComName, ota_data_initial):
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
           {"0xd000  ./bin/ota_data_initial.bin" if ota_data_initial else ""} \
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

        
    @app.route('/flash', methods=['GET', 'POST'])
    def test():
        if(len(request.files) == 0):
            return err_msg("No bin file posted!")

        bootloader_bin_file = request.files.get('bootloader')
        main_app_bin_file = request.files.get('main_app')
        partitions_bin_file = request.files.get('partitions')

        ota_data_initial = request.files.get('ota_data_initial')

        if ota_data_initial:
            ota_data_initial.save(f"./bin/ota_data_initial.bin")
        
        if bootloader_bin_file:
            bootloader_bin_file.save(f"./bin/bootloader.bin")
        else:
            return err_msg("No bootloader file posted!")

        if main_app_bin_file:
            main_app_bin_file.save(f"./bin/main_app.bin")
        else:
            return err_msg("No main_app file posted!")
            
        if partitions_bin_file:
            partitions_bin_file.save(f"./bin/partitions.bin")
        else:
            return err_msg("No partitions file posted!")
            
        def generate():
            # 拼接命令
            com_num = get_last_portName()
            if (com_num == "null"):
                yield err_msg("\nCOM is Null\n")
                return

            command_str = get_command(com_num, ota_data_initial)
            print(command_str)

            # 执行外部命令
            p = subprocess.Popen(command_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # 获取实时输出并处理
            for line in iter(p.stdout.readline, b''):
                tmp_line = line.decode('utf-8')
                sys.stdout.write(tmp_line)
                yield tmp_line
                sys.stdout.flush()
            
            print(success_msg("write flash OK, open COM_TOOL..."))
            yield success_msg("write flash OK, open COM_TOOL...\n")

            os.system(f"\"{com_tool_path}\"")
            print("Finish.")
            yield "Finish.\n"
            print("---------------------------------------------------\n")

        return Response(generate(), mimetype='text/plain')

    app.run(debug=True, port=9969, host="0.0.0.0")

