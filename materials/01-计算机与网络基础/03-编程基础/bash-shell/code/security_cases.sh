#!/bin/bash
#
# security_cases.sh —— Bash 安全案例集（防御/运维视角）
#
# 涵盖 4 个安全案例：
#   1. SSH 失败登录监测 — 分析 auth.log，检测暴力破解
#   2. 日志分析工具 — 多种日志统计和分析功能
#   3. 系统安全巡检 — 系统基本安全状态检查
#   4. 文件完整性检查 — 基于哈希的文件完整性校验
#
# 运行方式:
#   bash security_cases.sh              # 运行所有演示
#   bash security_cases.sh --help       # 查看帮助
#   bash security_cases.sh ssh auth.log # SSH 登录分析
#   bash security_cases.sh check        # 系统巡检
#
# 注意：
#   - 所有工具仅限在授权的环境中使用
#   - 生产环境使用前请充分测试
#   - 系统巡检部分需要 root 权限才能完整检查

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR=""

# 颜色输出（如果终端支持）
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'  # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }

# ============================================================
# 案例 1：SSH 失败登录监测
# ============================================================

ssh_login_monitor() {
    """
    SSH 登录失败监测
    分析认证日志，检测暴力破解行为

    用法:
      ssh_login_monitor <日志文件> [阈值]

    参数:
      日志文件    auth.log 或 secure 格式的日志文件
      阈值        失败次数阈值，默认 5 次
    """
    local log_file="$1"
    local threshold="${2:-5}"

    if [ -z "$log_file" ]; then
        error "请指定日志文件路径"
        return 1
    fi

    if [ ! -f "$log_file" ]; then
        error "日志文件不存在: $log_file"
        return 1
    fi

    info "分析 SSH 登录日志: $log_file"
    info "暴力破解阈值: $threshold 次"

    # 统计
    local total_lines
    total_lines=$(wc -l < "$log_file")

    local failed_count
    failed_count=$(grep -c -i "failed password\|authentication failure" "$log_file" 2>/dev/null || echo 0)

    local success_count
    success_count=$(grep -c -i "accepted password\|accepted publickey" "$log_file" 2>/dev/null || echo 0)

    echo ""
    echo "  ========================================================"
    echo "  SSH 登录分析报告"
    echo "  ========================================================"
    echo "  日志文件: $log_file"
    echo "  总行数: $total_lines"
    echo "  登录失败: $failed_count 次"
    echo "  登录成功: $success_count 次"

    if [ "$total_lines" -gt 0 ]; then
        local failure_rate
        failure_rate=$(awk "BEGIN {printf \"%.2f\", $failed_count / $total_lines * 100}")
        echo "  失败率: ${failure_rate}%"
    fi

    # 失败最多的 IP Top 10
    echo ""
    echo "  失败次数最多的 IP Top 10:"
    echo "  --------------------------------------------------------"
    printf "  %-18s %-10s %s\n" "IP 地址" "失败次数" "状态"
    echo "  --------------------------------------------------------"

    # 提取失败登录的 IP（兼容多种日志格式）
    local suspicious_ips
    suspicious_ips=$(grep -i "failed password" "$log_file" 2>/dev/null \
        | grep -oP 'from \K\S+' \
        | sort \
        | uniq -c \
        | sort -rn \
        | head -10)

    if [ -z "$suspicious_ips" ]; then
        echo "    （没有找到失败登录记录）"
    else
        while read -r count ip; do
            local status=""
            if [ "$count" -ge "$threshold" ]; then
                status="⚠️  可疑"
            else
                status="正常"
            fi
            printf "  %-18s %-10s %s\n" "$ip" "$count" "$status"
        done <<< "$suspicious_ips"
    fi

    # 被尝试最多的用户名
    echo ""
    echo "  被尝试最多的用户名 Top 10:"
    echo "  --------------------------------------------------------"

    local top_users
    top_users=$(grep -i "failed password" "$log_file" 2>/dev/null \
        | grep -oP 'for \K(invalid user )?\K\S+' \
        | sort \
        | uniq -c \
        | sort -rn \
        | head -10)

    if [ -z "$top_users" ]; then
        echo "    （数据不足）"
    else
        while read -r count user; do
            printf "  %-20s %-10s\n" "$user" "$count"
        done <<< "$top_users"
    fi

    echo "  ========================================================"

    # 返回可疑 IP 数量
    local suspect_count
    suspect_count=$(echo "$suspicious_ips" | awk -v t="$threshold" '$1 >= t {c++} END {print c+0}')
    echo ""
    [ "$suspect_count" -gt 0 ] \
        && warn "发现 $suspect_count 个可疑 IP（失败次数 >= $threshold）" \
        || success "未发现明显的暴力破解迹象"

    return 0
}

