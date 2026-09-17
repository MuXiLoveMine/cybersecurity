#!/bin/bash
# 14_awk_examples.sh
# awk 文本处理示例

# 创建示例文件
passwd_file="/tmp/awk_passwd_$$.txt"
cat > "$passwd_file" << 'EOF'
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
admin:x:1000:1000:Admin User:/home/admin:/bin/bash
testuser:x:1001:1001:Test User:/home/testuser:/bin/zsh
mysql:x:27:27:MySQL Server:/var/lib/mysql:/bin/false
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
EOF

score_file="/tmp/awk_scores_$$.txt"
cat > "$score_file" << 'EOF'
张三 语文 85
张三 数学 92
张三 英语 78
李四 语文 90
李四 数学 88
李四 英语 95
王五 语文 76
王五 数学 82
王五 英语 70
EOF

echo "=========================================="
echo "1. awk 基础"
echo "=========================================="

echo "打印所有行（默认动作是打印）："
awk '{print}' "$score_file" | head -5
echo "  ..."

echo ""
echo "打印第 1 列和第 3 列："
awk '{print $1, $3}' "$score_file" | head -5
echo "  ..."

echo ""
echo "打印整行（\$0）和行号（NR）："
awk '{print NR, $0}' "$score_file" | head -5
echo "  ..."

echo ""
echo "=========================================="
echo "2. 字段分隔符（-F）"
echo "=========================================="

echo "用冒号分隔，打印用户名和 UID："
awk -F: '{print $1, $3}' "$passwd_file"

echo ""
echo "打印使用 bash 的用户："
awk -F: '$7 == "/bin/bash" {print $1}' "$passwd_file"

echo ""
echo "=========================================="
echo "3. 条件过滤"
echo "=========================================="

echo "UID 大于 100 的用户："
awk -F: '$3 > 100 {print $1, $3}' "$passwd_file"

echo ""
echo "数学成绩大于 90 分的记录："
awk '$2 == "数学" && $3 > 90 {print $1, $3}' "$score_file"

echo ""
echo "包含 '张' 的行："
awk '/张/' "$score_file"

echo ""
echo "=========================================="
echo "4. 内置变量"
echo "=========================================="

echo "NR（行号）、NF（字段数）、\$NF（最后一列）："
awk -F: '{print "行"NR": 用户="$1" 字段数="NF" Shell="$NF}' "$passwd_file"

echo ""
echo "FILENAME（文件名）、FS（分隔符）："
awk -F: 'BEGIN {print "分隔符是: [" FS "]"} {print FILENAME, $1} END {print "共处理 " NR " 行"}' "$passwd_file"

echo ""
echo "=========================================="
echo "5. BEGIN 和 END 块"
echo "=========================================="

echo "统计所有学生的数学总分："
awk '
BEGIN { sum = 0; count = 0 }
$2 == "数学" { sum += $3; count++ }
END { 
    print "总人数：" count
    print "总分：" sum
    printf "平均分：%.2f\n", sum/count
}' "$score_file"

echo ""
echo "=========================================="
echo "6. 数组与分组统计"
echo "=========================================="

echo "按学生统计总分和平均分："
awk '
{
    sum[$1] += $3
    count[$1]++
}
END {
    printf "%-10s %-6s %-6s\n", "姓名", "总分", "平均分"
    print "--------------------------------"
    for (name in sum) {
        avg = sum[name] / count[name]
        printf "%-10s %-6d %.2f\n", name, sum[name], avg
    }
}' "$score_file"

echo ""
echo "=========================================="
echo "7. 条件分支（if/else）"
echo "=========================================="

echo "成绩分级（90+ 优秀，60+ 及格，其他 不及格）："
awk '{
    if ($3 >= 90) grade = "优秀"
    else if ($3 >= 60) grade = "及格"
    else grade = "不及格"
    printf "%s %s %d %s\n", $1, $2, $3, grade
}' "$score_file"

echo ""
echo "=========================================="
echo "8. 字符串函数"
echo "=========================================="

echo "length() - 字符串长度："
awk -F: '{print $1, length($1)}' "$passwd_file"

echo ""
echo "toupper()/tolower() - 大小写转换："
awk -F: '{print toupper($1), tolower($5)}' "$passwd_file" | head -3
echo "  ..."

echo ""
echo "index() - 查找子串位置："
awk -F: 'index($5, "User") > 0 {print $1, $5}' "$passwd_file"

echo ""
echo "substr() - 截取子串："
awk -F: '{print $1, "→", substr($1, 1, 3)}' "$passwd_file" | head -5
echo "  ..."

echo ""
echo "=========================================="
echo "9. 格式化输出（printf）"
echo "=========================================="

echo "表格化输出："
awk -F: '
BEGIN { printf "%-15s %-5s %-15s %-20s\n", "用户名", "UID", "主目录", "Shell"
        print "--------------------------------------------------------------" }
{     printf "%-15s %-5s %-15s %-20s\n", $1, $3, $6, $7 }
' "$passwd_file"

# 清理
rm -f "$passwd_file" "$score_file"
