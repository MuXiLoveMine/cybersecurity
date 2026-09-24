# awk

> **分类**：文本处理
> **说明**：强大的文本处理语言，适合处理结构化文本

---

## 语法

```bash
awk "pattern { action }" [files]
```

## 内置变量

- $0: 整行
- $1,$2...: 字段
- NF: 字段数
- NR: 行号
- FS: 字段分隔符
- OFS: 输出分隔符

## 示例代码

```bash
#!/bin/bash

# 基本用法：打印第1列
awk "{print $1}" file.txt

# 指定分隔符（冒号）
awk -F: "{print $1, $3}" /etc/passwd

# 打印最后一列
awk "{print $NF}" file.txt

# 打印行号和内容
awk "{print NR, $0}" file.txt

# 条件打印
awk "$3 > 100" file.txt        # 第3列大于100的行
awk "$1 == "error"" file.txt # 第1列是 error 的行
awk "/pattern/" file.txt       # 匹配正则的行

# BEGIN/END 块
awk "BEGIN {sum=0} {sum+=$1} END {print sum}" file.txt

# 计算平均值
awk "{sum+=$1; count++} END {print sum/count}" data.txt

# 多字段处理
awk -F: "{
    if ($3 > 100) {
        print $1, $3
    }
}" /etc/passwd

# 字符串函数
awk "{print length($0)}" file.txt    # 每行长度
awk "{print substr($1, 1, 3)}" file.txt  # 子串
awk "{print tolower($1)}" file.txt   # 转小写
awk "{print toupper($1)}" file.txt   # 转大写
awk -F: "{print split($0, arr, ":")}" file.txt

# 数组
awk "{count[$1]++} END {for (k in count) print k, count[k]}" file.txt

# 条件判断
awk "{
    if ($3 >= 90) grade = "A"
    else if ($3 >= 60) grade = "B"
    else grade = "C"
    print $1, grade
}" scores.txt

# 输出分隔符
awk -F: "BEGIN {OFS="\t"} {print $1, $3, $7}" /etc/passwd

# 求和
awk -F: "{sum += $3} END {print sum}" /etc/passwd

# 统计行数（类似 wc -l）
awk "END {print NR}" file.txt
```