# ============================================================
# 案例 2：日志分析工具
# ============================================================

log_analyzer() {
    """
    日志分析工具
    支持 Nginx/Apache access log 格式的基本分析

    用法:
      log_analyzer <日志文件> [类型]

    参数:
      日志文件    访问日志文件
      类型        日志类型: auto(默认), nginx, apache, auth
    """
    local log_file="$1"
    local log_type="${2:-auto}"

    if [ -z "$log_file" ]; then
        error "请指定日志文件"
        return 1
    fi

    if [ ! -f "$log_file" ]; then
        error "文件不存在: $log_file"
        return 1
    fi

    info "分析日志文件: $log_file"

    local total_lines
    total_lines=$(wc -l < "$log_file")

    echo ""
    echo "  ========================================================"
    echo "  日志分析报告"
    echo "  ========================================================"
    echo "  文件: $log_file"
    echo "  总行数: $total_lines"

    # 尝试判断是不是 access log（包含 HTTP 状态码）
    local is_access_log
    is_access_log=$(head -5 "$log_file" | grep -cE '" [0-9]{3} ' || true)

    if [ "$is_access_log" -gt 0 ]; then
        info "检测到访问日志格式"

        # 状态码分布
        echo ""
        echo "  HTTP 状态码分布:"
        echo "  --------------------------------------------------------"
        awk '{print $9}' "$log_file" \
            | sort \
            | uniq -c \
            | sort -rn \
            | awk '{printf "    %-8s %-10s %s\n", $2, $1, "个"}'

        # IP Top 10
        echo ""
        echo "  访问量 Top 10 IP:"
        echo "  --------------------------------------------------------"
        awk '{print $1}' "$log_file" \
            | sort \
            | uniq -c \
            | sort -rn \
            | head -10 \
            | awk '{printf "    %-18s %-10s\n", $2, $1}'

        # URL Top 10
        echo ""
        echo "  访问量 Top 10 URL:"
        echo "  --------------------------------------------------------"
        awk '{print $7}' "$log_file" \
            | sort \
            | uniq -c \
            | sort -rn \
            | head -10 \
            | awk '{printf "    %-40s %-10s\n", $2, $1}'

        # 404 Top 10
        echo ""
        echo "  404 最多的 URL Top 10:"
        echo "  --------------------------------------------------------"
        awk '$9 == 404 {print $7}' "$log_file" \
            | sort \
            | uniq -c \
            | sort -rn \
            | head -10 \
            | awk '{printf "    %-40s %-10s\n", $2, $1}'
    fi

    # 通用统计
    echo ""
    echo "  基本统计:"
    echo "  --------------------------------------------------------"
    echo "    总行数: $total_lines"
    echo "    文件大小: $(du -h "$log_file" | cut -f1)"
    echo "    唯一 IP 数: $(awk '{print $1}' "$log_file" | sort -u | wc -l)"

    echo "  ========================================================"
    return 0
}

# ============================================================
# 案例 3：系统安全巡检
# ============================================================

