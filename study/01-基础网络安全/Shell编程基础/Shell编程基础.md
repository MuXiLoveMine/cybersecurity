# Shell 编程基础

> 本文档系统介绍 Bash Shell 脚本编程的核心知识，配合 shell 目录中的代码示例，帮助快速掌握自动化脚本开发能力，为网络安全工具开发奠定基础。

---

## 目录

- [第一章：Shell 概述](#第一章shell-概述)
- [第二章：Shell 基础语法](#第二章shell-基础语法)
- [第三章：变量与数据类型](#第三章变量与数据类型)
- [第四章：条件判断与分支](#第四章条件判断与分支)
- [第五章：循环结构](#第五章循环结构)
- [第六章：函数](#第六章函数)
- [第七章：数组](#第七章数组)
- [第八章：字符串处理](#第八章字符串处理)
- [第九章：文件与目录操作](#第九章文件与目录操作)
- [第十章：正则表达式](#第十章正则表达式)
- [第十一章：信号与陷阱](#第十一章信号与陷阱)
- [第十二章：Shell 调试与最佳实践](#第十二章shell-调试与最佳实践)
- [附录：代码示例索引](#附录代码示例索引)

---

## 第一章：Shell 概述

### 1.1 什么是 Shell

Shell 是用户与操作系统内核之间的接口程序，它接收用户输入的命令，调用相应的应用程序或系统服务，是 Linux 系统中最重要的交互工具之一。

Shell 既是一种命令解释器，也是一种编程语言（Shell 脚本）。

### 1.2 常见的 Shell 类型

| Shell 名称 | 说明 | 默认位置 |
|-----------|------|---------|
| **Bash** (Bourne Again Shell) | 最流行的 Shell，Linux 默认 Shell，功能丰富 | `/bin/bash` |
| **sh** (Bourne Shell) | 最原始的 Unix Shell，兼容性好 | `/bin/sh` |
| **zsh** (Z Shell) | 功能强大，支持插件和主题，Mac 默认 | `/bin/zsh` |
| **csh / tcsh** | C Shell，语法类似 C 语言 | `/bin/csh` |
| **ksh** (Korn Shell) | 结合了 sh 和 csh 的优点 | `/bin/ksh` |
| **fish** | 友好的交互式 Shell，语法简单 | `/usr/bin/fish` |

> 本教程以 **Bash** 为标准，这是 Linux 系统中最通用的 Shell。

### 1.3 第一个 Shell 脚本

创建一个名为 `hello.sh` 的文件：

```bash
#!/bin/bash
# 这是注释：我的第一个 Shell 脚本
echo "Hello, World!"
```

**脚本结构说明**：
- `#!/bin/bash`：Shebang（释伴行），指定脚本使用的解释器
- `# 注释内容`：注释行，不被执行
- `echo`：输出命令

**运行脚本的方式**：

```bash
# 方式一：赋予执行权限后直接运行（推荐）
chmod +x hello.sh
./hello.sh

# 方式二：用 bash 解释器运行
bash hello.sh

# 方式三：用 source 运行（在当前 Shell 中执行）
source hello.sh
. hello.sh   # 等价于 source
```

### 1.4 Shell 脚本的执行过程

1. 读取脚本文件，逐行解析
2. 遇到 `#` 开头的行（除 `#!`）视为注释，跳过
3. 执行命令、变量替换、命令替换
4. 遇到控制结构（if/for/while 等）进行相应的逻辑判断
5. 逐行执行直到文件结束或遇到 `exit`

### 1.5 退出状态码

每个 Linux 命令执行后都会返回一个退出状态码（exit code）：

- **0**：命令执行成功
- **非 0**：命令执行失败（1~255）

```bash
# 查看上一条命令的退出状态码
echo $?

# 示例
ls /etc
echo $?   # 输出 0，表示成功

ls /nonexistent
echo $?   # 输出非 0，表示失败
```

---

## 第二章：Shell 基础语法

### 2.1 注释

```bash
# 这是单行注释

: '
这是多行注释
可以写多行内容
注意冒号和单引号之间有空格
'
```

### 2.2 echo 命令

```bash
# 普通输出
echo "Hello World"

# 输出不换行
echo -n "Hello "
echo "World"

# 启用转义字符
echo -e "Hello\tWorld\n"   # \t 制表符，\n 换行

# 输出带颜色
echo -e "\033[31m红色文字\033[0m"
echo -e "\033[32m绿色文字\033[0m"
echo -e "\033[33m黄色文字\033[0m"
echo -e "\033[34m蓝色文字\033[0m"
```

### 2.3 read 命令（读取用户输入）

```bash
# 基本用法
echo "请输入你的名字："
read name
echo "你好，$name！"

# 带提示的读取
read -p "请输入你的年龄：" age
echo "你 $age 岁了"

# 读取多个变量
read -p "请输入姓名和年龄（空格分隔）：" name age
echo "姓名：$name，年龄：$age"

# 静默输入（不显示输入内容，常用于密码）
read -s -p "请输入密码：" password
echo -e "\n密码已接收"

# 限制输入时间（超时自动继续）
read -t 5 -p "请在 5 秒内输入：" input
echo "你输入了：$input"
```

### 2.4 命令替换

将命令的输出结果赋值给变量：

```bash
# 方式一：$() （推荐）
current_date=$(date)
echo "当前日期：$current_date"

# 方式二：反引号 `` （旧风格）
current_date=`date`
echo "当前日期：$current_date"

# 嵌套使用
file_count=$(ls -l $(pwd) | wc -l)
echo "当前目录文件数：$file_count"
```

### 2.5 算术运算

Bash 本身只支持整数运算：

```bash
# 方式一：$(( 表达式 ))
a=10
b=3
echo "加法：$((a + b))"
echo "减法：$((a - b))"
echo "乘法：$((a * b))"
echo "除法：$((a / b))"    # 整数除法，结果为 3
echo "取余：$((a % b))"    # 结果为 1
echo "自增：$((a++))"
echo "自减：$((b--))"

# 方式二：let 命令
let "c = a + b"
echo "c = $c"

let "d = a * b"
echo "d = $d"

# 方式三：expr 命令
e=$(expr $a + $b)
echo "e = $e"
# 注意：expr 的运算符前后必须有空格，乘号需要转义
f=$(expr $a \* $b)
```

> **浮点运算**：Bash 不直接支持浮点数，需要借助 `bc` 或 `awk`：
> ```bash
> echo "scale=2; 10 / 3" | bc    # 输出 3.33
> awk 'BEGIN{print 10/3}'          # 输出 3.33333
> ```

---

## 第三章：变量与数据类型

### 3.1 变量定义

```bash
# 定义变量（等号两边不能有空格！）
name="张三"
age=25
pi=3.14

# 使用变量（在变量名前加 $）
echo "姓名：$name"
echo "年龄：$age"

# 推荐使用 ${变量名} 形式，避免歧义
echo "我叫${name}，今年${age}岁"

# 只读变量（不可修改）
readonly PI=3.14159
PI=3.14   # 报错：PI: readonly variable

# 删除变量（不能删除只读变量）
unset age
echo $age   # 空值
```

### 3.2 变量命名规则

- 变量名由字母、数字、下划线组成
- 不能以数字开头
- 区分大小写
- 不能使用 Shell 关键字（if、for、while 等）

```bash
# 正确
my_var="hello"
Var1=123
_user="admin"

# 错误
1var=123        # 数字开头
my-var="hello"  # 包含连字符
var name="hi"   # 有空格
```

### 3.3 变量类型

Bash 是弱类型语言，变量默认都是字符串，根据上下文自动转换。

```bash
# 字符串
str="hello world"

# 整数
num=100
result=$((num + 50))

# 数组
arr=("apple" "banana" "cherry")
```

### 3.4 特殊变量

| 变量 | 说明 |
|------|------|
| `$0` | 当前脚本的文件名 |
| `$n` | 第 n 个命令行参数（n=1~9，n>9 用 ${n}） |
| `$#` | 命令行参数的个数 |
| `$*` | 所有参数作为一个字符串 |
| `$@` | 所有参数，每个参数都是独立的（引号保留） |
| `$?` | 上一个命令的退出状态码 |
| `$$` | 当前 Shell 进程的 PID |
| `$!` | 后台运行的最后一个进程的 PID |
| `$_` | 上一个命令的最后一个参数 |

**示例**：

```bash
#!/bin/bash
echo "脚本名：$0"
echo "第一个参数：$1"
echo "第二个参数：$2"
echo "参数个数：$#"
echo "所有参数（\$*）：$*"
echo "所有参数（\$@）：$@"
echo "当前 PID：$$"
```

运行：`./script.sh hello world`

### 3.5 环境变量

环境变量是全局变量，对所有子进程可见：

```bash
# 查看所有环境变量
env
printenv

# 查看某个环境变量
echo $PATH
echo $HOME
echo $USER
echo $SHELL
echo $PWD
echo $LANG

# 设置环境变量（当前 Shell 有效）
export MY_VAR="hello"

# 永久设置环境变量
# 在 ~/.bashrc 或 ~/.bash_profile 中添加：
# export MY_VAR="hello"
```

**常见环境变量**：

| 变量 | 说明 |
|------|------|
| `PATH` | 命令搜索路径，目录间用冒号分隔 |
| `HOME` | 当前用户的主目录 |
| `USER` | 当前用户名 |
| `SHELL` | 当前使用的 Shell |
| `PWD` | 当前工作目录 |
| `OLDPWD` | 上一个工作目录 |
| `LANG` | 系统语言和字符编码 |
| `PS1` | 命令提示符格式 |
| `HOSTNAME` | 主机名 |

### 3.6 变量的高级用法

```bash
# 变量默认值
# ${var:-default}  var 不存在或为空时返回 default
echo ${name:-"匿名"}

# ${var:=default}  var 不存在或为空时赋值 default 并返回
echo ${name:="匿名"}

# ${var:?message}  var 不存在或为空时报错并退出
echo ${name:?"变量 name 未定义"}

# 变量长度
str="hello world"
echo ${#str}    # 输出 11

# 字符串截取
echo ${str:0:5}   # 从第 0 位开始取 5 个字符 → hello
echo ${str:6}     # 从第 6 位开始取到结尾 → world
echo ${str: -5}   # 从倒数第 5 位开始取 → world（注意冒号后空格）

# 删除匹配
str="hello world hello"
echo ${str#hello}    # 删除最短匹配（从左）→  world hello
echo ${str##hello}   # 删除最长匹配（从左）→  world hello
echo ${str%hello}    # 删除最短匹配（从右）→ hello world 
echo ${str%%hello}   # 删除最长匹配（从右）→ hello world 

# 替换
echo ${str/hello/hi}    # 替换第一个 → hi world hello
echo ${str//hello/hi}   # 替换所有 → hi world hi
```

---

## 第四章：条件判断与分支

### 4.1 if 语句

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
    # 条件1 为真
elif [ 条件2 ]; then
    # 条件2 为真
else
    # 都不满足
fi
```

### 4.2 条件测试

#### 4.2.1 test 命令与 []

`[ 条件 ]` 等价于 `test 条件`，注意括号内前后必须有空格。

#### 4.2.2 数值比较

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `-eq` | 等于（equal） | `[ $a -eq $b ]` |
| `-ne` | 不等于（not equal） | `[ $a -ne $b ]` |
| `-gt` | 大于（greater than） | `[ $a -gt $b ]` |
| `-ge` | 大于等于（greater or equal） | `[ $a -ge $b ]` |
| `-lt` | 小于（less than） | `[ $a -lt $b ]` |
| `-le` | 小于等于（less or equal） | `[ $a -le $b ]` |

```bash
age=18
if [ $age -ge 18 ]; then
    echo "已成年"
else
    echo "未成年"
fi
```

#### 4.2.3 字符串比较

| 运算符 | 说明 |
|--------|------|
| `=`, `==` | 字符串相等 |
| `!=` | 字符串不相等 |
| `<` | 字符串小于（字典序） |
| `>` | 字符串大于（字典序） |
| `-z` | 字符串长度为 0（空串） |
| `-n` | 字符串长度不为 0 |

```bash
str1="hello"
str2="world"

if [ "$str1" = "$str2" ]; then
    echo "相等"
else
    echo "不相等"
fi

if [ -z "$str1" ]; then
    echo "字符串为空"
fi

if [ -n "$str1" ]; then
    echo "字符串不为空"
fi
```

> **注意**：字符串比较时变量最好用双引号括起来，防止变量为空导致语法错误。

#### 4.2.4 文件测试

| 运算符 | 说明 |
|--------|------|
| `-e file` | 文件或目录是否存在 |
| `-f file` | 是否为普通文件 |
| `-d file` | 是否为目录 |
| `-r file` | 是否可读 |
| `-w file` | 是否可写 |
| `-x file` | 是否可执行 |
| `-s file` | 文件大小不为 0 |
| `-L file` | 是否为符号链接 |
| `-f file -a -r file` | 逻辑与（两个条件都满足） |
| `-f file -o -d file` | 逻辑或（满足一个即可） |

```bash
file="/etc/passwd"

if [ -f "$file" ]; then
    echo "$file 是普通文件"
fi

if [ -r "$file" -a -w "$file" ]; then
    echo "文件可读可写"
fi
```

### 4.3 逻辑运算

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `!` | 逻辑非 | `[ ! -f file ]` |
| `-a` | 逻辑与（test 内） | `[ $a -gt 0 -a $a -lt 10 ]` |
| `-o` | 逻辑或（test 内） | `[ $a -lt 0 -o $a -gt 10 ]` |
| `&&` | 逻辑与（连接命令） | `[ -f file ] && echo "存在"` |
| `\|\|` | 逻辑或（连接命令） | `[ -f file ] \|\| echo "不存在"` |

```bash
# && 和 || 的巧妙用法
# 如果前一个命令成功，则执行后一个
[ -f /etc/passwd ] && echo "文件存在"

# 如果前一个命令失败，则执行后一个
[ -f /etc/nonexist ] || echo "文件不存在"

# 组合使用
[ -d /tmp ] && echo "目录存在" || echo "目录不存在"
```

### 4.4 (( )) 双括号语法

双括号支持 C 语言风格的比较和运算，更直观：

```bash
a=10
b=20

if (( a > b )); then
    echo "a > b"
elif (( a == b )); then
    echo "a == b"
else
    echo "a < b"
fi

# 支持 && 和 ||
if (( a > 0 && b > 0 )); then
    echo "都大于 0"
fi
```

### 4.5 [[ ]] 双方括号语法

双方括号是 Bash 的增强版 test，支持字符串模式匹配和正则：

```bash
str="hello world"

# 模式匹配（右侧是通配符模式）
if [[ "$str" == h* ]]; then
    echo "以 h 开头"
fi

# 正则匹配（=~ 运算符，右侧是正则表达式）
if [[ "$str" =~ ^h.*d$ ]]; then
    echo "匹配正则"
fi

# 逻辑运算更自然
if [[ -f /etc/passwd && -r /etc/passwd ]]; then
    echo "文件存在且可读"
fi
```

### 4.6 case 语句

适用于多分支判断，相当于其他语言的 switch：

```bash
read -p "请输入一个数字（1-3）：" num

case $num in
    1)
        echo "你输入了 1"
        ;;
    2)
        echo "你输入了 2"
        ;;
    3)
        echo "你输入了 3"
        ;;
    *)
        echo "输入无效"
        ;;
esac
```

**case 的模式匹配**：

```bash
read -p "请输入文件名：" filename

case $filename in
    *.txt)
        echo "文本文件"
        ;;
    *.sh)
        echo "Shell 脚本"
        ;;
    *.jpg|*.png|*.gif)
        echo "图片文件"
        ;;
    [a-z]*)
        echo "以小写字母开头"
        ;;
    *)
        echo "其他类型"
        ;;
esac
```

---

## 第五章：循环结构

### 5.1 for 循环

#### 5.1.1 遍历列表

```bash
# 遍历字符串列表
for fruit in apple banana cherry; do
    echo "水果：$fruit"
done

# 遍历数组
fruits=("apple" "banana" "cherry")
for fruit in "${fruits[@]}"; do
    echo "水果：$fruit"
done

# 遍历命令输出
for file in $(ls /etc); do
    echo "文件：$file"
done

# 数字范围
for i in {1..5}; do
    echo "数字：$i"
done

# 带步长的范围
for i in {0..10..2}; do
    echo "偶数：$i"
done
```

#### 5.1.2 C 语言风格 for 循环

```bash
for ((i=1; i<=5; i++)); do
    echo "第 $i 次循环"
done

# 倒序
for ((i=5; i>=1; i--)); do
    echo "倒计时：$i"
done
```

### 5.2 while 循环

条件为真时循环执行：

```bash
i=1
while [ $i -le 5 ]; do
    echo "第 $i 次循环"
    i=$((i + 1))
done

# 读取文件逐行处理
while read line; do
    echo "内容：$line"
done < /etc/passwd

# 无限循环
while true; do
    echo "死循环，按 Ctrl+C 退出"
    sleep 1
done
```

### 5.3 until 循环

条件为假时循环执行（与 while 相反）：

```bash
i=1
until [ $i -gt 5 ]; do
    echo "第 $i 次循环"
    i=$((i + 1))
done
```

### 5.4 循环控制

```bash
# break：跳出循环
for i in {1..10}; do
    if [ $i -eq 5 ]; then
        break    # i=5 时跳出循环
    fi
    echo "i = $i"
done

# continue：跳过本次循环
for i in {1..10}; do
    if [ $((i % 2)) -eq 0 ]; then
        continue   # 偶数跳过
    fi
    echo "奇数：$i"
done

# break N / continue N：跳出/跳过 N 层循环
for i in {1..3}; do
    for j in {1..3}; do
        if [ $j -eq 2 ]; then
            break 2   # 跳出两层循环
        fi
        echo "i=$i, j=$j"
    done
done
```

### 5.5 select 循环

用于创建简单的交互式菜单：

```bash
PS3="请选择一个选项："

select choice in "选项一" "选项二" "选项三" "退出"; do
    case $choice in
        "选项一")
            echo "你选择了选项一"
            ;;
        "选项二")
            echo "你选择了选项二"
            ;;
        "选项三")
            echo "你选择了选项三"
            ;;
        "退出")
            echo "再见！"
            break
            ;;
        *)
            echo "无效选项"
            ;;
    esac
