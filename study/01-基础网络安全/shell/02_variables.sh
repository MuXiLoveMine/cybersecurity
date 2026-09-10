#!/bin/bash
# 02_variables.sh
# 变量定义与使用

# 基本变量定义
name="张三"
age=25
pi=3.14159

echo "姓名：$name"
echo "年龄：$age"
echo "圆周率：$pi"

# 使用 ${} 形式避免歧义
echo "我叫${name}，今年${age}岁"

# 命令替换
current_date=$(date "+%Y-%m-%d %H:%M:%S")
echo "当前时间：$current_date"

# 算术运算
a=10
b=3
echo "a = $a, b = $b"
echo "加法：$((a + b))"
echo "减法：$((a - b))"
echo "乘法：$((a * b))"
echo "除法（整数）：$((a / b))"
echo "取余：$((a % b))"

# 自增自减
c=5
echo "c = $c"
echo "c++ = $((c++))（后置，先返回后自增）"
echo "现在 c = $c"

# 浮点运算（借助 bc）
result=$(echo "scale=2; 10 / 3" | bc)
echo "浮点除法：10 / 3 = $result"

# 变量默认值
unset username
echo "用户名（默认匿名）：${username:-匿名}"

# 字符串长度
str="hello world"
echo "字符串 '$str' 的长度：${#str}"

# 字符串截取
echo "从第 0 位取 5 个：${str:0:5}"
echo "从第 6 位取到结尾：${str:6}"

# 删除匹配
path="/home/user/docs/file.txt"
echo "路径：$path"
echo "删除最短前缀（从左）：${path#*/}"
echo "删除最长前缀（从左）：${path##*/}"
echo "删除最短后缀（从右）：${path%/*}"
echo "删除最长后缀（从右）：${path%%/*}"

# 替换
echo "替换第一个 o：${str/o/O}"
echo "替换所有 o：${str//o/O}"
