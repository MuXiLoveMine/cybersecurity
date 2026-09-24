#!/bin/bash
# ============================================================
# info_gather.sh - 信息收集脚本
# 用法: ./info_gather.sh <目标域名或IP>
# ============================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 参数检查
if [ $# -lt 1 ]; then
    echo "用法: $0 <目标域名或IP>"
    echo "示例: $0 example.com"
    echo "示例: $0 192.168.1.1"
    exit 1
fi

TARGET="$1"
OUTPUT_DIR="/tmp/info_gather_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "  Bash 信息收集脚本"
echo "========================================"
echo -e "目标: ${YELLOW}$TARGET${NC}"
echo -e "输出目录: ${YELLOW}$OUTPUT_DIR${NC}"
echo "========================================"
echo ""

# 1. WHOIS 查询
echo -e "${CYAN}[1/10] WHOIS 查询${NC}"
echo "----------------------------------------"
if command -v whois &>/dev/null; then
    whois "$TARGET" > "$OUTPUT_DIR/whois.txt" 2>/dev/null
    echo "  注册商: $(grep -i "registrar:" "$OUTPUT_DIR/whois.txt" | head -1 | sed 's/.*: *//')"
    echo "  创建日期: $(grep -i "creation date:" "$OUTPUT_DIR/whois.txt" | head -1 | sed 's/.*: *//')"
    echo "  过期日期: $(grep -i "expir" "$OUTPUT_DIR/whois.txt" | head -1 | sed 's/.*: *//')"
    echo "  详细结果已保存到: $OUTPUT_DIR/whois.txt"
else
    echo -e "  ${YELLOW}[!] whois 命令不可用，跳过${NC}"
fi
echo ""

# 2. DNS 解析
echo -e "${CYAN}[2/10] DNS 解析${NC}"
echo "----------------------------------------"

# A 记录
echo "  A 记录 (IPv4):"
if command -v dig &>/dev/null; then
    dig +short A "$TARGET" 2>/dev/null | while read -r ip; do
        echo -e "    ${GREEN}$ip${NC}"
    done
elif command -v nslookup &>/dev/null; then
    nslookup "$TARGET" 2>/dev/null | grep "Address:" | tail -n +2 | awk '{print "    " $2}'
else
    echo "    $TARGET" | getent hosts 2>/dev/null | awk '{print "    " $1}'
fi

# MX 记录
echo "  MX 记录:"
if command -v dig &>/dev/null; then
    dig +short MX "$TARGET" 2>/dev/null | sort -n | while read -r prio server; do
        echo -e "    ${GREEN}$prio $server${NC}"
    done
fi

# NS 记录
echo "  NS 记录:"
if command -v dig &>/dev/null; then
    dig +short NS "$TARGET" 2>/dev/null | while read -r ns; do
        echo -e "    ${GREEN}$ns${NC}"
    done
fi

# TXT 记录
echo "  TXT 记录:"
if command -v dig &>/dev/null; then
    dig +short TXT "$TARGET" 2>/dev/null | while read -r txt; do
        echo -e "    ${GREEN}$txt${NC}"
    done | head -5
fi

echo ""

# 3. 反向 DNS 查找
echo -e "${CYAN}[3/10] 反向 DNS 查找${NC}"
echo "----------------------------------------"
# 先获取 IP
if command -v dig &>/dev/null; then
    target_ip=$(dig +short A "$TARGET" | head -1)
else
    target_ip=$(getent hosts "$TARGET" 2>/dev/null | awk '{print $1}' | head -1)
fi

if [ -n "$target_ip" ]; then
    echo "  目标 IP: $target_ip"
    if command -v dig &>/dev/null; then
        ptr=$(dig +short -x "$target_ip" 2>/dev/null)
        if [ -n "$ptr" ]; then
            echo -e "  反向解析: ${GREEN}$ptr${NC}"
        else
            echo "  反向解析: 无结果"
        fi
    fi
fi
echo ""

# 4. 子域名枚举
echo -e "${CYAN}[4/10] 子域名枚举（基础）${NC}"
echo "----------------------------------------"

subdomains=("www" "mail" "ftp" "admin" "api" "blog" "test" "dev" "staging" "cdn" "img" "static" "portal" "shop" "forum" "wiki" "vpn" "ns1" "ns2" "smtp" "pop" "imap" "remote" "webmail" "cpanel")

found_subs=()
for sub in "${subdomains[@]}"; do
    full="$sub.$TARGET"
    if command -v dig &>/dev/null; then
        ip=$(dig +short A "$full" 2>/dev/null | head -1)
    else
        ip=$(getent hosts "$full" 2>/dev/null | awk '{print $1}' | head -1)
    fi
    
    if [ -n "$ip" ]; then
        echo -e "  ${GREEN}[+]${NC} $full -> $ip"
        found_subs+=("$full|$ip")
    fi
done

echo "  共发现 ${#found_subs[@]} 个子域名"
echo ""

# 5. HTTP 头部信息
echo -e "${CYAN}[5/10] HTTP 头部信息${NC}"
echo "----------------------------------------"

if command -v curl &>/dev/null; then
    curl -sI -k --connect-timeout 10 -L "http://$TARGET" > "$OUTPUT_DIR/http_headers.txt" 2>/dev/null
    if [ -s "$OUTPUT_DIR/http_headers.txt" ]; then
        echo "  HTTP 响应头:"
        head -1 "$OUTPUT_DIR/http_headers.txt"
        grep -i "server:" "$OUTPUT_DIR/http_headers.txt" | head -1
        grep -i "x-powered-by:" "$OUTPUT_DIR/http_headers.txt" | head -1
        grep -i "content-type:" "$OUTPUT_DIR/http_headers.txt" | head -1
    else
        echo "  无法连接到 HTTP 服务"
    fi
    
    # HTTPS 检测
    curl -sI -k --connect-timeout 5 "https://$TARGET" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}[+] HTTPS 可用${NC}"
    fi
