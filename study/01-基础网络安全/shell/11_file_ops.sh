#!/bin/bash
# 11_file_ops.sh
# 文件与目录操作示例

echo "=========================================="
echo "1. 文件判断"
echo "=========================================="

file="/etc/passwd"
dir="/etc"

if [ -e "$file" ]; then
    echo "$file 存在"
fi

if [ -f "$file" ]; then
    echo "$file 是普通文件"
fi

if [ -d "$dir" ]; then
    echo "$dir 是目录"
fi

if [ -r "$file" ]; then
    echo "$file 可读"
fi

if [ -w "$file" ]; then
    echo "$file 可写"
else
    echo "$file 不可写（正常，普通用户无写权限）"
fi

if [ -x "/bin/bash" ]; then
    echo "/bin/bash 可执行"
fi

echo ""
echo "=========================================="
echo "2. 文件读写"
echo "=========================================="

temp_file="/tmp/shell_demo_$$.txt"
echo "临时文件：$temp_file"

# 写入（覆盖）
echo "第一行内容" > "$temp_file"
echo "第二行内容" >> "$temp_file"
echo "第三行内容" >> "$temp_file"

echo ""
echo "文件内容："
cat "$temp_file"

echo ""
echo "逐行读取："
line_num=0
while read -r line; do
    line_num=$((line_num + 1))
    echo "  行 $line_num：$line"
done < "$temp_file"

echo ""
echo "=========================================="
echo "3. Here Document 多行写入"
echo "=========================================="

cat > "$temp_file" << 'EOF'
姓名：张三
年龄：25
城市：北京
职业：工程师
EOF

echo "Here Document 写入后："
cat "$temp_file"

echo ""
echo "=========================================="
echo "4. 目录遍历"
echo "=========================================="

echo "当前目录下的 .sh 文件："
for f in *.sh; do
    if [ -f "$f" ]; then
        size=$(wc -c < "$f")
        echo "  $f ($size 字节)"
    fi
done

echo ""
echo "=========================================="
echo "5. 文件描述符与重定向"
echo "=========================================="

log_file="/tmp/shell_demo_log_$$.log"
echo "日志文件：$log_file"

# 重定向 stdout 到文件
echo "这是标准输出" > "$log_file"
echo "这是追加的内容" >> "$log_file"

# 重定向 stderr
ls /nonexistent_dir 2>> "$log_file"

echo "日志内容："
cat "$log_file"

echo ""
echo "丢弃输出示例（不显示输出）："
echo "  正常输出会被丢弃..."
ls /etc > /dev/null 2>&1
echo "  完成（上面的 ls 输出被丢弃了）"

# 清理
rm -f "$temp_file" "$log_file"

echo ""
echo "=========================================="
echo "6. 文件查找（find）"
echo "=========================================="

echo "当前目录下的 .sh 文件（find 查找）："
find . -maxdepth 1 -name "*.sh" -type f | head -5

echo ""
echo "查找大于 1KB 的文件："
find . -maxdepth 1 -type f -size +1k 2>/dev/null | head -5

echo ""
echo "=========================================="
echo "7. 文件权限"
echo "=========================================="

test_file="/tmp/test_perm_$$.txt"
touch "$test_file"
echo "初始权限：$(ls -l "$test_file" | awk '{print $1}')"

chmod 755 "$test_file"
echo "chmod 755 后：$(ls -l "$test_file" | awk '{print $1}')"

chmod +x "$test_file"
echo "chmod +x 后：$(ls -l "$test_file" | awk '{print $1}')"

rm -f "$test_file"
