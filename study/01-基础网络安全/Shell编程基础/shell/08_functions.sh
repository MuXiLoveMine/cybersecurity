#!/bin/bash
# 08_functions.sh
# 函数定义与使用示例

echo "=========================================="
echo "1. 基本函数"
echo "=========================================="

# 定义函数
greet() {
    echo "Hello, $1!"
}

# 调用函数
greet "World"
greet "张三"

echo ""
echo "=========================================="
echo "2. 函数返回值"
echo "=========================================="

# 方式一：return 返回退出码（0~255）
add() {
    local sum=$(( $1 + $2 ))
    return $sum
}

add 3 5
echo "3 + 5 = $?"

# 方式二：echo 返回字符串/大数值（推荐）
multiply() {
    echo $(( $1 * $2 ))
}

result=$(multiply 12 34)
echo "12 * 34 = $result"

echo ""
echo "=========================================="
echo "3. 局部变量"
echo "=========================================="

global_var="我是全局的"

test_local() {
    local local_var="我是局部的"
    echo "函数内 - global_var: $global_var"
    echo "函数内 - local_var: $local_var"
}

test_local
echo "函数外 - global_var: $global_var"
echo "函数外 - local_var: ${local_var:-未定义}"

echo ""
echo "=========================================="
echo "4. 递归函数 - 阶乘"
echo "=========================================="

factorial() {
    local n=$1
    if [ $n -le 1 ]; then
        echo 1
    else
        echo $(( n * $(factorial $((n - 1))) ))
    fi
}

for i in 0 1 2 3 4 5; do
    echo "$i! = $(factorial $i)"
done

echo ""
echo "=========================================="
echo "5. 递归函数 - 斐波那契数列"
echo "=========================================="

fib() {
    local n=$1
    if [ $n -le 1 ]; then
        echo $n
    else
        echo $(( $(fib $((n - 1))) + $(fib $((n - 2))) ))
    fi
}

echo "斐波那契数列前 10 项："
for i in {0..9}; do
    echo -n "$(fib $i) "
done
echo ""

echo ""
echo "=========================================="
echo "6. 函数库示例"
echo "=========================================="

# 模拟一个数学函数库
math_lib_add() { echo $(( $1 + $2 )); }
math_lib_sub() { echo $(( $1 - $2 )); }
math_lib_mul() { echo $(( $1 * $2 )); }
math_lib_div() { echo $(( $1 / $2 )); }

a=20
b=4
echo "a = $a, b = $b"
echo "加法：$(math_lib_add $a $b)"
echo "减法：$(math_lib_sub $a $b)"
echo "乘法：$(math_lib_mul $a $b)"
echo "除法：$(math_lib_div $a $b)"
