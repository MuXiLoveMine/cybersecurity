#!/bin/bash
# 04_if.sh
# if 条件判断示例

echo "=========================================="
echo "1. 数值比较"
echo "=========================================="

read -p "请输入你的年龄：" age

if [ $age -lt 0 ]; then
    echo "年龄不能为负数"
elif [ $age -lt 18 ]; then
    echo "未成年"
elif [ $age -lt 60 ]; then
    echo "成年"
else
    echo "老年"
fi

echo ""
echo "=========================================="
echo "2. 字符串比较"
echo "=========================================="

read -p "请输入用户名：" username

if [ "$username" = "admin" ]; then
    echo "欢迎管理员"
elif [ "$username" = "guest" ]; then
    echo "欢迎访客"
elif [ -z "$username" ]; then
    echo "用户名为空"
else
    echo "欢迎，$username"
fi

echo ""
echo "=========================================="
echo "3. 文件测试"
echo "=========================================="

file="/etc/passwd"
if [ -f "$file" ]; then
    echo "$file 存在且是普通文件"
    if [ -r "$file" ]; then
        echo "文件可读"
    fi
    if [ -s "$file" ]; then
        echo "文件非空"
    fi
else
    echo "$file 不存在"
fi

echo ""
echo "=========================================="
echo "4. 逻辑运算"
echo "=========================================="

num=15
if [ $num -gt 10 ] && [ $num -lt 20 ]; then
    echo "$num 在 10 和 20 之间"
fi

if [ $num -lt 10 ] || [ $num -gt 20 ]; then
    echo "$num 不在 10 和 20 之间"
else
    echo "$num 在 10 和 20 之间"
fi

# && 和 || 的巧妙用法
[ -f /etc/passwd ] && echo "文件存在" || echo "文件不存在"

echo ""
echo "=========================================="
echo "5. 双括号语法（(())）"
echo "=========================================="

a=10
b=20

if (( a > b )); then
    echo "a > b"
elif (( a == b )); then
    echo "a == b"
else
    echo "a < b"
fi

if (( a > 5 && b > 15 )); then
    echo "a > 5 且 b > 15"
fi

echo ""
echo "=========================================="
echo "6. 双方括号语法（[[]]）"
echo "=========================================="

str="hello world"

if [[ "$str" == h* ]]; then
    echo "字符串以 h 开头"
fi

if [[ "$str" =~ ^h.*d$ ]]; then
    echo "字符串匹配正则 ^h.*d$"
fi

if [[ -f /etc/passwd && -r /etc/passwd ]]; then
    echo "文件存在且可读（双方括号写法）"
fi
