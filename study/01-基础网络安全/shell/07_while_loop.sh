#!/bin/bash
# 07_while_loop.sh
# while 循环与 until 循环示例

echo "=========================================="
echo "1. 基本 while 循环"
echo "=========================================="

i=1
while [ $i -le 5 ]; do
    echo "第 $i 次循环"
    i=$((i + 1))
done

echo ""
echo "=========================================="
echo "2. 逐行读取文件"
echo "=========================================="

echo "/etc/passwd 前 5 行的用户名："
line_num=0
while IFS=: read -r username _; do
    echo "  $username"
    line_num=$((line_num + 1))
    if [ $line_num -ge 5 ]; then
        break
    fi
done < /etc/passwd

echo ""
echo "=========================================="
echo "3. until 循环"
echo "=========================================="

echo "倒计时："
count=5
until [ $count -eq 0 ]; do
    echo "  $count"
    count=$((count - 1))
    sleep 0.2
done
echo "  0（点火！）"

echo ""
echo "=========================================="
echo "4. 猜数字游戏"
echo "=========================================="

target=$((RANDOM % 100 + 1))
guess=0
tries=0

echo "我想了一个 1~100 之间的数字，你来猜猜看！"

while [ $guess -ne $target ]; do
    read -p "请输入你的猜测：" guess
    tries=$((tries + 1))

    if [ $guess -lt $target ]; then
        echo "太小了！再大一点"
    elif [ $guess -gt $target ]; then
        echo "太大了！再小一点"
    else
        echo "恭喜你，猜对了！答案就是 $target"
        echo "你一共猜了 $tries 次"
    fi
done

echo ""
echo "=========================================="
echo "5. while 读取用户输入"
echo "=========================================="

echo "输入 'quit' 退出"
while true; do
    read -p "> " input
    if [ "$input" = "quit" ]; then
        echo "再见！"
        break
    fi
    echo "你输入了：$input"
done