system_security_check() {
    """
    系统安全巡检
    检查系统基本安全配置和状态

    用法:
      system_security_check [输出目录]

    说明:
      部分检查需要 root 权限才能完整执行
    """
    local output_dir="${1:-/tmp/security_check_$$}"
    mkdir -p "$output_dir"

    info "系统安全巡检"
    info "输出目录: $output_dir"

    local report="$output_dir/report.txt"

    echo "============================================================" > "$report"
    echo "  系统安全巡检报告" >> "$report"
    echo "============================================================" >> "$report"
    echo "  巡检时间: $(date)" >> "$report"
    echo "  主机名: $(hostname)" >> "$report"
    echo "  内核: $(uname -r)" >> "$report"
    echo "" >> "$report"

    # ---- 1. 系统信息 ----
    echo ""
    info "[1/6] 系统信息检查"

    cat >> "$report" << 'EOF'
【1】系统信息
------------------------------------------------------------
EOF
    {
        echo "  操作系统: $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo "未知")"
        echo "  内核版本: $(uname -r)"
        echo "  架构: $(uname -m)"
        echo "  运行时间: $(uptime -p 2>/dev/null || uptime)"
        echo "  负载: $(cat /proc/loadavg | awk '{print $1, $2, $3}')"
    } >> "$report"

    cat "$report" | tail -10 | head -8 | sed 's/^/  /'
    success "系统信息收集完成"

    # ---- 2. 用户与认证 ----
    echo ""
    info "[2/6] 用户与认证检查"

    echo "" >> "$report"
    echo "【2】用户与认证" >> "$report"
    echo "------------------------------------------------------------" >> "$report"

    # UID 为 0 的账号
    local uid0_users
    uid0_users=$(awk -F: '$3 == 0 {print $1}' /etc/passwd)
    echo "  UID=0 的账号: $(echo "$uid0_users" | wc -w) 个" >> "$report"
    echo "$uid0_users" | while read -r u; do
        [ -n "$u" ] && echo "    - $u" >> "$report"
    done

    # 空密码账号（需要 root）
    local empty_pass
    empty_pass=$(awk -F: '($2 == "" || $2 == "!") {print $1}' /etc/shadow 2>/dev/null | head -5 || echo "（需要 root 权限）")
    echo "" >> "$report"
    echo "  空密码/锁定账号: " >> "$report"
    echo "$empty_pass" | while read -r u; do
        [ -n "$u" ] && echo "    - $u" >> "$report"
    done

    # sudoers
    echo "" >> "$report"
    echo "  sudo 用户:" >> "$report"
    grep -v '^\s*#\|^$' /etc/sudoers 2>/dev/null \
        | grep -v '^Defaults\|^User_Alias\|^Cmnd_Alias\|^Runas_Alias\|^Host_Alias' \
        | head -10 \
        | sed 's/^/    /' >> "$report"

    success "用户与认证检查完成"

    # ---- 3. 文件系统 ----
    echo ""
    info "[3/6] 文件系统安全检查"

    echo "" >> "$report"
    echo "【3】文件系统安全" >> "$report"
    echo "------------------------------------------------------------" >> "$report"

    # SUID 文件
    local suid_count
    suid_count=$(find / -xdev -perm -4000 -type f 2>/dev/null | wc -l)
    echo "  SUID 文件: $suid_count 个" >> "$report"
    find / -xdev -perm -4000 -type f 2>/dev/null | head -10 | sed 's/^/    /' >> "$report"
    [ "$suid_count" -gt 10 ] && echo "    ... 还有 $((suid_count - 10)) 个" >> "$report"

    # 全局可写文件
    local world_writable
    world_writable=$(find / -xdev -type f -perm -0002 2>/dev/null | wc -l)
    echo "" >> "$report"
    echo "  全局可写文件: $world_writable 个" >> "$report"

    # /tmp 下的可执行文件
    local tmp_exec
    tmp_exec=$(find /tmp -type f -executable 2>/dev/null | wc -l)
    echo "  /tmp 下可执行文件: $tmp_exec 个" >> "$report"

    # 关键文件权限
    echo "" >> "$report"
    echo "  关键文件权限检查:" >> "$report"
    local files_to_check=("/etc/passwd" "/etc/shadow" "/etc/sudoers" "/etc/ssh/sshd_config")
    for f in "${files_to_check[@]}"; do
        if [ -f "$f" ]; then
            local perms
            perms=$(stat -c "%a %U:%G" "$f" 2>/dev/null || echo "未知")
            echo "    $f: $perms" >> "$report"
        fi
    done

    success "文件系统检查完成"

    # ---- 4. 网络 ----
    echo ""
    info "[4/6] 网络安全检查"

    echo "" >> "$report"
    echo "【4】网络安全" >> "$report"
    echo "------------------------------------------------------------" >> "$report"

    # 监听端口
    echo "  监听端口:" >> "$report"
    ss -tulnp 2>/dev/null | head -20 | sed 's/^/    /' >> "$report"

    # 防火墙状态
    echo "" >> "$report"
    echo "  防火墙状态:" >> "$report"
    if command -v iptables >/dev/null 2>&1; then
        local iptables_count
        iptables_count=$(iptables -L -n 2>/dev/null | wc -l)
        echo "    iptables 规则数: $iptables_count" >> "$report"
    fi
    if command -v ufw >/dev/null 2>&1; then
        echo "    ufw: $(ufw status 2>/dev/null | head -1)" >> "$report"
    fi
    if command -v firewalld >/dev/null 2>&1; then
        echo "    firewalld: $(firewall-cmd --state 2>/dev/null || echo "未知")" >> "$report"
    fi

    success "网络安全检查完成"

    # ---- 5. 服务与进程 ----
    echo ""
    info "[5/6] 服务与进程检查"

    echo "" >> "$report"
    echo "【5】服务与进程" >> "$report"
    echo "------------------------------------------------------------" >> "$report"

    # 运行的服务数
    if command -v systemctl >/dev/null 2>&1; then
        local running_services
        running_services=$(systemctl list-units --type=service --state=running --no-pager 2>/dev/null | wc -l)
        echo "  运行中的服务: $running_services 个" >> "$report"
    fi

    # 进程数
    echo "  总进程数: $(ps aux | wc -l)" >> "$report"
    echo "  root 进程数: $(ps -u root | wc -l)" >> "$report"

    # 僵尸进程
    local zombie_count
    zombie_count=$(ps aux | awk '$8 == "Z"' | wc -l)
    echo "  僵尸进程数: $zombie_count" >> "$report"

    success "服务与进程检查完成"

    # ---- 6. 资源使用 ----
    echo ""
    info "[6/6] 资源使用检查"

    echo "" >> "$report"
    echo "【6】资源使用" >> "$report"
    echo "------------------------------------------------------------" >> "$report"

    echo "  磁盘使用:" >> "$report"
    df -h 2>/dev/null | grep -E '^/dev/|Filesystem' | sed 's/^/    /' >> "$report"

    echo "" >> "$report"
    echo "  内存使用:" >> "$report"
    free -h 2>/dev/null | sed 's/^/    /' >> "$report"

    success "资源使用检查完成"

    # ---- 汇总 ----
    echo ""
    echo "" >> "$report"
    echo "============================================================" >> "$report"
    echo "  巡检完成" >> "$report"
    echo "  报告文件: $report" >> "$report"
    echo "============================================================" >> "$report"

    success "系统安全巡检完成！"
    info "完整报告: $report"
    echo ""
    echo "  报告摘要:"
    echo "    - UID=0 用户: $(echo "$uid0_users" | wc -w) 个"
    echo "    - SUID 文件: $suid_count 个"
    echo "    - 全局可写文件: $world_writable 个"
    echo "    - 僵尸进程: $zombie_count 个"

    return 0
}

