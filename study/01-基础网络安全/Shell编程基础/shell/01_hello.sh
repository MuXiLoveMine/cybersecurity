#!/bin/bash
# 01_hello.sh
# 第一个 Shell 脚本示例
echo "Hello, World!"

# 带颜色的输出
echo -e "\033[31m红色文字\033[0m"
echo -e "\033[32m绿色文字\033[0m"
echo -e "\033[33m黄色文字\033[0m"
echo -e "\033[34m蓝色文字\033[0m"

# 不换行输出
echo -n "Hello "
echo "World"

# 启用转义字符
echo -e "Name\tAge\tCity"
echo -e "张三\t25\t北京"
