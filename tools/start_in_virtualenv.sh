#!/bin/bash

set -e

# 检查是否安装了必要的工具
for cmd in curl wget unzip python3; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd is not installed."
        exit 1
    fi
done

# 下载 Script-Server 最新发布版本
echo "Downloading the latest release of Script-Server..."
latest_release_url=$(curl -s https://api.github.com/repos/bugy/script-server/releases/latest | grep browser_download_url | cut -d '"' -f 4)
wget -q $latest_release_url -O script-server.zip
unzip -q script-server.zip
rm script-server.zip
echo "Download and extraction complete."

# 创建 Python 虚拟环境
echo "Creating virtual environment..."
python3 -m venv virtual_env

# 安装依赖
echo "Installing dependencies..."
virtual_env/bin/pip install --quiet wheel
wget -q https://github.com/bugy/script-server/raw/master/requirements.txt
virtual_env/bin/pip install --quiet -r requirements.txt
rm requirements.txt
echo "Dependencies installed."

# 启动 Script-Server
echo "Starting Script-Server..."
virtual_env/bin/python3 launcher.py &

# 捕获退出信号并进行清理
trap 'echo "Stopping Script-Server..."; kill $!; exit 0' SIGINT SIGTERM

# 等待服务器启动
wait $!
