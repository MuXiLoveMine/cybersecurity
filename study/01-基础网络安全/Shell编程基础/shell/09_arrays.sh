#!/bin/bash
# 09_arrays.sh
# 数组操作示例

echo "=========================================="
echo "1. 数组定义与访问"
echo "=========================================="

# 定义数组
fruits=("苹果" "香蕉" "樱桃" "枣" "橙子")

# 访问单个元素
echo "第 0 个元素：${fruits[0]}"
echo "第 2 个元素：${fruits[2]}"

# 访问所有元素
echo "所有元素：${fruits[@]}"

# 数组长度
echo "数组长度：${#fruits[@]}"

# 所有索引
echo "所有索引：${!fruits[@]}"

echo ""
echo "=========================================="
echo "2. 遍历数组"
echo "=========================================="

echo "方式一：for in 遍历元素"
for fruit in "${fruits[@]}"; do
    echo "  $fruit"
done

echo ""
echo "方式二：通过索引遍历"
for i in "${!fruits[@]}"; do
    echo "  索引 $i：${fruits[$i]}"
done

echo ""
echo "=========================================="
echo "3. 添加和删除元素"
echo "=========================================="

# 末尾添加
fruits+=("葡萄")
echo "添加葡萄后：${fruits[@]}"

# 指定索引添加
fruits[10]="西瓜"
echo "索引 10 添加西瓜后：${fruits[@]}"
echo "现在长度：${#fruits[@]}"

# 删除元素
unset fruits[2]
echo "删除索引 2 后：${fruits[@]}"
echo "现在索引：${!fruits[@]}"

echo ""
echo "=========================================="
echo "4. 数组切片"
echo "=========================================="

nums=(10 20 30 40 50 60 70)
echo "原数组：${nums[@]}"
echo "从索引 2 开始取 3 个：${nums[@]:2:3}"
echo "从索引 3 开始到结尾：${nums[@]:3}"

echo ""
echo "=========================================="
echo "5. 数组合并"
echo "=========================================="

arr1=(a b c)
arr2=(d e f)
arr3=("${arr1[@]}" "${arr2[@]}")
echo "arr1: ${arr1[@]}"
echo "arr2: ${arr2[@]}"
echo "合并后 arr3: ${arr3[@]}"

echo ""
echo "=========================================="
echo "6. 关联数组"
echo "=========================================="

declare -A user
user["name"]="张三"
user["age"]=25
user["city"]="北京"
user["email"]="zhangsan@example.com"

echo "姓名：${user[name]}"
echo "年龄：${user[age]}"

echo ""
echo "所有键：${!user[@]}"
echo "所有值：${user[@]}"

echo ""
echo "遍历关联数组："
for key in "${!user[@]}"; do
    echo "  $key: ${user[$key]}"
done
