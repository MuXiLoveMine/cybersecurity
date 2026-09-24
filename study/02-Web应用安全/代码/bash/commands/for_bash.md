# for_bash

> **分类**：循环
> **说明**：for/while/until 循环

---

## 语法

```bash
for var in list; do ... done\nwhile condition; do ... done
```

## 相关

break - 跳出循环\ncontinue - 跳过本次

## 示例代码

```bash
#!/bin/bash

# for 循环遍历列表
for fruit in apple banana cherry; do
    echo "水果: $fruit"
done

# 遍历数字范围
for i in {1..5}; do
    echo "数字: $i"
done

# 带步长
for i in {0..10..2}; do
    echo $i  # 0, 2, 4, 6, 8, 10
done

# C 风格 for 循环
for ((i=0; i<5; i++)); do
    echo $i
done

# 遍历文件
for file in *.txt; do
    echo "处理: $file"
done

# 遍历命令输出
for line in $(cat file.txt); do
    echo $line
done

# 遍历数组
arr=("apple" "banana" "cherry")
for item in "${arr[@]}"; do
    echo $item
done

# while 循环
count=0
while [ $count -lt 5 ]; do
    echo $count
    ((count++))
done

# 逐行读取文件
while read line; do
    echo "行内容: $line"
done < file.txt

# until 循环（条件为假时执行）
count=0
until [ $count -ge 5 ]; do
    echo $count
    ((count++))
done

# break 和 continue
for i in {1..10}; do
    if [ $i -eq 3 ]; then
        continue  # 跳过3
    fi
    if [ $i -eq 7 ]; then
        break     # 到7停止
    fi
    echo $i
done

# 循环输出数字 1 到 100
for i in {1..100}; do echo $i; done

# 死循环
while true; do
    echo "无限循环"
    sleep 1
done
```