# ============================================================
# 案例 4：文件完整性检查
# ============================================================

file_integrity_check() {
    """
    文件完整性检查
    计算和校验文件/目录的哈希值，用于检测文件篡改

    用法:
      file_integrity_check <目标路径> [基准文件]
      file_integrity_check --generate <目录> [输出文件]

    子命令:
      --generate    生成基准哈希（首次使用）
      --verify      校验文件完整性（需要基准文件）
    """
    local mode="check"
    local target=""
    local baseline=""
    local output=""

    # 简单参数解析
    while [ $# -gt 0 ]; do
        case "$1" in
            --generate)
                mode="generate"
                shift
                target="$1"
                shift
                ;;
            --verify)
                mode="verify"
                shift
                target="$1"
                baseline="$2"
                shift 2
                ;;
            -o|--output)
                output="$2"
                shift 2
                ;;
            *)
                if [ -z "$target" ]; then
                    target="$1"
                else
                    baseline="$1"
                fi
                shift
                ;;
        esac
    done

    if [ -z "$target" ]; then
        error "请指定目标文件或目录"
        return 1
    fi

    if [ ! -e "$target" ]; then
        error "目标不存在: $target"
        return 1
    fi

    # 选择哈希算法（优先用 sha256）
    local hash_cmd="sha256sum"
    local hash_name="SHA256"
    if ! command -v sha256sum >/dev/null 2>&1; then
        # macOS 兼容
        hash_cmd="shasum -a 256"
    fi

    case "$mode" in
        generate)
            info "生成文件完整性基准: $target"
            output="${output:-${target%/}.baseline.sha256}"

            if [ -f "$target" ]; then
                # 单个文件
                $hash_cmd "$target" > "$output"
                success "基准已保存到: $output"
            elif [ -d "$target" ]; then
                # 目录
                info "计算目录下所有文件的哈希..."
                find "$target" -type f -exec $hash_cmd {} \; > "$output"
                local file_count
                file_count=$(wc -l < "$output")
                success "基准已保存到: $output（共 $file_count 个文件）"
            fi
            ;;

        verify)
            info "校验文件完整性: $target"
            info "基准文件: $baseline"

            if [ ! -f "$baseline" ]; then
                error "基准文件不存在: $baseline"
                return 1
            fi

            local tmp_current="/tmp/integrity_current_$$.txt"

            if [ -f "$target" ]; then
                $hash_cmd "$target" > "$tmp_current"
            elif [ -d "$target" ]; then
                find "$target" -type f -exec $hash_cmd {} \; > "$tmp_current"
            fi

            # 对比
            echo ""
            echo "  ========================================================"
            echo "  文件完整性校验结果"
            echo "  ========================================================"

            local total_files
            total_files=$(wc -l < "$baseline")
            echo "  基准文件数: $total_files"

            # 找出变化的文件
            local changed=0
            local added=0
            local removed=0

            # 提取文件路径和哈希
            local baseline_sorted="/tmp/baseline_sorted_$$"
            local current_sorted="/tmp/current_sorted_$$"

            # 格式：哈希 文件名 → 按文件名字典序排序
            awk '{print $2, $1}' "$baseline" | sort > "$baseline_sorted"
            awk '{print $2, $1}' "$tmp_current" | sort > "$current_sorted"

            echo ""
            echo "  变更文件:"
            echo "  --------------------------------------------------------"

            # 用 diff 对比
            local diff_output
            diff_output=$(diff "$baseline_sorted" "$current_sorted" 2>/dev/null || true)

            if [ -z "$diff_output" ]; then
                success "所有文件完整性校验通过，没有发现变更"
            else
                # 解析 diff 输出
                while IFS= read -r line; do
                    case "$line" in
                        "< "*)
                            removed=$((removed + 1))
                            local file
                            file=$(echo "$line" | sed 's/^< //' | awk '{print $1}')
                            echo -e "  ${RED}- 已删除${NC}: $file"
                            ;;
                        "> "*)
                            added=$((added + 1))
                            local file
                            file=$(echo "$line" | sed 's/^> //' | awk '{print $1}')
                            echo -e "  ${GREEN}+ 新增${NC}: $file"
                            ;;
                    esac
                done <<< "$diff_output"

                # 计算修改的文件（两边都有但哈希不同）
                local baseline_files
                baseline_files=$(awk '{print $1}' "$baseline_sorted")
                local current_files
                current_files=$(awk '{print $1}' "$current_sorted")
                local common_files
                common_files=$(comm -12 <(echo "$baseline_files" | sort) <(echo "$current_files" | sort))

                while IFS= read -r f; do
                    [ -z "$f" ] && continue
                    local old_hash
                    old_hash=$(grep -F "$f " "$baseline_sorted" | awk '{print $2}')
                    local new_hash
                    new_hash=$(grep -F "$f " "$current_sorted" | awk '{print $2}')
                    if [ "$old_hash" != "$new_hash" ]; then
                        changed=$((changed + 1))
                        echo -e "  ${YELLOW}~ 修改${NC}: $f"
                    fi
                done <<< "$common_files"

                echo "  --------------------------------------------------------"
                echo "  变更统计:"
                echo "    修改: $changed 个"
                echo "    新增: $added 个"
                echo "    删除: $removed 个"
            fi

            echo "  ========================================================"

            # 清理
            rm -f "$tmp_current" "$baseline_sorted" "$current_sorted"

            if [ "$changed" -gt 0 ] || [ "$added" -gt 0 ] || [ "$removed" -gt 0 ]; then
                warn "发现文件变更，请核实是否为正常修改"
                return 2
            else
                success "文件完整性校验通过"
                return 0
            fi
            ;;

        check)
            # 简单模式：只计算哈希
            info "计算 $hash_name 哈希: $target"
            if [ -f "$target" ]; then
                $hash_cmd "$target"
            elif [ -d "$target" ]; then
                find "$target" -type f -exec $hash_cmd {} \;
            fi
            ;;
    esac
}

