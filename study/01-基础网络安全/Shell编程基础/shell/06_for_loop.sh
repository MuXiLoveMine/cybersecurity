#!/bin/bash
# 06_for_loop.sh
# for 循环示例

echo "=========================================="
echo "1. 遍历列表"
echo "=========================================="

for fruit in apple banana cherry date; do
    echo "水果：$fruit"
done

echo ""
echo "=========================================="
echo "2. 数字范围"
echo "=========================================="

echo "1 到 5："
for i in {1..5}; do
    echo "  $i"
done

echo "偶数（0 到 10，步长 2）："
for i in {0..10..2}; do
    echo "  $i"
done

echo "倒序（5 到 1）："
for i in {5..1}; do
    echo "  $i"
done

echo ""
echo "=========================================="
echo "3. C 语言风格 for 循环"
echo "=========================================="

echo "1 到 5："
for ((i=1; i<=5; i++)); do
    echo "  第 $i 次"
done

echo "计算 1 到 100 的和："
sum=0
for ((i=1; i<=100; i++)); do
    sum=$((sum + i))
done
echo "  总和：$sum"

echo ""
echo "=========================================="
echo "4. 遍历数组"
echo "=========================================="

fruits=("苹果" "香蕉" "樱桃" "枣")
for fruit in "${fruits[@]}"; do
    echo "水果：$fruit"
done

echo ""
echo "=========================================="
echo "5. 遍历命令输出"
echo "=========================================="

echo "当前目录的 .sh 文件："
count=0
for file in *.sh; do
    if [ -f "$file" ]; then
        echo "  $file"
        count=$((count + 1))
    fi
done
echo "共 $count 个脚本文件"

echo ""
echo "=========================================="
echo "6. 九九乘法表"
echo "=========================================="

for ((i=1; i<=9; i++)); do
    for ((j=1; j<=i; j++)); do
        echo -ne "${j}x${i}=$((i*j))\t"
    done
    echo ""
done

echo ""
echo "=========================================="
echo "7. break 和 continue"
echo "=========================================="

echo "continue 跳过偶数："
for i in {1..10}; do
    if (( i % 2 == 0 )); then
        continue
    fi
    echo "  奇数：$i"
done

echo "break 遇到 5 跳出："
for i in {1..10}; do
    if [ $i -eq 5 ]; then
        break
    fi
    echo "  i = $i"
done
