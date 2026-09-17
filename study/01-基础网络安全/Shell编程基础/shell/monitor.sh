#!/bin/bash
# monitor.sh
# 综合示例：系统监控脚本
# 功能：监控 CPU、内存、磁盘、网络等系统资源，超过阈值告警

set -euo pipefail

# ============================================================
# 配置
# ============================================================
CPU_THRESHOLD=80          # CPU 使用率告警阈值（%）
MEM_THRESHOLD=85          # 内存使用率告警阈值（%）
DISK_THRESHOLD=90         # 磁盘使用率告警阈值（%）
CHECK_INTERVAL=5          # 检查间隔（秒）
LOG_FILE="/tmp/monitor.log"

# ============================================================
# 颜色
# ============================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================
# 日志
# ============================================================
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

alert() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [告警] $*"
    echo -e "${RED}$msg${NC}"
    echo "$msg" >> "$LOG_FILE"
}

# ============================================================
# CPU 监控
# ============================================================
check_cpu() {
    # 使用 /proc/stat 计算 CPU 使用率
    local cpu_info=($(awk '/^cpu / {print $2,$3,$4,$5,$6,$7,$8}' /proc/stat))
    local idle1=${cpu_info[3]}
    local total1=0
    for v in "${cpu_info[@]}"; do
        total1=$((total1 + v))
    done

    sleep 1

    local cpu_info2=($(awk '/^cpu / {print $2,$3,$4,$5,$6,$7,$8}' /proc/stat))
    local idle2=${cpu_info2[3]}
    local total2=0
    for v in "${cpu_info2[@]}"; do
        total2=$((total2 + v))
    done

    local idle_diff=$((idle2 - idle1))
    local total_diff=$((total2 - total1))
    local usage=$(( 100 * (total_diff - idle_diff) / total_diff ))

    if (( usage >= CPU_THRESHOLD )); then
        alert "CPU 使用率过高：${usage}%（阈值 ${CPU_THRESHOLD}%）"
        echo "  Top 5 CPU 进程："
        ps -eo pid,pcpu,comm --sort=-pcpu | head -6 | tail -5 | awk '{printf "    PID: %-6s CPU: %-5s 命令: %s\n", $1, $2, $3}'
    else
        log "CPU 使用率：${usage}%（正常）"
    fi
}

# ============================================================
# 内存监控
# ============================================================
check_memory() {
    local mem_total=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
    local mem_available=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
    local mem_used=$((mem_total - mem_available))
    local mem_usage=$((100 * mem_used / mem_total))

    if (( mem_usage >= MEM_THRESHOLD )); then
        alert "内存使用率过高：${mem_usage}%（阈值 ${MEM_THRESHOLD}%）"
        echo "  总内存：$((mem_total / 1024)) MB"
        echo "  已使用：$((mem_used / 1024)) MB"
        echo "  Top 5 内存进程："
        ps -eo pid,rss,comm --sort=-rss | head -6 | tail -5 | awk '{printf "    PID: %-6s 内存: %-8s 命令: %s\n", $1, $2"KB", $3}'
    else
        log "内存使用率：${mem_usage}%（正常）"
    fi
}

# ============================================================
# 磁盘监控
# ============================================================
check_disk() {
    local alerted=0
    while read -r usage mount; do
        local num=${usage%\%}
        if (( num >= DISK_THRESHOLD )); then
            alert "磁盘使用率过高：$mount - ${usage}（阈值 ${DISK_THRESHOLD}%）"
            alerted=1
        fi
    done < <(df -h | awk 'NR>1 && /^\// {print $5, $6}')

    if (( alerted == 0 )); then
        log "磁盘使用率正常（最高：$(df -h | awk 'NR>1 && /^\// {print $5}' | sort -n | tail -1)）"
    fi
}

# ============================================================
# 网络监控
# ============================================================
check_network() {
    # 找到默认网卡
    local iface=$(ip route | awk '/default/ {print $5; exit}')
    if [[ -z "$iface" ]]; then
        log "网络：未找到默认网络接口"
        return
    fi

    local rx1=$(cat "/sys/class/net/$iface/statistics/rx_bytes" 2>/dev/null || echo 0)
    local tx1=$(cat "/sys/class/net/$iface/statistics/tx_bytes" 2>/dev/null || echo 0)
    sleep 1
    local rx2=$(cat "/sys/class/net/$iface/statistics/rx_bytes" 2>/dev/null || echo 0)
    local tx2=$(cat "/sys/class/net/$iface/statistics/tx_bytes" 2>/dev/null || echo 0)

    local rx_speed=$(( (rx2 - rx1) / 1024 ))
    local tx_speed=$(( (tx2 - tx1) / 1024 ))

    log "网络（$iface）：↓ ${rx_speed} KB/s  ↑ ${tx_speed} KB/s"
}

# ============================================================
# 系统负载
# ============================================================
check_load() {
    local load=($(cat /proc/loadavg))
    local cpu_count=$(nproc)
    local load1=${load[0]}

    log "系统负载：1分钟=$load1  5分钟=${load[1]}  15分钟=${load[2]}  CPU核数=$cpu_count"
}

# ============================================================
# 打印头部
# ============================================================
print_header() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "   系统监控工具 v1.0"
    echo "=========================================="
    echo "CPU 告警阈值：${CPU_THRESHOLD}%"
    echo "内存告警阈值：${MEM_THRESHOLD}%"
    echo "磁盘告警阈值：${DISK_THRESHOLD}%"
    echo "检查间隔：${CHECK_INTERVAL} 秒"
    echo "日志文件：$LOG_FILE"
    echo "=========================================="
    echo -e "${NC}"
}

# ============================================================
# 主函数
# ============================================================
main() {
    print_header
    log "系统监控开始运行，按 Ctrl+C 退出"
    echo ""

    while true; do
        echo -e "${BLUE}[ $(date '+%H:%M:%S') ] 第 ${count:-1} 次检查${NC}"
        check_cpu
        check_memory
        check_disk
        check_network
        check_load
        echo ""

        count=$(( ${count:-0} + 1 ))
        sleep "$CHECK_INTERVAL"
    done
}

# 捕获退出
trap 'echo -e "\n${YELLOW}监控已停止，日志保存在 $LOG_FILE${NC}"; exit 0' SIGINT SIGTERM

main "$@"