else
    echo -e "  ${YELLOW}[!] curl 不可用，跳过${NC}"
fi
echo ""

# 6. 常用端口扫描
echo -e "${CYAN}[6/10] 常用端口扫描${NC}"
echo "----------------------------------------"

common_ports=(21 22 23 25 53 80 110 143 443 445 3306 3389 5432 6379 8080 8443)

for port in "${common_ports[@]}"; do
    (echo > /dev/tcp/"$TARGET"/"$port") 2>/dev/null &
    pid=$!
    sleep 1
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}[+]${NC} 端口 $port 开放"
    fi
done
echo ""

# 7. SSL/TLS 证书信息
echo -e "${CYAN}[7/10] SSL/TLS 证书信息${NC}"
echo "----------------------------------------"

if command -v openssl &>/dev/null; then
    cert_info=$(echo | openssl s_client -connect "$TARGET:443" -servername "$TARGET" 2>/dev/null | openssl x509 -noout -subject -issuer -dates 2>/dev/null)
    if [ -n "$cert_info" ]; then
        echo "$cert_info" | while IFS= read -r line; do
            echo "  $line"
        done
    else
        echo "  无法获取证书信息"
    fi
else
    echo -e "  ${YELLOW}[!] openssl 不可用，跳过${NC}"
fi
echo ""

# 8. 服务器操作系统指纹（粗略）
echo -e "${CYAN}[8/10] 操作系统探测（TTL 分析）${NC}"
echo "----------------------------------------"

if command -v ping &>/dev/null; then
    ttl_result=$(ping -c 1 -W 2 "$TARGET" 2>/dev/null | grep -oP 'ttl=\K[0-9]+' | head -1)
    if [ -n "$ttl_result" ]; then
        echo "  TTL: $ttl_result"
        if [ "$ttl_result" -le 64 ]; then
            echo -e "  推测 OS: ${GREEN}Linux/Unix${NC}"
        elif [ "$ttl_result" -le 128 ]; then
            echo -e "  推测 OS: ${GREEN}Windows${NC}"
        else
            echo -e "  推测 OS: ${GREEN}网络设备或其他${NC}"
        fi
    else
        echo "  无法获取 TTL（可能禁 ping）"
    fi
fi
echo ""

# 9. robots.txt 和 sitemap
echo -e "${CYAN}[9/10] robots.txt 和 sitemap 检查${NC}"
echo "----------------------------------------"

if command -v curl &>/dev/null; then
    robots=$(curl -s -k --connect-timeout 5 "http://$TARGET/robots.txt" 2>/dev/null | head -20)
    if [ -n "$robots" ] && [ "$robots" != "<html"* ]; then
        echo "  robots.txt 内容（前20行）:"
        echo "$robots" | sed 's/^/    /'
    else
        echo "  robots.txt 不存在或为空"
    fi
    
    sitemap=$(curl -sI -k --connect-timeout 5 "http://$TARGET/sitemap.xml" 2>/dev/null | head -1)
    if echo "$sitemap" | grep -q "200"; then
        echo -e "  ${GREEN}[+] sitemap.xml 存在${NC}"
    fi
fi
echo ""

# 10. CMS 指纹识别
echo -e "${CYAN}[10/10] CMS 指纹识别${NC}"
echo "----------------------------------------"

if command -v curl &>/dev/null; then
    page_content=$(curl -s -k --connect-timeout 10 "http://$TARGET/" 2>/dev/null)
    
    detected=()
    
    # WordPress
    if echo "$page_content" | grep -qi "wordpress\|wp-content\|wp-includes"; then
        detected+=("WordPress")
    fi
    
    # Drupal
    if echo "$page_content" | grep -qi "drupal\|sites/all\|Drupal.settings"; then
        detected+=("Drupal")
    fi
    
    # Joomla
    if echo "$page_content" | grep -qi "joomla\|/media/system/js\|Joomla!"; then
        detected+=("Joomla")
    fi
    
    # Typecho
    if echo "$page_content" | grep -qi "typecho\|/usr/themes"; then
        detected+=("Typecho")
    fi
    
    # Discuz
    if echo "$page_content" | grep -qi "discuz\|/source/"; then
        detected+=("Discuz")
    fi
    
    if [ ${#detected[@]} -gt 0 ]; then
        echo -e "  检测到 CMS: ${GREEN}${detected[*]}${NC}"
    else
        echo "  未检测到常见 CMS"
    fi
fi
echo ""

echo "========================================"
echo -e "  信息收集完成！"
echo -e "  详细结果保存在: ${GREEN}$OUTPUT_DIR${NC}"
echo "========================================"
