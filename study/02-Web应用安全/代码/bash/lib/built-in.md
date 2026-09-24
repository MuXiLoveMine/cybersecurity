# built-in functions - Bash 内置命令与函数

> Bash Shell 的常用内置命令、内置函数和常用工具。

---

## 一、常用内置命令

### 1.1 基本输出与输入

```bash
# echo - 输出文本
echo "Hello World"
echo -n "no newline"    # 不换行
echo -e "tab\there"     # 解析转义字符

# printf - 格式化输出（更强大）
printf "Name: %s, Age: %d\n" "Alice" 25
printf "%.2f\n" 3.14159  # 保留两位小数

# read - 读取输入
read -p "Enter your name: " name
echo "Hello, $name"

read -s -p "Enter password: " password  # -s 不回显
echo

read -t 10 -p "10秒内输入: " input  # -t 超时
```

### 1.2 变量与环境

```bash
# 变量赋值
name="Alice"
age=25

# 引用变量
echo $name
echo ${name}  # 更清晰的写法

# 只读变量
readonly PI=3.14159

# 环境变量
export PATH="/usr/local/bin:$PATH"
echo $HOME
echo $USER
echo $PWD

# 变量默认值
echo ${var:-default}   # var 未设置则用 default
echo ${var:=default}   # var 未设置则赋值并返回
echo ${var:?message}   # var 未设置则报错退出
echo ${var:+replacement} # var 已设置则返回 replacement

# 变量长度
str="hello"
echo ${#str}  # 5

# 字符串截取
str="hello world"
echo ${str:0:5}   # hello
echo ${str:6}     # world
echo ${str: -5}   # world（从末尾数）

# 字符串替换
str="hello world hello"
echo ${str/hello/hi}   # hi world hello（替换第一个）
echo ${str//hello/hi}  # hi world hi（替换所有）

# 字符串删除
path="/usr/local/bin/program"
echo ${path#*/}   # usr/local/bin/program（删最短前缀）
echo ${path##*/}  # program（删最长前缀）
echo ${path%/*}   # /usr/local/bin（删最短后缀）
echo ${path%%/*}  # 空（删最长后缀）
```

### 1.3 条件测试

```bash
# [ ] 或 test 命令
if [ -f file.txt ]; then
    echo "文件存在"
fi

# [[ ]] 推荐（bash 扩展，支持更多功能）
if [[ -f file.txt && -r file.txt ]]; then
    echo "文件存在且可读"
fi

# 字符串测试
[[ "$a" == "$b" ]]    # 相等
[[ "$a" != "$b" ]]    # 不相等
[[ -z "$str" ]]       # 空字符串
[[ -n "$str" ]]       # 非空字符串
[[ "$str" =~ pattern ]]  # 正则匹配

# 数值测试
[[ $a -eq $b ]]   # 等于
[[ $a -ne $b ]]   # 不等于
[[ $a -gt $b ]]   # 大于
[[ $a -ge $b ]]   # 大于等于
[[ $a -lt $b ]]   # 小于
[[ $a -le $b ]]   # 小于等于

# 文件测试
[[ -e file ]]   # 存在
[[ -f file ]]   # 普通文件
[[ -d dir ]]    # 目录
[[ -r file ]]   # 可读
[[ -w file ]]   # 可写
[[ -x file ]]   # 可执行
[[ -s file ]]   # 非空（大小 > 0）
[[ -L file ]]   # 符号链接
[[ file1 -nt file2 ]]  # file1 比 file2 新
[[ file1 -ot file2 ]]  # file1 比 file2 旧
```

### 1.4 控制流

```bash
# if-elif-else
if [[ condition1 ]]; then
    # ...
elif [[ condition2 ]]; then
    # ...
else
    # ...
fi

# for 循环
for i in 1 2 3 4 5; do
    echo $i
done

for file in *.txt; do
    echo "处理: $file"
done

# C 风格 for 循环
for ((i=0; i<10; i++)); do
    echo $i
done

# while 循环
while [[ condition ]]; do
    # ...
done

# until 循环（条件为假时执行）
until [[ condition ]]; do
    # ...
done

# case
case "$var" in
    pattern1)
        # ...
        ;;
    pattern2)
        # ...
        ;;
    *)
        # 默认
        ;;
esac
```

### 1.5 函数

```bash
# 定义函数
function greet {
    echo "Hello, $1!"
    return 0  # 返回状态码（0-255）
}

# 或
greet() {
    echo "Hello, $1!"
}

# 调用
greet "World"

# 函数参数
example() {
    echo "参数个数: $#"
    echo "第一个参数: $1"
    echo "第二个参数: $2"
    echo "所有参数: $@"
    echo "所有参数（字符串）: $*"
}

# 局部变量
func() {
    local localVar="only in function"
    echo $localVar
}
```

