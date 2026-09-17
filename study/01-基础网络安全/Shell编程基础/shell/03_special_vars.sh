#!/bin/bash
# 03_special_vars.sh
# 特殊变量与命令行参数

echo "=========================================="
echo "特殊变量示例"
echo "=========================================="

# 脚本名
echo "脚本文件名：$0"

# 命令行参数
echo "参数个数：$#"
echo "第 1 个参数：$1"
echo "第 2 个参数：$2"
echo "第 3 个参数：$3"
echo "第 10 个参数：${10}"

echo ""
echo "所有参数（\$*）：$*"
echo "所有参数（\$@）：$@"

echo ""
echo "遍历 \$*："
for arg in "$*"; do
    echo "  -> $arg"
done

echo ""
echo "遍历 \$@："
for arg in "$@"; do
    echo "  -> $arg"
done

echo ""
echo "当前 Shell 进程 PID：$$"

echo ""
echo "上一条命令退出状态码：$?"

echo ""
echo "上一个命令的最后一个参数：$_"

# 检查参数个数
if [ $# -lt 2 ]; then
    echo "用法：$0 <参数1> <参数2>"
    echo "示例：$0 hello world"
    exit 1
fi

echo ""
echo "参数检查通过，继续执行..."
