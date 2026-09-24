#!/bin/bash
# ============================================================
# dir_brute.sh - 目录爆破工具
# 用法: ./dir_brute.sh <目标URL> [字典文件]
# ============================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 参数检查
if [ $# -lt 1 ]; then
    echo "用法: $0 <目标URL> [字典文件]"
    echo "示例: $0 http://example.com /path/to/wordlist.txt"
    echo "示例: $0 https://target.com /usr/share/wordlists/dirb/common.txt"
    exit 1
fi

TARGET_URL="$1"
WORDLIST="${2:-}"

# 确保 URL 以 / 结尾
if [[ ! "$TARGET_URL" =~ /$ ]]; then
    TARGET_URL="${TARGET_URL}/"
fi

echo "========================================"
echo "  Bash 目录爆破工具"
echo "========================================"
echo -e "目标 URL: ${YELLOW}$TARGET_URL${NC}"

# 内置小型字典（如果没有提供字典文件）
if [ -z "$WORDLIST" ] || [ ! -f "$WORDLIST" ]; then
    echo -e "${YELLOW}[!] 未指定字典文件或文件不存在，使用内置字典${NC}"
    WORDLIST="/tmp/dir_brute_wordlist.txt"
    cat > "$WORDLIST" << 'EOF'
admin
login
wp-admin
wp-login.php
phpmyadmin
administrator
config.php
.htaccess
robots.txt
sitemap.xml
backup
backup.sql
database.sql
test.php
info.php
phpinfo.php
uploads
images
css
js
api
api/v1
api/v2
dashboard
console
shell
cmd
cpanel
webmail
server-status
server-info
cgi-bin
.git
.svn
.DS_Store
crossdomain.xml
clientaccesspolicy.xml
wp-content
wp-includes
wp-config.php
readme.html
license.txt
xmlrpc.php
EOF
fi

echo -e "字典文件: ${YELLOW}$WORDLIST${NC}"
echo "========================================"
echo ""

# 检查 curl 是否可用
if ! command -v curl &>/dev/null; then
    echo -e "${RED}[错误] 需要 curl 工具，请先安装 curl${NC}"
    exit 1
fi

# 统计字典行数
total=$(wc -l < "$WORDLIST")
echo -e "字典条目数: ${YELLOW}$total${NC}"
echo ""

# 结果数组
found_dirs=()

# 爆破函数
brute_dir() {
    local url="$1"
    local path="$2"
    
    # 发送 HEAD 请求以节省带宽
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 -k -L "$url$path" 2>/dev/null)
    
    case "$response" in
        200)
            echo -e "  ${GREEN}[200]${NC} /$path  (存在)"
            found_dirs+=("200|$path")
            ;;
        301|302)
            redirect_url=$(curl -s -o /dev/null -w "%{redirect_url}" --connect-timeout 5 --max-time 10 -k "$url$path" 2>/dev/null)
            echo -e "  ${BLUE}[$response]${NC} /$path  -> $redirect_url"
            found_dirs+=("$response|$path|$redirect_url")
            ;;
        403)
            echo -e "  ${YELLOW}[403]${NC} /$path  (禁止访问)"
            found_dirs+=("403|$path")
            ;;
        401)
            echo -e "  ${YELLOW}[401]${NC} /$path  (需要认证)"
            found_dirs+=("401|$path")
            ;;
    esac
}

# 主循环
count=0
while IFS= read -r line; do
    # 跳过空行和注释
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    
    count=$((count + 1))
    printf "\r扫描进度: [%d/%d]  当前: %-40s" "$count" "$total" "$line"
    
    brute_dir "$TARGET_URL" "$line"
    
done < "$WORDLIST"

echo ""
echo ""
echo "========================================"
echo -e "扫描完成！发现 ${GREEN}${#found_dirs[@]}${NC} 个结果:"
echo "========================================"

for entry in "${found_dirs[@]}"; do
    code=${entry%%|*}
    rest=${entry#*|}
    path=${rest%%|*}
    redirect=${rest#*|}
    
    case "$code" in
        200)
            echo -e "  ${GREEN}[200]${NC} ${TARGET_URL}${path}"
            ;;
        301|302)
            echo -e "  ${BLUE}[$code]${NC} ${TARGET_URL}${path}  ->  $redirect"
            ;;
        403)
            echo -e "  ${YELLOW}[403]${NC} ${TARGET_URL}${path}"
            ;;
        401)
            echo -e "  ${YELLOW}[401]${NC} ${TARGET_URL}${path}"
            ;;
        *)
            echo -e "  [$code] ${TARGET_URL}${path}"
            ;;
    esac
done

if [ ${#found_dirs[@]} -eq 0 ]; then
    echo -e "  ${YELLOW}[!] 未发现有效目录${NC}"
fi

# 清理临时文件
if [ "$WORDLIST" = "/tmp/dir_brute_wordlist.txt" ]; then
    rm -f "$WORDLIST"
fi

echo ""
echo "目录爆破完成。"