done
```

---

## 第六章：函数

### 6.1 函数定义

```bash
# 方式一
function func_name {
    # 函数体
}

# 方式二（推荐，更可移植）
func_name() {
    # 函数体
}
```

### 6.2 函数调用与参数

```bash
greet() {
    echo "Hello, $1!"
    echo "你今年 $2 岁"
}

# 调用函数并传参
greet "张三" 25
```

### 6.3 函数返回值

Shell 函数的返回值是退出状态码（0~255），与命令一样：

```bash
add() {
    local sum=$(( $1 + $2 ))
    return $sum    # return 只能返回 0~255 的整数
}

add 3 5
echo "结果：$?"    # 通过 $? 获取返回值
```

如果需要返回字符串或大数值，使用 echo 输出并捕获：

```bash
greet() {
    echo "Hello, $1!"
}

result=$(greet "World")
echo $result
```

### 6.4 局部变量

使用 `local` 关键字定义局部变量，仅在函数内部有效：

```bash
global_var="我是全局的"

test_func() {
    local local_var="我是局部的"
    echo "函数内：$global_var"
    echo "函数内：$local_var"
}

test_func
echo "函数外：$global_var"
echo "函数外：$local_var"   # 空，因为是局部变量
```

### 6.5 递归函数

函数可以调用自身：

```bash
# 计算阶乘
factorial() {
    local n=$1
    if [ $n -le 1 ]; then
        echo 1
    else
        echo $(( n * $(factorial $((n - 1))) ))
    fi
}

