#!/bin/bash
# ============================================================
# 06_string.sh - 字符串处理
# ============================================================

echo "========== 1. 字符串基本操作 =========="

str="Hello, Bash World!"
echo "原始字符串: $str"
echo "字符串长度: ${#str}"

echo ""
echo "========== 2. 字符串拼接 =========="

first="Hello"
second="World"
greeting="${first}, ${second}!"
echo "拼接结果: $greeting

# 无引号拼接
combined=$first$second
echo "无引号拼接: $combined"

echo ""
echo "========== 3. 字符串切片 =========="

str="abcdefghij"
echo "原始字符串: $str"
echo "从索引3开始: ${str:3}"
echo "从索引2开始取5个: ${str:2:5}"
echo "从末尾取4个: ${str: -4}"
echo "从索引-6开始取3个: ${str: -6:3}"

echo ""
echo "========== 4. 字符串查找 =========="

str="Hello World, Hello Bash"
echo "原始字符串: $str"

# 查找子串第一次出现的位置（从1开始计数）
pos=$(expr index "$str "World")
echo "World 第一次出现的位置: $pos"

# 使用 awk 查找
echo "Bash 的位置（awk）: $(echo "$str" | awk '{print index($0, "Bash")}')"

echo ""
echo "========== 5. 字符串替换 =========="

str="I like apples. apples are red."
echo "原始字符串: $str"

# 替换第一个匹配
echo "替换第一个 apples: ${str/apples/oranges}"

# 替换所有匹配
echo "替换所有 apples: ${str//apples/oranges}"

# 替换前缀
path="/usr/local/bin/bash"
echo "路径: $path"
echo "去掉最短前缀 /*/: ${path#*/}"
echo "去掉最长前缀 /*/: ${path##*/}"

# 替换后缀
echo "去掉最短后缀 /*: ${path%/*}"
echo "去掉最长后缀 /*: ${path%%/*}"

echo ""
echo "========== 6. 字符串大小写转换 =========="

str="Hello World"
echo "原始: $str"
echo "全小写: ${str,,}"
echo "全大写: ${str^^}"
echo "首字母大写: ${str^}"
echo "首字母小写: ${str,}"

# 使用 tr 命令
echo "全小写 (tr): $(echo "$str" | tr '[:upper:]' '[:lower:]')"
echo "全大写 (tr): $(echo "$str" | tr '[:lower:]' '[:upper:]')"

echo ""
echo "========== 7. 字符串删除 =========="

str="   Hello World   "
echo "原始: '${str}'"

# 删除前导空白
echo "删除前导空白: '$(echo "$str" | sed 's/^[[:space:]]*//')'"

# 删除尾随空白
echo "删除尾随空白: '$(echo "$str" | sed 's/[[:space:]]*$//')'"

# 删除两端空白
trimmed=$(echo "$str" | xargs)
echo "删除两端空白: '${trimmed}'"

echo ""
echo "========== 8. 字符串比较 =========="

str1="hello"
str2="Hello"
str3="hello"

echo "str1=$str1, str2=$str2, str3=$str3"

[ "$str1" = "$str3" ] && echo "str1 等于 str3"
[ "$str1" != "$str2" ] && echo "str1 不等于 str2"

# 字典序比较
if [[ "$str1" < "$str2" ]]; then
    echo "str1 字典序小于 str2"
fi

echo ""
echo "========== 9. 字符串包含判断 =========="

str="Hello World, Bash is great"
echo "字符串: $str"

if [[ "$str" == *"Bash"* ]]; then
    echo "包含 'Bash'"
fi

if [[ "$str" == Hello* ]]; then
    echo "以 'Hello' 开头"
fi

if [[ "$str" == *great ]]; then
    echo "以 'great' 结尾"
fi

echo ""
echo "========== 10. 字符串分割 =========="

str="apple,banana,orange,grape"
echo "原始字符串: $str"

# 方法一：使用 IFS 分割
IFS=',' read -ra fruits <<< "$str"
echo "分割结果:"
for fruit in "${fruits[@]}"; do
    echo "  - $fruit"
done

# 方法二：使用 tr 转换
echo "使用 tr 分割:"
echo "$str" | tr ',' '\n' | while read -r item; do
    echo "  - $item"
done

echo ""
echo "========== 11. 字符串重复 =========="

# 重复字符
repeat_char() {
    local char="$1"
    local count="$2"
    printf "%${count}s" | tr ' ' "$char"
}

echo "重复 '=' 20次: $(repeat_char '=' 20)"
echo "重复 '*' 10次: $(repeat_char '*' 10)"

echo ""
echo "========== 12. 字符串反转 =========="

str="Hello World"
echo "原始: $str"
echo "反转: $(echo "$str" | rev)"

echo ""
echo "========== 13. URL 编码与解码 =========="

url_encode() {
    local string="$1"
    local strlen=${#string}
    local encoded=""
    local pos c o

    for (( pos=0 ; pos<strlen ; pos++ )); do
        c=${string:$pos:1}
        case "$c" in
            [-_.~a-zA-Z0-9]) o="${c}" ;;
            *)  printf -v o '%%%02X' "'$c"
        esac
        encoded+="${o}"
    done
    echo "${encoded}"
}

url_decode() {
    printf '%b' "${1//%/\\x}"
}

original="Hello World! 你好世界"
encoded=$(url_encode "$original")
decoded=$(url_decode "$encoded")

echo "原始: $original"
echo "编码: $encoded"
echo "解码: $decoded"

echo ""
echo "========== 14. Base64 编解码 =========="

original="Hello, Bash!"
encoded=$(echo -n "$original" | base64)
decoded=$(echo -n "$encoded" | base64 -d)

echo "原始: $original"
echo "Base64编码: $encoded"
echo "Base64解码: $decoded"
