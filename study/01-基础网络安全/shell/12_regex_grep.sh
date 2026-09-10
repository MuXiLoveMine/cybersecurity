#!/bin/bash
# 12_regex_grep.sh
# 正则表达式与 grep 示例

# 创建示例文件
demo_file="/tmp/grep_demo_$$.txt"
cat > "$demo_file" << 'EOF'
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
mysql:x:27:27:MySQL Server:/var/lib/mysql:/bin/false
admin:x:1000:1000:Admin User:/home/admin:/bin/bash
testuser:x:1001:1001:Test User:/home/testuser:/bin/zsh
EOF

echo "示例文件（模拟 /etc/passwd）："
echo "----------------------------------------"
cat "$demo_file"
echo "----------------------------------------"
echo ""

echo "=========================================="
echo "1. 基本匹配"
echo "=========================================="

echo "匹配包含 'root' 的行："
grep "root" "$demo_file"

echo ""
echo "匹配以 'root' 开头的行（^）："
grep "^root" "$demo_file"

echo ""
echo "匹配以 'bash' 结尾的行（$）："
grep "bash$" "$demo_file"

echo ""
echo "=========================================="
echo "2. 字符类"
echo "=========================================="

echo "匹配包含数字的行："
grep "[0-9]" "$demo_file" | head -3
echo "  ...（共 $(grep -c "[0-9]" "$demo_file") 行）"

echo ""
echo "匹配以 m 或 n 开头的行："
grep "^[mn]" "$demo_file"

echo ""
echo "匹配不以 r 开头的行（取反）："
grep "^[^r]" "$demo_file" | head -3
echo "  ...（共 $(grep -c "^[^r]" "$demo_file") 行）"

echo ""
echo "=========================================="
echo "3. 量词"
echo "=========================================="

echo "匹配包含冒号 : 出现 6 次的行（即有 7 个字段）："
grep "^[^:]*\(:[^:]*\)\{6\}$" "$demo_file" | head -3
echo "  ...（共 $(grep -c "^[^:]*\(:[^:]*\)\{6\}$" "$demo_file") 行）"

echo ""
echo "匹配 UID（第3字段）是 2 位数的行（扩展正则）："
grep -E "^[^:]*:[^:]*:[0-9]{2}:" "$demo_file"

echo ""
echo "=========================================="
echo "4. 扩展正则（grep -E）"
echo "=========================================="

echo "匹配包含 mysql 或 admin 的行（| 或）："
grep -E "mysql|admin" "$demo_file"

echo ""
echo "匹配 UID 是 1 位或 2 位或 3 位数字（+ 一次或多次）："
grep -E "^[^:]*:[^:]*:[0-9]+:" "$demo_file" | head -5
echo "  ..."

echo ""
echo "匹配 UID 是 1000 多（? 零次或一次）："
grep -E "^[^:]*:[^:]*:100[0-9]?:" "$demo_file"

echo ""
echo "=========================================="
echo "5. 常用选项"
echo "=========================================="

echo "忽略大小写匹配 'ADMIN'："
grep -i "ADMIN" "$demo_file"

echo ""
echo "显示行号（-n）："
grep -n "bash$" "$demo_file"

echo ""
echo "统计匹配行数（-c）："
echo "以 nologin 结尾的行数：$(grep -c "nologin$" "$demo_file")"

echo ""
echo "反向匹配（-v，不包含的行）："
echo "不以 nologin 结尾的行数：$(grep -cv "nologin$" "$demo_file")"

echo ""
echo "只输出匹配的部分（-o）："
echo "所有用户名："
grep -oE "^[^:]+" "$demo_file" | head -5
echo "  ..."

echo ""
echo "=========================================="
echo "6. 实战：提取信息"
echo "=========================================="

echo "提取所有使用 /bin/bash 的用户："
grep "/bin/bash$" "$demo_file" | cut -d: -f1

echo ""
echo "提取 UID 大于 100 的用户："
awk -F: '$3 > 100 {print $1, $3}' "$demo_file"

# 清理
rm -f "$demo_file"
