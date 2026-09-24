#!/bin/bash
# ============================================================
# 05_array.sh - 数组操作
# ============================================================

echo "========== 1. 创建数组 =========="

# 方式一：逐个赋值
fruits[0]="苹果"
fruits[1]="香蕉"
fruits[2]="橙子"
echo "方式一: ${fruits[@]}"

# 方式二：一次性赋值
colors=("红色" "绿色" "蓝色" "黄色")
echo "方式二: ${colors[@]}"

# 方式三：使用键值对
declare -A person
person["name"]="张三"
person["age"]=25
person["city"]="北京"
echo "关联数组 name: ${person[name]}"

echo ""
echo "========== 2. 访问数组元素 =========="

numbers=(10 20 30 40 50)

echo "第一个元素: ${numbers[0]}"
echo "第二个元素: ${numbers[1]}"
echo "最后一个元素: ${numbers[-1]}"
echo "所有元素(@): ${numbers[@]}"
echo "所有元素(*): ${numbers[*]}"

echo ""
echo "========== 3. 数组长度 =========="

arr=("a" "b" "c" "d" "e")
echo "数组元素个数: ${#arr[@]}"
echo "数组长度: ${#arr[*]}"

echo ""
echo "========== 4. 遍历数组 =========="

languages=("Bash" "Python" "Java" "Go" "Ruby")

echo "使用 for 循环遍历:"
for lang in "${languages[@]}"; do
    echo "  - $lang"
done

echo ""
echo "使用索引遍历:"
for i in "${!languages[@]}"; do
    echo "  索引 $i: ${languages[$i]}"
done

echo ""
echo "========== 5. 添加元素 =========="

# 方式一：追加元素
stack=("first" "second")
stack+=("third")
stack+=("fourth" "fifth")
echo "追加后: ${stack[@]}"

# 方式二：指定索引赋值
stack[10]="tenth"
echo "指定索引后: ${stack[@]}"
echo "数组长度: ${#stack[@]}"

echo ""
echo "========== 6. 删除元素 =========="

nums=(1 2 3 4 5 6 7 8)
echo "原始数组: ${nums[@]}"

# 删除指定索引的元素
unset nums[2]
echo "删除索引2后: ${nums[@]}"

# 删除整个数组
unset nums
echo "删除整个数组后: ${nums[@]:-空}"

echo ""
echo "========== 7. 数组切片 =========="

arr=(a b c d e f g h)
echo "原始数组: ${arr[@]}"
echo "从索引2开始取3个: ${arr[@]:2:3}"
echo "从索引5开始到末尾: ${arr[@]:5}"
echo "从末尾取3个: ${arr[@]: -3}"

echo ""
echo "========== 8. 关联数组（字典） =========="

declare -A config

config["host"]="127.0.0.1"
config["port"]=8080
config["user"]="admin"
config["password"]="123456"

echo "配置项数量: ${#config[@]}"
echo "host: ${config[host]}"
echo "port: ${config[port]}"

echo ""
echo "遍历所有键:"
for key in "${!config[@]}"; do
    echo "  $key = ${config[$key]}"
done

echo ""
echo "========== 9. 数组合并 =========="

arr1=(1 2 3)
arr2=(4 5 6)
merged=("${arr1[@]}" "${arr2[@]}")
echo "arr1: ${arr1[@]}"
echo "arr2: ${arr2[@]}"
echo "合并后: ${merged[@]}"

echo ""
echo "========== 10. 数组元素查找与替换 =========="

files=("file1.txt" "file2.sh" "file3.py" "file4.txt" "file5.sh")

echo "原始数组: ${files[@]}"

# 查找匹配的元素（不会修改原数组）
echo "匹配 .txt 的: ${files[@]/*.txt/}"

# 替换第一个匹配
temp=("${files[@]}")
temp=("${temp[@]/file/file_}")
echo "替换第一个 file: ${temp[@]}"

# 替换所有匹配
temp=("${files[@]}")
temp=("${temp[@]//file/file_}")
echo "替换所有 file: ${temp[@]}"

echo ""
echo "========== 11. 数组排序与去重 =========="

unsorted=(5 2 8 1 9 3 7 4 6 2 5 8)
echo "原始数组: ${unsorted[@]}"

# 排序（借助 sort 命令）
sorted=($(printf '%s\n' "${unsorted[@]}" | sort -n))
echo "排序后: ${sorted[@]}"

# 去重
unique=($(printf '%s\n' "${unsorted[@]}" | sort -n | uniq))
echo "去重后: ${unique[@]}"

echo ""
echo "========== 12. 从命令输出创建数组 =========="

# 将命令输出按行存入数组
IFS=$'\n' read -r -d '' -a lines < <(ls -la | head -5 && printf '\0')
echo "ls 输出的前5行:"
for line in "${lines[@]}"; do
    echo "  $line"
done