# ============================================================
# 生成示例日志（用于演示）
# ============================================================

generate_sample_logs() {
    """生成示例日志文件，用于演示"""
    local output_dir="${1:-/tmp/security_demo_logs}"
    mkdir -p "$output_dir"

    # 生成 auth.log 示例
    local auth_log="$output_dir/auth.log"
    cat > "$auth_log" << 'EOF'
Oct 10 10:00:01 server sshd[1001]: Failed password for root from 10.0.0.5 port 22 ssh2
Oct 10 10:00:02 server sshd[1002]: Failed password for admin from 10.0.0.5 port 22 ssh2
Oct 10 10:00:03 server sshd[1003]: Accepted password for alice from 192.168.1.10 port 22 ssh2
Oct 10 10:00:04 server sshd[1004]: Failed password for root from 10.0.0.6 port 22 ssh2
Oct 10 10:00:05 server sshd[1005]: Failed password for root from 10.0.0.5 port 22 ssh2
Oct 10 10:00:06 server sshd[1006]: Accepted password for bob from 192.168.1.11 port 22 ssh2
Oct 10 10:00:07 server sshd[1007]: Failed password for test from 10.0.0.7 port 22 ssh2
Oct 10 10:00:08 server sshd[1008]: Failed password for root from 10.0.0.5 port 22 ssh2
Oct 10 10:00:09 server sshd[1009]: Accepted publickey for deploy from 192.168.1.20 port 22 ssh2
Oct 10 10:00:10 server sshd[1010]: Failed password for administrator from 10.0.0.6 port 22 ssh2
Oct 10 10:00:11 server sshd[1011]: Failed password for root from 10.0.0.5 port 22 ssh2
Oct 10 10:00:12 server sshd[1012]: Failed password for user from 10.0.0.8 port 22 ssh2
Oct 10 10:00:13 server sshd[1013]: Failed password for oracle from 10.0.0.5 port 22 ssh2
Oct 10 10:00:14 server sshd[1014]: Failed password for mysql from 10.0.0.6 port 22 ssh2
Oct 10 10:00:15 server sshd[1015]: Failed password for postgres from 10.0.0.5 port 22 ssh2
Oct 10 10:00:16 server sshd[1016]: Failed password for www-data from 10.0.0.5 port 22 ssh2
Oct 10 10:00:17 server sshd[1017]: Failed password for ftp from 10.0.0.7 port 22 ssh2
Oct 10 10:00:18 server sshd[1018]: Accepted password for charlie from 192.168.1.12 port 22 ssh2
Oct 10 10:00:19 server sshd[1019]: Failed password for root from 10.0.0.9 port 22 ssh2
Oct 10 10:00:20 server sshd[1020]: Failed password for root from 10.0.0.5 port 22 ssh2
EOF

    # 生成 access.log 示例
    local access_log="$output_dir/access.log"
    cat > "$access_log" << 'EOF'
192.168.1.100 - - [10/Oct/2024:10:00:01 +0800] "GET /index.html HTTP/1.1" 200 1234
192.168.1.100 - - [10/Oct/2024:10:00:02 +0800] "GET /style.css HTTP/1.1" 200 567
10.0.0.5 - - [10/Oct/2024:10:00:03 +0800] "GET /admin HTTP/1.1" 302 0
10.0.0.5 - - [10/Oct/2024:10:00:04 +0800] "POST /admin/login HTTP/1.1" 401 45
192.168.1.101 - - [10/Oct/2024:10:00:05 +0800] "GET /api/users HTTP/1.1" 200 2345
10.0.0.5 - - [10/Oct/2024:10:00:06 +0800] "POST /admin/login HTTP/1.1" 401 45
192.168.1.100 - - [10/Oct/2024:10:00:07 +0800] "GET /about.html HTTP/1.1" 200 890
10.0.0.5 - - [10/Oct/2024:10:00:08 +0800] "GET /admin/users HTTP/1.1" 403 23
192.168.1.102 - - [10/Oct/2024:10:00:09 +0800] "GET /index.html HTTP/1.1" 200 1234
10.0.0.6 - - [10/Oct/2024:10:00:10 +0800] "GET /wp-login.php HTTP/1.1" 404 200
192.168.1.100 - - [10/Oct/2024:10:00:11 +0800] "POST /api/submit HTTP/1.1" 200 67
10.0.0.7 - - [10/Oct/2024:10:00:12 +0800] "GET /phpmyadmin HTTP/1.1" 404 200
EOF

    echo "$auth_log"
    echo "$access_log"
}

