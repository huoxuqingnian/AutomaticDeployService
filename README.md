# Jar 自动部署脚本

## 一 环境检查

1. Python 环境检查:

运行 `python3 --version`, 可打印出 python 版本号。

如果提示 `Command not found`。则需要安装 python3, 具体安装步骤请百度。

2. 必要模块检查:

运行 `python3 -m pip list|grep paramiko`, 可打印出 paramiko 模块版本号。

如果无提示，则需要执行 `python3 -m pip install paramiko` 安装 paramiko 模块。

## 二 修改配置文件

同目录下 `ads.json` 文件为脚本配置文件，在配置文件中，配置需要发版的 jar 包相关配置。

配置文件可自定义, 需满足 `ads-xxx.json` 格式, 当同目录下存在多个配置文件时, 需手动选择对应配置文件的索引号 (如不输入则默认使用第一个)

### server 节点

| 节点 | 说明 |
| --- | --- |
| host | 服务器地址(ip) |
| port | 服务器端口(port) |
| username | 连接服务器用户名 |
| password | 连接服务器密码 |
| timeout | 超时时间 |

### jars 节点

| 节点 | 说明 |
| --- | --- |
| index | 文件索引 |
| filename | jar **完整文件名** |
| local_path | jar 本地路径(**完整地址**) |
| remote_path | jar 服务器地址(**完整地址**) |
| log_filename | 服务器日志文件名 |

## 三 执行脚本

在当前文件夹内打开终端, 执行 `sh ./run.sh` 命令，根据提示进行操作即可。

## 四 特殊说明

1. 配置文件中 `jars:index` 节点请勿重复配置, 否则都会执行