#!/bin/bash
# ============================================================
# log_analyzer.sh - 日志分析脚本
# 支持: Apache/Nginx 访问日志、认证日志等
# 用法: ./log_analyzer.sh <日志文件> [日志类型]
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
    echo "用法: $0 <日志文件> [日志类型]"
    echo ""
    echo "支持的日志类型:"
    echo "  access  - Apache/Nginx 访问日志 (默认)"
    echo "  auth    - Linux 认证日志 (/var/log/auth.log)"
    echo "  secure  - CentOS/RHEL 安全日志 (/var/log/secure)"
    echo "  auto    - 自动检测"
    echo ""
    echo "示例: $0 /var/log/nginx/access.log"
    echo "示例: $0 /var/log/auth.log auth"
    exit 1
fi

LOG_FILE="$1"
LOG_TYPE="${2:-auto}"

# 检查文件
if [ ! -f "$LOG_FILE" ]; then
    echo -e "${RED}[错误] 日志文件不存在: $LOG_FILE${NC}"
    exit 1
fi

echo "========================================"
echo "  Bash 日志分析脚本"
echo "========================================"
echo -e "日志文件: ${YELLOW}$LOG_FILE${NC}"

# 自动检测日志类型
detect_log_type() {
    local file="$1"
    local sample=$(head -5 "$file" 2>/dev/null)
    
    # 检测访问日志（包含 IP 和 HTTP 方法）
    if echo "$sample" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ .*"(GET|POST|HEAD|PUT|DELETE) '; then
        echo "access"
        return
    fi
    
    # 检测 auth/secure 日志
    if echo "$sample" | grep -qiE "(sshd|sudo|pam_unix|Failed password|Accepted password)"; then
        # 判断是 auth.log 还是 secure
        if echo "$sample" | grep -q "pam_unix"; then
            echo "secure"
        else
            echo "auth"
        fi
        return
    fi
    
    echo "unknown"
}

if [ "$LOG_TYPE" = "auto" ]; then
    LOG_TYPE=$(detect_log_type "$LOG_FILE")
    echo -e "检测到日志类型: ${GREEN}$LOG_TYPE${NC}"
else
    echo -e "日志类型: ${GREEN}$LOG_TYPE${NC}"
fi

# 统计总行数
total_lines=$(wc -l < "$LOG_FILE")
echo -e "日志行数: ${YELLOW}$total_lines${NC}"
echo "========================================"
echo ""

# ============== 访问日志分析 ==============
analyze_access_log() {
    local logfile="$1"
    
    echo -e "${CYAN}=== 访问日志分析 ===${NC}"
    echo ""
    
    # 1. 基本统计
    echo -e "${GREEN}[1] 基本统计${NC}"
    echo "  总请求数: $total_lines"
    
    # 时间范围
    first_time=$(head -1 "$logfile" | grep -oP '\[.*?\]' | head -1 | tr -d '[]')
    last_time=$(tail -1 "$logfile" | grep -oP '\[.*?\]' | head -1 | tr -d '[]')
    echo "  起始时间: ${first_time:-未知}"
    echo "  结束时间: ${last_time:-未知}"
    
    # 独立 IP 数
    unique_ips=$(awk '{print $1}' "$logfile" | sort -u | wc -l)
    echo "  独立 IP 数: $unique_ips"
    
    # 状态码统计
    echo ""
    echo -e "${GREEN}[2] HTTP 状态码分布${NC}"
    awk '{print $9}' "$logfile" | sort | uniq -c | sort -rn | head -10 | while read -r count code; do
        case "$code" in
            200|201|204) color=$GREEN ;;
            301|302|304) color=$BLUE ;;
            400|401|403|404) color=$YELLOW ;;
            500|502|503|504) color=$RED ;;
            *) color=$NC ;;
        esac
        printf "  ${color}%s${NC} %-6s %d 次\n" "$code" "" "$count"
    done
    
    # 3. Top 10 访问 IP
    echo ""
    echo -e "${GREEN}[3] Top 10 访问最多的 IP${NC}"
    awk '{print $1}' "$logfile" | sort | uniq -c | sort -rn | head -10 | \
    awk '{printf "  %-15s %s 次\n", $2, $1}'
    
    # 4. Top 10 访问页面
    echo ""
    echo -e "${GREEN}[4] Top 10 访问最多的 URL${NC}"
    awk '{print $7}' "$logfile" | sort | uniq -c | sort -rn | head -10 | \
    awk '{printf "  %-50s %s 次\n", $2, $1}'
    
    # 5. Top 10 User-Agent
    echo ""
    echo -e "${GREEN}[5] Top 10 User-Agent${NC}"
    awk -F'"' '{print $6}' "$logfile" | sort | uniq -c | sort -rn | head -10 | \
    awk '{count=$1; $1=""; printf "  %-60s %s 次\n", $0, count}'
    
    # 6. 404 页面统计
    echo ""
    echo -e "${GREEN}[6] Top 10 404 页面${NC}"
    awk '$9 == 404 {print $7}' "$logfile" | sort | uniq -c | sort -rn | head -10 | \
    awk '{printf "  %-50s %s 次\n", $2, $1}'
    
    # 7. 攻击特征检测
    echo ""
    echo -e "${GREEN}[7] 疑似攻击检测${NC}"
    
    # SQL 注入特征
    sqli_count=$(grep -ciE "(\bunion\b.*\bselect\b|select.*from|information_schema|order by[[:space:]]+[0-9])" "$logfile" 2>/dev/null || echo 0)
    echo -e "  SQL 注入尝试: ${RED}$sqli_count${NC} 次"
    
    # XSS 特征
    xss_count=$(grep -ciE "(<script|javascript:|onerror=|onload=|alert\()" "$logfile" 2>/dev/null || echo 0)
    echo -e "  XSS 攻击尝试: ${RED}$xss_count${NC} 次"
    
    # 目录遍历
    traversal_count=$(grep -ciE "(\.\./|\.\.\\\|/etc/passwd|/etc/shadow)" "$logfile" 2>/dev/null || echo 0)
    echo -e "  目录遍历尝试: ${RED}$traversal_count${NC} 次"
    
    # 暴力破解（401）
    brute_count=$(awk '$9 == 401 {print $1}' "$logfile" | sort | uniq -c | awk '$1 > 10' | wc -l)
    echo -e "  可能的暴力破解 IP: ${RED}$brute_count${NC} 个"
    
    # SQL 注入详情
    if [ "$sqli_count" -gt 0 ]; then
        echo ""
        echo "  SQL 注入示例 (前5条):"
        grep -iE "(\bunion\b.*\bselect\b|select.*from|information_schema)" "$logfile" 2>/dev/null | head -5 | \
        awk '{printf "    %s %s\n", $1, $7}'
    fi
}