# ============================================================
# 演示模式
# ============================================================

run_demo() {
    """运行所有演示案例"""
    echo "============================================================"
    echo "  Bash 安全案例集演示"
    echo "  Security Cases Demo (Defensive Perspective)"
    echo "============================================================"

    local demo_dir="/tmp/bash_security_demo_$$"
    mkdir -p "$demo_dir"

    # 生成示例日志
    echo ""
    info "生成示例日志文件..."
    log_dir="$demo_dir/logs"
    generate_sample_logs "$log_dir" > /dev/null
    success "示例日志已生成: $log_dir"

    # 案例 1：SSH 登录监测
    echo ""
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  案例 1：SSH 失败登录监测                                  ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    ssh_login_monitor "$log_dir/auth.log" 5

    # 案例 2：日志分析
    echo ""
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  案例 2：访问日志分析                                      ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    log_analyzer "$log_dir/access.log"

    # 案例 3：系统巡检
    echo ""
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  案例 3：系统安全巡检                                      ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    system_security_check "$demo_dir/check_report"

    # 案例 4：文件完整性
    echo ""
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  案例 4：文件完整性检查                                    ║"
    echo "╚══════════════════════════════════════════════════════════╝"

    # 生成测试文件
    local test_dir="$demo_dir/integrity_test"
    mkdir -p "$test_dir"
    echo "初始内容" > "$test_dir/file1.txt"
    echo "配置文件" > "$test_dir/config.ini"
    echo "数据文件" > "$test_dir/data.csv"

    info "文件完整性检查演示"
    echo "  测试目录: $test_dir"

    # 生成基准
    echo ""
    info "步骤 1：生成基准哈希"
    local baseline="$demo_dir/baseline.sha256"
    file_integrity_check --generate "$test_dir" "$baseline"

    # 修改一个文件
    echo ""
    info "步骤 2：模拟文件变更（修改 file1.txt）"
    echo "被篡改的内容" > "$test_dir/file1.txt"
    echo "新增文件" > "$test_dir/new_file.txt"
    rm -f "$test_dir/data.csv"

    # 校验
    echo ""
    info "步骤 3：校验完整性"
    file_integrity_check --verify "$test_dir" "$baseline" || true

    # 结束
    echo ""
    echo "============================================================"
    success "所有案例演示完成！"
    info "演示文件保存在: $demo_dir"
    echo "============================================================"
}

