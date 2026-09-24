#!/bin/bash
# ============================================================
# 04_functions.sh - 函数定义与使用
# ============================================================

echo "========== 1. 基本函数定义 =========="

# 简单函数
function hello {
    echo "Hello, 这是一个函数！"
}

# 也可以不用 function 关键字
greet() {
    echo "你好，世界！"
}

hello
greet

echo ""
echo "========== 2. 带参数的函数 =========="

print_info() {
    echo "参数个数: $#"
    echo "第一个参数: $1"
    echo "第二个参数: $2"
    echo "所有参数: $@"
}

print_info "张三" 25 "北京"

echo ""
echo "========== 3. 函数返回值 =========="

# 使用 return 返回状态码（0-255）
add() {
    local sum=$(( $1 + $2 ))
    return $sum
}

add 10 20
echo "10 + 20 = $?"

# 使用 echo 返回值（更灵活）
multiply() {
    local result=$(( $1 * $2 ))
    echo "$result"
}

product=$(multiply 6 7)
echo "6 * 7 = $product"

echo ""
echo "========== 4. 局部变量与全局变量 =========="

global_var="我是全局的"

test_local() {
    local local_var="我是局部的"
    global_var="已被修改"
    echo "函数内 - local_var: $local_var"
    echo "函数内 - global_var: $global_var"
}

test_local
echo "函数外 - global_var: $global_var"
echo "函数外 - local_var: ${local_var:-不存在}"

echo ""
echo "========== 5. 递归函数 =========="

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

echo "5! = $(factorial 5)"
echo "10! = $(factorial 10)"

echo ""
echo "========== 6. 函数作为参数（回调） =========="

apply_operation() {
    local op=$1
    shift
    $op "$@"
}

operation_add() {
    echo "加法结果: $(($1 + $2))"
}

operation_multiply() {
    echo "乘法结果: $(($1 * $2))"
}

apply_operation operation_add 5 3
apply_operation operation_multiply 5 3

echo ""
echo "========== 7. 匿名函数 / eval 技巧 =========="

# Bash 没有真正的匿名函数，但可以用 eval 或变量存储函数名
func_name="hello"
$func_name  # 调用变量中存储的函数名

echo ""
echo "========== 8. 函数库与 source =========="

# 创建一个临时函数库文件
cat > /tmp/math_lib.sh << 'EOF'
#!/bin/bash
# 数学函数库

add_numbers() {
    echo $(($1 + $2))
}

sub_numbers() {
    echo $(($1 - $2))
}

mul_numbers() {
    echo $(($1 * $2))
}

div_numbers() {
    if [ $2 -ne 0 ]; then
        echo $(($1 / $2))
    else
        echo "错误：除数不能为零" >&2
        return 1
    fi
}
EOF

# 引入函数库
source /tmp/math_lib.sh

echo "3 + 4 = $(add_numbers 3 4)"
echo "10 - 6 = $(sub_numbers 10 6)"
echo "5 * 8 = $(mul_numbers 5 8)"
echo "20 / 4 = $(div_numbers 20 4)"

rm -f /tmp/math_lib.sh

echo ""
echo "========== 9. 函数中的错误处理 =========="

safe_divide() {
    if [ $# -ne 2 ]; then
        echo "错误：需要两个参数" >&2
        return 1
    fi

    if ! [[ "$1" =~ ^-?[0-9]+$ ]] || ! [[ "$2" =~ ^-?[0-9]+$ ]]; then
        echo "错误：参数必须是整数" >&2
        return 2
    fi

    if [ $2 -eq 0 ]; then
        echo "错误：除数不能为零" >&2
        return 3
    fi

    echo $(($1 / $2))
    return 0
}

safe_divide 10 2
echo "退出码: $?"

safe_divide 10 0
echo "退出码: $?"

safe_divide 10 abc
echo "退出码: $?"

echo ""
echo "========== 10. 可变参数函数 =========="

sum_all() {
    local total=0
    for num in "$@"; do
        total=$((total + num))
    done
    echo $total
}

echo "1+2+3+4+5 = $(sum_all 1 2 3 4 5)"
echo "10+20+30 = $(sum_all 10 20 30)"