result=$(factorial 5)
echo "5! = $result"    # 120
```

### 6.6 函数库

将常用函数放到单独的文件中，通过 `source` 引入：

```bash
# 函数库文件：mylib.sh
add() { echo $(( $1 + $2 )); }
sub() { echo $(( $1 - $2 )); }
mul() { echo $(( $1 * $2 )); }

# 在主脚本中引入
source mylib.sh
# 或
. mylib.sh

add 1 2
```

---

## 第七章：数组

### 7.1 数组定义

```bash
# 方式一：直接赋值
arr=("apple" "banana" "cherry")

# 方式二：逐个赋值
arr[0]="apple"
arr[1]="banana"
arr[2]="cherry"

# 方式三：使用键值对（关联数组，需先声明）
declare -A dict
dict["name"]="张三"
dict["age"]=25
```

### 7.2 访问数组元素

```bash
arr=("apple" "banana" "cherry")

# 访问单个元素
echo ${arr[0]}    # apple
echo ${arr[1]}    # banana

# 访问所有元素
echo ${arr[@]}    # apple banana cherry
echo ${arr[*]}    # apple banana cherry

# 数组长度
echo ${#arr[@]}   # 3

# 数组索引列表
echo ${!arr[@]}   # 0 1 2

# 切片
echo ${arr[@]:1:2}   # 从索引 1 开始取 2 个 → banana cherry
```

### 7.3 数组操作

```bash
arr=("apple" "banana" "cherry")

# 添加元素
arr+=("date")        # 在末尾添加
arr[4]="elderberry"  # 指定索引添加

# 删除元素
unset arr[1]         # 删除索引 1 的元素
echo ${arr[@]}       # apple cherry date elderberry

# 拼接数组
arr1=(a b c)
arr2=(d e f)
arr3=("${arr1[@]}" "${arr2[@]}")
echo ${arr3[@]}      # a b c d e f

# 遍历数组
for item in "${arr[@]}"; do
    echo "元素：$item"
done

# 带索引遍历
for i in "${!arr[@]}"; do
    echo "索引 $i：${arr[$i]}"
done
```

### 7.4 关联数组

```bash
declare -A user
user["name"]="张三"
user["age"]=25
user["city"]="北京"

# 访问
echo ${user["name"]}    # 张三

# 所有值
echo ${user[@]}

# 所有键
echo ${!user[@]}

# 遍历
for key in "${!user[@]}"; do
    echo "$key: ${user[$key]}"
done
```

---

## 第八章：字符串处理

### 8.1 字符串基本操作

```bash
str="Hello World"

# 长度
echo ${#str}    # 11

# 拼接
str2="${str}, How are you?"
echo $str2

# 重复（利用 printf）
repeat=$(printf "%0.s-" {1..10})
echo $repeat    # ----------
```

### 8.2 字符串截取

```bash
str="Hello World"

# 从左截取：${str:起始位置:长度}
echo ${str:0:5}     # Hello
echo ${str:6}       # World（从第6位到结尾）
echo ${str: -5}     # World（从右数第5位，冒号后必须有空格）

# 删除匹配
# # 从左删除最短匹配
echo ${str#Hello }   # World
# ## 从左删除最长匹配
echo ${str##* }      # World
# % 从右删除最短匹配
echo ${str% World}   # Hello
# %% 从右删除最长匹配
echo ${str%% *}      # Hello
```

### 8.3 字符串替换

```bash
str="Hello World Hello"

# 替换第一个匹配
echo ${str/Hello/Hi}    # Hi World Hello

# 替换所有匹配
echo ${str//Hello/Hi}   # Hi World Hi

# 删除匹配（替换为空）
echo ${str//Hello/}     #  World 
```

### 8.4 字符串大小写转换

```bash
str="Hello World"

# 全部转大写
echo ${str^^}    # HELLO WORLD

# 全部转小写
echo ${str,,}    # hello world

# 首字母大写
echo ${str^}     # Hello World

# 首字母小写
echo ${str,}     # hello World
```

### 8.5 字符串判断

```bash
str="hello world"

# 是否包含子串（用 [[ ]] 和模式匹配）
if [[ "$str" == *"hello"* ]]; then
    echo "包含 hello"
fi

# 是否以指定开头
if [[ "$str" == h* ]]; then
    echo "以 h 开头"
fi

# 是否以指定结尾
if [[ "$str" == *d ]]; then
    echo "以 d 结尾"
fi

# 空字符串判断
if [ -z "$str" ]; then
    echo "空字符串"
fi

if [ -n "$str" ]; then
    echo "非空字符串"
fi
```

### 8.6 字符串与 awk/sed 配合

```bash
str="hello world"

# 使用 awk 截取第 2 个字段
echo $str | awk '{print $2}'    # world

# 使用 sed 替换
echo $str | sed 's/world/Shell/'   # hello Shell

# 使用 cut 截取
echo "a,b,c,d" | cut -d, -f2    # b
```

---

## 第九章：文件与目录操作

### 9.1 文件读写

```bash
# 读取文件内容
content=$(cat filename)

# 逐行读取文件
while read line; do
    echo "行内容：$line"
done < filename

# 写入文件（覆盖）
echo "hello" > output.txt

# 追加写入
echo "world" >> output.txt

# 多行写入（Here Document）
cat > output.txt << EOF
第一行内容
第二行内容
第三行内容
EOF

# Here String（从字符串读取）
read a b <<< "hello world"
echo "a=$a, b=$b"
```

### 9.2 文件属性判断

| 测试符 | 含义 |
|--------|------|
| `-e` | 存在 |
| `-f` | 普通文件 |
| `-d` | 目录 |
| `-r` | 可读 |
| `-w` | 可写 |
| `-x` | 可执行 |
| `-s` | 非空（大小 > 0） |
| `-L` | 符号链接 |
| `-b` | 块设备文件 |
| `-c` | 字符设备文件 |
| `-p` | 管道文件 |
| `-S` | 套接字文件 |
| `-nt` | 比...新（file1 -nt file2） |
| `-ot` | 比...旧（file1 -ot file2） |

```bash
file="/etc/passwd"

if [ -f "$file" ]; then
    echo "$file 存在且是普通文件"
    if [ -r "$file" ]; then
        echo "文件可读"
    fi
    if [ -s "$file" ]; then
        echo "文件非空"
    fi
fi
```

### 9.3 目录遍历

```bash
# 遍历目录下的文件
for file in /etc/*; do
    if [ -f "$file" ]; then
        echo "文件：$file"
    fi
done

# 递归遍历目录
find /etc -name "*.conf" -type f | while read file; do
    echo "配置文件：$file"
done

# 遍历目录树
for dir in $(find /path -type d); do
    echo "目录：$dir"
done
```

### 9.4 文件描述符与重定向

| 文件描述符 | 名称 | 说明 |
|-----------|------|------|
| 0 | stdin | 标准输入 |
| 1 | stdout | 标准输出 |
| 2 | stderr | 标准错误 |

```bash
# 重定向标准输出
echo "hello" > output.txt     # 覆盖
echo "hello" >> output.txt    # 追加

# 重定向标准错误
ls /nonexist 2> error.log     # 错误输出到文件
ls /nonexist 2>> error.log    # 追加错误

# 同时重定向 stdout 和 stderr
command > output.txt 2>&1
# 或简写（Bash 4+）
command &> output.txt

# 丢弃输出（黑洞）
command > /dev/null 2>&1

# 从文件读取输入
read line < input.txt

# 同时重定向输入和输出
command < input.txt > output.txt 2>&1
```

### 9.5 文件权限操作

```bash
# 修改权限
chmod 755 script.sh
chmod +x script.sh       # 添加执行权限
chmod -R 644 /path/dir   # 递归修改

# 修改所有者
chown user:group file.txt
chown -R user:group /path

# 修改所属组
chgrp group file.txt
```

---

## 第十章：正则表达式

### 10.1 正则基础

正则表达式（Regular Expression，简称 regex）是用于匹配字符串模式的强大工具，在 Shell 中常与 `grep`、`sed`、`awk` 配合使用。

#### 基础元字符

| 符号 | 说明 | 示例 |
|------|------|------|
| `.` | 匹配任意单个字符（除换行） | `a.c` 匹配 abc, a1c, a@c |
| `*` | 前一个字符出现 0 次或多次 | `ab*c` 匹配 ac, abc, abbc |
| `+` | 前一个字符出现 1 次或多次 | `ab+c` 匹配 abc, abbc（不匹配 ac） |
| `?` | 前一个字符出现 0 次或 1 次 | `ab?c` 匹配 ac, abc |
| `{n}` | 前一个字符恰好出现 n 次 | `a{3}` 匹配 aaa |
| `{n,}` | 前一个字符至少出现 n 次 | `a{2,}` 匹配 aa, aaa, ... |
| `{n,m}` | 前一个字符出现 n~m 次 | `a{2,4}` 匹配 aa, aaa, aaaa |
| `^` | 匹配行首 | `^hello` 匹配以 hello 开头的行 |
| `$` | 匹配行尾 | `world$` 匹配以 world 结尾的行 |
| `[...]` | 匹配括号内任意一个字符 | `[abc]` 匹配 a, b, c 中的一个 |
| `[^...]` | 匹配不在括号内的任意字符 | `[^abc]` 匹配除 a,b,c 外的字符 |
| `[a-z]` | 匹配范围内的字符 | `[0-9]` 匹配数字，`[a-z]` 匹配小写字母 |
| `\` | 转义特殊字符 | `\.` 匹配真正的点号 |
| `\(` `\)` | 分组捕获（基础正则） | `\(ab\)*` 匹配 ab 出现任意次 |
| `\|` | 或（基础正则） | `a\|b` 匹配 a 或 b |

#### 扩展正则元字符（grep -E / sed -r）

| 符号 | 说明 |
|------|------|
| `+` | 一次或多次 |
| `?` | 零次或一次 |
| `{n,m}` | 范围次数（不用转义） |
| `()` | 分组（不用转义） |
| `\|` | 或（不用转义） |

#### 预定义字符类

| 符号 | 说明 | 等价于 |
|------|------|--------|
| `\d` | 数字（仅扩展正则） | `[0-9]` |
| `\w` | 单词字符（字母数字下划线） | `[a-zA-Z0-9_]` |
| `\s` | 空白字符（空格、制表符等） | `[ \t\r\n]` |
| `\b` | 单词边界 | - |

### 10.2 grep 与正则

```bash
# 基本用法
grep "pattern" file.txt

# 常用选项
grep -i "pattern" file    # 忽略大小写
grep -v "pattern" file    # 反向匹配（不包含的行）
grep -n "pattern" file    # 显示行号
grep -c "pattern" file    # 统计匹配行数
grep -E "pattern" file    # 使用扩展正则（等价 egrep）
grep -o "pattern" file    # 只输出匹配的部分
grep -r "pattern" /dir    # 递归搜索目录

# 示例
grep "^root" /etc/passwd          # 以 root 开头的行
grep "bash$" /etc/passwd          # 以 bash 结尾的行
grep "[0-9]\{3\}" file.txt        # 包含 3 位数字的行
grep -E "[0-9]{3}" file.txt       # 同上（扩展正则）
grep -E "error|fail" log.txt      # 包含 error 或 fail 的行
```

### 10.3 sed 与正则

sed（Stream Editor）是流编辑器，常用于文本替换：

```bash
# 基本替换
sed 's/old/new/' file.txt     # 替换每行第一个匹配
sed 's/old/new/g' file.txt    # 替换所有匹配
sed 's/old/new/2' file.txt    # 替换每行第 2 个匹配

# 直接修改文件（谨慎使用）
sed -i 's/old/new/g' file.txt

# 常用操作
sed -n '1,10p' file.txt       # 显示第 1-10 行
sed '1,10d' file.txt          # 删除第 1-10 行
sed '/pattern/d' file.txt     # 删除匹配行
sed -i '/^$/d' file.txt       # 删除空行
sed 's/^#//' file.txt         # 删除行首的 # 号
sed 'y/abc/ABC/' file.txt     # 字符替换（a→A, b→B, c→C）
```

### 10.4 awk 与正则

awk 是强大的文本处理语言，支持正则：

```bash
# 匹配包含 pattern 的行
awk '/pattern/' file.txt

# 条件判断
awk '$1 == "root"' /etc/passwd
awk '$3 >= 1000' /etc/passwd

# 常用内置变量
awk -F: '{print $1, $3}' /etc/passwd    # -F 指定分隔符，$1 第一列
awk '{print NR, $0}' file.txt            # NR 行号，$0 整行
awk '{print NF, $NF}' file.txt           # NF 字段数，$NF 最后一列

# 示例
awk -F: '$7 == "/bin/bash" {print $1}' /etc/passwd   # 打印使用 bash 的用户
```

---

## 第十一章：信号与陷阱

### 11.1 常见信号

| 信号 | 编号 | 说明 |
|------|------|------|
| HUP | 1 | 挂起（终端断开时发送） |
| INT | 2 | 中断（Ctrl+C） |
| QUIT | 3 | 退出（Ctrl+\） |
| KILL | 9 | 强制终止（不能被捕获） |
| TERM | 15 | 终止（默认信号） |
| STOP | 19 | 暂停（不能被捕获） |
| TSTP | 20 | 终端暂停（Ctrl+Z） |
| ALRM | 14 | 闹钟信号 |
| CHLD | 17 | 子进程结束 |

### 11.2 trap 命令

`trap` 用于捕获信号并执行指定命令：

```bash
# 捕获 Ctrl+C 信号
trap "echo '收到中断信号，正在退出...'; exit" SIGINT

# 捕获多个信号
trap "cleanup; exit" SIGINT SIGTERM SIGHUP

# 忽略信号
trap '' SIGINT

# 恢复默认行为
trap - SIGINT
```

**完整示例**：

```bash
#!/bin/bash

# 清理函数
cleanup() {
    echo "正在清理临时文件..."
    rm -f /tmp/temp_file_$$
    echo "清理完成"
}

# 注册信号处理
trap cleanup EXIT    # 脚本退出时执行
trap 'echo "收到中断信号"; exit 1' SIGINT SIGTERM

# 主逻辑
echo "脚本运行中，PID: $$"
echo "按 Ctrl+C 中断"
sleep 10
echo "脚本正常结束"
```

---

## 第十二章：Shell 调试与最佳实践

### 12.1 Shell 调试

```bash
# 方式一：使用 bash -x 运行脚本
bash -x script.sh

# 方式二：在脚本中添加 set -x
set -x     # 开启调试（显示执行的命令和变量）
# ... 调试的代码段 ...
set +x     # 关闭调试

# 其他调试选项
set -e     # 遇到错误立即退出
set -u     # 使用未定义的变量时报错
set -o pipefail   # 管道中任一命令失败则整体失败
```

**常用 set 选项**：

| 选项 | 说明 |
|------|------|
| `-e` | 命令失败（非 0 退出码）时立即退出脚本 |
| `-u` | 使用未定义变量时报错 |
| `-x` | 调试模式，打印执行的命令和参数 |
| `-v` | 详细模式，打印读取的每一行输入 |
| `-n` | 语法检查，不实际执行 |
| `-o pipefail` | 管道中任一命令失败，整体返回失败 |

> **推荐脚本开头**：`set -euo pipefail`

### 12.2 错误处理

```bash
# 检查命令是否成功
if command; then
    echo "成功"
else
    echo "失败"
    exit 1
fi

# 失败时退出
command || exit 1

# 失败时输出错误信息并退出
command || { echo "命令失败"; exit 1; }

# 自定义错误函数
error_exit() {
    echo "错误：$1" >&2
    exit 1
}

command || error_exit "执行 command 失败"
```

### 12.3 最佳实践

1. **脚本开头加上 Shebang 和基本设置**
   ```bash
   #!/bin/bash
   set -euo pipefail
   ```

2. **使用有意义的变量名**，避免 a、b、c 这种无意义的命名

3. **变量用双引号括起来**，防止单词拆分和空变量问题
   ```bash
   if [ "$name" = "admin" ]; then ...
   ```

4. **函数内使用 local 变量**，避免污染全局命名空间

5. **添加注释**，说明脚本的用途、参数、返回值等

6. **使用函数封装重复代码**，提高复用性和可维护性

7. **使用 `$()` 代替反引号**，更易读且支持嵌套

8. **脚本加执行权限**，使用 `./script.sh` 方式运行

9. **输入验证**，检查用户输入和参数是否合法

10. **错误处理**，对可能失败的命令进行错误检查

11. **使用 [[ ]] 代替 [ ]**，更强大更安全

12. **脚本文件命名规范**，使用 `.sh` 后缀，小写字母和下划线

### 12.4 常用脚本模板

```bash
#!/bin/bash
set -euo pipefail

# ============================================================
# 脚本名称：script_name.sh
# 功能描述：脚本的功能说明
# 作者：Your Name
# 创建日期：2026-01-01
# 用法：./script_name.sh [参数]
# ============================================================

# 常量定义
readonly SCRIPT_NAME=$(basename "$0")
readonly SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# 用法说明
usage() {
    echo "用法：$SCRIPT_NAME [选项] <参数>"
    echo "选项："
    echo "  -h, --help    显示帮助信息"
    echo "  -v, --version 显示版本信息"
    exit 0
}

# 主函数
main() {
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                ;;
            -v|--version)
                echo "v1.0.0"
                exit 0
                ;;
            *)
                echo "未知选项：$1"
                usage
                ;;
        esac
        shift
    done

    echo "脚本开始执行..."
    # 主逻辑
    echo "脚本执行完成"
}

main "$@"
```

---

## 附录：代码示例索引

所有示例代码保存在 `shell/` 目录下：

| 文件名 | 对应章节 | 内容说明 |
|--------|---------|---------|
| `01_hello.sh` | 第一章 | 第一个 Shell 脚本 |
| `02_variables.sh` | 第三章 | 变量定义与使用 |
| `03_special_vars.sh` | 第三章 | 特殊变量与命令行参数 |
| `04_if.sh` | 第四章 | if 条件判断 |
| `05_case.sh` | 第四章 | case 多分支 |
| `06_for_loop.sh` | 第五章 | for 循环 |
| `07_while_loop.sh` | 第五章 | while 循环 |
| `08_functions.sh` | 第六章 | 函数定义与使用 |
| `09_arrays.sh` | 第七章 | 数组操作 |
| `10_strings.sh` | 第八章 | 字符串处理 |
| `11_file_ops.sh` | 第九章 | 文件与目录操作 |
| `12_regex_grep.sh` | 第十章 | 正则与 grep |
| `13_sed_examples.sh` | 第十章 | sed 示例 |
| `14_awk_examples.sh` | 第十章 | awk 示例 |
| `15_signal_trap.sh` | 第十一章 | 信号与 trap |
| `16_debug.sh` | 第十二章 | 调试与最佳实践 |
| `template.sh` | 第十二章 | 脚本模板 |
| `backup.sh` | 综合示例 | 自动备份脚本 |
| `monitor.sh` | 综合示例 | 系统监控脚本 |
| `batch_rename.sh` | 综合示例 | 批量重命名脚本 |

---

> **延伸学习**：Shell 脚本是自动化运维和安全工具开发的基础。结合实际场景多练习，尝试用脚本解决日常工作中的重复性问题。同时可学习 Python 等其他脚本语言，根据不同场景选择最合适的工具。
