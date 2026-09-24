#!/bin/bash
# ============================================================
# 02_variables.sh - 变量与环境变量
# ============================================================

echo "========== 1. 基本变量定义 =========="

# 变量定义（注意：等号两边不能有空格）
name="张三"
age=25
is_student=true

echo "姓名: $name"
echo "年龄: $age"
echo "是否学生: $is_student"

echo ""
echo "========== 2. 变量命名规则 =========="

# 变量名只能包含字母、数字、下划线，且不能以数字开头
my_var="合法变量"
_var123="以下划线开头"
MyVar="驼峰命名"

echo "my_var: $my_var"
echo "_var123: $_var123"
echo "MyVar: $MyVar"

echo ""
echo "========== 3. 只读变量 =========="

readonly PI=3.14159
echo "PI = $PI"
# PI=3.14  # 取消注释会报错，只读变量不能修改

echo ""
echo "========== 4. 删除变量 =========="

temp_var="临时变量"
echo "删除前: temp_var = $temp_var"
unset temp_var
echo "删除后: temp_var = $temp_var"

echo ""
echo "========== 5. 环境变量 =========="

echo "HOME: $HOME"
echo "PATH: $PATH"
echo "USER: $USER"
echo "SHELL: $SHELL"
echo "PWD: $PWD"
echo "HOSTNAME: $HOSTNAME"
echo "LANG: $LANG"

# 导出变量为环境变量
export MY_ENV_VAR="这是一个环境变量"
echo "MY_ENV_VAR: $MY_ENV_VAR"

echo ""
echo "========== 6. 特殊变量 =========="

echo "脚本名称: $0"
echo "参数个数: $#"
echo "所有参数(\$*): $*"
echo "所有参数(\$@): $@"
echo "当前进程ID: $$"
echo "上一个命令退出状态: $?"

echo ""
echo "========== 7. 命令替换 =========="

# 使用 $() 或 `` 进行命令替换
current_date=$(date +"%Y-%m-%d")
current_time=`date +"%H:%M:%S"`
file_count=$(ls -l | wc -l)

echo "当前日期: $current_date"
echo "当前时间: $current_time"
echo "当前目录文件数: $file_count"

echo ""
echo "========== 8. 变量作用域 =========="

# 默认变量是全局的
global_var="我是全局变量"

function test_scope {
    # 使用 local 声明局部变量
    local local_var="我是局部变量"
    echo "函数内 - local_var: $local_var"
    echo "函数内 - global_var: $global_var"
}

test_scope
echo "函数外 - global_var: $global_var"
echo "函数外 - local_var: $local_var  # 局部变量在函数外不可见"
