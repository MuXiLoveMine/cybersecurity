# Bash/Shell 编程基础与安全学习资源

> 本文系统介绍 Bash/Shell 编程基础与安全领域应用：Shell 在安全中的定位、Bash 编程基础（安全视角）、常用命令速查、安全运维核心用法、2026 年免费学习资源、推荐 GitHub 项目，以及两个可运行的示例脚本（basics.sh 和 security_cases.sh）。面向运维工程师与安全工程师，全部内容从防御、自动化和授权测试的正向角度出发。

---

## 目录

- [一、Bash/Shell 在网络安全中的定位](#一bashshell-在网络安全中的定位)
- [二、Bash 编程基础（安全视角）](#二bash-编程基础安全视角)
- [三、常用命令速查](#三常用命令速查)
- [四、安全运维核心用法](#四安全运维核心用法)
- [五、2026 年免费学习资源](#五2026-年免费学习资源)
- [六、2026 年推荐 GitHub 项目](#六2026-年推荐-github-项目)
- [七、示例代码文件](#七示例代码文件)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、Bash/Shell 在网络安全中的定位

### 1.1 为什么安全从业者必须掌握 Bash

**Bash（Bourne Again Shell）** 是 Linux 系统的默认 Shell，也是安全运维的核心脚本语言。任何 Linux 环境里都有 Bash，它是你和系统对话的最直接方式。

| 优势 | 说明 |
|------|------|
| **无处不在** | 任何 Linux/Unix 系统都有 Shell，不用额外安装 |
| **最快自动化** | 想快速做件事，写几行 Bash 比什么都快 |
| **管道哲学** | 把小工具用管道串起来，组合出强大的能力 |
| **系统级能力** | 直接操作文件、进程、网络，调用所有系统命令 |
| **应急响应必备** | 紧急情况下，系统里不一定有 Python，但一定有 Bash |
| **运维基本功** | 看不懂 Bash 脚本，Linux 安全运维没法做 |

### 1.2 Shell 类型对比

| Shell | 全称 | 默认系统 | 特点 | 安全场景 |
|-------|------|---------|------|---------|
| **Bash** | Bourne Again Shell | 大多数 Linux（Ubuntu/CentOS 等） | 功能丰富、最常用、脚本生态最好 | ✅ 脚本开发首选 |
| **sh** | Bourne Shell | 传统 Unix、部分嵌入式 | 最简、兼容性最好，但功能少 | ✅ 最简脚本兼容 |
| **zsh** | Z Shell | macOS（Catalina+）、手动安装 | 交互强、插件多、Oh My Zsh | ✅ 日常交互使用 |
| **dash** | Debian Almquist Shell | Debian/Ubuntu 的 /bin/sh | 轻量、快速，适合启动脚本 | ⚠️ 功能少，注意兼容问题 |
| **ksh** | Korn Shell | AIX、Solaris 等 Unix | 商业 Unix 常用 | ⚠️ 特定系统才用 |
| **fish** | Friendly Interactive Shell | 手动安装 | 友好、语法高亮、自动补全 | ⚠️ 语法差异大，不适合写通用脚本 |

> **安全脚本的最佳实践**：生产环境的脚本优先用 Bash 写（功能全、兼容性好），如果追求最大兼容性（比如嵌入式、精简系统），可以用 POSIX sh 语法。交互使用可以选 zsh/fish 提升效率。

### 1.3 安全领域的应用方向

| 方向 | Bash 的作用 | 典型场景 |
|------|-----------|---------|
| **日志分析** | 快速过滤、统计、提取信息 | grep 找关键字、awk 统计 Top N、sed 清洗数据 |
| **自动化巡检** | 批量检查系统安全状态 | 基线检查脚本、健康检查、配置审计 |
| **应急响应** | 快速信息收集和排查 | 一键信息收集脚本、进程排查、日志取证 |
| **批量运维** | 多服务器批量操作 | 批量改配置、批量部署、批量检查 |
| **备份与恢复** | 自动备份和恢复脚本 | 配置备份、日志归档、数据库备份 |
| **安全监控** | 简单的监控和告警 | 磁盘/CPU/内存监控、异常登录检测 |
| **渗透测试（授权）** | 信息收集和后渗透脚本 | 枚举脚本、权限提升检测、数据提取 |

> ⚠️ **重要声明**：Bash 脚本本身是中性的工具。本文所有内容均从防御、运维和授权测试的角度讲解。使用 Bash 编写的任何脚本，只能在自己管理的或有明确书面授权的系统上运行。未经授权对他人系统进行探测、入侵、破坏是违法行为。

---

## 二、Bash 编程基础（安全视角）

### 2.1 第一个脚本

```bash
#!/bin/bash
# hello.sh —— 我的第一个 Bash 脚本
# 运行方式：chmod +x hello.sh && ./hello.sh

echo "Hello, Security World!"
echo "当前时间: $(date)"
echo "当前用户: $USER"
echo "当前目录: $PWD"
```

**脚本结构三要素**：
1. **Shebang（`#!/bin/bash`）**：第一行，告诉系统用什么解释器执行
2. **注释（`#` 开头）**：说明脚本用途，方便自己和别人理解
3. **命令**：一行一个命令，从上到下执行

```bash
# 运行脚本的三种方式：
chmod +x script.sh && ./script.sh   # 1. 加执行权限，直接运行（推荐）
bash script.sh                       # 2. 用 bash 解释器运行
source script.sh                     # 3. 在当前 shell 中运行（影响当前环境）
```

### 2.2 变量与环境变量

```bash
# ===== 自定义变量 =====
# 注意：等号两边不能有空格！
name="Alice"
age=25
ip_address="192.168.1.100"

# 使用变量：变量名前加 $
echo "姓名: $name"
echo "年龄: $age"
echo "IP: $ip_address"

# 推荐用花括号把变量名括起来，避免歧义
echo "${name}的IP是${ip_address}"

# ===== 环境变量 =====
# 系统预置的环境变量，所有进程都能访问
echo "当前用户: $USER"
echo "宿主名: $HOSTNAME"
echo "Home 目录: $HOME"
echo "Shell: $SHELL"
echo "PATH: $PATH"
echo "PID: $$"            # 当前脚本的进程号
echo "退出码: $?"         # 上一个命令的退出码（0=成功，非0=失败）
echo "参数数量: $#"       # 脚本的参数数量
echo "所有参数: $@"       # 所有参数列表

# 查看所有环境变量
env
printenv

# 设置环境变量（子进程能访问）
export MY_VAR="hello"

# 只读变量（不能修改）
readonly PI=3.14159

# ===== 特殊变量 =====
$0    # 脚本名称
$1    # 第一个参数（$2 第二个，以此类推）
$@    # 所有参数（列表形式）
$#    # 参数个数
$$    # 当前进程 PID
$?    # 上一条命令的退出状态码
$!    # 最近一个后台进程的 PID
```

### 2.3 引用与转义

Bash 里引号的学问很大，搞错了很容易出 bug。

```bash
# ===== 三种引号 =====

# 1. 双引号 " " —— 弱引用
# 会解析变量、命令替换、转义字符
name="Bob"
echo "你好, $name"          # 输出：你好, Bob
echo "今天是 $(date)"       # 输出：今天是 星期三...

# 2. 单引号 ' ' —— 强引用
# 原样输出，什么都不解析
echo '你好, $name'          # 输出：你好, $name
echo '今天是 $(date)'       # 输出：今天是 $(date)

# 3. 反引号 ` ` 或 $() —— 命令替换
# 执行命令，把输出替换到这里
result=`date`               # 老写法
result=$(date)              # 推荐写法（可嵌套）
echo "当前时间: $result"

# ===== 转义字符 =====
# 反斜线 \ 转义特殊字符
echo "价格: \$100"          # $ 转义，输出：价格: $100
echo "换行: line1\nline2"   # \n 是换行（需要 echo -e 才生效）
echo -e "第一行\n第二行"

# ===== 常用转义序列 =====
\n    换行
\t    制表符（Tab）
\\    反斜线本身
\$    美元符号
\"    双引号
\'    单引号（单引号内无法转义单引号）
```

> **安全小贴士**：写脚本时，变量引用尽量用双引号括起来，防止变量为空或包含空格时出问题。比如 `[ "$name" = "alice" ]` 比 `[ $name = "alice" ]` 安全得多。

### 2.4 流程控制

#### （1）条件判断 if

```bash
# ===== if 语句 =====
# 基本语法：
if [ 条件 ]; then
    # 条件成立执行
elif [ 条件 ]; then
    # 第二个条件
else
    # 都不成立执行
fi

# 示例：检查文件是否存在
filename="test.txt"
if [ -f "$filename" ]; then
    echo "$filename 存在"
elif [ -d "$filename" ]; then
    echo "$filename 是目录"
else
    echo "$filename 不存在"
fi

# ===== 常用测试条件 =====

# 文件测试：
[ -f file ]    # 是普通文件
[ -d dir ]     # 是目录
[ -e path ]    # 存在（文件或目录）
[ -r file ]    # 可读
[ -w file ]    # 可写
[ -x file ]    # 可执行
[ -s file ]    # 文件大小 > 0（非空）
[ file1 -nt file2 ]  # file1 比 file2 新
[ file1 -ot file2 ]  # file1 比 file2 旧

# 字符串测试：
[ "$a" = "$b" ]     # 相等
[ "$a" != "$b" ]    # 不相等
[ -z "$str" ]       # 字符串长度为 0（空）
[ -n "$str" ]       # 字符串长度不为 0
[ "$a" \< "$b" ]    # 按字典序 a 在 b 前面（注意转义 <）

# 数字测试：
[ $a -eq $b ]   # 等于 equal
[ $a -ne $b ]   # 不等于 not equal
[ $a -gt $b ]   # 大于 greater than
[ $a -lt $b ]   # 小于 less than
[ $a -ge $b ]   # 大于等于 greater or equal
[ $a -le $b ]   # 小于等于 less or equal

# 逻辑运算：
[ 条件1 -a 条件2 ]   # 与（AND）
[ 条件1 -o 条件2 ]   # 或（OR）
[ ! 条件 ]           # 非（NOT）

# 也可以用 && 和 || 组合多个 [ ]
[ -f "$file" ] && [ -r "$file" ]    # 文件存在且可读
[ "$a" = "yes" ] || [ "$b" = "yes" ]  # a 或 b 是 yes
```

#### （2）case 分支

```bash
# ===== case 语句 =====
# 适合多分支的场景，比多个 if-elif 清晰

echo "请选择操作:"
echo "1. 系统信息"
echo "2. 磁盘检查"
echo "3. 网络状态"
read -p "输入选项: " choice

case "$choice" in
    1)
        echo "=== 系统信息 ==="
        uname -a
        ;;
    2)
        echo "=== 磁盘使用 ==="
        df -h
        ;;
    3)
        echo "=== 网络连接 ==="
        ss -tulnp
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac

# case 也支持通配符匹配
os=$(uname -s)
case "$os" in
    Linux)
        echo "Linux 系统"
        ;;
    Darwin)
        echo "macOS 系统"
        ;;
    CYGWIN*|MINGW*)
        echo "Windows 系统"
        ;;
    *)
        echo "未知系统: $os"
        ;;
esac
```

#### （3）for 循环

```bash
# ===== for 循环 =====

# 遍历列表
for ip in 192.168.1.1 192.168.1.2 192.168.1.3; do
    echo "检查 $ip..."
    ping -c 1 -W 1 "$ip" > /dev/null && echo "  $ip 在线" || echo "  $ip 离线"
done

# 数字范围（C 语言风格，Bash 特有）
for ((i=1; i<=10; i++)); do
    echo "第 $i 次"
done

# 遍历命令输出
for user in $(cat user_list.txt); do
    echo "处理用户: $user"
done

# 遍历文件
for file in *.log; do
    if [ -f "$file" ]; then
        echo "处理日志文件: $file"
    fi
done

# 遍历数组
fruits=("apple" "banana" "cherry")
for fruit in "${fruits[@]}"; do
    echo "水果: $fruit"
done
```

#### （4）while / until 循环

```bash
# ===== while 循环 =====
# 条件为真时执行

count=1
while [ $count -le 5 ]; do
    echo "计数: $count"
    count=$((count + 1))
done

# 逐行读取文件（推荐用法）
while IFS= read -r line; do
    echo "读取行: $line"
done < input.txt

# ===== until 循环 =====
# 条件为假时执行（直到条件为真才停止）

count=1
until [ $count -gt 5 ]; do
    echo "until 计数: $count"
    count=$((count + 1))
done

# ===== 循环控制 =====
# break    跳出整个循环
# continue 跳过本次循环，继续下一次

for i in {1..10}; do
    if [ $i -eq 5 ]; then
        continue   # 跳过 5
    fi
    if [ $i -eq 8 ]; then
        break      # 到 8 就退出
    fi
    echo "$i"
done
```

### 2.5 函数

```bash
# ===== 函数定义 =====
# 注意：函数定义必须在调用之前

# 简单函数
say_hello() {
    echo "Hello, $1!"
}

# 带返回值的函数
# Bash 函数的 return 只能返回 0~255 的数字（退出码）
# 要返回字符串，用 echo 输出，然后用 $() 捕获
add() {
    local a=$1    # local 声明局部变量
    local b=$2
    echo $((a + b))
}

# 检查 IP 格式的函数（安全脚本常用）
validate_ip() {
    local ip=$1
    local IFS=.
    local parts count=0

    # 用 . 分割
    parts=($ip)

    # 必须是 4 段
    if [ ${#parts[@]} -ne 4 ]; then
        return 1
    fi

    for part in "${parts[@]}"; do
        # 必须是数字
        if ! [[ "$part" =~ ^[0-9]+$ ]]; then
            return 1
        fi
        # 必须在 0-255 之间
        if [ "$part" -lt 0 ] || [ "$part" -gt 255 ]; then
            return 1
        fi
        count=$((count + 1))
    done

    return 0
}

# ===== 函数调用 =====
say_hello "World"

result=$(add 3 5)
echo "3 + 5 = $result"

if validate_ip "192.168.1.1"; then
    echo "IP 格式有效"
else
    echo "IP 格式无效"
fi

# ===== 函数中的变量作用域 =====
# 不加 local 的变量是全局的
# 加 local 的变量只在函数内部有效（推荐！）
```

### 2.6 输入输出重定向与管道

这是 Shell 最强大的特性之一——把多个小工具用管道串起来。

```bash
# ===== 重定向 =====

# 标准输出重定向（覆盖）
echo "hello" > output.txt

# 标准输出重定向（追加）
echo "world" >> output.txt

# 标准错误重定向
ls /nonexistent 2> error.log

# 标准输出和错误都重定向到同一个文件
command > output.log 2>&1
# 或 Bash 4+ 的简写：
command &> output.log

# 丢弃输出（黑洞）
command > /dev/null 2>&1

# 标准输入重定向（从文件读）
cat < input.txt

# ===== 管道 =====
# 把前一个命令的输出作为后一个命令的输入

# 统计日志中 IP 出现次数，取前 10
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# 查找所有失败登录，统计 IP
grep "Failed password" auth.log | awk '{print $NF}' | sort | uniq -c | sort -rn

# ===== Here Document =====
# 在脚本中嵌入多行文本
cat << 'EOF'
这是一段多行文本
可以写很多行
变量不会被解析（因为加了引号的 EOF）
EOF

cat << EOF
这是另一段
当前用户是 $USER
变量会被解析
EOF

# 用 heredoc 写入文件
cat > config.txt << 'EOF'
[security]
enabled = true
port = 22
EOF

# ===== Here String =====
# 把字符串作为输入传给命令
tr a-z A-Z <<< "hello world"
```

### 2.7 命令替换与算术运算

```bash
# ===== 命令替换 =====
# 把命令的输出赋值给变量

# 两种写法：
current_date=$(date)     # 推荐（可嵌套）
current_date=`date`      # 老写法（不推荐，嵌套麻烦）

# 嵌套示例：统计当前目录下的文件数
file_count=$(ls | wc -l)
echo "当前目录有 $file_count 个文件"

# ===== 算术运算 =====

# $(( 表达式 )) —— 整数运算
a=10
b=3
echo "a + b = $((a + b))"
echo "a - b = $((a - b))"
echo "a * b = $((a * b))"
echo "a / b = $((a / b))"    # 整数除法，结果是 3
echo "a % b = $((a % b))"    # 取余，结果是 1

# 自增自减
i=0
i=$((i + 1))    # 加 1
((i++))          # 后置自增（Bash 特有）
((++i))          # 前置自增

# let 命令
let result=a+b
echo $result

# expr 命令（兼容性更好，功能弱一点）
result=$(expr 10 + 3)
echo $result

# ⚠️ 注意：Bash 只支持整数运算
# 小数运算需要用 bc 或 awk
echo "10 / 3 = $(echo "scale=2; 10 / 3" | bc)"
awk 'BEGIN {printf "10 / 3 = %.2f\n", 10/3}'
```

### 2.8 测试与判断

```bash
# ===== [ ] vs [[ ]] =====
# [ ]    POSIX 标准，兼容性最好
# [[ ]]   Bash 增强版，功能更强（支持正则、逻辑运算符等）

# 字符串正则匹配（只有 [[ ]] 支持）
ip="192.168.1.1"
if [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "看起来像 IP 地址"
fi

# 逻辑运算（[[ ]] 里可以直接用 && ||）
if [[ -f "$file" && -r "$file" ]]; then
    echo "文件存在且可读"
fi

# ===== 退出码 =====
# 每个命令执行完都有一个退出码（$?）
# 0 = 成功，非 0 = 失败（1-255）

ls /tmp
echo "退出码: $?"    # 0 成功

ls /nonexistent
echo "退出码: $?"    # 非 0 失败

# ===== && 和 || =====
# 短路运算符，根据上一个命令的退出码决定是否执行下一个

# &&：前面成功了，才执行后面
mkdir backup && cp *.txt backup/
# 意思：创建目录成功了，才复制文件

# ||：前面失败了，才执行后面
ping -c 1 192.168.1.1 || echo "主机不可达"
# 意思：ping 失败了，才输出提示

# 组合使用
[ -f "$config" ] && source "$config" || echo "配置文件不存在"
```

### 2.9 脚本调试与安全选项

```bash
# ===== 常用调试选项 =====
# 可以写在脚本开头，也可以在命令行用 bash -x script.sh

set -e      # 遇到错误立即退出（命令返回非 0 就退出）
            # ⚠️ 注意：有些命令正常也会返回非 0，可能误触发
set -u      # 使用未定义的变量时报错（防止拼写错误）
set -x      # 执行前打印命令（调试用，看实际执行了什么）
set -o pipefail  # 管道中任何一个命令失败，整个管道就算失败
set -n      # 只检查语法，不执行

# 常用组合：安全脚本的开头
#!/bin/bash
set -euo pipefail
# 这是很多严谨脚本的标准开头
# -e: 出错即停
# -u: 未定义变量报错
# -o pipefail: 管道失败传播

# ===== trap 信号捕获 =====
# 脚本退出时执行清理操作（很有用！）

cleanup() {
    echo "正在清理临时文件..."
    rm -f /tmp/temp_$$
    echo "清理完成"
}

trap cleanup EXIT    # 脚本退出时（正常或异常）执行 cleanup

# 捕获其他信号
trap 'echo "收到中断信号"; exit 1' INT    # Ctrl+C
trap 'echo "收到终止信号"; exit 1' TERM   # kill

# ===== 调试技巧 =====
# 1. 用 bash -x 运行脚本，看每一步执行了什么
bash -x script.sh

# 2. 在关键位置加 echo 输出变量值
echo "DEBUG: ip = $ip, port = $port"

# 3. 用 set -n 检查语法错误
bash -n script.sh

# 4. 分段注释，逐步排查
```

> ⚠️ **`set -e` 的坑**：`set -e` 不是万能的。比如管道命令、if 条件里的命令、函数返回值等情况可能不触发退出。重要的地方还是要自己判断返回值。

---

## 三、常用命令速查

### 3.1 文件与目录

| 命令 | 作用 | 安全场景常用示例 |
|------|------|----------------|
| **ls** | 列出目录内容 | `ls -la` 详细列表、`ls -ltr` 按时间排序 |
| **cd** | 切换目录 | `cd -` 回到上一个目录、`cd ~` 回家目录 |
| **pwd** | 显示当前路径 | 确认当前位置 |
| **mkdir** | 创建目录 | `mkdir -p a/b/c` 递归创建 |
| **rmdir** | 删除空目录 | 只能删空目录 |
| **cp** | 复制文件/目录 | `cp -r src dest` 递归复制目录 |
| **mv** | 移动/重命名 | `mv old new` |
| **rm** | 删除 | `rm -rf dir` 递归删除（⚠️ 高风险！） |
| **find** | 查找文件 | 查找指定名称/大小/时间/权限的文件 |
| **file** | 查看文件类型 | 判断文件真实类型（不是看后缀） |
| **stat** | 文件详细信息 | 权限、大小、时间戳（atime/mtime/ctime） |
| **chmod** | 修改权限 | `chmod 644 file`、`chmod +x script.sh` |
| **chown** | 修改属主 | `chown user:group file` |
| **ln** | 创建链接 | `ln -s target link` 软链接、`ln target link` 硬链接 |

**find 命令（安全排查神器）**：

```bash
# 按名称查找
find / -name "*.log" -type f 2>/dev/null
find /etc -name "*.conf"

# 按类型查找
find / -type f     # 文件
find / -type d     # 目录
find / -type l     # 符号链接

# 按大小查找
find / -size +100M          # 大于 100M 的文件
find / -size -1k            # 小于 1K 的文件

# 按时间查找
find / -mtime -1            # 24 小时内修改过的文件
find / -mtime +7            # 7 天前修改的
find / -atime -1            # 24 小时内访问过的
find / -ctime -1            # 24 小时内状态改变的
find / -newer file.txt      # 比 file.txt 新的文件

# 按权限查找
find / -perm -4000 -type f  # SUID 文件（安全排查重点）
find / -perm -2000 -type f  # SGID 文件
find / -perm -1000 -type d  # Sticky bit 目录
find / -perm /o+w -type f   # 全局可写的文件

# 按用户/组查找
find / -user root           # root 拥有的文件
find / -nouser              # 没有属主的文件
find / -nogroup             # 没有属组的文件

# 执行操作（对找到的文件执行命令）
find /tmp -name "*.tmp" -delete          # 删除（谨慎使用）
find / -perm -4000 -ls                    # 详细列出
find /var/log -name "*.log" -exec ls -l {} \;  # 对每个文件执行命令
```

> ⚠️ **find -delete 警告**：`find ... -delete` 会直接删除文件，没有提示，不可恢复。使用前先用 `-print` 确认要删的文件对不对！

### 3.2 文本处理三件套

grep、sed、awk 是 Shell 文本处理的三大利器，安全脚本中天天用。

#### grep — 查找过滤

```bash
# 基本用法
grep "pattern" file.txt          # 在文件中查找匹配的行
grep -i "pattern" file.txt       # 忽略大小写
grep -v "pattern" file.txt       # 反向匹配（不包含的行）
grep -c "pattern" file.txt       # 统计匹配的行数
grep -n "pattern" file.txt       # 显示行号
grep -r "pattern" /path          # 递归搜索目录下所有文件
grep -l "pattern" *.txt          # 只显示包含匹配的文件名
grep -o "pattern" file.txt       # 只输出匹配的部分（不是整行）
grep -E "regex" file.txt         # 扩展正则（相当于 egrep）
grep -f patterns.txt file.txt    # 从文件读取匹配模式

# 安全场景示例：
grep "Failed password" /var/log/auth.log    # 找登录失败
grep -i error *.log                         # 找错误信息
grep -r "password" /etc --include="*.conf"  # 配置文件中找密码
grep -oP '\d+\.\d+\.\d+\.\d+' access.log    # 提取 IP 地址（Perl 正则）
```

#### sed — 流编辑器（替换/删除/插入）

```bash
# 替换（最常用）
sed 's/old/new/' file.txt         # 每行第一个 old 换成 new
sed 's/old/new/g' file.txt        # 所有 old 都换成 new（g = global）
sed 's/old/new/gi' file.txt       # 忽略大小写替换
sed -i 's/old/new/g' file.txt     # 直接修改文件（in-place）⚠️

# 删除行
sed '5d' file.txt                 # 删除第 5 行
sed '1,5d' file.txt               # 删除 1-5 行
sed '/pattern/d' file.txt         # 删除匹配的行
sed '/^$/d' file.txt              # 删除空行
sed '/^\s*#/d' file.txt           # 删除注释行（# 开头）

# 插入/追加
sed '5i\new line' file.txt        # 第 5 行前插入
sed '5a\new line' file.txt        # 第 5 行后追加

# 打印指定行
sed -n '5p' file.txt              # 打印第 5 行
sed -n '1,10p' file.txt           # 打印 1-10 行
sed -n '/pattern/p' file.txt      # 打印匹配的行（类似 grep）

# 安全场景示例：
sed -i 's/password=.*/password=***/g' config.ini  # 脱敏（把密码替换掉）
sed '/^\s*#/d; /^$/d' config.conf  # 去掉注释和空行
sed -i 's/\r$//' file.txt          # 去掉 Windows 换行符（\r）
```

> ⚠️ **sed -i 警告**：`sed -i` 直接修改文件，修改前务必备份！可以用 `sed -i.bak` 先备份再修改（会生成 .bak 文件）。

#### awk — 文本处理的"瑞士军刀"

```bash
# 基本结构：awk 'pattern { action }' file

# 按列提取（awk 的强项）
awk '{print $1}' access.log       # 提取第一列
awk '{print $1, $7}' access.log   # 提取第 1 列和第 7 列
awk -F: '{print $1}' /etc/passwd  # 用冒号分隔（默认是空格/Tab）

# 内置变量
#   $0    整行
#   $1-$N 第 N 列
#   NF    列数（Number of Fields）
#   NR    行号（Number of Records）
#   FS    输入字段分隔符
#   OFS   输出字段分隔符

# 条件过滤
awk '$9 == 200' access.log        # 第 9 列等于 200 的行
awk '$9 != 200 {print $1, $7, $9}' access.log  # 非 200 的请求
awk '$NF > 10000' access.log      # 最后一列大于 10000

# 统计汇总
awk '{sum += $NF} END {print sum}' access.log   # 最后一列求和
awk '{count[$1]++} END {for (ip in count) print count[ip], ip}' access.log | sort -rn
# 统计每个 IP 出现次数（Top N 统计神器）

# 安全场景示例：
# 统计访问最多的前 10 个 IP
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# 统计 HTTP 状态码分布
awk '{print $9}' access.log | sort | uniq -c | sort -rn

# 找失败登录最多的 IP（auth.log）
grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -10
```

### 3.3 其他文本处理命令

| 命令 | 作用 | 常用示例 |
|------|------|---------|
| **cat** | 输出文件内容 | `cat file.txt`、`cat -n file.txt` 显示行号 |
| **less** | 分页查看（推荐，功能多） | `less file.txt`、`/pattern` 搜索 |
| **head** | 看开头 | `head -20 file.txt` 前 20 行 |
| **tail** | 看结尾 | `tail -f log.txt` 实时跟踪、`tail -100` 最后 100 行 |
| **sort** | 排序 | `sort file.txt`、`sort -rn` 数字逆序、`sort -u` 去重排序 |
| **uniq** | 去重（相邻重复行） | `uniq file.txt`、`uniq -c` 统计次数、`uniq -d` 只显示重复的 |
| **wc** | 统计 | `wc -l` 行数、`wc -c` 字节数、`wc -w` 单词数 |
| **cut** | 切割列 | `cut -d: -f1 /etc/passwd` 用冒号切取第 1 列 |
| **tr** | 字符转换 | `tr a-z A-Z` 转大写、`tr -d '\r'` 删除回车 |
| **tee** | 分叉输出 | `command \| tee file.txt` 既输出到屏幕又写入文件 |
| **paste** | 合并文件 | `paste file1 file2` 按列合并 |
| **diff** | 比较文件 | `diff file1 file2`、`diff -u` unified 格式 |

### 3.4 进程管理

| 命令 | 作用 | 安全场景常用示例 |
|------|------|----------------|
| **ps** | 查看进程 | `ps aux` 所有进程、`ps -ef` 全格式 |
| **top** | 实时进程监控 | 看 CPU/内存占用最高的进程 |
| **htop** | 增强版 top | 更好用的进程监控（需安装） |
| **pstree** | 进程树 | 看进程父子关系 |
| **kill** | 终止进程 | `kill PID`、`kill -9 PID` 强制杀（⚠️ 慎用） |
| **killall** | 按名称杀进程 | `killall nginx` 杀所有 nginx 进程 |
| **pkill** | 按模式杀进程 | `pkill -f pattern` 按命令行匹配杀 |
| **pgrep** | 查找进程 PID | `pgrep -f nginx` 找 PID |
| **nice/renice** | 优先级 | 调整进程优先级 |
| **nohup** | 后台运行 | `nohup command &` 不挂断后台运行 |

### 3.5 网络命令

| 命令 | 作用 | 安全场景常用示例 |
|------|------|----------------|
| **ss** | socket 统计 | `ss -tulnp` 监听端口、`ss -ant` 所有连接 |
| **netstat** | 网络统计（旧） | `netstat -tulnp`、`netstat -an` |
| **ip** | 网络配置 | `ip addr`、`ip route`、`ip link` |
| **ping** | 连通性测试 | `ping -c 3 ip`、`ping -f ip` flood（需 root） |
| **traceroute** | 路由跟踪 | `traceroute ip`、`traceroute -T -p 443 ip` |
| **curl** | HTTP 客户端 | 测试 Web 服务、API 调用、下载文件 |
| **wget** | 文件下载 | 下载文件，支持断点续传 |
| **nc** | 网络瑞士军刀 | 端口测试、文件传输、简单聊天 |
| **tcpdump** | 抓包 | 网络流量捕获和分析（需 root） |
| **dig** | DNS 查询 | DNS 解析测试（比 nslookup 强大） |
| **nslookup** | DNS 查询 | 简单的 DNS 测试 |
| **ssh** | 远程登录 | 安全远程登录和执行命令 |
| **scp** | 安全复制 | 远程文件传输（基于 SSH） |

---

## 四、安全运维核心用法

### 4.1 日志分析

日志分析是安全运维最常见的场景，Bash + 管道工具是最快的方式。

```bash
# ===== 认证日志分析 =====

# 登录失败的 IP Top 10
grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -10

# 登录成功的 IP Top 10
grep "Accepted" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -10

# 尝试登录的用户名 Top 10
grep "Failed password" /var/log/auth.log | grep -oP 'for \K\S+' | sort | uniq -c | sort -rn | head -10

# 暴力破解检测（某个 IP 失败次数超过阈值）
THRESHOLD=5
grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | awk -v t=$THRESHOLD '$1 > t {print $2, $1}'

# 非工作时间的登录（比如凌晨 0-6 点）
grep "Accepted" /var/log/auth.log | awk '$2 >= "00:00" && $2 <= "06:00" {print}'

# ===== Nginx/Apache 日志分析 =====

# 状态码分布
awk '{print $9}' access.log | sort | uniq -c | sort -rn

# 404 最多的 URL Top 10
awk '$9 == 404 {print $7}' access.log | sort | uniq -c | sort -rn | head -10

# 访问量最大的 IP Top 10
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# 流量最大的 URL Top 10
awk '{bytes[$7] += $NF} END {for (url in bytes) print bytes[url], url}' access.log | sort -rn | head -10

# 慢请求（响应时间长，需要日志包含耗时字段）
# 根据具体日志格式调整
```

### 4.2 系统巡检

```bash
#!/bin/bash
# ===== 系统安全巡检脚本（简化版）=====
# 用法：sudo ./system_check.sh

echo "=== 系统安全巡检报告 ==="
echo "时间: $(date)"
echo "主机: $(hostname)"
echo ""

# 1. 系统信息
echo "[1] 系统信息"
echo "  内核: $(uname -r)"
echo "  发行版: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "  运行时间: $(uptime -p)"
echo ""

# 2. 用户检查
echo "[2] 用户检查"
echo "  UID 为 0 的账号:"
awk -F: '$3 == 0 {print "    " $1}' /etc/passwd
echo "  空密码账号:"
awk -F: '$2 == "" {print "    " $1}' /etc/shadow 2>/dev/null || echo "    (需要 root 权限查看)"
echo ""

# 3. SUID/SGID 文件
echo "[3] SUID/SGID 文件"
echo "  SUID 文件数: $(find / -perm -4000 -type f 2>/dev/null | wc -l)"
echo "  SGID 文件数: $(find / -perm -2000 -type f 2>/dev/null | wc -l)"
echo ""

# 4. 网络检查
echo "[4] 网络检查"
echo "  监听端口:"
ss -tulnp 2>/dev/null | head -10
echo "  防火墙状态:"
if command -v iptables >/dev/null 2>&1; then
    echo "    iptables 规则数: $(iptables -L -n 2>/dev/null | wc -l)"
fi
if command -v ufw >/dev/null 2>&1; then
    echo "    ufw: $(ufw status 2>/dev/null | head -1)"
fi
echo ""

# 5. 磁盘使用
echo "[5] 磁盘使用"
df -h | grep -E '^/dev/|文件系统'
echo ""

# 6. 内存使用
echo "[6] 内存使用"
free -h
echo ""

echo "=== 巡检完成 ==="
```

### 4.3 批量操作

```bash
# ===== 批量 SSH 执行命令 =====
# 前提：配置了 SSH 密钥免密登录

SERVERS=("server1" "server2" "server3")
USER="admin"

for server in "${SERVERS[@]}"; do
    echo "=== $server ==="
    ssh "$USER@$server" '
        echo "主机名: $(hostname)"
        echo "磁盘使用:"
        df -h /
        echo "内存使用:"
        free -h | head -2
    '
    echo ""
done

# ===== 批量文件分发 =====
for server in "${SERVERS[@]}"; do
    echo "分发配置文件到 $server..."
    scp config.conf "$USER@$server:/etc/app/"
    ssh "$USER@$server" "systemctl reload app"
done

# ⚠️ 批量操作注意事项：
# - 先在一台机器上测试，没问题再批量执行
# - 重要操作前先备份
# - 用 tmux/screen 防止 SSH 中断
# - 高风险操作要有回滚方案
```

### 4.4 应急响应

```bash
#!/bin/bash
# ===== 应急响应信息收集脚本 =====
# 快速收集系统信息，用于初步排查
# 用法：sudo ./ir_collect.sh

OUTPUT_DIR="/tmp/ir_collection_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "正在收集信息到: $OUTPUT_DIR"

# 1. 系统基本信息
{
    echo "=== 系统信息 ==="
    uname -a
    echo ""
    echo "=== 主机名 ==="
    hostname
    echo ""
    echo "=== 时间 ==="
    date
    echo ""
    echo "=== 运行时间 ==="
    uptime
} > "$OUTPUT_DIR/system.txt"

# 2. 网络信息
{
    echo "=== 接口 ==="
    ip addr
    echo ""
    echo "=== 路由 ==="
    ip route
    echo ""
    echo "=== 连接 ==="
    ss -antp
    echo ""
    echo "=== 监听端口 ==="
    ss -tulnp
    echo ""
    echo "=== ARP ==="
    ip neigh
} > "$OUTPUT_DIR/network.txt"

# 3. 进程信息
{
    echo "=== 进程列表 ==="
    ps auxf
    echo ""
    echo "=== 进程树 ==="
    pstree -p
    echo ""
    echo "=== 打开的端口/进程对应 ==="
    ss -tulnp
} > "$OUTPUT_DIR/process.txt"

# 4. 用户信息
{
    echo "=== 用户列表 ==="
    cat /etc/passwd
    echo ""
    echo "=== 最近登录 ==="
    last -20
    echo ""
    echo "=== 当前登录用户 ==="
    who
    echo ""
    echo "=== sudoers ==="
    cat /etc/sudoers 2>/dev/null | grep -v '^#' | grep -v '^$'
} > "$OUTPUT_DIR/users.txt"

# 5. 日志（最近的）
mkdir -p "$OUTPUT_DIR/logs"
if [ -f /var/log/auth.log ]; then
    tail -200 /var/log/auth.log > "$OUTPUT_DIR/logs/auth.log"
fi
if [ -f /var/log/syslog ]; then
    tail -200 /var/log/syslog > "$OUTPUT_DIR/logs/syslog.log"
fi
journalctl --since "24 hours ago" > "$OUTPUT_DIR/logs/journalctl.log" 2>/dev/null

# 6. 可疑文件
{
    echo "=== SUID 文件 ==="
    find / -perm -4000 -type f 2>/dev/null
    echo ""
    echo "=== /tmp 下的可执行文件 ==="
    find /tmp -type f -executable 2>/dev/null
    echo ""
    echo "=== 全局可写文件 ==="
    find / -xdev -type f -perm -0002 2>/dev/null | head -50
} > "$OUTPUT_DIR/suspicious_files.txt"

# 打包
tar -czf "${OUTPUT_DIR}.tar.gz" -C "$(dirname "$OUTPUT_DIR")" "$(basename "$OUTPUT_DIR")" 2>/dev/null

echo "收集完成！"
echo "输出目录: $OUTPUT_DIR"
echo "打包文件: ${OUTPUT_DIR}.tar.gz"
```

---

## 五、2026 年免费学习资源

### 5.1 资源总表

| 类别 | 资源名称 | 说明 | 适合阶段 |
|------|---------|------|---------|
| **系统入门** | Linux Journey | 免费互动式 Linux 学习教程 | 入门 |
| **Bash 课程** | bahamas10/bash-course (GitHub) | 完整的 Bash 脚本课程，免费开源 | 入门→进阶 |
| **Bash 入门** | nbicocchi/learn-bash (GitHub) | 面向初学者的 Unix 系统管理 Bash 课程 | 入门 |
| **Bash 电子书** | bobbyiliev/introduction-to-bash-scripting (GitHub) | MIT 许可的 Bash 脚本入门电子书 | 入门 |
| **命令解释** | explainshell.com | 输入任意 Shell 命令，解释每个参数的含义 | 全程（神器！） |
| **高级脚本** | Advanced Bash-Scripting Guide | 经典的 Bash 高级脚本指南 | 进阶 |
| **Bash 手册** | Bash 官方手册（gnu.org） | 最权威的 Bash 参考文档 | 进阶参考 |
| **实战练习** | OverTheWire (Bandit) | 通过游戏学习 Linux 和 Bash，从 Bandit 开始 | 入门→进阶 |
| **Shellcheck** | shellcheck.net | Shell 脚本静态检查工具，找 bug | 全程 |

### 5.2 资源使用建议

```
学习路径推荐：

  完全零基础：
    1. Linux Journey 学 Linux 基础命令
    2. bobbyiliev 的 Bash 入门电子书
    3. 跟着 bash-course 系统学

  有基础，想提升：
    1. Advanced Bash-Scripting Guide 深入学习
    2. 读优秀开源安全脚本的源码
    3. OverTheWire Bandit 练手（边玩边学）

  工具推荐（日常必用）：
    - explainshell.com：看不懂的命令贴进去，瞬间明白
    - shellcheck.net：写的脚本跑一下，找出问题
    - tldr：简化版 man 手册，直接给常用示例
```

---

## 六、2026 年推荐 GitHub 项目

### 6.1 学习资源类

| 项目 | Stars | 说明 |
|------|-------|------|
| **bahamas10/bash-course** | 课程类 | 完整的 Bash 脚本课程，从基础到高级 |
| **nbicocchi/learn-bash** | 课程类 | 面向初学者的 Unix 系统管理 Bash 课程 |
| **bobbyiliev/introduction-to-bash-scripting** | 电子书 | MIT 许可免费电子书，入门友好 |
| **MDPorsch/Bash-Scripting-for-Security** | 安全向 | 面向安全从业者的 Bash 脚本系列，含 Homelab 实验 |
| **kwxnzu/Cybersecurity101** | 入门向 | Shell 脚本基础，涵盖变量、循环、条件、自动化、cron 等 |
| **xpert4cyber/Learn2Scripting** | 综合向 | 面向自动化和安全的脚本综合指南，Bash/PowerShell/Python 都有 |

### 6.2 工具与脚本类（读源码学习）

读优秀的开源安全脚本，是提升 Bash 安全编程能力的好方法。

| 项目 | 说明 | 学习价值 |
|------|------|---------|
| **Lynis** | 系统安全审计工具（Bash 写的） | 学习大型 Bash 项目的架构和代码规范 |
| **unhide** | 查找隐藏进程的工具 | 学习底层系统排查技巧 |
| **rkhunter** | Rootkit 检测工具 | 学习恶意特征检测和系统取证 |
| **Bashfuscator** | Bash 混淆工具（防御角度学习） | 理解 Shell 混淆与检测原理 |

> ⚠️ **学习原则**：读这些项目的源码是为了学习技术和原理，理解安全工具的工作方式，从而更好地防御和检测。不要将学到的知识用于未授权的攻击或规避检测。

> **说明**：GitHub 项目的 Star 数和内容会随时间变化，建议直接搜索项目名获取最新信息。使用时请遵守各项目的开源协议。

---

## 七、示例代码文件

本文配套两个可运行的 Shell 脚本示例，位于 `code/` 目录下：

### 7.1 basics.sh — Bash 基础示例

涵盖：变量、条件判断、循环、函数、文件操作、管道、重定向、正则、命令行参数等。

**文件路径**：`code/basics.sh`

**运行方式**：
```bash
cd code
bash basics.sh
```

### 7.2 security_cases.sh — 安全案例示例

涵盖 3 个安全案例（防御/运维视角）：
- **SSH 失败登录监测**：分析 auth.log，检测暴力破解
- **日志分析工具**：多种日志统计和分析功能
- **系统安全巡检**：系统基本安全状态检查
- **文件完整性检查**：基于哈希的文件完整性校验

**文件路径**：`code/security_cases.sh`

**运行方式**：
```bash
cd code
bash security_cases.sh          # 运行所有演示
bash security_cases.sh --help   # 查看帮助
```

---

## 附：优化后的提示词模板

以下是可复用的 Bash/Shell 安全编程类提示词模板：

```markdown
# 角色
你是一名资深 Linux 系统与 Bash 脚本专家，精通 Shell 编程、
系统管理自动化与安全运维脚本开发。

# 任务
请系统介绍【主题】，包括：
1. 概念与定位（在安全运维中的作用）
2. Bash 实现方法/语法要点
3. 安全场景实战
   - 每个场景：用途 + 实现思路 + 完整脚本示例 + 说明
4. 常用命令/工具配合
5. 最佳实践与坑点
6. 学习资源推荐

# 输出要求
- Markdown 格式，按大类小类组织
- 表格对比，脚本附详细注释
- 重要术语中英文对照
- 面向运维工程师、安全工程师
- 深度：原理理解 + 实战脚本 + 安全应用

# 约束
- 仅从防御、自动化和授权测试角度讲解
- 高风险命令（rm -rf、dd、iptables -F 等）给出警告
- 生产环境使用提示测试验证和备份
- 仅限授权环境使用
- 最后附"优化后的提示词模板"
```

**使用说明**：将【主题】替换为"Bash 日志分析实战""Bash 应急响应脚本""Bash 安全巡检""Bash 批量运维""Bash 取证脚本""Bash 性能调优"等，即可生成同等深度和结构的 Bash 安全编程专题文档。

---

> **总结**：Bash 是安全从业者的基本功——它无处不在、上手快速、管道哲学强大。学习 Bash 要掌握：变量与引用、流程控制（if/for/while/case）、函数、输入输出重定向与管道、文本处理三件套（grep/sed/awk）、以及调试技巧（set -x/set -e/trap）。在安全领域，Bash 广泛用于日志分析、系统巡检、应急响应、批量运维等场景，是每天都要用到的技能。学习资源非常丰富，从入门电子书到高级指南，从互动课程到游戏化练习（OverTheWire），都可以免费获取。最重要的还是多写多练——从简单的自动化脚本开始，逐步挑战更复杂的巡检、取证、分析脚本，在实战中不断提升。记住：Bash 的精髓在于"组合"——用管道把简单的小工具串起来，解决复杂的大问题。