---

## 二、常用外部命令

### 2.1 文件操作

```bash
# ls - 列出目录
ls -la        # 详细列表
ls -lh        # 人类可读大小
ls -lt        # 按时间排序
ls -R         # 递归

# cp - 复制
cp src dst
cp -r src_dir dst_dir   # 递归复制目录
cp -i src dst           # 交互模式（覆盖前提示）
cp -a src dst           # 归档模式（保留属性）

# mv - 移动/重命名
mv old new
mv file /path/to/dest/

# rm - 删除
rm file
rm -r dir       # 递归删除目录
rm -rf dir      # 强制递归删除（危险！）
rm -i file      # 交互模式

# mkdir - 创建目录
mkdir dirname
mkdir -p path/to/dir   # 递归创建
mkdir -m 755 dir       # 指定权限

# touch - 创建文件/修改时间
touch filename
touch -d "2024-01-01" filename  # 指定时间

# cat - 查看文件
cat file.txt
cat file1 file2 > combined  # 合并

# less / more - 分页查看
less filename   # 推荐（支持向前翻页）

# head / tail - 查看头尾
head -n 20 file.txt   # 前 20 行
tail -n 20 file.txt   # 后 20 行
tail -f file.txt      # 实时跟踪文件变化
```

### 2.2 文本处理

```bash
# grep - 文本搜索
grep "pattern" file.txt
grep -i "pattern" file.txt    # 忽略大小写
grep -r "pattern" /path/      # 递归搜索
grep -n "pattern" file.txt    # 显示行号
grep -v "pattern" file.txt    # 反向匹配（不包含）
grep -c "pattern" file.txt    # 统计匹配行数
grep -E "regex" file.txt      # 扩展正则
grep -o "pattern" file.txt    # 只输出匹配部分

# sed - 流编辑器
sed 's/old/new/' file.txt        # 替换每行第一个
sed 's/old/new/g' file.txt       # 全局替换
sed -i 's/old/new/g' file.txt    # 直接修改文件
sed '2d' file.txt                # 删除第 2 行
sed -n '1,5p' file.txt           # 显示 1-5 行
sed '/pattern/d' file.txt        # 删除匹配行

# awk - 文本处理语言
awk '{print $1}' file.txt          # 打印第一列
awk -F: '{print $1}' /etc/passwd   # 指定分隔符
awk '$3 > 100' file.txt            # 条件过滤
awk '{sum += $1} END {print sum}'  # 求和

# sort - 排序
sort file.txt
sort -r file.txt     # 逆序
sort -n file.txt     # 按数值排序
sort -u file.txt     # 去重
sort -k2 file.txt    # 按第二列排序

# uniq - 去重（需先排序）
sort file.txt | uniq
sort file.txt | uniq -c   # 统计出现次数
sort file.txt | uniq -d   # 只显示重复行

# wc - 统计
wc file.txt         # 行数 单词数 字节数
wc -l file.txt      # 行数
wc -w file.txt      # 单词数
wc -c file.txt      # 字节数

# cut - 截取列
cut -d: -f1 /etc/passwd    # 第一列
cut -c1-10 file.txt        # 第 1-10 个字符

# tr - 字符转换
echo "hello" | tr a-z A-Z     # 转大写
echo "hello" | tr -d 'l'      # 删除字符
```

### 2.3 进程与系统

```bash
# ps - 查看进程
ps aux          # 所有进程详细信息
ps -ef          # 所有进程
ps aux | grep nginx

# top / htop - 实时进程监控
top

# kill - 终止进程
kill PID           # 发送 TERM 信号
kill -9 PID        # 强制终止（SIGKILL）
kill -l            # 列出所有信号

# killall / pkill - 按名称终止
killall nginx
pkill -f pattern

# systemctl - 系统服务管理
systemctl start nginx
systemctl stop nginx
systemctl restart nginx
systemctl status nginx
systemctl enable nginx    # 开机自启
systemctl disable nginx   # 取消开机自启

# jobs / bg / fg - 作业控制
command &         # 后台运行
jobs              # 列出作业
bg %1             # 后台继续
fg %1             # 前台继续
Ctrl+Z            # 挂起当前进程

# nohup - 不挂断运行
nohup command &   # 退出终端也继续运行
```

### 2.4 网络工具

