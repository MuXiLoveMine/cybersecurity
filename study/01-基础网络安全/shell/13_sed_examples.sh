#!/bin/bash
# 13_sed_examples.sh
# sed 文本处理示例

# 创建示例文件
demo_file="/tmp/sed_demo_$$.txt"
cat > "$demo_file" << 'EOF'
Hello World
This is a test file
hello again
APPLE banana CHERRY
line with numbers 12345
# comment line
another comment # at end
foo bar baz
EOF

echo "原始文件内容："
echo "----------------------------------------"
cat -n "$demo_file"
echo "----------------------------------------"
echo ""

echo "=========================================="
echo "1. 基本替换"
echo "=========================================="

echo "替换第一个 hello 为 hi（s/pattern/replace/）："
sed 's/hello/hi/' "$demo_file"

echo ""
echo "替换所有 hello 为 hi（s/.../.../g）："
sed 's/hello/hi/g' "$demo_file"

echo ""
echo "忽略大小写替换（s/.../.../gi）："
sed 's/hello/hi/gi' "$demo_file"

echo ""
echo "替换每行第 2 个匹配（s/.../.../2）："
echo "  （在多个 a 的行上测试）"
echo "banana apple papaya" | sed 's/a/A/2'

echo ""
echo "=========================================="
echo "2. 指定行替换"
echo "=========================================="

echo "只替换第 3 行："
sed '3s/hello/HELLO/' "$demo_file"

echo ""
echo "替换第 2 到 5 行："
sed '2,5s/[aeiou]/_/g' "$demo_file"

echo ""
echo "替换包含 'test' 的行："
sed '/test/s/file/DOCUMENT/' "$demo_file"

echo ""
echo "=========================================="
echo "3. 删除行"
echo "=========================================="

echo "删除第 3 行："
sed '3d' "$demo_file"

echo ""
echo "删除第 2 到 4 行："
sed '2,4d' "$demo_file"

echo ""
echo "删除包含 comment 的行："
sed '/comment/d' "$demo_file"

echo ""
echo "删除空行（如果有）："
sed '/^$/d' "$demo_file"

echo ""
echo "删除以 # 开头的注释行："
sed '/^#/d' "$demo_file"

echo ""
echo "=========================================="
echo "4. 插入和追加"
echo "=========================================="

echo "在第 2 行前插入（i）："
sed '2i\--- 插入的行 ---' "$demo_file"

echo ""
echo "在第 2 行后追加（a）："
sed '2a\--- 追加的行 ---' "$demo_file"

echo ""
echo "在包含 'test' 的行后追加："
sed '/test/a\  ← 这是 test 行' "$demo_file"

echo ""
echo "=========================================="
echo "5. 行替换"
echo "=========================================="

echo "替换第 4 行整行内容（c）："
sed '4c\=== 替换后的第四行 ===' "$demo_file"

echo ""
echo "替换包含 'numbers' 的行："
sed '/numbers/c\[数字行已被替换]' "$demo_file"

echo ""
echo "=========================================="
echo "6. 字符转换（y）"
echo "=========================================="

echo "小写转大写（y/abc/ABC/）："
sed 'y/abcdefghijklmnopqrstuvwxyz/ABCDEFGHIJKLMNOPQRSTUVWXYZ/' "$demo_file"

echo ""
echo "数字替换："
echo "12345" | sed 'y/12345/一二三四五/'

echo ""
echo "=========================================="
echo "7. 打印指定行（-n + p）"
echo "=========================================="

echo "只打印第 3 行："
sed -n '3p' "$demo_file"

echo ""
echo "打印第 2 到 5 行："
sed -n '2,5p' "$demo_file"

echo ""
echo "打印包含 hello 的行（忽略大小写）："
sed -n '/hello/Ip' "$demo_file"

echo ""
echo "=========================================="
echo "8. 反向引用与分组"
echo "=========================================="

echo "交换单词位置（hello world → world hello）："
echo "hello world" | sed 's/\(hello\) \(world\)/\2 \1/'

echo ""
echo "提取括号内容："
echo "这是(重要内容)的示例" | sed 's/.*(\(.*\)).*/\1/'

echo ""
echo "格式化电话号码："
echo "13812345678" | sed 's/\(....\)\(....\)\(...\)/\1-\2-\3/'

echo ""
echo "=========================================="
echo "9. 批量修改文件扩展名"
echo "=========================================="

echo "将 .txt 替换为 .md（演示，不实际修改）："
for f in file1.txt file2.txt file3.txt; do
    newname=$(echo "$f" | sed 's/\.txt$/.md/')
    echo "  $f → $newname"
done

# 清理
rm -f "$demo_file"
