#!/bin/bash

set -e

# 创建和配置 runners 目录
mkdir -p conf/runners
cp -r samples/configs/* conf/runners/

# 启动应用服务器
./launcher.py > /dev/null &
SERVER_PID=$!

# 捕获意外错误并进行清理
cleanup() {
    echo "Cleaning up..."
    kill $SERVER_PID 2>/dev/null || true
    rm -rf conf/runners
}
trap cleanup EXIT

# 禁用 set -e 以便捕获测试的退出状态
set +e

# 运行 E2E 测试
echo "Running E2E tests..."
cd src/e2e_tests
../../e2e_venv/bin/python -m pytest --alluredir /tmp/allure_result
STATUS=$?

# 启用 set -e 以便后续命令遇到错误时退出
set -e

# 生成 Allure 测试报告
echo "Generating Allure report..."
../../web-src/node_modules/allure-commandline/dist/bin/allure generate /tmp/allure_result --clean -o /tmp/allure_report

# 退出脚本并返回测试的退出状态
exit $STATUS
