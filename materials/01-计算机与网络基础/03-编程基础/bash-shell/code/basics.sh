#!/bin/bash
#
# basics.sh —— Bash 基础语法示例（安全从业者视角）
#
# 涵盖内容：
#   1. 变量与环境变量
#   2. 条件判断（if / case）
#   3. 循环（for / while / until）
#   4. 函数
#   5. 文件操作
#   6. 管道与重定向
#   7. 命令替换与算术运算
#   8. 字符串处理
#   9. 数组
#  10. 命令行参数
#
# 运行方式：
#   bash basics.sh
#
# 注意：本脚本用于学习参考，可以直接运行查看输出。

# 安全选项（严谨的脚本会加这些）
# set -euo pipefail
# 这里没开是因为示例脚本需要展示各种情况

echo "============================================================"
echo "  Bash 基础语法示例（安全从业者视角）"
echo "  Bash Basics for Security Practitioners"
echo "============================================================"
echo ""

# ============================================================
# 1. 变量与环境变量
# ============================================================
demo_variables() {
    echo "============================================================"
    echo "【1. 变量与环境变量】"
    echo "============================================================"

    # 自定义变量（等号两边不能有空格！）
    name="Alice"
    age=25
    ip_address="192.168.1.100"

    echo ""
    echo "1.1 自定义变量"
    echo "  姓名: $name"
    echo "  年龄: $age"
    echo "  IP: $ip_address"
    echo "  花括号形式: ${name}的IP是${ip_address}"

    # 只读变量
    readonly PI=3.14159
    echo ""
    echo "1.2 只读变量"
    echo "  PI = $PI (不能修改)"

    # 环境变量
    echo ""
    echo "1.3 常用环境变量"
    echo "  当前用户: $USER"
    echo "  宿主名: $HOSTNAME"
    echo "  Home 目录: $HOME"
    echo "  Shell: $SHELL"
    echo "  脚本 PID: $$"
    echo "  脚本名称: $0"
    echo "  参数数量: $#"
    echo "  所有参数: $@"

    # 特殊变量
    echo ""
    echo "1.4 特殊变量"
    echo "  \$0 = $0 (脚本名)"
    echo "  \$1 = ${1:-空} (第一个参数)"
    echo "  \$# = $# (参数个数)"
    echo "  \$@ = $@ (所有参数)"

    # 变量的默认值
    echo ""
    echo "1.5 变量默认值"
    unset undefined_var
    echo "  undefined_var = ${undefined_var:-'默认值'}"
    echo "  （如果变量未定义或为空，使用默认值）"
    echo ""
}

