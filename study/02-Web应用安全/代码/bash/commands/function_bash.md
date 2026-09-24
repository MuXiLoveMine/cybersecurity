# function_bash

> **分类**：函数
> **说明**：Shell 函数定义与使用

---

## 语法

```bash
function_name() { ... }  或  function function_name { ... }
```

## 返回值

return 只能返回 0-255 的数字，0表示成功

## 参数

函数参数用 $1, $2... 访问，$@ 所有参数，$# 参数个数

## 示例代码

```bash
#!/bin/bash

# 基本函数定义
greet() {
    echo "Hello, $1!"
}

greet "World"  # 调用

# return 返回值（0-255，0表示成功）
add() {
    local sum=$(($1 + $2))
    echo $sum
    return 0  # 0=成功
}

result=$(add 3 5)  # 捕获输出
echo "结果: $result"

# 局部变量（不加 local 就是全局）
count() {
    local i=0      # 局部变量
    while [ $i -lt $1 ]; do
        echo $i
        ((i++))
    done
}

# 递归函数
factorial() {
    if [ $1 -le 1 ]; then
        echo 1
    else
        local prev=$(factorial $(($1 - 1)))
        echo $(($1 * prev))
    fi
}

factorial 5  # 120

# 函数返回多个值（通过输出）
get_info() {
    echo "Alice"
    echo "25"
    echo "Beijing"
}

# 读取多个返回值
{ read name; read age; read city; } < <(get_info)
echo "$name, $age, $city"

# 函数作为命令
mkcd() {
    mkdir -p "$1" && cd "$1"
}

# 数组参数传递
process_array() {
    local arr=("$@")
    echo "收到 ${#arr[@]} 个元素"
    for item in "${arr[@]}"; do
        echo "  $item"
    done
}

my_array=(a b c d)
process_array "${my_array[@]}"
```
