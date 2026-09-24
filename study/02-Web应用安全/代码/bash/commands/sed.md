# sed

> **分类**：文本处理
> **说明**：流编辑器，用于文本替换和转换

---

## 语法

```bash
sed [options] "command" [files]
```

## 示例代码

```bash
#!/bin/bash

# 基本替换（每行第一个匹配）
sed "s/old/new/" file.txt

# 全局替换（每行所有匹配）
sed "s/old/new/g" file.txt

# 忽略大小写
sed "s/old/new/gi" file.txt

# 原地修改文件（直接修改原文件）
sed -i "s/old/new/g" file.txt
# macOS: sed -i "" "s/old/new/g" file.txt

# 备份后修改
sed -i.bak "s/old/new/g" file.txt  # 生成 .bak 备份

# 删除行
sed "5d" file.txt          # 删除第5行
sed "1,3d" file.txt        # 删除1-3行
sed "/pattern/d" file.txt  # 删除匹配的行
sed "/^$/d" file.txt       # 删除空行
sed "/^#/d" file.txt       # 删除注释行

# 打印指定行
sed -n "5p" file.txt       # 只打印第5行
sed -n "1,10p" file.txt    # 打印1-10行
sed -n "/pattern/p" file.txt  # 打印匹配的行

# 替换分隔符（/ 可以换成其他字符）
sed "s|/usr/local|/opt|" file.txt  # 用 | 当分隔符

# 多个命令
sed -e "s/foo/bar/g" -e "s/baz/qux/g" file.txt

# 在匹配行后插入
sed "/pattern/a\新行内容" file.txt

# 在匹配行前插入
sed "/pattern/i\前置内容" file.txt

# 变量替换
name="Alice"
sed "s/USER/$name/g" file.txt

# 批量替换多个文件
sed -i "s/old/new/g" *.txt

# 只替换第N次匹配
sed "s/old/new/2" file.txt  # 每行第2个匹配

# 替换多个空格为一个
sed "s/  */ /g" file.txt

# 删除首尾空白
sed "s/^[[:space:]]*//;s/[[:space:]]*$//" file.txt
```
