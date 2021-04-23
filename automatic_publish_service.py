import os.path
import time
import json
import re

import paramiko

# 作者信息
SCRIPT_AUTHOR = "tian_p"
SCRIPT_BUILD_TIME = "2021-04-22"
SCRIPT_VERSION = "1.0"
GITHUB_ADDRESS = 'https://github.com/huoxuqingnian/AutomaticDeployService'

# 配置文件
DEFAULT_CONFIG_FILE_PATH = "./"
DEFAULT_CONFIG_FILE_NAME = "aps.json"

CONFIG_NODE_SERVER = "server"
CONFIG_NODE_SERVER_HOST = "host"
CONFIG_NODE_SERVER_USERNAME = "username"
CONFIG_NODE_SERVER_PASSWORD = "password"
CONFIG_NODE_SERVER_PORT = "port"
CONFIG_NODE_SERVER_TIMEOUT = "timeout"
CONFIG_NODE_JARS = "jars"
CONFIG_NODE_JARS_INDEX = "index"
CONFIG_NODE_JARS_FILENAME = "filename"
CONFIG_NODE_JARS_LOCAL_PATH = "local_path"
CONFIG_NODE_JARS_REMOTE_PATH = "remote_path"
CONFIG_NODE_JARS_LOG_FILENAME = "log_filename"

# 全部节点
ALL_CONFIG_INDEX = "all"
# 多节点分割字符
CONFIG_INDEX_SEPARATOR = ","
# 编码
ENCODING = "utf-8"
# 配置文件 pattern
CONFIG_FILE_PATTERN = re.compile(r'^aps(-.+)?\.json$', re.I)


def byte_translate(file_size):
    """
    字节转换
    :param file_size: 文件数据大小
    :return:
    """
    byte = float(file_size)
    kilo_byte = float(1024)
    mega_byte = float(kilo_byte ** 2)
    giga_byte = float(mega_byte ** 2)
    trillion_byte = float(giga_byte ** 2)
    if byte < kilo_byte:
        return '{} {}'.format(byte, 'bytes' if byte > 1 else "byte")
    elif kilo_byte < byte < mega_byte:
        return '{:.2f} KB'.format(byte / kilo_byte)
    elif mega_byte < byte < giga_byte:
        return '{:.2f} MB'.format(byte / mega_byte)
    elif giga_byte < byte < trillion_byte:
        return '{:.2f} GB'.format(byte / giga_byte)
    else:
        return '{:.2f} TB'.format(byte / trillion_byte)


def progress_display(transferred, file_size):
    """
    进度条展示
    :param transferred: 已传输数据大小
    :param file_size: 文件数据大小
    :return: None
    """
    timing = time.perf_counter() - start_time
    progress = transferred / file_size * 100
    print("\rUploading [{}]: {:^3.0f}% ({}/{}) Cost: {:.2f}s"
          .format(filename, progress, byte_translate(transferred), byte_translate(file_size), timing), end="")


def get_transport():
    t = paramiko.Transport((host, port))
    t.banner_timeout = timeout
    t.connect(username=username, password=password)
    return t


def get_sftp():
    """
    获取 sftp
    :return:
    """
    sftp_client = paramiko.SFTPClient.from_transport(transport)
    print("sftp connect to {}:{} by {}".format(host, port, username))
    return sftp_client


def close_sftp():
    sftp.close()
    print("\n断开 sftp 连接")


def close_transport():
    transport.close()
    print("\n断开 transport", end="")


def close_ssh():
    ssh.close()
    print("\n断开 ssh 连接", end="")


def upload_file():
    """
    上传文件
    :return: None
    """
    sftp.put(os.path.join(local_path, filename), os.path.join(remote_path, filename), callback=progress_display)


