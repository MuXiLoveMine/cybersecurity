# Bash 基础

> 本文档为 Web 安全学习项目的 Bash 脚本编程基础材料，涵盖 Shell 概述、Bash 语法、脚本编写等核心知识点，并包含大量代码示例。

---

## 目录

- [一、Shell 概述](#一shell-概述)
- [二、Bash 基础](#二bash-基础)
- [三、变量与环境](#三变量与环境)
- [四、运算符](#四运算符)
- [五、条件判断](#五条件判断)
- [六、循环结构](#六循环结构)
- [七、函数](#七函数)
- [八、数组](#八数组)
- [九、字符串操作](#九字符串操作)
- [十、文件测试与操作](#十文件测试与操作)
- [十一、输入输出重定向](#十一输入输出重定向)
- [十二、管道](#十二管道)
- [十三、正则表达式](#十三正则表达式)
- [十四、命令替换](#十四命令替换)
- [十五、Shell 脚本调试](#十五shell-脚本调试)
- [十六、安全脚本编写](#十六安全脚本编写)

---

## 一、Shell 概述

### 1.1 什么是 Shell

Shell（壳）是用户与操作系统内核之间的**命令行解释器**，它接收用户输入的命令，然后调用相应的应用程序。Shell 既是一种命令语言，又是一种程序设计语言。

简单来说：
- 用户输入命令 → Shell 解释 → 内核执行 → 返回结果

### 1.2 常见的 Shell 种类

| Shell 名称 | 说明 | 特点 |
|-----------|------|------|
| **Bash** (Bourne Again Shell) | GNU 项目的 Shell | Linux 默认，功能最丰富，兼容性好 |
| **sh** (Bourne Shell) | 最早的 Unix Shell | 最基础，POSIX 标准 |
| **zsh** (Z Shell) | 增强版 Shell | 强大的自动补全、主题、插件 |
| **csh** (C Shell) | C 语言风格的 Shell | 语法类似 C 语言 |
| **tcsh** | csh 的增强版 | 提供更多交互功能 |
| **ksh** (Korn Shell) | 结合了 sh 和 csh 优点 | 商业 Unix 常用 |
| **fish** | 友好的交互式 Shell | 语法简单，自动补全强大 |

### 1.3 Bash 的地位

- **Linux 系统默认 Shell**：绝大多数 Linux 发行版默认使用 Bash
- **脚本编写首选**：Bash 脚本是运维、渗透测试中最常用的脚本语言
- **跨平台**：macOS 也使用 Bash（新版本已切换为 zsh），Windows 可通过 WSL/Git Bash 运行
- **安全性工具链**：nmap、metasploit、sqlmap 等工具都可通过 Bash 调用

### 1.4 第一个 Shell 脚本

创建 `hello.sh`：

```bash
#!/bin/bash
# 这是注释，以 # 开头
echo "Hello, World!"
```

脚本说明：
- 第一行 `#!/bin/bash` 称为 **Shebang**，指定脚本的解释器
- `#` 开头的行是注释
- `echo` 是输出命令

运行方式：

```bash
# 方式一：添加执行权限后直接运行
chmod +x hello.sh
./hello.sh

# 方式二：用解释器运行
bash hello.sh
sh hello.sh

# 方式三：source 运行（在当前 shell 中执行）
source hello.sh
. hello.sh
```

---

## 二、Bash 基础

### 2.1 命令格式

```bash
命令 [选项] [参数]
```

示例：

```bash
ls -la /home
# ls 是命令
# -la 是选项（-l 长格式，-a 显示所有文件）
# /home 是参数
```

### 2.2 常用基础命令

```bash
# 目录操作
pwd          # 显示当前目录
cd /path     # 切换目录
cd ~         # 切换到用户主目录
cd -         # 切换到上一个目录
mkdir dir    # 创建目录
mkdir -p a/b/c  # 递归创建目录
rmdir dir    # 删除空目录

# 文件操作
ls           # 列出文件
ls -la       # 详细列表（含隐藏文件）
cp src dst   # 复制文件
cp -r src dst # 递归复制目录
mv src dst   # 移动/重命名
rm file      # 删除文件
rm -rf dir   # 递归强制删除目录
touch file   # 创建空文件或更新时间戳

# 文件查看
cat file     # 查看文件内容
more file    # 分页查看
less file    # 更强大的分页查看
head -n 10 file  # 查看前10行
tail -n 10 file  # 查看后10行
tail -f file     # 实时跟踪文件

# 系统信息
uname -a     # 系统信息
hostname     # 主机名
whoami       # 当前用户
id           # 用户 ID 信息
date         # 当前时间
uptime       # 运行时间
df -h        # 磁盘使用情况
free -m      # 内存使用情况
top          # 进程监控
ps aux       # 进程列表

# 用户和权限
useradd user    # 添加用户
passwd user     # 修改密码
su - user       # 切换用户
sudo command    # 以 root 权限执行
chmod 755 file  # 修改权限
chown user:group file  # 修改所有者
```

### 2.3 通配符

| 通配符 | 说明 | 示例 |
|--------|------|------|
| `*` | 匹配任意数量的任意字符 | `*.txt` 匹配所有 .txt 文件 |
| `?` | 匹配单个任意字符 | `file?.txt` 匹配 file1.txt, fileA.txt |
| `[]` | 匹配括号内的任意一个字符 | `file[123].txt` 匹配 file1/2/3.txt |
| `[a-z]` | 匹配范围内的字符 | `file[a-z].txt` 匹配 filea 到 filez |
| `[!abc]` | 匹配不在括号内的字符 | `file[!12].txt` 不匹配 file1/2.txt |
| `{a,b,c}` | 匹配括号内的任一字符串 | `file_{a,b}.txt` 匹配 file_a.txt, file_b.txt |

```bash
# 示例
ls *.sh          # 列出所有 .sh 文件
ls file?.txt     # 列出 file 后跟一个字符的 .txt 文件
ls [abc]*.sh     # 列出以 a/b/c 开头的 .sh 文件
cp file{,.bak}   # 快速备份：file 复制为 file.bak
```

---

## 三、变量与环境

### 3.1 变量定义

```bash
# 基本定义（等号两边不能有空格！）
name="张三"
age=25
is_student=true

# 使用变量（推荐加花括号）
echo $name
echo ${name}
echo "姓名: $name，年龄: $age"

# 花括号的作用：区分变量边界
echo "${name}是学生"   # 正确
echo "$name是学生"     # 错误：会把"name是学生"当作变量名
```

### 3.2 变量命名规则

- 变量名只能包含**字母、数字、下划线**
- 不能以**数字**开头
- 区分大小写
- 不能使用关键字

```bash
# 合法变量名
my_var="合法"
_var="以下划线开头"
Var123="包含数字"

# 不合法（会报错）
# 123var="数字开头"
# my-var="包含减号"
```

### 3.3 只读变量

```bash
# 使用 readonly 声明只读变量
readonly PI=3.14159
echo $PI

# PI=3.14  # 尝试修改会报错：readonly variable
```

### 3.4 删除变量

```bash
temp="临时变量"
echo $temp   # 输出: 临时变量

unset temp
echo $temp   # 输出: 空
```

### 3.5 环境变量

环境变量是全局变量，对所有子进程可见。

```bash
# 查看所有环境变量
env
printenv

# 查看单个环境变量
echo $HOME
echo $PATH
echo $USER
echo $SHELL
echo $PWD
echo $HOSTNAME
echo $LANG

# 设置环境变量（仅当前 shell 有效）
export MY_VAR="hello"

# 永久设置环境变量
# 编辑 ~/.bashrc 或 ~/.bash_profile
# 添加：export MY_VAR="hello"
```

常见环境变量：

| 变量 | 说明 |
|------|------|
| `HOME` | 用户主目录 |
| `PATH` | 命令搜索路径 |
| `USER` | 当前用户名 |
| `SHELL` | 当前 Shell |
| `PWD` | 当前工作目录 |
| `HOSTNAME` | 主机名 |
| `LANG` | 语言设置 |
| `PS1` | 命令提示符格式 |
| `HISTSIZE` | 历史命令数量 |

### 3.6 特殊变量

| 变量 | 说明 |
|------|------|
| `$0` | 脚本名称 |
| `$1` ~ `$9` | 第 1 到第 9 个参数 |
| `${10}` | 第 10 个及以上参数 |
| `$#` | 参数个数 |
| `$*` | 所有参数（作为一个字符串） |
| `$@` | 所有参数（每个参数是独立的） |
| `$$` | 当前进程 ID |
| `$?` | 上一个命令的退出状态码（0 成功，非 0 失败） |
| `$!` | 最后一个后台进程的 PID |

```bash
#!/bin/bash
# 特殊变量示例

echo "脚本名: $0"
echo "参数个数: $#"
echo "第一个参数: $1"
echo "第二个参数: $2"
echo "所有参数(\$*): $*"
echo "所有参数(\$@): $@"
echo "进程ID: $$"

# 运行: ./script.sh a b c
# 输出:
# 脚本名: ./script.sh
# 参数个数: 3
# 第一个参数: a
# 第二个参数: b
```

### 3.7 变量作用域

```bash
#!/bin/bash

# 默认变量是全局的
global_var="全局"

function test_func {
    # local 声明局部变量，仅在函数内有效
    local local_var="局部"
    echo "函数内: local_var=$local_var"
    echo "函数内: global_var=$global_var"
}

test_func
echo "函数外: global_var=$global_var"
echo "函数外: local_var=$local_var"  # 空，因为是局部变量
```

---

## 四、运算符

### 4.1 算术运算符

Bash 本身不支持浮点运算，只支持整数运算。

```bash
a=10
b=20

# 方式一：使用 $((...))
echo $((a + b))   # 30
echo $((a - b))   # -10
echo $((a * b))   # 200
echo $((b / a))   # 2（整数除法）
echo $((b % a))   # 0（取余）

# 方式二：使用 let
let "result = a + b"
echo $result

let a++   # 自增
let b--   # 自减

# 方式三：使用 expr
result=`expr $a + $b`
echo $result
# 注意：expr 的运算符两边必须有空格，且 * 需要转义 \*
```

运算符列表：

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `+` | 加法 | `$((a + b))` |
| `-` | 减法 | `$((a - b))` |
| `*` | 乘法 | `$((a * b))` |
| `/` | 除法（整数） | `$((b / a))` |
| `%` | 取余 | `$((b % a))` |
| `=` | 赋值 | `a=10` |
| `==` | 相等 | `$((a == b))` |
| `!=` | 不等 | `$((a != b))` |

### 4.2 关系运算符

用于数值比较，配合 `[ ]` 或 `test` 使用。

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `-eq` | equal 等于 | `[ $a -eq $b ]` |
| `-ne` | not equal 不等于 | `[ $a -ne $b ]` |
| `-gt` | greater than 大于 | `[ $a -gt $b ]` |
| `-lt` | less than 小于 | `[ $a -lt $b ]` |
| `-ge` | greater or equal 大于等于 | `[ $a -ge $b ]` |
| `-le` | less or equal 小于等于 | `[ $a -le $b ]` |

```bash
a=10
b=20

if [ $a -eq $b ]; then
    echo "相等"
fi

if [ $a -lt $b ]; then
    echo "a 小于 b"
fi
```

### 4.3 字符串运算符

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `=` | 相等 | `[ "$a" = "$b" ]` |
| `!=` | 不相等 | `[ "$a" != "$b" ]` |
| `-z` | 长度为 0 | `[ -z "$a" ]` |
| `-n` | 长度不为 0 | `[ -n "$a" ]` |
| `$` | 字符串不为空 | `[ "$a" ]` |

```bash
str1="hello"
str2="world"
str3=""

[ "$str1" = "$str2" ] && echo "相等" || echo "不等"
[ -z "$str3" ] && echo "空字符串"
[ -n "$str1" ] && echo "非空字符串"
```

### 4.4 布尔运算符

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `!` | 非（取反） | `[ ! 条件 ]` |
| `-a` | 与（and） | `[ 条件1 -a 条件2 ]` |
| `-o` | 或（or） | `[ 条件1 -o 条件2 ]` |

```bash
a=10
b=20

if [ $a -gt 5 -a $b -gt 15 ]; then
    echo "两个条件都满足"
fi

# 也可以用 && 和 || 连接多个 [ ]
if [ $a -gt 5 ] && [ $b -gt 15 ]; then
    echo "两个条件都满足"
fi
```

### 4.5 逻辑运算符（[[ ]] 中使用）

```bash
a=10
b=20

if [[ $a -gt 5 && $b -gt 15 ]]; then
    echo "都满足"
fi

if [[ $a -gt 5 || $b -lt 10 ]]; then
    echo "至少一个满足"
fi

if [[ ! $a -eq $b ]]; then
    echo "不相等"
fi
```

### 4.6 文件测试运算符

| 运算符 | 说明 |
|--------|------|
| `-d file` | 是否是目录 |
| `-f file` | 是否是普通文件 |
| `-r file` | 是否可读 |
| `-w file` | 是否可写 |
| `-x file` | 是否可执行 |
| `-s file` | 文件大小是否不为 0 |
| `-e file` | 文件是否存在 |
| `-L file` | 是否是符号链接 |
| `-S file` | 是否是 socket |
| `-p file` | 是否是管道 |
| `-b file` | 是否是块设备 |
| `-c file` | 是否是字符设备 |
| `-u file` | 是否设置了 SUID 位 |
| `-g file` | 是否设置了 SGID 位 |
| `-k file` | 是否设置了 sticky 位 |
| `f1 -nt f2` | f1 是否比 f2 新 |
| `f1 -ot f2` | f1 是否比 f2 旧 |
| `f1 -ef f2` | f1 和 f2 是否是同一个文件 |

```bash
file="/etc/passwd"

if [ -f "$file" ]; then
    echo "是普通文件"
fi

if [ -r "$file" ] && [ -s "$file" ]; then
    echo "文件可读且不为空"
fi
```

---

## 五、条件判断

### 5.1 if 语句

```bash
# 基本语法
if [ 条件 ]; then
    # 条件为真时执行
fi

# if-else
if [ 条件 ]; then
    # 条件为真
else
    # 条件为假
fi

# if-elif-else
if [ 条件1 ]; then
    # 条件1为真
elif [ 条件2 ]; then
    # 条件2为真
else
    # 都不满足
fi
```

示例：

```bash
#!/bin/bash

score=85

if [ $score -ge 90 ]; then
    echo "优秀"
elif [ $score -ge 80 ]; then
    echo "良好"
elif [ $score -ge 60 ]; then
    echo "及格"
else
    echo "不及格"
fi
```

### 5.2 test 命令

`test` 命令和 `[ ]` 是等价的：

```bash
# 两种写法等价
if test -f file.txt; then
    echo "文件存在"
fi

if [ -f file.txt ]; then
    echo "文件存在"
fi
```

### 5.3 [ ] 与 [[ ]] 的区别

`[[ ]]` 是 Bash 的增强版条件判断，推荐使用：

| 特性 | `[ ]` | `[[ ]]` |
|------|-------|---------|
| 字符串比较中的 `<` `>` | 需要转义 `\<` `\>` | 直接使用 |
| 逻辑运算符 | `-a` `-o` | `&&` `\|\|` |
| 模式匹配 | 不支持 | `=~` 支持正则 |
| 变量为空时 | 需要加引号 | 自动处理 |
| 标准 | POSIX 标准 | Bash 特有 |

```bash
str1="apple"
str2="banana"

# [[ ]] 中可以直接使用 < >
if [[ "$str1" < "$str2" ]]; then
    echo "$str1 字典序在 $str2 前面"
fi

# [[ ]] 支持正则匹配
email="test@example.com"
if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
    echo "邮箱格式正确"
fi
```

### 5.4 case 语句

用于多分支选择：

```bash
case $变量 in
    模式1)
        # 匹配模式1时执行
        ;;
    模式2)
        # 匹配模式2时执行
        ;;
    *)
        # 默认情况
        ;;
esac
```

示例：

```bash
#!/bin/bash

os="linux"

case $os in
    "linux")
        echo "Linux 系统"
        ;;
    "macos"|"darwin")
        echo "macOS 系统"
        ;;
    "windows"|"win*")
        echo "Windows 系统"
        ;;
    *)
        echo "其他系统"
        ;;
esac
```

case 模式支持通配符：
- `*` 匹配任意字符串
- `?` 匹配单个字符
- `[abc]` 匹配括号内任一字符
- `a|b` 匹配 a 或 b

---

## 六、循环结构

### 6.1 for 循环

```bash
# 遍历列表
for var in item1 item2 item3; do
    echo "$var"
done

# 遍历数字范围
for i in {1..5}; do
    echo "$i"
done

# 带步长
for i in {1..10..2}; do
    echo "$i"
done

# C 风格 for 循环
for ((i=1; i<=5; i++)); do
    echo "$i"
done

# 遍历数组
fruits=("苹果" "香蕉" "橙子")
for fruit in "${fruits[@]}"; do
    echo "$fruit"
done

# 遍历命令输出
for file in $(ls *.txt); do
    echo "处理文件: $file"
done

# 遍历目录中的文件
for file in /etc/*.conf; do
    if [ -f "$file" ]; then
        echo "$file"
    fi
done
```

### 6.2 while 循环

```bash
# 基本 while 循环
count=1
while [ $count -le 5 ]; do
    echo "$count"
    count=$((count + 1))
done

# 读取文件逐行处理
while read -r line; do
    echo "读取: $line"
done < file.txt

# 带字段分割
while read -r name age city; do
    echo "姓名: $name, 年龄: $age, 城市: $city"
done < data.txt

# 无限循环
while true; do
    echo "循环中..."
    sleep 1
done
```

### 6.3 until 循环

`until` 与 `while` 相反，条件为假时执行循环：

```bash
count=5
until [ $count -eq 0 ]; do
    echo "$count"
    count=$((count - 1))
done
echo "结束！"
```

### 6.4 break 和 continue

```bash
# break：跳出循环
for i in 1 2 3 4 5; do
    if [ $i -eq 3 ]; then
        break
    fi
    echo "$i"
done
# 输出: 1 2

# continue：跳过本次循环
for i in 1 2 3 4 5; do
    if [ $i -eq 3 ]; then
        continue
    fi
    echo "$i"
done
# 输出: 1 2 4 5
```

### 6.5 select 菜单循环

用于创建简单的文本菜单：

```bash
#!/bin/bash

echo "请选择："
select choice in "选项1" "选项2" "选项3" "退出"; do
    case $choice in
        "选项1")
            echo "你选择了选项1"
            ;;
        "选项2")
            echo "你选择了选项2"
            ;;
        "选项3")
            echo "你选择了选项3"
            ;;
        "退出")
            echo "退出"
            break
            ;;
        *)
            echo "无效选项"
            ;;
    esac
done
```

---

## 七、函数

### 7.1 函数定义

```bash
# 方式一：使用 function 关键字
function hello {
    echo "Hello!"
}

# 方式二：省略 function（推荐）
greet() {
    echo "你好！"
}

# 调用函数
hello
greet
```

### 7.2 函数参数

函数通过 `$1`、`$2` 等获取参数：

```bash
print_info() {
    echo "参数个数: $#"
    echo "第一个参数: $1"
    echo "第二个参数: $2"
    echo "所有参数: $@"
}

print_info "张三" 25 "北京"
```

### 7.3 函数返回值

Bash 函数的 `return` 只能返回状态码（0-255）：

```bash
add() {
    local sum=$(( $1 + $2 ))
    return $sum
}

add 10 20
echo "结果: $?"  # 30（通过 $? 获取返回值）
```

返回更大的值或字符串，使用 `echo`：

```bash
greet() {
    echo "你好，$1！"
}

result=$(greet "张三")
echo "$result"  # 你好，张三！
```

### 7.4 局部变量

使用 `local` 关键字声明局部变量：

```bash
global_var="全局"

test_func() {
    local local_var="局部"
    global_var="已修改"
    echo "函数内: local_var=$local_var"
}

test_func
echo "函数外: global_var=$global_var"  # 已修改
echo "函数外: local_var=$local_var"    # 空
```

### 7.5 递归函数

```bash
# 阶乘计算
factorial() {
    local n=$1
    if [ $n -le 1 ]; then
        echo 1
    else
        local prev=$(factorial $((n - 1)))
        echo $(( n * prev ))
    fi
}

echo "5! = $(factorial 5)"  # 120
```

### 7.6 函数库

可以将常用函数放在单独的文件中，用 `source` 引入：

```bash
# math_lib.sh
add() { echo $(($1 + $2)); }
sub() { echo $(($1 - $2)); }
mul() { echo $(($1 * $2)); }

# 主脚本
source ./math_lib.sh

echo $(add 5 3)   # 8
echo $(mul 4 6)   # 24
```

---

## 八、数组

### 8.1 创建数组

```bash
# 方式一：逐个赋值
fruits[0]="苹果"
fruits[1]="香蕉"
fruits[2]="橙子"

# 方式二：一次性赋值
colors=("红色" "绿色" "蓝色" "黄色")

# 方式三：空数组
empty_arr=()

# 方式四：从命令输出创建
files=($(ls *.txt))
```

### 8.2 访问数组元素

```bash
arr=("a" "b" "c" "d" "e")

echo ${arr[0]}     # 第一个元素: a
echo ${arr[-1]}    # 最后一个元素: e
echo ${arr[@]}     # 所有元素: a b c d e
echo ${arr[*]}     # 所有元素（作为单个字符串）
echo ${!arr[@]}    # 所有索引: 0 1 2 3 4
echo ${#arr[@]}    # 元素个数: 5
```

### 8.3 遍历数组

```bash
arr=("苹果" "香蕉" "橙子")

# 方式一：遍历元素
for item in "${arr[@]}"; do
    echo "$item"
done

# 方式二：遍历索引
for i in "${!arr[@]}"; do
    echo "索引 $i: ${arr[$i]}"
done

# 方式三：C 风格遍历
for ((i=0; i<${#arr[@]}; i++)); do
    echo "${arr[$i]}"
done
```

### 8.4 添加和删除元素

```bash
arr=("a" "b" "c")

# 追加元素
arr+=("d" "e")
echo ${arr[@]}  # a b c d e

# 指定索引添加
arr[10]="z"
echo ${#arr[@]}  # 6（索引可以不连续）

# 删除元素
unset arr[2]
echo ${arr[@]}  # a b d e z

# 删除整个数组
unset arr
```

### 8.5 数组切片

```bash
arr=(a b c d e f g h)

echo ${arr[@]:2:3}    # 从索引2开始取3个: c d e
echo ${arr[@]:5}      # 从索引5到末尾: f g h
echo ${arr[@]: -3}    # 从末尾取3个: f g h（注意空格）
```

### 8.6 关联数组（字典）

Bash 4.0+ 支持关联数组：

```bash
# 声明关联数组
declare -A person

# 赋值
person["name"]="张三"
person["age"]=25
person["city"]="北京"

# 访问
echo ${person["name"]}  # 张三
echo ${person[age]}     # 25（键可以不加引号）

# 遍历
for key in "${!person[@]}"; do
    echo "$key = ${person[$key]}"
done

# 元素个数
echo ${#person[@]}  # 3
```

### 8.7 数组合并

```bash
arr1=(1 2 3)
arr2=(4 5 6)
merged=("${arr1[@]}" "${arr2[@]}")
echo ${merged[@]}  # 1 2 3 4 5 6
```

---

## 九、字符串操作

### 9.1 基本操作

```bash
str="Hello, Bash World!"

# 长度
echo ${#str}  # 18

# 拼接
str1="Hello"
str2="World"
echo "${str1}, ${str2}!"  # Hello, World!
```

### 9.2 字符串切片

```bash
str="abcdefghij"

echo ${str:3}      # 从索引3开始: defghij
echo ${str:2:5}    # 从索引2开始取5个: cdefg
echo ${str: -4}    # 从末尾取4个: ghij（注意空格）
echo ${str: -6:3}  # 从-6开始取3个: efg
```

### 9.3 字符串替换

```bash
str="I like apples. Apples are red."

# 替换第一个匹配
echo ${str/apples/oranges}
# I like oranges. Apples are red.

# 替换所有匹配
echo ${str//apples/oranges}
# I like oranges. Apples are red.（区分大小写）

# 替换前缀
path="/usr/local/bin/bash"
echo ${path#*/}     # usr/local/bin/bash（删除最短匹配前缀）
echo ${path##*/}    # bash（删除最长匹配前缀）

# 替换后缀
echo ${path%/*}     # /usr/local/bin（删除最短匹配后缀）
echo ${path%%/*}    # （空）（删除最长匹配后缀）
```

### 9.4 大小写转换

```bash
str="Hello World"

echo ${str,,}  # 全小写: hello world
echo ${str^^}  # 全大写: HELLO WORLD
echo ${str^}   # 首字母大写: Hello World
echo ${str,}   # 首字母小写: hello World

# 使用 tr 命令
echo "$str" | tr '[:upper:]' '[:lower:]'  # 转小写
echo "$str" | tr '[:lower:]' '[:upper:]'  # 转大写
```

### 9.5 字符串包含判断

```bash
str="Hello World, Bash is great"

# 包含
if [[ "$str" == *"Bash"* ]]; then
    echo "包含 Bash"
fi

# 以...开头
if [[ "$str" == Hello* ]]; then
    echo "以 Hello 开头"
fi

# 以...结尾
if [[ "$str" == *great ]]; then
    echo "以 great 结尾"
fi
```

### 9.6 字符串分割

```bash
str="apple,banana,orange,grape"

# 方法一：IFS + read
IFS=',' read -ra arr <<< "$str"
echo "${arr[0]}"  # apple

# 方法二：tr 转换
echo "$str" | tr ',' '\n'
```

### 9.7 删除空白

```bash
str="   Hello World   "

# 删除前导空白
echo "$str" | sed 's/^[[:space:]]*//'

# 删除尾随空白
echo "$str" | sed 's/[[:space:]]*$//'

# 删除两端空白
echo "$str" | xargs
```

### 9.8 字符串反转

```bash
str="Hello World"
echo "$str" | rev  # dlroW olleH
```

---

## 十、文件测试与操作

### 10.1 文件测试

```bash
file="/etc/passwd"

# 常用文件测试
[ -f "$file" ] && echo "普通文件"
[ -d "$file" ] && echo "目录"
[ -r "$file" ] && echo "可读"
[ -w "$file" ] && echo "可写"
[ -x "$file" ] && echo "可执行"
[ -e "$file" ] && echo "存在"
[ -s "$file" ] && echo "大小不为零"
[ -L "$file" ] && echo "符号链接"
```

### 10.2 文件读取

```bash
# 全部读取
content=$(cat file.txt)

# 逐行读取（推荐）
while IFS= read -r line; do
    echo "$line"
done < file.txt

# 读取前 N 行
head -n 10 file.txt

# 读取后 N 行
tail -n 10 file.txt

# 实时跟踪文件
tail -f log.txt
```

### 10.3 文件写入

```bash
# 覆盖写入
echo "内容" > file.txt

# 追加写入
echo "追加内容" >> file.txt

# 多行写入（here document）
cat > file.txt << 'EOF'
第一行
第二行
第三行
EOF

# 写入时不展开变量（加引号的 EOF）
cat > file.txt << 'EOF'
$var 不会被展开
EOF

# 写入时展开变量
cat > file.txt << EOF
当前目录: $PWD
EOF
```

### 10.4 文件权限

```bash
# 修改权限
chmod 755 file.sh   # rwxr-xr-x
chmod +x file.sh    # 添加执行权限
chmod -R 755 dir/   # 递归修改

# 修改所有者
chown user:group file.txt
chown -R user:group dir/

# 权限数字表示
# r = 4, w = 2, x = 1
# 7 = rwx, 6 = rw-, 5 = r-x, 4 = r--
```

### 10.5 文件查找

```bash
# 按名称查找
find /path -name "*.txt"
find /path -iname "*.txt"  # 忽略大小写

# 按类型查找
find /path -type f  # 文件
find /path -type d  # 目录
find /path -type l  # 符号链接

# 按大小查找
find /path -size +10M   # 大于 10MB
find /path -size -100k  # 小于 100KB

# 按时间查找
find /path -mtime -7   # 7 天内修改过
find /path -atime +30  # 30 天前访问过
find /path -mmin -60   # 60 分钟内修改过

# 按权限查找
find /path -perm 777   # 权限为 777
find /path -perm -4000 # 设置了 SUID

# 对找到的文件执行操作
find /path -name "*.log" -exec rm {} \;
find /path -name "*.bak" -delete
```

---

## 十一、输入输出重定向

### 11.1 标准文件描述符

| 描述符 | 名称 | 说明 |
|--------|------|------|
| 0 | stdin | 标准输入 |
| 1 | stdout | 标准输出 |
| 2 | stderr | 标准错误 |

### 11.2 输出重定向

```bash
# 标准输出重定向（覆盖）
echo "内容" > file.txt
echo "内容" 1> file.txt  # 等价

# 标准输出重定向（追加）
echo "内容" >> file.txt

# 标准错误重定向
ls /nonexistent 2> error.log

# 同时重定向 stdout 和 stderr
command > output.log 2>&1
command &> output.log  # 简写（Bash 4+）

# 丢弃输出
command > /dev/null
command &> /dev/null  # 全部丢弃
```

### 11.3 输入重定向

```bash
# 从文件读取
cat < file.txt

# here document（将多行内容作为输入）
cat << 'EOF'
第一行
第二行
EOF

# here string（将字符串作为输入）
cat <<< "Hello World"

# 从文件读取到变量
content=$(< file.txt)
```

### 11.4 exec 操作文件描述符

```bash
# 打开文件描述符 3 用于写入
exec 3> output.txt
echo "写入fd3" >&3
exec 3>&-  # 关闭

# 打开文件描述符 4 用于读取
exec 4< input.txt
read -r line <&4
exec 4<&-  # 关闭
```

### 11.5 tee 命令

同时输出到屏幕和文件：

```bash
# 覆盖
echo "内容" | tee output.txt

# 追加
echo "内容" | tee -a output.txt

# 多个文件
echo "内容" | tee file1.txt file2.txt
```

---

## 十二、管道

### 12.1 管道基础

管道（Pipeline）将前一个命令的**标准输出**作为后一个命令的**标准输入**。

```bash
# 语法：command1 | command2 | command3 ...

# 统计文件数
ls -la | wc -l

# 排序后去重
cat file.txt | sort | uniq

# 查找并统计
grep "error" log.txt | wc -l

# 显示前 10 行
ls /usr/bin | head -10

# 显示包含 bash 的行
ls /bin | grep "bash"
```

### 12.2 常用过滤器

**grep - 文本搜索**

```bash
# 基本搜索
grep "pattern" file.txt

# 忽略大小写
grep -i "pattern" file.txt

# 显示行号
grep -n "pattern" file.txt

# 反向匹配（不包含的行）
grep -v "pattern" file.txt

# 统计匹配行数
grep -c "pattern" file.txt

# 递归搜索目录
grep -r "pattern" /path/

# 只显示匹配的部分
grep -o "pattern" file.txt

# 正则表达式搜索
grep -E "[0-9]+" file.txt
```

**sed - 流编辑器**

```bash
# 替换文本
sed 's/old/new/' file.txt      # 替换每行第一个
sed 's/old/new/g' file.txt     # 全局替换
sed 's/old/new/2' file.txt     # 替换每行第二个

# 删除行
sed '2d' file.txt              # 删除第2行
sed '2,5d' file.txt            # 删除第2-5行
sed '/pattern/d' file.txt      # 删除匹配的行

# 插入/追加
sed '2i\new line' file.txt     # 第2行前插入
sed '2a\new line' file.txt     # 第2行后追加

# 直接修改文件
sed -i 's/old/new/g' file.txt
```

**awk - 文本处理语言**

```bash
# 打印指定字段
awk '{print $1, $3}' file.txt  # 打印第1和第3列

# 指定分隔符
awk -F: '{print $1}' /etc/passwd  # 以冒号分隔

# 条件过滤
awk '$3 >= 1000 {print $1}' /etc/passwd

# 计算
awk '{sum += $1} END {print sum}' numbers.txt

# 内置变量
awk '{print NR, NF, $0}' file.txt
# NR = 行号, NF = 字段数, $0 = 整行

# 模式匹配
awk '/pattern/ {print $1}' file.txt
```

**sort - 排序**

```bash
sort file.txt                  # 字典序排序
sort -r file.txt               # 逆序
sort -n file.txt               # 数值排序
sort -u file.txt               # 去重排序
sort -k2 file.txt              # 按第2列排序
sort -t: -k3 -n /etc/passwd    # 按冒号分隔的第3列数值排序
```

**uniq - 去重**

```bash
uniq file.txt                  # 去除相邻重复行
uniq -c file.txt               # 统计重复次数
uniq -d file.txt               # 只显示重复行
uniq -u file.txt               # 只显示不重复行
# 注意：uniq 只去除相邻的重复行，通常先 sort 再 uniq
sort file.txt | uniq -c
```

**head / tail - 取行**

```bash
head file.txt                  # 前10行
head -n 20 file.txt            # 前20行
head -c 100 file.txt           # 前100字节

tail file.txt                  # 后10行
tail -n 20 file.txt            # 后20行
tail -f file.txt               # 实时跟踪
tail -F file.txt               # 跟踪文件（文件被截断也能继续）
```

**cut - 截取**

```bash
cut -c 3-7 file.txt            # 截取第3-7个字符
cut -d: -f 1 /etc/passwd       # 按冒号分隔取第1列
cut -d, -f 1,3 data.csv        # 按逗号分隔取第1、3列
```

**tr - 字符转换**

```bash
echo "Hello" | tr 'a-z' 'A-Z'  # 转大写
echo "Hello" | tr 'A-Z' 'a-z'  # 转小写
echo "a1b2c3" | tr -d '0-9'    # 删除数字
echo "hello   world" | tr -s ' ' # 压缩重复空格
```

**wc - 统计**

```bash
wc -l file.txt                 # 行数
wc -w file.txt                 # 单词数
wc -c file.txt                 # 字节数
wc -m file.txt                 # 字符数
```

### 12.3 管道链组合示例

```bash
# 统计访问日志中 IP 出现次数 Top 10
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# 查找占用空间最大的 5 个目录
du -sh /* | sort -rh | head -5

# 统计最常用的 10 个命令
history | awk '{print $2}' | sort | uniq -c | sort -rn | head -10

# 提取日志中的所有 IP
grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' log.txt | sort | uniq

# 查找大文件并排序
find / -type f -size +100M 2>/dev/null | xargs ls -lh | sort -k5 -hr
```

### 12.4 xargs 命令

将标准输入转换为命令参数：

```bash
# 基本用法
echo "file1 file2 file3" | xargs rm

# 按行处理
cat filelist.txt | xargs -I{} cp {} /backup/

# 限制参数数量
cat filelist.txt | xargs -n 2 echo

# find + xargs 组合
find . -name "*.log" | xargs rm
find . -name "*.txt" | xargs grep "pattern"
```

### 12.5 命名管道（FIFO）

```bash
# 创建命名管道
mkfifo mypipe

# 写入管道（后台）
echo "hello" > mypipe &

# 从管道读取
cat mypipe

# 删除管道
rm mypipe
```

---

## 十三、正则表达式

### 13.1 基础语法

| 元字符 | 说明 | 示例 |
|--------|------|------|
| `.` | 匹配任意单个字符 | `a.c` 匹配 abc, adc |
| `*` | 前一个字符出现 0 次或多次 | `ab*c` 匹配 ac, abc, abbc |
| `+` | 前一个字符出现 1 次或多次 | `ab+c` 匹配 abc, abbc |
| `?` | 前一个字符出现 0 次或 1 次 | `ab?c` 匹配 ac, abc |
| `^` | 匹配行首 | `^hello` |
| `$` | 匹配行尾 | `world$` |
| `[abc]` | 匹配括号内任一字符 | `[aeiou]` |
| `[^abc]` | 匹配不在括号内的字符 | `[^0-9]` |
| `[a-z]` | 匹配范围内的字符 | `[a-zA-Z0-9]` |
| `{n}` | 精确匹配 n 次 | `a{3}` 匹配 aaa |
| `{n,}` | 至少匹配 n 次 | `a{2,}` |
| `{n,m}` | 匹配 n 到 m 次 | `a{2,5}` |
| `\|` | 或 | `cat\|dog` |
| `()` | 分组 | `(ab)+` |
| `\d` | 数字（扩展正则） | 等价于 `[0-9]` |
| `\w` | 单词字符（扩展正则） | 等价于 `[a-zA-Z0-9_]` |
| `\s` | 空白字符（扩展正则） | 空格、制表符等 |
| `\b` | 单词边界 | `\bword\b` |

### 13.2 grep 与正则

```bash
# 基本正则（BRE）
grep "pattern" file.txt
grep "^[0-9]" file.txt         # 以数字开头
grep "\.txt$" file.txt         # 以 .txt 结尾

# 扩展正则（ERE）- 使用 -E
grep -E "[0-9]+" file.txt      # 一个或多个数字
grep -E "cat|dog" file.txt     # cat 或 dog
grep -E "(ab)+" file.txt       # ab 重复一次或多次

# Perl 正则（PCRE）- 使用 -P
grep -P "\d+" file.txt         # 数字
grep -P "\w+@\w+\.\w+" file.txt  # 简单邮箱
```

### 13.3 常用正则模式

```bash
# IP 地址
grep -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" file.txt

# 邮箱地址
grep -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" file.txt

# URL
grep -E "https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" file.txt

# 手机号码（中国）
grep -E "1[3-9][0-9]{9}" file.txt

# 身份证号
grep -E "[1-9][0-9]{5}(19|20)[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])[0-9]{3}[0-9Xx]" file.txt

# HTML 标签
grep -E "<[^>]+>" file.txt

# 中文字符
grep -P "[\x{4e00}-\x{9fa5}]" file.txt
```

### 13.4 sed 中的正则

```bash
# 替换
sed 's/[0-9]*/NUM/' file.txt

# 删除空白行
sed '/^$/d' file.txt

# 删除注释行
sed '/^#/d' file.txt

# 提取匹配部分
sed -n 's/.*\(pattern\).*/\1/p' file.txt
```

### 13.5 Bash 中的正则匹配

```bash
# [[ ]] 中使用 =~ 进行正则匹配
str="test@example.com"

if [[ "$str" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
    echo "邮箱格式正确"
fi

# 捕获组
phone="13812345678"
if [[ "$phone" =~ ^(1[3-9])([0-9]{9})$ ]]; then
    echo "号段: ${BASH_REMATCH[1]}"
    echo "号码: ${BASH_REMATCH[2]}"
fi
```

---

## 十四、命令替换

### 14.1 命令替换语法

```bash
# 方式一：$()（推荐）
result=$(command)

# 方式二：``（反引号）
result=`command`

# 示例
current_date=$(date +"%Y-%m-%d")
echo "今天是: $current_date"

file_count=$(ls *.txt | wc -l)
echo "txt 文件数: $file_count"
```

### 14.2 $() 与 `` 的区别

```bash
# $() 支持嵌套
result=$(echo $(date))

# 反引号嵌套需要转义
result=`echo \`date\``

# $() 可读性更好，推荐使用
```

### 14.3 命令替换的使用场景

```bash
# 变量赋值
files=$(ls /etc/*.conf)

# 循环中使用
for file in $(find . -name "*.log"); do
    echo "处理: $file"
done

# 条件判断
if [ $(id -u) -eq 0 ]; then
    echo "root 用户"
fi

# 数组创建
arr=($(cat file.txt))

# 命令替换与管道
count=$(grep -c "error" log.txt | tr -d ' ')
```

### 14.4 进程替换（Process Substitution）

```bash
# <(command) 将命令输出当作文件
diff <(sort file1.txt) <(sort file2.txt)

# >(command) 将输入当作命令的输入
tee >(gzip > log.gz) < log.txt

# 避免管道中的子 shell 问题
# 管道方式（count 在子 shell 中，外部不可见）
count=0
echo -e "a\nb\nc" | while read line; do
    count=$((count + 1))
done
echo $count  # 0

# 进程替换方式（在当前 shell 中执行）
count=0
while read line; do
    count=$((count + 1))
done < <(echo -e "a\nb\nc")
echo $count  # 3
```

---

## 十五、Shell 脚本调试

### 15.1 set 命令

```bash
# 显示执行的命令（跟踪）
set -x
# ... 脚本内容 ...
set +x  # 关闭

# 遇到错误立即退出
set -e

# 使用未定义变量时报错
set -u

# 管道中任一命令失败则整体失败
set -o pipefail

# 常用组合
set -euo pipefail
```

| 选项 | 说明 |
|------|------|
| `set -e` | 命令失败时立即退出 |
| `set -u` | 使用未定义变量时报错 |
| `set -x` | 打印执行的命令（调试模式） |
| `set -v` | 打印读取的脚本行 |
| `set -n` | 只检查语法，不执行 |
| `set -o pipefail` | 管道中任一失败则失败 |

### 15.2 命令行调试

```bash
# 跟踪执行
bash -x script.sh

# 只检查语法
bash -n script.sh

# 详细模式
bash -v script.sh

# 组合
bash -xv script.sh
```

### 15.3 自定义调试函数

```bash
#!/bin/bash

# 调试级别
DEBUG=${DEBUG:-0}

debug() {
    if [ "$DEBUG" -ge 1 ]; then
        echo "[DEBUG] $*" >&2
    fi
}

info() {
    echo "[INFO] $*"
}

error() {
    echo "[ERROR] $*" >&2
}

# 使用
DEBUG=1
debug "这是调试信息"
info "这是普通信息"
error "这是错误信息"
```

### 15.4 trap 捕获信号

```bash
#!/bin/bash

# 出错时打印信息
error_handler() {
    echo "错误在第 $1 行：命令 '$2' 失败，退出码 $3" >&2
}

trap 'error_handler $LINENO "$BASH_COMMAND" $?' ERR

# 模拟错误
ls /nonexistent_file
```

### 15.5 常见调试技巧

```bash
# 1. 打印变量值
echo "变量值: $var"

# 2. 打印数组内容
echo "数组: ${arr[@]}"
echo "数组长度: ${#arr[@]}"

# 3. 检查命令退出码
command
echo "退出码: $?"

# 4. 使用 set -x 包裹可疑代码
set -x
# 可疑代码
set +x

# 5. 用 read 暂停脚本
read -p "按回车继续..."

# 6. 写入日志文件
exec > >(tee script.log) 2>&1
```

---

## 十六、安全脚本编写

### 16.1 输入验证

```bash
#!/bin/bash

# 验证参数数量
if [ $# -ne 2 ]; then
    echo "用法: $0 <参数1> <参数2>" >&2
    exit 1
fi

# 验证是否为数字
if ! [[ "$1" =~ ^[0-9]+$ ]]; then
    echo "错误：参数1必须是正整数" >&2
    exit 1
fi

# 验证是否为 IP 地址
validate_ip() {
    local ip=$1
    if [[ "$ip" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        IFS='.' read -ra octets <<< "$ip"
        for octet in "${octets[@]}"; do
            if [ "$octet" -gt 255 ] || [ "$octet" -lt 0 ]; then
                return 1
            fi
        done
        return 0
    fi
    return 1
}

if ! validate_ip "$1"; then
    echo "错误：无效的 IP 地址" >&2
    exit 1
fi

# 验证文件是否存在
if [ ! -f "$2" ]; then
    echo "错误：文件不存在: $2" >&2
    exit 1
fi
```

### 16.2 变量引用与引号

```bash
#!/bin/bash

# 错误：变量中有空格会被分割
filename="my file.txt"
rm $filename  # 会被解析为 rm my file.txt

# 正确：用双引号包裹
filename="my file.txt"
rm "$filename"  # 正确处理

# 数组变量使用 "@"
arr=("a" "b c" "d")
for item in "${arr[@]}"; do  # 正确：三个元素
    echo "$item"
done

# 安全的命令参数拼接
# 错误：可能注入
cmd="ls $dir"
$cmd

# 正确：使用数组
args=("ls" "-la" "$dir")
"${args[@]}"
```

### 16.3 防止命令注入

```bash
#!/bin/bash

# 危险：用户输入直接拼接到命令中
read -p "输入文件名: " filename
ls -l $filename  # 可能注入：; rm -rf /

# 安全：验证输入 + 引号
read -p "输入文件名: " filename
if [[ "$filename" =~ ^[a-zA-Z0-9._-]+$ ]]; then
    ls -l "$filename"
else
    echo "无效的文件名" >&2
    exit 1
fi

# 使用 printf 安全构造命令
safe_cmd=$(printf 'ls -l %q' "$filename")
eval "$safe_cmd"
```

### 16.4 权限与敏感信息

```bash
#!/bin/bash

# 检查是否以 root 运行
if [ "$(id -u)" -eq 0 ]; then
    echo "警告：不建议以 root 运行此脚本" >&2
    # exit 1
fi

# 密码输入（不显示）
read -s -p "请输入密码: " password
echo ""

# 敏感信息不要打印到日志
# 错误：echo "密码: $password"

# 临时文件使用安全权限
temp_file=$(mktemp)
chmod 600 "$temp_file"
# ... 使用 ...
rm -f "$temp_file"

# 不在脚本中硬编码密码
# 错误：password="secret123"
# 正确：从环境变量或配置文件读取
password="${DB_PASSWORD:-}"
```

### 16.5 错误处理

```bash
#!/bin/bash

# 严格模式
set -euo pipefail

# 清理函数
cleanup() {
    echo "清理中..."
    rm -f /tmp/temp_file_$$
    # 其他清理操作
}

trap cleanup EXIT

# 错误处理函数
on_error() {
    local line=$1
    local cmd=$2
    local exit_code=$3
    echo "错误：第 $line 行，命令 '$cmd' 失败，退出码 $exit_code" >&2
    exit "$exit_code"
}

trap 'on_error $LINENO "$BASH_COMMAND" $?' ERR

# 主要逻辑
echo "脚本开始"
# ...
echo "脚本结束"
```

### 16.6 安全最佳实践清单

1. **使用严格模式**：`set -euo pipefail`
2. **验证所有输入**：参数、用户输入、文件内容都要验证
3. **引用变量**：始终用双引号包裹变量 `"$var"`
4. **避免 eval**：尽量不用 eval，除非必要且安全
5. **最小权限**：脚本以最小权限运行，不要用 root
6. **安全的临时文件**：使用 `mktemp`，设置 600 权限
7. **清理资源**：使用 trap 在退出时清理临时文件
8. **不硬编码密码**：使用环境变量或安全的配置文件
9. **日志脱敏**：日志中不要包含密码、密钥等敏感信息
10. **代码审计**：定期审查脚本中的安全问题

---

> 本文档涵盖了 Bash 脚本编程的基础知识。更多进阶内容请参考《进阶知识与使用案例》文档。



---

## 学习资源与知识拓展

### 官方资源

- **Bash/Shell 官方文档**：各语言官网提供最权威的文档和教程
- **Bash/Shell 标准库参考**：官方标准库 API 文档

### 在线教程

- **菜鸟教程 Bash/Shell**：https://www.runoob.com/ — 中文入门教程
- **W3Schools**：https://www.w3schools.com/ — 交互式学习平台
- **MDN Web Docs**：https://developer.mozilla.org/ — Web 技术文档（适用于 JS/HTML/CSS）

### 安全编程资源

- **OWASP 速查表系列**：https://cheatsheetseries.owasp.org/ — 各种安全最佳实践
- **CWE 常见弱点枚举**：https://cwe.mitre.org/ — 软件弱点分类体系
- **安全开发指南**：各语言官方安全文档与最佳实践

### 安全工具与库

- 根据语言选择相应的安全库和工具（加密库、HTTP 库、网络库等）
- 关注 GitHub 上的安全开源项目与社区

### 练习平台

- **LeetCode**：https://leetcode.cn/ — 算法练习平台
- **Codewars**：https://www.codewars.com/ — 编程挑战网站
- **Hack The Box**：https://www.hackthebox.com/ — 安全靶场
- **TryHackMe**：https://tryhackme.com/ — 安全学习房间
- **Bugku**：https://ctf.bugku.com/ — 国内 CTF 平台
- **攻防世界**：https://adworld.xctf.org.cn/ — XCTF 竞赛平台

### 推荐书籍

- 《Bash/Shell程序设计》— 入门经典教材
- 《Bash/Shell高级编程》— 进阶学习指南
- 各类安全相关技术书籍

### 社区与资讯

- **GitHub**：https://github.com/ — 开源项目托管平台
- **Stack Overflow**：https://stackoverflow.com/ — 编程问答社区
- **FreeBuf**：https://www.freebuf.com/ — 安全资讯媒体
- **安全客**：https://www.anquanke.com/ — 安全技术媒体
- **先知社区**：https://xz.aliyun.com/ — 阿里云安全社区

### 学习路线建议

1. **入门阶段**（1-2月）：掌握基本语法、数据类型、控制流
2. **进阶阶段**（2-3月）：函数、面向对象、异常处理、标准库
3. **实战练习**（1-2月）：通过项目巩固知识
4. **安全方向**（持续）：了解语言相关的安全漏洞和防护
5. **持续学习**：关注社区、阅读源码、参与开源