```bash
# curl - HTTP 客户端
curl https://example.com
curl -o file.html https://example.com   # 保存到文件
curl -O https://example.com/file.zip    # 用原名保存
curl -I https://example.com             # 只看响应头
curl -d "name=test" https://api.example.com  # POST
curl -H "Authorization: Bearer token" https://api.example.com
curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' url
curl -s https://example.com             # 静默模式
curl -L https://example.com             # 跟随重定向

# wget - 文件下载
wget https://example.com/file.zip
wget -c https://example.com/file.zip    # 断点续传
wget -r https://example.com             # 递归下载

# netstat / ss - 网络连接
netstat -tulnp     # 监听端口（需要 root）
ss -tulnp          # 更现代的版本
netstat -an        # 所有连接

# ping - 网络连通性
ping example.com
ping -c 4 example.com   # 只发 4 个包

# traceroute / tracepath - 路由追踪
traceroute example.com

# dig / nslookup - DNS 查询
dig example.com
dig example.com MX       # 查询 MX 记录
nslookup example.com

# ifconfig / ip - 网络接口
ifconfig
ip addr show
ip link show
ip route show
```

---

## 三、安全相关内容

### 3.1 命令注入风险

```bash
# ===== 危险：直接使用用户输入 =====
# 脚本中如果有这样的代码：
echo "输入文件名:"
read filename
cat $filename
# 攻击：输入 `; rm -rf /;` 或 `$(rm -rf /)`

# ===== 危险：eval 执行用户输入 =====
input="ls; rm -rf /"
eval $input  # ❌ 极度危险！

# ===== 安全：正确引用变量 =====
filename="test file.txt"
cat "$filename"  # ✅ 用双引号包裹，防止空格分割

# ===== 安全：参数验证 =====
if [[ ! "$filename" =~ ^[a-zA-Z0-9_.]+$ ]]; then
    echo "非法文件名"
    exit 1
fi

# ===== 数组参数（避免分词问题）=====
args=("file1.txt" "file with spaces.txt")
cat "${args[@]}"  # ✅ 安全
```

### 3.2 脚本安全最佳实践

```bash
#!/bin/bash

# 在脚本开头添加这些设置
set -e          # 任何命令失败就退出
set -u          # 使用未定义变量时报错
set -o pipefail # 管道中任一命令失败则整个管道失败
# 通常可以合并为：
set -euo pipefail

# 或者加上 x 用于调试
set -x          # 打印执行的命令（调试用）

# ===== 安全的临时文件 =====
# 不要用固定的临时文件名（竞争条件）
tmpfile="/tmp/myscript.tmp"  # ❌ 危险！

# 用 mktemp 创建唯一临时文件
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT  # 脚本退出时自动清理

# 临时目录
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

# ===== 权限检查 =====
if [[ $EUID -ne 0 ]]; then
    echo "需要 root 权限运行"
    exit 1
fi

# ===== 输入验证 =====
validate_port() {
    local port="$1"
    if [[ ! "$port" =~ ^[0-9]+$ ]]; then
        echo "端口必须是数字"
        return 1
    fi
    if [[ $port -lt 1 || $port -gt 65535 ]]; then
        echo "端口范围 1-65535"
        return 1
    fi
    return 0
}
```

### 3.3 敏感信息处理

```bash
# ===== 不要在脚本中硬编码密码 =====
# ❌ 错误
DB_PASSWORD="super_secret"

# ✅ 正确：使用环境变量
DB_PASSWORD="${DB_PASSWORD:-}"
if [[ -z "$DB_PASSWORD" ]]; then
    echo "请设置 DB_PASSWORD 环境变量"
    exit 1
fi

# 或从文件读取（限制文件权限）
# chmod 600 /etc/secret.conf
source /etc/secret.conf

# ===== 隐藏命令中的敏感参数 =====
# 密码出现在命令行中会被其他用户通过 ps 看到
# ❌ 危险
mysql -u root -p"password" database

# ✅ 安全：使用配置文件
# ~/.my.cnf
# [client]
# password = password

# 或从 stdin 读取
echo "$password" | mysql -u root --password-stdin database

# ===== 日志中隐藏敏感数据 =====
# 不要把密码等敏感信息写入日志
# 打印参数时脱敏
log_params() {
    echo "username: $username"
    echo "password: ***"  # 不输出真实密码
}
```

---

## 四、特殊变量

| 变量 | 含义 |
|------|------|
| `$0` | 脚本名称 |
| `$1` - `$9` | 第 1-9 个参数 |
| `$#` | 参数个数 |
| `$@` | 所有参数（数组形式） |
| `$*` | 所有参数（字符串形式） |
| `$$` | 当前进程 PID |
| `$!` | 最后一个后台进程 PID |
| `$?` | 上一个命令的退出状态码 |
| `$PWD` | 当前工作目录 |
| `$HOME` | 用户主目录 |
| `$USER` | 当前用户名 |
| `$PATH` | 命令搜索路径 |
| `$RANDOM` | 0-32767 之间的随机数（不加密安全） |
