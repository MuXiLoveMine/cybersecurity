# echo

> **分类**：输出
> **说明**：输出一行文本

---

## 语法

```bash
echo [options] [string]
```

## 常用选项

- -n: 不换行
- -e: 解释转义字符

## 示例代码

```bash
#!/bin/bash

# 基本输出
echo "Hello, World!"

# 不换行
echo -n "输入你的名字: "

# 转义字符（需要 -e）
echo -e "第一行\n第二行\t制表符"

# 变量输出
name="Alice"
echo "你好, $name!"
echo "你好, ${name}!"  # 更明确的写法

# 命令替换
echo "今天是: $(date)"
echo "当前目录: $(pwd)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'  # 恢复默认
echo -e "${RED}错误${NC}: 出错了"
echo -e "${GREEN}成功${NC}: 操作完成"

# 单引号 vs 双引号
echo '变量不会被解析: $name'   # 原样输出
echo "变量会被解析: $name"     # 解析变量
```
