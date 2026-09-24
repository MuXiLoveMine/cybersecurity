#!/bin/bash
# ============================================================
# 07_file_io.sh - 文件读写与重定向
# ============================================================

TEST_DIR="/tmp/bash_file_io_test"
mkdir -p "$TEST_DIR"

echo "========== 1. 文件写入 =========="

# 使用 > 写入文件（覆盖）
echo "第一行内容" > "$TEST_DIR/file1.txt"
echo "使用 > 写入: $(cat "$TEST_DIR/file1.txt")"

# 使用 >> 追加写入
echo "追加的第一行" >> "$TEST_DIR/file1.txt"
echo "追加的第二行" >> "$TEST_DIR/file1.txt"
echo "使用 >> 追加后:"
cat "$TEST_DIR/file1.txt"

echo ""
echo "========== 2. 使用 cat 写入多行 =========="

cat > "$TEST_DIR/file2.txt" << 'EOF'
这是第一行
这是第二行
这是第三行
  这是缩进的行
特殊字符: $var `cmd` "quote"
EOF

echo "cat here document 写入:"
cat "$TEST_DIR/file2.txt"

echo ""
echo "========== 3. 文件读取 =========="

echo "方法一：使用 cat 全部读取"
cat "$TEST_DIR/file1.txt"

echo ""
echo "方法二：逐行读取（推荐）"
while IFS= read -r line; do
    echo "读取行: $line"
done < "$TEST_DIR/file1.txt"

echo ""
echo "方法三：读取到变量"
content=$(< "$TEST_DIR/file1.txt")
echo "文件内容变量长度: ${#content} 字符"

echo ""
echo "========== 4. 文件描述符与重定向 =========="

# 文件描述符：0=stdin, 1=stdout, 2=stderr

echo "标准输出重定向:"
echo "这是标准输出" > "$TEST_DIR/stdout.txt"
echo "stdout.txt 内容: $(cat "$TEST_DIR/stdout.txt")"

echo ""
echo "标准错误重定向:"
ls /nonexistent_file_xyz 2> "$TEST_DIR/stderr.txt"
echo "stderr.txt 内容: $(cat "$TEST_DIR/stderr.txt")"

echo ""
echo "同时重定向 stdout 和 stderr:"
{
    echo "标准输出内容"
    ls /nonexistent_file_xyz
} > "$TEST_DIR/both.log" 2>&1
echo "both.log 内容:"
cat "$TEST_DIR/both.log"

echo ""
echo "========== 5. 输入重定向 =========="

echo "从文件读取输入:"
while read -r name age city; do
    echo "姓名: $name, 年龄: $age, 城市: $city"
done <<< "张三 25 北京
李四 30 上海
王五 28 广州"

echo ""
echo "========== 6. exec 与文件描述符 =========="

# 打开文件描述符进行写入
exec 3> "$TEST_DIR/fd3.txt"
echo "这行写入fd3" >&3
echo "这行也写入fd3" >&3
exec 3>&-  # 关闭文件描述符
echo "fd3.txt 内容:"
cat "$TEST_DIR/fd3.txt"

# 打开文件描述符进行读取
exec 4< "$TEST_DIR/file1.txt"
echo ""
echo "从fd4读取一行:"
read -r line <&4
echo "读取: $line"
exec 4<&-  # 关闭

echo ""
echo "========== 7. tee 命令 =========="

echo "使用 tee 同时输出到屏幕和文件:"
echo "Hello Tee!" | tee "$TEST_DIR/tee_output.txt"

echo ""
echo "tee追加模式:"
echo "追加的内容" | tee -a "$TEST_DIR/tee_output.txt"
echo "tee_output.txt 内容:"
cat "$TEST_DIR/tee_output.txt"

echo ""
echo "========== 8. 文件属性检查 =========="

test_file="$TEST_DIR/file1.txt"
echo "检查文件: $test_file"

[ -e "$test_file" ] && echo "  文件存在"
[ -f "$test_file" ] && echo "  是普通文件"
[ -d "$test_file" ] && echo "  是目录" || echo "  不是目录"
[ -r "$test_file" ] && echo "  可读"
[ -w "$test_file" ] && echo "  可写"
[ -x "$test_file" ] && echo "  可执行" || echo "  不可执行"
[ -s "$test_file" ] && echo "  文件大小不为零"

echo ""
echo "文件大小: $(wc -c < "$test_file") 字节"
echo "文件行数: $(wc -l < "$test_file") 行"

echo ""
echo "========== 9. 文件比较与差异 =========="

echo "apple" > "$TEST_DIR/a.txt"
echo "banana" >> "$TEST_DIR/a.txt"
echo "cherry" >> "$TEST_DIR/a.txt"

echo "apple" > "$TEST_DIR/b.txt"
echo "orange" >> "$TEST_DIR/b.txt"
echo "cherry" >> "$TEST_DIR/b.txt"

echo "diff 比较:"
diff "$TEST_DIR/a.txt" "$TEST_DIR/b.txt" || true

echo ""
echo "comm 比较（需要先排序）:"
comm <(sort "$TEST_DIR/a.txt") <(sort "$TEST_DIR/b.txt")

echo ""
echo "========== 10. 临时文件与目录 =========="

# 创建临时文件
temp_file=$(mktemp)
echo "临时文件: $temp_file"
echo "临时内容" > "$temp_file"
echo "临时文件内容: $(cat "$temp_file")"
rm -f "$temp_file"

# 创建临时目录
temp_dir=$(mktemp -d)
echo "临时目录: $temp_dir"
rm -rf "$temp_dir"

echo ""
echo "========== 11. 文件查找 =========="

echo "查找 $TEST_DIR 下的 .txt 文件:"
find "$TEST_DIR" -name "*.txt" -type f | sort

echo ""
echo "查找大于 10 字节的文件:"
find "$TEST_DIR" -type f -size +10c | sort

echo ""
echo "========== 12. 文件权限操作 =========="

perm_file="$TEST_DIR/perm_test.sh"
echo '#!/bin/bash' > "$perm_file"
echo 'echo "test"' >> "$perm_file"

echo "修改前权限: $(ls -l "$perm_file" | awk '{print $1}')"
chmod 755 "$perm_file"
echo "修改后权限: $(ls -l "$perm_file" | awk '{print $1}')"

# 清理
rm -rf "$TEST_DIR"

echo ""
echo "文件 I/O 测试完成！"