# ============================================================
# 2. 条件判断
# ============================================================
demo_conditionals() {
    echo "============================================================"
    echo "【2. 条件判断（if / case）】"
    echo "============================================================"

    # ---- if 基础 ----
    echo ""
    echo "2.1 if 语句基础"
    score=85
    echo "  分数: $score"

    if [ "$score" -ge 90 ]; then
        echo "  评级: 优秀 (A)"
    elif [ "$score" -ge 80 ]; then
        echo "  评级: 良好 (B)"
    elif [ "$score" -ge 60 ]; then
        echo "  评级: 及格 (C)"
    else
        echo "  评级: 不及格 (D)"
    fi

    # ---- 文件测试 ----
    echo ""
    echo "2.2 文件测试"
    test_file="/tmp/bash_basics_test_$$.txt"
    touch "$test_file"

    if [ -f "$test_file" ]; then
        echo "  $test_file 是文件 ✓"
    fi
    if [ -s "$test_file" ]; then
        echo "  $test_file 非空"
    else
        echo "  $test_file 是空的"
    fi
    if [ -w "$test_file" ]; then
        echo "  $test_file 可写 ✓"
    fi

    rm -f "$test_file"

    # ---- 字符串测试 ----
    echo ""
    echo "2.3 字符串测试"
    str1="hello"
    str2="world"

    if [ "$str1" = "$str2" ]; then
        echo "  字符串相等"
    else
        echo "  字符串不相等: '$str1' vs '$str2'"
    fi

    if [ -z "$empty_str" ]; then
        echo "  empty_str 是空的 (z = zero length)"
    fi
    if [ -n "$str1" ]; then
        echo "  str1 非空 (n = non-zero)"
    fi

    # ---- 数字比较 ----
    echo ""
    echo "2.4 数字比较"
    a=10
    b=20
    echo "  a = $a, b = $b"
    [ "$a" -lt "$b" ] && echo "  a < b ✓"
    [ "$a" -le "$b" ] && echo "  a <= b ✓"
    [ "$b" -gt "$a" ] && echo "  b > a ✓"

    # ---- 逻辑运算 ----
    echo ""
    echo "2.5 逻辑运算"
    has_ip=true
    has_port=true

    if [ "$has_ip" = true ] && [ "$has_port" = true ]; then
        echo "  IP 和端口都配置了，可以扫描"
    fi

    if [ "$has_ip" = false ] || [ "$has_port" = false ]; then
        echo "  配置不完整"
    else
        echo "  配置完整（逻辑或测试通过）"
    fi

    # ---- [[ ]] 增强测试 ----
    echo ""
    echo "2.6 [[ ]] 增强测试（正则匹配）"
    ip="192.168.1.1"
    if [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "  '$ip' 看起来像 IP 地址格式"
    else
        echo "  '$ip' 不像 IP 地址"
    fi

    # ---- case 语句 ----
    echo ""
    echo "2.7 case 分支"
    os=$(uname -s)
    echo "  当前系统: $os"
    case "$os" in
        Linux)
            echo "  → Linux 系统"
            ;;
        Darwin)
            echo "  → macOS 系统"
            ;;
        CYGWIN*|MINGW*)
            echo "  → Windows 系统 (Cygwin/MinGW)"
            ;;
        *)
            echo "  → 未知系统: $os"
            ;;
    esac
    echo ""
}

# ============================================================
# 3. 循环
# ============================================================
demo_loops() {
    echo "============================================================"
    echo "【3. 循环（for / while / until）】"
    echo "============================================================"

    # ---- for 循环：遍历列表 ----
    echo ""
    echo "3.1 for 循环：遍历 IP 列表"
    ips=("127.0.0.1" "192.168.1.1" "10.0.0.1")
    for ip in "${ips[@]}"; do
        echo "  检查 IP: $ip"
    done

    # ---- for 循环：数字范围 ----
    echo ""
    echo "3.2 for 循环：端口扫描（模拟）"
    echo "  扫描常用端口:"
    for port in 21 22 25 53 80 443 3306 8080; do
        # 模拟检测（实际用 nc 或 socket）
        status="closed"
        [ "$port" = "22" ] || [ "$port" = "80" ] && status="open"
        echo "    端口 $port: $status"
    done

    # ---- C 风格 for ----
    echo ""
    echo "3.3 C 风格 for 循环"
    for ((i=1; i<=5; i++)); do
        echo "  第 $i 次尝试..."
    done

    # ---- while 循环 ----
    echo ""
    echo "3.4 while 循环：倒计时"
    count=3
    while [ "$count" -gt 0 ]; do
        echo "  $count..."
        count=$((count - 1))
    done
    echo "  Go!"

    # ---- 逐行读取文件 ----
    echo ""
    echo "3.5 while 逐行读取"
    test_file="/tmp/bash_basics_lines_$$.txt"
    cat > "$test_file" << 'EOF'
192.168.1.1  server1
192.168.1.2  server2
10.0.0.1     gateway
EOF
    echo "  读取文件内容:"
    while IFS=' ' read -r ip hostname; do
        echo "    $hostname 的 IP 是 $ip"
    done < "$test_file"
    rm -f "$test_file"

    # ---- until 循环 ----
    echo ""
    echo "3.6 until 循环"
    n=0
    until [ "$n" -ge 3 ]; do
        echo "  n = $n (until n >= 3 停止)"
        n=$((n + 1))
    done

    # ---- break 和 continue ----
    echo ""
    echo "3.7 break 和 continue"
    echo "  1-10，跳过 5，到 8 停止:"
    for i in {1..10}; do
        if [ "$i" -eq 5 ]; then
            continue   # 跳过 5
        fi
        if [ "$i" -eq 8 ]; then
            break      # 到 8 就退出
        fi
        echo -n "  $i"
    done
    echo ""
    echo ""
}