def get_ssh():
    """
    结束原有进程
    :return:
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=host, port=port, username=username, password=password, timeout=timeout)
    print("\nssh connect to {}:{} by {}".format(host, port, username))
    return ssh_client


def get_pid():
    stdin, stdout, stderr = ssh.exec_command("ps -ef|grep {}|grep -v 'grep'".format(filename))
    process_status = stdout.read().decode(ENCODING)
    if process_status:
        print("\n查找到正在运行的 {} 进程状态如下: \n{}".format(filename, process_status))
        return process_status.split()[1]
    return None


def shutdown_process():
    """
    结束进程
    :return:
    """
    stdin, stdout, stderr = ssh.exec_command("kill -9 {}".format(pid))
    process_status = stdout.read().decode(ENCODING)
    print("结束进程 {}".format(pid))


def backup_file():
    """
    备份文件
    :return:
    """
    new_filename = time.strftime('%Y-%m-%d', time.localtime()) + "-" + filename
    stdin, stdout, stderr = ssh.exec_command("cd {}; mv {} {}".format(remote_path, filename, new_filename))
    err_result = stderr.read().decode(ENCODING)
    if err_result:
        print("备份文件失败: {}", err_result)
    else:
        print("备份文件成功, 文件名: {}".format(new_filename))


def run_jar():
    """
    运行 jar 文件
    :return:
    """
    stdin, stdout, stderr = ssh.exec_command("cd {};nohup java -jar {} > {} &"
                                             .format(remote_path, filename, log_filename))
    print("\n运行 {}".format(filename))


def author_info():
    """
    作者信息
    :return: None
    """
    print("Jar automatic publish script (Author: {}  Build: {} Version: {}). Learn more: {} \n"
          .format(SCRIPT_AUTHOR, SCRIPT_BUILD_TIME, SCRIPT_VERSION, GITHUB_ADDRESS))


def load_config_file():
    """
    加载配置文件
    :return: 配置文件内容
    """
    with open(os.path.join(DEFAULT_CONFIG_FILE_PATH, DEFAULT_CONFIG_FILE_NAME), 'r', encoding=ENCODING) as f:
        return json.load(f)


def filter_config():
    """
    筛选配置
    :return: 筛选后的配置, 如果是 all, 则返回全部配置
    """
    if str(jar_index) == ALL_CONFIG_INDEX:
        return jars_configs
    filters = []
    for jar_config in jars_configs:
        if str(jar_config[CONFIG_NODE_JARS_INDEX]) in jar_index:
            filters.append(jar_config)
    return filters


def config_print():
    """
    打印配置信息
    :return:
    """
    print('已加载配置文件: {}'.format(DEFAULT_CONFIG_FILE_NAME))
    for cc in config_json:
        sc = cc[CONFIG_NODE_SERVER]
        jcs = cc[CONFIG_NODE_JARS]
        for jc in jcs:
            print('[{}] {} ({}:{})'.format(jc[CONFIG_NODE_JARS_INDEX],
                                           jc[CONFIG_NODE_JARS_FILENAME],
                                           sc[CONFIG_NODE_SERVER_HOST],
                                           sc[CONFIG_NODE_SERVER_PORT]))


def find_config_file():
    """
    多配置文件适配
    :return:
    """
    config_files = []
    global DEFAULT_CONFIG_FILE_NAME
    for file in os.listdir(DEFAULT_CONFIG_FILE_PATH):
        match_result = CONFIG_FILE_PATTERN.match(file)
        if match_result:
            config_files.insert(0, match_result.group())
    if config_files:
        if len(config_files) == 1:
            DEFAULT_CONFIG_FILE_NAME = config_files[0]
            print("使用配置文件 {}".format(DEFAULT_CONFIG_FILE_NAME))
        else:
            print("匹配到多个配置文件:")
            index = 0
            for config_file in config_files:
                index = index + 1
                print("[{}] {}".format(index, config_file))
            config_file_index = input("请选择: ")
            if config_file_index:
                DEFAULT_CONFIG_FILE_NAME = config_files[int(config_file_index) - 1]


author_info()
find_config_file()
config_json = load_config_file()
config_print()
jar_index = input("请输入需要部署的 jar 文件索引(多个使用 '{}' 隔开; 全部使用 '{}'): "
                  .format(CONFIG_INDEX_SEPARATOR, ALL_CONFIG_INDEX))
jar_index = jar_index.split(CONFIG_INDEX_SEPARATOR)
file_num = 0
start = time.perf_counter()
for config in config_json:
    jars_configs = config[CONFIG_NODE_JARS]
    filter_configs = filter_config()
    if not filter_configs:
        continue
    server_config = config[CONFIG_NODE_SERVER]
    host = server_config[CONFIG_NODE_SERVER_HOST]
    username = server_config[CONFIG_NODE_SERVER_USERNAME]
    password = server_config[CONFIG_NODE_SERVER_PASSWORD]
    port = server_config[CONFIG_NODE_SERVER_PORT]
    timeout = server_config[CONFIG_NODE_SERVER_TIMEOUT]
    transport = get_transport()
    for jars_config in filter_configs:
        filename = jars_config[CONFIG_NODE_JARS_FILENAME]
        local_path = jars_config[CONFIG_NODE_JARS_LOCAL_PATH]
        remote_path = jars_config[CONFIG_NODE_JARS_REMOTE_PATH]
        log_filename = jars_config[CONFIG_NODE_JARS_LOG_FILENAME]
        ssh = get_ssh()
        pid = get_pid()
        if pid:
            shutdown_process()
        backup_file()
        start_time = time.perf_counter()
        sftp = get_sftp()
        upload_file()
        file_num += 1
        run_jar()
        print()
    close_transport()
    close_sftp()
    close_ssh()
total_cost = time.perf_counter() - start
print('\r脚本执行结束, 总计部署 {} 个 jar 文件, 总耗时 {:.2f} 秒'.format(file_num, total_cost))
