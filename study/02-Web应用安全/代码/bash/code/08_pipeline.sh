#!/bin/bash
# ============================================================
# 08_pipeline.sh - 管道与过滤器
# ============================================================

echo "========== 1. 管道基础 =========="

# 简单管道：将前一个命令的输出作为后一个命令的输入
echo "统计当前目录文件数:"
ls -la | wc -l

echo ""
echo "列出文件并排序:"
ls /usr/bin | head -10 | sort

echo ""
echo "========== 2. 常用过滤器：grep =========="

echo "grep 过滤包含 'sh' 的行:"
ls /bin | grep "sh" | head -10

echo ""
echo "grep -v 反向过滤（不包含的行）:"
echo -e "apple\nbanana\ncherry\ndate" | grep -v "banana"

echo ""
echo "grep -i 忽略大小写:"
echo -e "Apple\nbanana\nAPPLE\nCherry" | grep -i "apple"

echo ""
echo "grep -c 计数:"
echo -e "apple\nbanana\napple\ncherry\napple" | grep -c "apple"

echo ""
echo "========== 3. 常用过滤器：sed =========="

echo "sed 替换（s/old/new/）:"
echo "Hello World" | sed 's/World/Bash/'

echo ""
echo "sed 全局替换（s/old/new/g）:"
echo "a b a b a b" | sed 's/a/x/g'

echo ""
echo "sed 删除行:"
echo -e "line1\nline2\nline3\nline4\nline5" | sed '2,4d'

echo ""
echo "sed 在行首/行尾添加内容:"
echo -e "line1\nline2\nline3" | sed 's/^/>>> /'

echo ""
echo "========== 4. 常用过滤器：awk =========="

echo "awk 打印指定字段:"
echo "张三 25 北京
李四 30 上海
王五 28 广州" | awk '{print $1, $3}'

echo ""
echo "awk 条件过滤:"
echo "张三 25 北京
李四 30 上海
王五 28 广州" | awk '$2 >= 28 {print $1, "年龄:", $2}'

echo ""
echo "awk 计算总和:"
echo "10
20
30
40
50" | awk '{sum += $1} END {print "总和:", sum}'

echo ""
echo "awk 指定分隔符:"
echo "apple,banana,orange,grape" | awk -F',' '{print $2}'

echo ""
echo "========== 5. 常用过滤器：cut =========="

echo "cut 截取字符:"
echo "abcdefghij" | cut -c 3-7

echo ""
echo "cut 按分隔符截取字段:"
echo "root:x:0:0:root:/root:/bin/bash" | cut -d':' -f 1,7

echo ""
echo "========== 6. 常用过滤器：sort =========="

echo "sort 排序:"
echo -e "banana\napple\ncherry\ndate" | sort

echo ""
echo "sort -r 逆序:"
echo -e "banana\napple\ncherry\ndate" | sort -r

echo ""
echo "sort -n 数值排序:"
echo -e "10\n2\n30\n4\n5" | sort -n

echo ""
echo "sort -u 去重排序:"
echo -e "apple\nbanana\napple\ncherry\nbanana" | sort -u

echo ""
echo "========== 7. 常用过滤器：uniq =========="

echo "uniq 去重（相邻重复行）:"
echo -e "apple\napple\nbanana\nbanana\nbanana\ncherry" | uniq

echo ""
echo "uniq -c 计数:"
echo -e "apple\napple\nbanana\nbanana\nbanana\ncherry" | uniq -c

echo ""
echo "========== 8. 常用过滤器：head / tail =========="

echo "head -n 3 取前3行:"
echo -e "line1\nline2\nline3\nline4\nline5" | head -n 3

echo ""
echo "tail -n 3 取后3行:"
echo -e "line1\nline2\nline3\nline4\nline5" | tail -n 3

echo ""
echo "tail -f 实时跟踪（演示用 head 模拟）:"
# tail -f 常用于日志监控，这里用 head 演示
echo "日志文件最后 5 行（模拟）" | head -5

echo ""
echo "========== 9. 常用过滤器：tr =========="

echo "tr 字符转换（小写转大写）:"
echo "hello world" | tr 'a-z' 'A-Z'

echo ""
echo "tr 删除字符:"
echo "a1b2c3d4e5" | tr -d '0-9'

echo ""
echo "tr 压缩重复字符:"
echo "hello    world   foo" | tr -s ' '

echo ""
echo "========== 10. 常用过滤器：wc =========="

echo "wc 统计:"
echo -e "line1\nline2\nline3" | wc -l
echo "hello world" | wc -c
echo "hello world bash" | wc -w

echo ""
echo "========== 11. 管道链组合示例 =========="

echo "示例1：统计最常用的 5 个命令:"
# 获取 PATH 中的命令并统计前 5 个首字母
ls /bin /usr/bin 2>/dev/null | cut -c1 | sort | uniq -c | sort -rn | head -5

echo ""
echo "示例2：查找并统计文件类型:"
ls -la /etc 2>/dev/null | head -20 | awk '{print $1}' | sort | uniq -c | sort -rn

echo ""
echo "示例3：提取 IP 地址并去重:"
echo "192.168.1.1 - GET /index.html
192.168.1.2 - POST /login
192.168.1.1 - GET /css/style.css
10.0.0.1 - GET /admin
192.168.1.2 - GET /dashboard" | awk '{print $1}' | sort | uniq -c | sort -rn

echo ""
echo "========== 12. xargs 用法 =========="

echo "xargs 基本用法:"
echo "file1 file2 file3" | xargs echo "创建文件:"

echo ""
echo "xargs -I 占位符:"
echo "apple banana cherry" | xargs -n1 -I{} echo "水果: {}"

echo ""
echo "find + xargs 组合:"
# 示例：查找并处理文件
echo "tmp1 tmp2 tmp3" | xargs -I{} sh -c 'echo "处理: {}"'

echo ""
echo "========== 13. 管道与子 shell =========="

echo "管道中的变量作用域问题:"
count=0
echo -e "a\nb\nc" | while read -r line; do
    count=$((count + 1))
done
echo "管道外 count = $count  # 子 shell 中的修改不影响父 shell"

echo ""
echo "使用进程替换避免子 shell:"
count=0
while read -r line; do
    count=$((count + 1))
done < <(echo -e "a\nb\nc")
echo "进程替换后 count = $count"

echo ""
echo "========== 14. named pipe (命名管道) =========="

PIPE_FILE="/tmp/test_pipe"
mkfifo "$PIPE_FILE" 2>/dev/null

echo "命名管道演示:"
# 写入管道（后台运行）
echo "Hello from named pipe" > "$PIPE_FILE" &
# 从管道读取
cat "$PIPE_FILE"

rm -f "$PIPE_FILE"

echo ""
echo "管道与过滤器学习完成！"