# ============== 认证日志分析 ==============
analyze_auth_log() {
    local logfile="$1"
    
    echo -e "${CYAN}=== 认证日志分析 ===${NC}"
    echo ""
    
    # 1. SSH 登录统计
    echo -e "${GREEN}[1] SSH 登录统计${NC}"
    
    failed_count=$(grep -ci "Failed password" "$logfile" 2>/dev/null || echo 0)
    accepted_count=$(grep -ci "Accepted password" "$logfile" 2>/dev/null || echo 0)
    
    echo "  成功登录: ${GREEN}$accepted_count${NC} 次"
    echo "  失败登录: ${RED}$failed_count${NC} 次"
    
    # 2. 失败登录 Top 10 IP
    echo ""
    echo -e "${GREEN}[2] Top 10 失败登录 IP${NC}"
    grep "Failed password" "$logfile" 2>/dev/null | grep -oP 'from \K[0-9.]+' | \
    sort | uniq -c | sort -rn | head -10 | \
    awk '{printf "  %-15s %s 次\n", $2, $1}'
    
    # 3. 成功登录 IP
    echo ""
    echo -e "${GREEN}[3] Top 10 成功登录 IP${NC}"
    grep "Accepted password" "$logfile" 2>/dev/null | grep -oP 'from \K[0-9.]+' | \
    sort | uniq -c | sort -rn | head -10 | \
    awk '{printf "  %-15s %s 次\n", $2, $1}'
    
    # 4. 尝试登录的用户名
    echo ""
    echo -e "${GREEN}[4] 失败登录尝试的用户名 Top 10${NC}"
    grep "Failed password" "$logfile" 2>/dev/null | grep -oP 'for \K\S+' | \
    sort | uniq -c | sort -rn | head -10 | \
    awk '{printf "  %-20s %s 次\n", $2, $1}'
    
    # 5. root 登录尝试
    echo ""
    echo -e "${GREEN}[5] root 登录尝试${NC}"
    root_failed=$(grep -c "Failed password for root" "$logfile" 2>/dev/null || echo 0)
    root_accepted=$(grep -c "Accepted password for root" "$logfile" 2>/dev/null || echo 0)
    echo "  root 失败: ${RED}$root_failed${NC} 次"
    echo "  root 成功: ${GREEN}$root_accepted${NC} 次"
    
    # 6. sudo 使用记录
    echo ""
    echo -e "${GREEN}[6] sudo 使用记录${NC}"
    sudo_count=$(grep -c "sudo:" "$logfile" 2>/dev/null || echo 0)
    echo "  sudo 命令次数: $sudo_count"
    
    echo "  Top 10 sudo 用户:"
    grep "sudo:" "$logfile" 2>/dev/null | grep -oP ':\s+\K\S+' | head -1 | \
    sort | uniq -c | sort -rn | head -10 2>/dev/null || echo "    无数据"
    
    # 7. 暴力破解检测
    echo ""
    echo -e "${GREEN}[7] 暴力破解检测${NC}"
    brute_ips=$(grep "Failed password" "$logfile" 2>/dev/null | grep -oP 'from \K[0-9.]+' | \
    sort | uniq -c | awk '$1 >= 50' | wc -l)
    echo "  失败 >= 50 次的 IP: ${RED}$brute_ips${NC} 个"
    
    if [ "$brute_ips" -gt 0 ]; then
        echo "  暴力破解 IP 列表 (前10):"
        grep "Failed password" "$logfile" 2>/dev/null | grep -oP 'from \K[0-9.]+' | \
        sort | uniq -c | sort -rn | awk '$1 >= 50' | head -10 | \
        awk '{printf "    %-15s %s 次\n", $2, $1}'
    fi
}

# 根据日志类型执行分析
case "$LOG_TYPE" in
    access)
        analyze_access_log "$LOG_FILE"
        ;;
    auth|secure)
        analyze_auth_log "$LOG_FILE"
        ;;
    *)
        echo -e "${RED}[错误] 不支持的日志类型: $LOG_TYPE${NC}"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "  日志分析完成"
echo "========================================"
