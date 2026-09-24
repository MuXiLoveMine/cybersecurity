# grep

> **分类**：文本处理
> **说明**：在文件中搜索匹配的行

---

## 语法

```bash
grep [options] pattern [files]
```

## 常用选项

- -i: 忽略大小写
- -v: 反向匹配
- -r: 递归搜索
- -n: 显示行号
- -c: 统计数量
- -E: 扩展正则
- -l: 只显示文件名
- -o: 只输出匹配部分

## 示例代码

```bash
#!/bin/bash

# 基本用法
grep "error" logfile.txt

# 忽略大小写
grep -i "error" logfile.txt

# 显示行号
grep -n "pattern" file.txt

# 反向匹配（不包含的行）
grep -v "注释" file.txt

# 递归搜索目录
grep -r "TODO" /path/to/dir/

# 扩展正则（| 或 + 等）
grep -E "error|warning" logfile.txt

# 只显示匹配的部分
grep -o "[0-9]*" file.txt

# 只显示匹配的文件名
grep -l "pattern" *.txt

# 统计匹配行数
grep -c "error" logfile.txt

# 显示匹配行及前后几行
grep -B 2 "pattern" file.txt  # 前2行
grep -A 3 "pattern" file.txt  # 后3行
grep -C 2 "pattern" file.txt  # 前后各2行

# 颜色高亮（默认）
grep --color=auto "error" logfile.txt

# 从管道输入
cat logfile.txt | grep "error" | grep -v "debug"

# 多文件搜索
grep "pattern" file1.txt file2.txt file3.txt

# 匹配以...开头/结尾
grep "^start" file.txt   # 以 start 开头的行
grep "end$" file.txt     # 以 end 结尾的行

# 常用正则模式
grep "^[0-9]*$" file.txt    # 纯数字行
grep "^[a-zA-Z]*$" file.txt # 纯字母行
grep "^\s*#" file.txt       # 注释行
grep "^\s*$" file.txt       # 空行
```
