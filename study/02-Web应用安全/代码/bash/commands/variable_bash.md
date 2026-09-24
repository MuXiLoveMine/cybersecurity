# variable_bash

> **分类**：变量
> **说明**：Shell 变量定义与使用

---

## 语法

```bash
variable_name=value  （等号两边不能有空格）
```

## 类型

用户变量/环境变量/位置参数/特殊变量

## 示例代码

```bash
#!/bin/bash

# 定义变量（等号两边不能有空格！）
name="Alice"
age=25
pi=3.14159

# 使用变量
echo "姓名: $name"
echo "姓名: ${name}"  # 更推荐，明确边界

# 只读变量
readonly MAX_SIZE=100

# 环境变量（子进程可继承）
export PATH="$PATH:/usr/local/bin"

# 删除变量
unset age

# ===== 特殊变量 =====
echo "脚本名: $0"
echo "参数1: $1"
echo "参数2: $2"
echo "所有参数: $@"
echo "所有参数(单串): $*"
echo "参数个数: $#"
echo "当前PID: $$"
echo "上一个命令退出码: $?"
echo "后台最后一个进程PID: $!"

# ===== 位置参数 =====
echo "脚本名: $0"
echo "第一个参数: $1"
echo "第十个参数: ${10}"  # 10以上要用大括号

# 遍历所有参数
for arg in "$@"; do
    echo "参数: $arg"
done

# ===== 默认值 =====
echo "${name:-默认值}"   # name 为空或未设置时用默认值
echo "${name:=默认值}"   # 同上，且会给 name 赋值
echo "${name:?未设置}"   # name 未设置时报错
echo "${name:+有值}"     # name 有值时输出后面的

# ===== 命令替换 =====
current_dir=$(pwd)
files_count=$(ls | wc -l)
echo "当前目录: $current_dir，文件数: $files_count"

# 反引号方式（旧写法）
today=`date +%Y-%m-%d`

# ===== 算术运算 =====
a=10
b=3
echo $((a + b))   # 13
echo $((a - b))   # 7
echo $((a * b))   # 30
echo $((a / b))   # 3（整数除法）
echo $((a % b))   # 1（取余）
echo $((a ** 2))  # 100（幂）

# 自增/自减
i=0
((i++))
((i += 5))
```
