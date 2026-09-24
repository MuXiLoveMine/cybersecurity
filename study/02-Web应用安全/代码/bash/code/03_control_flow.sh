#!/bin/bash
# ============================================================
# 03_control_flow.sh - 条件判断与循环
# ============================================================

echo "========== 1. if 条件判断 =========="

score=85

if [ $score -ge 90 ]; then
    echo "优秀"
elif [ $score -ge 80 ]; then
    echo "良好"
elif [ $score -ge 60 ]; then
    echo "及格"
else
    echo "不及格"
fi

echo ""
echo "========== 2. 数值比较运算符 =========="

a=10
b=20

echo "a=$a, b=$b"
[ $a -eq $b ] && echo "a 等于 b" || echo "a 不等于 b"
[ $a -ne $b ] && echo "a 不等于 b"
[ $a -gt $b ] && echo "a 大于 b" || echo "a 不大于 b"
[ $a -lt $b ] && echo "a 小于 b"
[ $a -ge $b ] && echo "a 大于等于 b" || echo "a 小于 b"
[ $a -le $b ] && echo "a 小于等于 b"

echo ""
echo "========== 3. 字符串比较 =========="

str1="hello"
str2="world"
str3=""

echo "str1=$str1, str2=$str2"
[ "$str1" = "$str2" ] && echo "字符串相等" || echo "字符串不相等"
[ "$str1" != "$str2" ] && echo "字符串不相等"
[ -z "$str3" ] && echo "str3 是空字符串"
[ -n "$str1" ] && echo "str1 是非空字符串"

echo ""
echo "========== 4. 文件测试 =========="

script_file="$0"
echo "测试文件: $script_file"

[ -f "$script_file" ] && echo "是普通文件"
[ -r "$script_file" ] && echo "可读"
[ -w "$script_file" ] && echo "可写"
[ -x "$script_file" ] && echo "可执行"
[ -s "$script_file" ] && echo "文件大小不为零"

echo ""
echo "========== 5. 逻辑运算符 =========="

age=25
[ $age -gt 18 ] && [ $age -lt 60 ] && echo "年龄在 18-60 之间"
[ $age -lt 18 ] || [ $age -gt 60 ] && echo "不在工作年龄范围" || echo "在工作年龄范围"

echo ""
echo "========== 6. case 语句 =========="

os="linux"

case $os in
    "linux")
        echo "Linux 系统"
        ;;
    "macos")
        echo "macOS 系统"
        ;;
    "windows")
        echo "Windows 系统"
        ;;
    *)
        echo "其他系统"
        ;;
esac

echo ""
echo "========== 7. for 循环 =========="

echo "遍历数字范围:"
for i in 1 2 3 4 5; do
    echo "数字: $i"
done

echo ""
echo "遍历序列 (1-10 步长2):"
for i in $(seq 1 2 10); do
    echo "数字: $i"
done

echo ""
echo "遍历数组元素:"
fruits=("苹果" "香蕉" "橙子" "葡萄")
for fruit in "${fruits[@]}"; do
    echo "水果: $fruit"
done

echo ""
echo "C 风格 for 循环:"
for ((i=1; i<=5; i++)); do
    echo "i = $i"
done

echo ""
echo "========== 8. while 循环 =========="

echo "while 循环计数:"
count=1
while [ $count -le 5 ]; do
    echo "count = $count"
    count=$((count + 1))
done

echo ""
echo "读取文件行:"
echo "line1" > /tmp/test_lines.txt
echo "line2" >> /tmp/test_lines.txt
echo "line3" >> /tmp/test_lines.txt

while read -r line; do
    echo "读取: $line"
done < /tmp/test_lines.txt
rm -f /tmp/test_lines.txt

echo ""
echo "========== 9. until 循环 =========="

echo "until 循环:"
num=5
until [ $num -eq 0 ]; do
    echo "num = $num"
    num=$((num - 1))
done
echo "倒计时结束！"

echo ""
echo "========== 10. break 和 continue =========="

echo "break 示例 (遇到3跳出):"
for i in 1 2 3 4 5; do
    if [ $i -eq 3 ]; then
        break
    fi
    echo "i = $i"
done

echo ""
echo "continue 示例 (跳过3):"
for i in 1 2 3 4 5; do
    if [ $i -eq 3 ]; then
        continue
    fi
    echo "i = $i"
done

echo ""
echo "========== 11. select 菜单循环 =========="

echo "请选择一个选项:"
select choice in "选项一" "选项二" "选项三" "退出"; do
    case $choice in
        "选项一")
            echo "你选择了选项一"
            ;;
        "选项二")
            echo "你选择了选项二"
            ;;
        "选项三")
            echo "你选择了选项三"
            ;;
        "退出")
            echo "退出菜单"
            break
            ;;
        *)
            echo "无效选项"
            ;;
    esac
done
