# find

> **分类**：文件查找
> **说明**：在目录树中查找文件

---

## 语法

```bash
find [path] [expression]
```

## 常用选项

- -name: 按名称
- -type: 按类型(f/d/l)
- -size: 按大小
- -mtime: 按修改时间
- -exec: 对结果执行命令
- -delete: 删除匹配的文件

## 示例代码

```bash
#!/bin/bash

# 按名称查找
find /path -name "*.txt"
find /path -iname "test"  # 忽略大小写

# 按类型查找
find /path -type f   # 普通文件
find /path -type d   # 目录
find /path -type l   # 符号链接

# 按大小查找
find /path -size +10M   # 大于10MB
find /path -size -1k    # 小于1KB
find /path -size 100c   # 正好100字节

# 按时间查找
find /path -mtime -7   # 7天内修改的
find /path -mtime +30  # 30天前修改的
find /path -mmin -60   # 60分钟内修改的
find /path -newer ref.txt  # 比 ref.txt 新的

# 按权限查找
find /path -perm 755
find /path -perm -u+s   # 有 SUID 位的

# 按用户/组
find /path -user username
find /path -group groupname

# 查找深度限制
find /path -maxdepth 2 -name "*.txt"  # 最多2层

# 对找到的文件执行命令
find /path -name "*.log" -exec rm {} \;
find /path -name "*.txt" -exec cat {} \;
find /path -name "*.bak" -delete  # 直接删除

# 查找并压缩
find /path -name "*.log" -exec gzip {} \;

# 按多个条件查找（AND）
find /path -name "*.txt" -size +1M

# 或条件（OR）
find /path \( -name "*.txt" -o -name "*.md" \)

# 非条件（NOT）
find /path -not -name "*.tmp"

# 查找空文件
find /path -empty

# 查找后复制到某处
find /path -name "*.jpg" -exec cp {} /dest/ \;
```
