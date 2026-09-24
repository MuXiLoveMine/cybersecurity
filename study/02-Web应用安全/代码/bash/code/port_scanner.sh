#!/bin/bash
# ============================================================
# port_scanner.sh - 简单端口扫描器
# 用法: ./port_scanner.sh <目标IP> [起始端口] [结束端口]
# ============================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 参数检查
if [ $# -lt 1 ]; then
    echo "用法: $0 <目标IP> [起始端口] [结束端口]"
    echo "示例: $0 192.168.1.1 1 1000"
    echo "示例: $0 192.168.1.100 80,443,22,21,3306"
    exit 1
fi

TARGET="$1"
START_PORT=${2:-1}
END_PORT=${3:-1000}

# 常见端口对应服务
declare -A PORT_SERVICES
PORT_SERVICES=(
    [21]="FTP"
    [22]="SSH"
    [23]="Telnet"
    [25]="SMTP"
    [53]="DNS"
    [80]="HTTP"
    [110]="POP3"
    [143]="IMAP"
    [443]="HTTPS"
    [445]="SMB"
    [3306]="MySQL"
    [3389]="RDP"
    [5432]="PostgreSQL"
    [6379]="Redis"
    [8080]="HTTP-Proxy"
    [8443]="HTTPS-Alt"
    [27017]="MongoDB"
)

echo "========================================"
echo "  Bash 端口扫描器"
echo "========================================"
echo -e "目标: ${YELLOW}$TARGET${NC}"

# 判断是端口列表还是范围
if [[ "$START_PORT" =~ ^[0-9]+,[0-9,]+$ ]]; then
    echo -e "端口列表: ${YELLOW}$START_PORT${NC}"
    PORT_MODE="list"
else
    echo -e "端口范围: ${YELLOW}$START_PORT - $END_PORT${NC}"
    PORT_MODE="range"
fi

echo "========================================"
echo ""

# 扫描函数 - 使用 /dev/tcp
scan_port_tcp() {
    local host=$1
    local port=$2
    local timeout=${3:-1}
    
    # 使用 bash 内置的 /dev/tcp 进行连接测试
    (echo > /dev/tcp/"$host"/"$port") 2>/dev/null &
    local pid=$!
    sleep "$timeout"
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
    
    if [ $? -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# 扫描函数 - 使用 nc (netcat)
scan_port_nc() {
    local host=$1
    local port=$2
    local timeout=${3:-1}
    
    if command -v nc &>/dev/null; then
        nc -z -w "$timeout" "$host" "$port" 2>/dev/null
        return $?
    else
        # 回退到 /dev/tcp 方式
        scan_port_tcp "$host" "$port" "$timeout"
        return $?
    fi
}

open_ports=()

# 执行扫描
if [ "$PORT_MODE" = "list" ]; then
    IFS=',' read -ra PORTS <<< "$START_PORT"
    total=${#PORTS[@]}
    current=0
    
    for port in "${PORTS[@]}"; do
        current=$((current + 1))
        printf "\r扫描进度: [%d/%d]  当前端口: %-6d" "$current" "$total" "$port"
        
        if scan_port_nc "$TARGET" "$port" 1; then
            service=${PORT_SERVICES[$port]:-"未知"}
            printf "\n  [+] 端口 %-6d 开放  - 服务: %s\n" "$port" "$service"
            open_ports+=("$port/$service")
        fi
    done
else
    total=$((END_PORT - START_PORT + 1))
    current=0
    
    for ((port=START_PORT; port<=END_PORT; port++)); do
        current=$((current + 1))
        printf "\r扫描进度: [%d/%d]  当前端口: %-6d" "$current" "$total" "$port"
        
        if scan_port_nc "$TARGET" "$port" 1; then
            service=${PORT_SERVICES[$port]:-"未知"}
            printf "\n  [+] 端口 %-6d 开放  - 服务: %s\n" "$port" "$service"
            open_ports+=("$port/$service")
        fi
    done
fi

echo ""
echo "========================================"
echo -e "扫描完成！发现 ${GREEN}${#open_ports[@]}${NC} 个开放端口:"
echo "========================================"

for entry in "${open_ports[@]}"; do
    port=${entry%%/*}
    service=${entry##*/}
    echo -e "  ${GREEN}[+]${NC} 端口 $port - $service"
done

if [ ${#open_ports[@]} -eq 0 ]; then
    echo -e "  ${YELLOW}[!] 未发现开放端口${NC}"
fi

echo ""
echo "扫描结束。"
