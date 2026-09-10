#!/bin/bash
# 16_debug.sh
# Shell 调试与最佳实践示例

echo "=========================================="
echo "1. set -x 调试模式"
echo "=========================================="

echo "开启 set -x 后，每行命令都会被打印出来："
set -x
name="张三"
age=25
greeting="Hello, $name!"
result=$((age * 2))
set +x
echo "调试已关闭"

echo ""
echo "=========================================="
echo "2. set -e 遇到错误立即退出"
echo "=========================================="

echo "set -e 会在命令失败时立即终止脚本"
echo "（为了演示，我们临时关闭，用函数包装）"

test_set_e() {
    set -e
    echo "  步骤 1：执行成功"
    echo "  步骤 2：执行成功"
    # 下面这行如果失败会立即退出
    # ls /nonexistent_dir
    echo "  步骤 3：执行成功"
    set +e
}

test_set_e
echo "函数执行完毕"

echo ""
echo "=========================================="
echo "3. set -u 未定义变量报错"
echo "=========================================="

test_set_u() {
    set -u
    defined_var="我已定义"
    echo "  defined_var = $defined_var"
    # 下面这行会报错：undefined_var: unbound variable
    # echo "  undefined_var = $undefined_var"
    set +u
}

test_set_u
echo "（已避免未定义变量错误）"

echo ""
echo "=========================================="
echo "4. 检查脚本语法"
echo "=========================================="

echo "使用 bash -n 检查语法（不执行）："
bash -n "$0" && echo "  语法检查通过 ✓" || echo "  语法有错误 ✗"

echo ""
echo "=========================================="
echo "5. 自定义日志函数"
echo "=========================================="

log_info()  { echo -e "\033[32m[INFO]\033[0m  $*"; }
log_warn()  { echo -e "\033[33m[WARN]\033[0m  $*" >&2; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $*" >&2; }
log_debug() {
    if [ "${DEBUG:-0}" = "1" ]; then
        echo -e "\033[36m[DEBUG]\033[0m $*"
    fi
}

log_info "这是一条信息日志"
log_warn "这是一条警告日志"
log_error "这是一条错误日志"
log_debug "这是调试日志（默认不显示）"

echo ""
echo "开启 DEBUG=1 后再看调试日志："
DEBUG=1
log_debug "现在调试日志显示出来了"

echo ""
echo "=========================================="
echo "6. 错误处理示例"
echo "=========================================="

# 方式一：if 判断
if ls /nonexistent_dir 2>/dev/null; then
    echo "目录存在"
else
    echo "目录不存在（预期结果）"
fi

# 方式二：|| 运算符
ls /nonexistent_dir 2>/dev/null || echo "ls 命令失败（预期）"

# 方式三：自定义错误函数
error_exit() {
    log_error "$1"
    exit 1
}

# error_exit "严重错误，脚本退出"  # 这行会退出脚本，注释掉了

echo ""
echo "=========================================="
echo "7. 常用最佳实践总结"
echo "=========================================="

cat << 'TIPS'
Shell 脚本最佳实践：
1. 脚本开头：#!/bin/bash + set -euo pipefail
2. 变量名要有意义，不用 a/b/c
3. 字符串变量用双引号括起来："$var"
4. 函数内使用 local 变量
5. 使用 $() 代替反引号
6. 用 [[ ]] 代替 [ ]
7. 关键操作前检查参数和环境
8. 善用 trap 做清理工作
9. 添加足够的注释和使用说明
10. 使用 bash -n 检查语法，bash -x 调试
TIPS