# ============================================================
# 帮助信息
# ============================================================

usage() {
    cat << 'EOF'
Bash 安全案例集（防御/运维视角）

用法:
  bash security_cases.sh [命令] [选项] [参数...]

命令:
  demo              运行所有案例演示（默认）
  ssh <日志文件>     SSH 失败登录监测
  log <日志文件>     日志分析工具
  check             系统安全巡检
  integrity         文件完整性检查
  gen-samples <目录> 生成示例日志文件
  help              显示此帮助

SSH 登录监测:
  bash security_cases.sh ssh <auth.log> [阈值]
  阈值默认为 5 次失败

日志分析:
  bash security_cases.sh log <access.log>

系统巡检:
  bash security_cases.sh check [输出目录]
  部分检查需要 root 权限

文件完整性:
  bash security_cases.sh integrity --generate <目录> [输出文件]
  bash security_cases.sh integrity --verify <目录> <基准文件>

示例:
  bash security_cases.sh demo
  bash security_cases.sh ssh /var/log/auth.log 10
  bash security_cases.sh check /tmp/report
  bash security_cases.sh integrity --generate /etc/ config.baseline

⚠️  所有工具仅限在授权环境中使用
EOF
}

# ============================================================
# 主入口
# ============================================================

main() {
    if [ $# -eq 0 ]; then
        run_demo
        return
    fi

    local cmd="$1"
    shift

    case "$cmd" in
        help|-h|--help)
            usage
            ;;
        demo)
            run_demo
            ;;
        ssh)
            ssh_login_monitor "$@"
            ;;
        log)
            log_analyzer "$@"
            ;;
        check)
            system_security_check "$@"
            ;;
        integrity)
            file_integrity_check "$@"
            ;;
        gen-samples)
            local out_dir="${1:-/tmp/sample_logs}"
            generate_sample_logs "$out_dir"
            success "示例日志已生成: $out_dir"
            ;;
        *)
            error "未知命令: $cmd"
            echo ""
            usage
            exit 1
            ;;
    esac
}

main "$@"
