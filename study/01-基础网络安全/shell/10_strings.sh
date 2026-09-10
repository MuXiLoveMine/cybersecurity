#!/bin/bash
# 10_strings.sh
# 字符串处理示例

str="Hello World"
echo "原始字符串：$str"
echo ""

echo "=========================================="
echo "1. 字符串长度"
echo "=========================================="
echo "长度：${#str}"

echo ""
echo "=========================================="
echo "2. 字符串截取"
echo "=========================================="
echo "从第 0 位取 5 个：${str:0:5}"
echo "从第 6 位取到结尾：${str:6}"
echo "从倒数第 5 位开始：${str: -5}"

echo ""
echo "=========================================="
echo "3. 删除匹配"
echo "=========================================="

path="/home/user/docs/report.txt"
echo "路径：$path"
echo "删除最短前缀（#）：${path#*/}"
echo "删除最长前缀（##）：${path##*/}"
echo "删除最短后缀（%）：${path%/*}"
echo "删除最长后缀（%%）：${path%%/*}"

echo ""
echo "=========================================="
echo "4. 字符串替换"
echo "=========================================="

text="apple banana apple cherry apple"
echo "原字符串：$text"
echo "替换第一个 apple：${text/apple/orange}"
echo "替换所有 apple：${text//apple/orange}"
echo "删除所有 apple：${text//apple/}"

echo ""
echo "=========================================="
echo "5. 大小写转换"
echo "=========================================="

s="Hello World"
echo "原字符串：$s"
echo "全部大写：${s^^}"
echo "全部小写：${s,,}"
echo "首字母大写：${s^}"
echo "首字母小写：${s,}"

echo ""
echo "=========================================="
echo "6. 字符串判断"
echo "=========================================="

email="user@example.com"

if [[ "$email" == *@* ]]; then
    echo "$email 看起来像邮箱地址（包含 @）"
fi

if [[ "$email" == *.com ]]; then
    echo "$email 以 .com 结尾"
fi

if [[ "$email" =~ ^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]+$ ]]; then
    echo "$email 匹配邮箱正则"
fi

empty=""
if [ -z "$empty" ]; then
    echo "empty 是空字符串"
fi

if [ -n "$email" ]; then
    echo "email 是非空字符串"
fi

echo ""
echo "=========================================="
echo "7. 字符串拼接"
echo "=========================================="

first="Hello"
last="World"
full="${first} ${last}!"
echo "拼接结果：$full"

echo ""
echo "=========================================="
echo "8. 使用 cut/awk/sed 处理"
echo "=========================================="

csv="张三,25,北京,工程师"
echo "CSV 数据：$csv"

echo "用 cut 取第 2 列：$(echo $csv | cut -d, -f2)"
echo "用 awk 取第 1 和第 4 列：$(echo $csv | awk -F, '{print $1, $4}')"
echo "用 sed 替换逗号为竖线：$(echo $csv | sed 's/,/ | /g')"