# ============================================================
# 4. 函数
# ============================================================

# IP 格式验证函数
validate_ip() {
    local ip="$1"
    local IFS=.
    local parts count=0

    # 用 . 分割
    parts=($ip)

    # 必须是 4 段
    if [ ${#parts[@]} -ne 4 ]; then
        return 1
    fi

    for part in "${parts[@]}"; do
        # 必须是纯数字
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

# 端口扫描函数（简化版，仅用于学习）
check_port() {
    local host="$1"
    local port="$2"
    local timeout="${3:-1}"

    # 用 bash 的 /dev/tcp 伪设备测试端口
    # 这是 Bash 特有的功能，不需要额外工具
    if (echo > /dev/tcp/"$host"/"$port") 2>/dev/null; then
        return 0  # 开放
    else
        return 1  # 关闭
    fi
}

demo_functions() {
    echo "============================================================"
    echo "【4. 函数】"
    echo "============================================================"

    echo ""
    echo "4.1 IP 格式验证函数"
    test_ips=("192.168.1.1" "10.0.0.1" "256.1.1.1" "abc" "1.2.3")
    for ip in "${test_ips[@]}"; do
        if validate_ip "$ip"; then
            echo "  ✓ $ip → 格式有效"
        else
            echo "  ✗ $ip → 格式无效"
        fi
    done

    echo ""
    echo "4.2 端口检测函数（用 /dev/tcp）"
    echo "  检测本地几个常用端口:"
    for port in 22 80 443 8080; do
        if check_port "127.0.0.1" "$port" "0.1"; then
            echo "    127.0.0.1:$port → OPEN ✓"
        else
            echo "    127.0.0.1:$port → closed"
        fi
    done

    echo ""
    echo "4.3 函数返回值的两种方式"
    echo "  方式 1: return 返回状态码（0-255）"
    echo "    if validate_ip '1.2.3.4'; then ..."
    echo "  方式 2: echo 输出，用 \$() 捕获"
    echo "    result=\$(my_function)"

    # 演示返回字符串的函数
    to_uppercase() {
        echo "$1" | tr '[:lower:]' '[:upper:]'
    }
    result=$(to_uppercase "hello world")
    echo "  to_uppercase('hello world') = '$result'"
    echo ""
}

# ============================================================
# 5. 文件操作
# ============================================================
demo_file_operations() {
    echo "============================================================"
    echo "【5. 文件操作】"
    echo "============================================================"

    test_dir="/tmp/bash_basics_demo_$$"
    mkdir -p "$test_dir"

    echo ""
    echo "5.1 写入文件"

    # 普通写入
    echo "第一行内容" > "$test_dir/file1.txt"
    echo "第二行内容" >> "$test_dir/file1.txt"

    echo "  写入 file1.txt 完成"

    # heredoc 写入多行
    cat > "$test_dir/config.ini" << 'EOF'
[server]
host = 0.0.0.0
port = 8080

[security]
enabled = true
ssl = false
EOF
    echo "  用 heredoc 写入 config.ini"

    echo ""
    echo "5.2 读取文件"
    echo "  file1.txt 内容:"
    cat "$test_dir/file1.txt" | sed 's/^/    /'

    echo ""
    echo "  config.ini 内容:"
    cat "$test_dir/config.ini" | sed 's/^/    /'

    echo ""
    echo "5.3 文件查找"
    echo "  测试目录下的文件:"
    find "$test_dir" -type f | sed "s|^|    |"

    echo ""
    echo "5.4 文件信息"
    echo "  config.ini 详情:"
    ls -l "$test_dir/config.ini" | sed 's/^/    /'
    echo "  文件类型: $(file "$test_dir/config.ini" | cut -d: -f2)"

    # 清理
    rm -rf "$test_dir"
    echo ""
}

# ============================================================
# 6. 管道与重定向
# ============================================================
demo_pipes() {
    echo "============================================================"
    echo "【6. 管道与重定向】"
    echo "============================================================"

    test_file="/tmp/bash_basics_pipe_$$.txt"

    # 生成测试日志
    cat > "$test_file" << 'EOF'
192.168.1.100 - - [10/Oct/2024:10:00:01 +0800] "GET /index.html HTTP/1.1" 200 1234
192.168.1.101 - - [10/Oct/2024:10:00:02 +0800] "POST /login HTTP/1.1" 200 567
10.0.0.5 - - [10/Oct/2024:10:00:03 +0800] "GET /admin HTTP/1.1" 403 89
192.168.1.100 - - [10/Oct/2024:10:00:04 +0800] "GET /api/users HTTP/1.1" 200 2345
10.0.0.5 - - [10/Oct/2024:10:00:05 +0800] "POST /admin/login HTTP/1.1" 401 45
192.168.1.100 - - [10/Oct/2024:10:00:06 +0800] "GET /static/style.css HTTP/1.1" 200 5678
10.0.0.5 - - [10/Oct/2024:10:00:07 +0800] "GET /admin/users HTTP/1.1" 403 23
192.168.1.102 - - [10/Oct/2024:10:00:08 +0800] "GET /index.html HTTP/1.1" 200 1234
EOF

    echo ""
    echo "6.1 管道示例：日志统计"
    echo "  测试日志文件: $test_file"
    echo ""

    # 统计行数
    echo "  总行数: $(wc -l < "$test_file")"

    # 状态码分布
    echo ""
    echo "  HTTP 状态码分布:"
    awk '{print $9}' "$test_file" | sort | uniq -c | sort -rn | sed 's/^/    /'

    # IP 统计 Top
    echo ""
    echo "  IP 访问 Top:"
    awk '{print $1}' "$test_file" | sort | uniq -c | sort -rn | sed 's/^/    /'

    # 4xx 请求
    echo ""
    echo "  4xx 错误请求:"
    awk '$9 ~ /^4/ {print $1, $7, $9}' "$test_file" | sed 's/^/    /'

    echo ""
    echo "6.2 重定向示例"
    echo "  标准输出和错误分开保存"

    # 成功命令输出到 stdout
    ls "$test_file" > /tmp/stdout_$$.txt 2> /tmp/stderr_$$.txt
    echo "  stdout: $(cat /tmp/stdout_$$.txt)"
    echo "  stderr: $(cat /tmp/stderr_$$.txt)"

    # 失败命令输出到 stderr
    ls /nonexistent_$$ > /tmp/stdout2_$$.txt 2> /tmp/stderr2_$$.txt
    echo "  失败命令 stderr: $(cat /tmp/stderr2_$$.txt)"

    # 丢弃所有输出
    echo "  丢弃输出（黑洞 /dev/null）:"
    ls /nonexistent_$$ > /dev/null 2>&1 && echo "    成功" || echo "    失败（错误被丢弃了）"

    # 清理
    rm -f "$test_file" /tmp/stdout_$$.txt /tmp/stderr_$$.txt /tmp/stdout2_$$.txt /tmp/stderr2_$$.txt
    echo ""
}

# ============================================================
# 7. 命令替换与算术运算
# ============================================================
demo_arithmetic() {
    echo "============================================================"
    echo "【7. 命令替换与算术运算】"
    echo "============================================================"

    echo ""
    echo "7.1 命令替换"
    echo "  当前时间: $(date)"
    echo "  当前目录文件数: $(ls | wc -l)"
    echo "  内核版本: $(uname -r)"

    echo ""
    echo "7.2 整数算术运算"
    a=10
    b=3
    echo "  a = $a, b = $b"
    echo "  a + b = $((a + b))"
    echo "  a - b = $((a - b))"
    echo "  a * b = $((a * b))"
    echo "  a / b = $((a / b))  (整数除法)"
    echo "  a % b = $((a % b))  (取余)"
    echo "  a ** b = $((a ** b))  (幂运算)"

    echo ""
    echo "7.3 自增自减"
    i=0
    echo "  i 初始 = $i"
    ((i++))
    echo "  i++ 后 = $i"
    ((i += 5))
    echo "  i += 5 后 = $i"

    echo ""
    echo "7.4 小数运算（用 bc 或 awk）"
    echo "  10 / 3 = $(echo "scale=4; 10 / 3" | bc)"
    echo "  3.14 * 2 = $(echo "3.14 * 2" | bc)"

    awk_result=$(awk 'BEGIN {printf "%.2f", 10 / 3}')
    echo "  awk 计算 10/3 = $awk_result"
    echo ""
}

# ============================================================
# 8. 字符串处理
# ============================================================
demo_string() {
    echo "============================================================"
    echo "【8. 字符串处理】"
    echo "============================================================"

    str="Hello, Security World!"
    echo ""
    echo "8.1 基础操作"
    echo "  原字符串: $str"
    echo "  长度: ${#str}"
    echo "  转大写: $(echo "$str" | tr '[:lower:]' '[:upper:]')"
    echo "  转小写: $(echo "$str" | tr '[:upper:]' '[:lower:]')"

    echo ""
    echo "8.2 字符串截取"
    echo "  从第 7 个字符开始: ${str:7}"
    echo "  从第 7 个开始取 8 个: ${str:7:8}"

    echo ""
    echo "8.3 查找替换"
    echo "  替换第一个 o 为 0: ${str/o/0}"
    echo "  替换所有 o 为 0: ${str//o/0}"

    echo ""
    echo "8.4 删除前缀/后缀"
    filename="report_2024_final.txt"
    echo "  文件名: $filename"
    echo "  删除第一个 _ 前的内容: ${filename#*_}"
    echo "  删除最后一个 . 后的内容: ${filename%.*}"
    echo "  文件名（去掉后缀）: ${filename%.txt}"
    echo "  扩展名: ${filename##*.}"

    echo ""
    echo "8.5 提取 IP 地址示例"
    log_line='192.168.1.100 - - [10/Oct/2024:10:00:01 +0800] "GET / HTTP/1.1" 200 1234'
    ip=$(echo "$log_line" | awk '{print $1}')
    echo "  日志行: $log_line"
    echo "  提取的 IP: $ip"
    echo ""
}

# ============================================================
# 9. 数组
# ============================================================
demo_arrays() {
    echo "============================================================"
    echo "【9. 数组】"
    echo "============================================================"

    echo ""
    echo "9.1 数组基本操作"

    # 定义数组
    ports=(21 22 25 53 80 443 3306 8080)
    services=("FTP" "SSH" "SMTP" "DNS" "HTTP" "HTTPS" "MySQL" "HTTP-Proxy")

    echo "  端口数组: ${ports[*]}"
    echo "  元素个数: ${#ports[@]}"
    echo "  第一个元素: ${ports[0]}"
    echo "  最后一个元素: ${ports[-1]}"
    echo "  第 2-4 个: ${ports[@]:1:3}"

    echo ""
    echo "9.2 遍历数组"
    echo "  常用端口对照表:"
    for i in "${!ports[@]}"; do
        printf "    %4d → %s\n" "${ports[$i]}" "${services[$i]}"
    done

    echo ""
    echo "9.3 增删元素"
    fruits=("apple" "banana" "cherry")
    echo "  初始: ${fruits[*]}"

    # 添加元素
    fruits+=("date")
    echo "  添加后: ${fruits[*]}"

    # 删除元素
    unset 'fruits[1]'
    echo "  删除索引 1 后: ${fruits[*]}"

    echo ""
    echo "9.4 关联数组（Bash 4+）"
    # declare -A 声明关联数组（类似字典）
    if declare -A ass_array 2>/dev/null; then
        declare -A os_info
        os_info["name"]="Linux"
        os_info["kernel"]="5.15.0"
        os_info["distro"]="Ubuntu"

        echo "  OS 名称: ${os_info[name]}"
        echo "  内核版本: ${os_info[kernel]}"
        echo "  发行版: ${os_info[distro]}"
        echo "  所有键: ${!os_info[*]}"
    else
        echo "  当前 Bash 版本不支持关联数组（需要 Bash 4+）"
    fi
    echo ""
}

# ============================================================
# 10. 命令行参数
# ============================================================
demo_args() {
    echo "============================================================"
    echo "【10. 命令行参数】"
    echo "============================================================"

    echo ""
    echo "10.1 基本参数"
    echo "  脚本名: $0"
    echo "  参数总数: $#"
    echo "  所有参数 (\$@): $@"
    echo "  所有参数 (\$*): $*"

    echo ""
    echo "10.2 位置参数"
    echo "  \$1 = ${1:-（未提供）}"
    echo "  \$2 = ${2:-（未提供）}"
    echo "  \$3 = ${3:-（未提供）}"

    echo ""
    echo "10.3 shift 移动参数"
    # 用 shift 遍历参数
    args=("$@")
    count=1
    for arg in "${args[@]}"; do
        echo "  参数 $count: $arg"
        count=$((count + 1))
    done

    echo ""
    echo "10.4 getopts 解析选项"
    echo "  （在主函数中演示，用 -h 查看帮助）"
    echo ""
}

# ============================================================
# 主函数
# ============================================================

usage() {
    cat << 'EOF'
Bash 基础语法示例

用法:
  bash basics.sh [选项] [参数...]

选项:
  -h, --help      显示帮助
  -d, --demo N    只运行第 N 个示例 (1-10)
  -a, --all       运行所有示例（默认）

示例:
  bash basics.sh              # 运行所有示例
  bash basics.sh -d 3         # 只运行第 3 个（循环）
  bash basics.sh arg1 arg2    # 传参数看效果
EOF
}

main() {
    local demo_num=""

    # 简单的参数解析
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            -d|--demo)
                demo_num="$2"
                shift 2
                ;;
            -a|--all)
                demo_num=""
                shift
                ;;
            *)
                # 其他的作为参数传递，让 demo_args 显示
                shift
                ;;
        esac
    done

    if [ -n "$demo_num" ]; then
        # 只运行指定的示例
        case "$demo_num" in
            1) demo_variables ;;
            2) demo_conditionals ;;
            3) demo_loops ;;
            4) demo_functions ;;
            5) demo_file_operations ;;
            6) demo_pipes ;;
            7) demo_arithmetic ;;
            8) demo_string ;;
            9) demo_arrays ;;
            10) demo_args ;;
            *)
                echo "错误: 无效的示例编号 $demo_num (1-10)"
                exit 1
                ;;
        esac
    else
        # 运行所有示例
        demo_variables
        demo_conditionals
        demo_loops
        demo_functions
        demo_file_operations
        demo_pipes
        demo_arithmetic
        demo_string
        demo_arrays
        demo_args "$@"

        echo "============================================================"
        echo "  所有示例运行完成！"
        echo "  提示: 用 -h 查看更多用法"
        echo "============================================================"
    fi
}

main "$@"
