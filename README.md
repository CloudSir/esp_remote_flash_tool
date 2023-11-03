## 介绍

`esp_remote_flash_tool` 是一款基于 esptool.py 的远程自动烧录工具，支持 ESP32 和 ESP8266。

**使用场景**

- 基于 ESP-IDF 、ESP8266 NONO SDK、ESP8266 RTOS SDK 进行开发的项目
- 项目代码存储在 Linux 编译机上，Windows 通过 SSH 连接到 Linux 进行开发，且开发板连接在 Windows 开发机上

**为什么选择这样的开发模式？**

- Windows 下编译的效率太低，完整编译一个程序大概需要 5-6 分钟，而同样的项目 Linux 仅需要 1 分钟，所以在 Linux 下进行编译开发可以大大提高效率。

- 但是，直接在 Linux 下开发可能遇到一些问题，比如：
  1. Linux 开发机是服务器，主机在服务器机房中，无法通过串口连接开发板进行烧录和调试
  2. Linux下缺少好用的串口调试工具，而且如果遇到串口输出中文的情况，还可能出现乱码的问题
  2. Linux缺少一些常用的软件，例如公司要求使用的办公软件

- 权衡之后，最佳开发方式将项目代码存储在 Linux 编译机上，Windows 通过 SSH 连接到 Linux 进行开发，且开发板连接在 Windows 开发机上，负责烧录和调试。


**问题与解决**

因为开发板连接在 Windows 开发机上，每次修改完代码想要验证程序时，都需要经过一系列步骤：
  1. 编译程序
  2. 将编译后的程序复制到开发机
  3. 利用烧录软件将程序烧录到开发板
  4. 打开串口调试软件进行调试

`esp_remote_flash_tool` 将这些步骤进行简化，只需要执行一行命令，就可以完成上述操作，提高了开发时验证代码的效率。


## 开始使用

## 下载项目

```shell
# 使用Github
git clone https://github.com/CloudSir/esp_remote_flash_tool

# 使用Gitee
git clone https://gitee.com/Cloud-Sir/esp_remote_flash_tool
```

### 开启服务端

1. 复制服务端程序：将 esp_remote_flash_tool 文件夹下的 `server` 复制到 Windows 开发机上

2. 下载依赖：进入 Windows 开发机的 `server` 目录，执行

```shell
pip install -r requirements.txt
```

3. 运行服务端程序：在 Windows 开发机的 `server` 目录下执行

```shell
python main.py
```

复制 running on 后面的服务器地址。


### 开始远程烧录

1. 复制远程烧录客户端程序：将 esp_remote_flash_tool 文件夹下的 `client` 复制到 Linux 编译机上（与你的ESP项目文件夹同级文件夹下）

2. 下载依赖：进入 Linux 编译机的 `client` 目录，执行

```shell
pip install -r requirements.txt
```

2. 根据自己的项目的配置修改 `client` 目录下的 `config.yaml`

    - server_url: 刚才复制的服务器的文件地址

    - com_port：Windows 开发机下连接 ESP8266/ESP32 的串口号，如果 Winsows下只连接了一个串口，可以设置为 `auto`，此时会自动选择该串口

    - basic_options：esptool.py 的基本选项，与 esptool.py 的选项相同，具体请参考 esptool.py 的文档

    - flash_options：esptool.py 的 flash 选项，与 esptool.py 的选项相同，具体请参考 esptool.py 的文档

    - firmware_list：要烧录的固件列表，是一个键值对类型，键为固件烧录地址，值为固件文件的**绝对路径地址**，例如：

        ```yaml
        firmware_list:
            0x0000: 
                'firmware/bootloader.bin'
            0x1000: 
                'firmware/app.bin'
        ```
3. 你的项目编译成功后，可以在 Linux 编译机下调用 `esp_remote_flash_tool` 进行远程烧录(确保 Windows 开发机的服务器端程序已运行，且 Windows 开发机和 Linux 编译机在同一局域网下)

```shell
# 确保 client 文件夹和项目文件夹在同一目录下，且当前目录是你的项目根目录


# 仅烧录
python ../client/main.py

# 编译并烧录（使用 make 构建时）
make && python../client/main.py

# 编译并烧录（使用 ninja 构建时）
ninja && python../client/main.py

# 编译并烧录（使用 idf.py 时）
idf.py build && python../client/main.py

```


## 说明

1. esptool 版本：esptool.py v4.7.dev2
