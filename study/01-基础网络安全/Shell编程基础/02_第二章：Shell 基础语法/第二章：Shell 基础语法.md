# 第二章：Shell 基础语法

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

---

