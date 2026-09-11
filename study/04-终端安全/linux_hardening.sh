#!/bin/bash
# ============================================================
# Linux 安全加固脚本
# 版本：v1.0
# 适用系统：CentOS 7+ / RHEL 7+ / Ubuntu 18.04+ / Debian 10+
# 运行要求：以 root 身份运行
# ============================================================

# ============================================================
# 初始化部分
# ============================================================

# 检查是否为 root 用户
if [ "$(id -u)" -ne 0 ]; then
    echo "[-] 错误：请以 root 身份运行此脚本！"
    echo "[-] 请使用 sudo 或 su 切换到 root 用户后再运行"
    exit 1
fi

# 彩色输出定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[1;30m'
NC='\033[0m' # No Color

# 日志函数
LOG_FILE="/var/log/hardening_log_$(date +'%Y%m%d_%H%M%S').log"
echo "=== Linux 安全加固日志 - $(date) ===" > "$LOG_FILE"

log_info() {
    echo -e "${GREEN}[+]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" >> "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[-]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >> "$LOG_FILE"
}

log_skip() {
    echo -e "${GRAY}[=]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SKIP] $1" >> "$LOG_FILE"
}

# 检测系统发行版
detect_os() {
    if [ -f /etc/redhat-release ]; then
        OS="centos"
        OS_VERSION=$(cat /etc/redhat-release | grep -oP '\d+\.\d+' | head -1 | cut -d. -f1)
    elif [ -f /etc/lsb-release ]; then
        OS="ubuntu"
        OS_VERSION=$(grep DISTRIB_RELEASE /etc/lsb-release | cut -d= -f2 | cut -d. -f1)
    elif [ -f /etc/debian_version ]; then
        OS="debian"
        OS_VERSION=$(cat /etc/debian_version | cut -d. -f1)
    else
        log_error "无法识别的操作系统"
        exit 1
    fi
    log_info "检测到操作系统：$OS (版本: $OS_VERSION)"
}

# 备份函数
backup_file() {
    local file="$1"
    if [ -f "$file" ]; then
        local backup="${file}.bak.$(date +'%Y%m%d_%H%M%S')"
        cp -p "$file" "$backup"
        log_info "已备份 $file 到 $backup"
    fi
}

# 脚本开始
echo -e "${CYAN}"
echo "============================================================"
echo "  Linux 系统安全加固脚本 v1.0"
echo "============================================================"
echo -e "${NC}"
echo ""

detect_os
log_info "日志文件路径：$LOG_FILE"

# ============================================================
# 一、系统更新
# ============================================================

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}一、系统更新${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

update_system() {
    log_info "正在更新系统软件包..."
    
    if [ "$OS" = "centos" ]; then
        # CentOS/RHEL 使用 yum/dnf
        if command -v dnf &> /dev/null; then
            dnf update -y >> "$LOG_FILE" 2>&1
            log_info "已使用 dnf 更新系统软件包"
        else
            yum update -y >> "$LOG_FILE" 2>&1
            log_info "已使用 yum 更新系统软件包"
        fi
        
        # 安装 EPEL 源（额外软件包）
        if ! rpm -q epel-release &> /dev/null; then
            log_info "正在安装 EPEL 源..."
            yum install -y epel-release >> "$LOG_FILE" 2>&1
            log_info "EPEL 源安装完成"
        fi
        
    elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # Debian/Ubuntu 使用 apt
        apt-get update -y >> "$LOG_FILE" 2>&1
        apt-get upgrade -y >> "$LOG_FILE" 2>&1
        apt-get dist-upgrade -y >> "$LOG_FILE" 2>&1
        log_info "已使用 apt 更新系统软件包"
        
        # 自动移除不需要的包
        apt-get autoremove -y >> "$LOG_FILE" 2>&1
        log_info "已清理不需要的软件包"
    fi
    
    log_info "系统更新完成"
}

# 执行系统更新
update_system

# ============================================================
# 二、账户安全配置
# ============================================================

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}二、账户安全配置${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# 2.1 密码策略配置
log_info "正在配置密码策略..."

if [ "$OS" = "centos" ]; then
    # CentOS/RHEL 密码策略
    backup_file /etc/security/pwquality.conf
    backup_file /etc/login.defs
    
    # 安装密码质量检查库
    yum install -y libpwquality >> "$LOG_FILE" 2>&1
    
    # 配置 pwquality.conf
    cat > /etc/security/pwquality.conf << 'EOF'
# 密码最小长度
minlen = 14

# 数字字符最少个数（负值表示最少个数）
dcredit = -1

# 大写字母最少个数
ucredit = -1

# 小写字母最少个数
lcredit = -1

# 特殊字符最少个数
ocredit = -1

# 最多连续相同字符数
maxrepeat = 3

# 最多同类字符连续数
maxclassrepeat = 4

# 字典检查
dictcheck = 1

# 用户名字符串检查
usercheck = 1

# 几何序列检查（如 qwerty、12345）
gecoscheck = 1
EOF
    log_info "密码复杂度策略已配置（pwquality.conf）"
    
    # 配置 PAM 密码策略
    backup_file /etc/pam.d/system-auth
    backup_file /etc/pam.d/password-auth
    
    # 修改 system-auth
    sed -i 's/password    requisite     pam_pwquality.so try_first_pass local_users_only/password    requisite     pam_pwquality.so try_first_pass local_users_only retry=3 authtok_type=/' /etc/pam.d/system-auth
    sed -i 's/password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok/password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok remember=24/' /etc/pam.d/system-auth
    
    # 修改 password-auth
    sed -i 's/password    requisite     pam_pwquality.so try_first_pass local_users_only/password    requisite     pam_pwquality.so try_first_pass local_users_only retry=3 authtok_type=/' /etc/pam.d/password-auth
    sed -i 's/password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok/password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok remember=24/' /etc/pam.d/password-auth
    
    log_info "PAM 密码策略已配置（密码历史 24 个）"
    
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    # Ubuntu/Debian 密码策略
    backup_file /etc/pam.d/common-password
    backup_file /etc/login.defs
    
    # 安装密码质量检查库
    apt-get install -y libpam-pwquality >> "$LOG_FILE" 2>&1
    
    # 配置 common-password
    sed -i 's/pam_pwquality.so retry=3/pam_pwquality.so retry=3 minlen=14 dcredit=-1 ucredit=-1 lcredit=-1 ocredit=-1 maxrepeat=3/' /etc/pam.d/common-password
    
    # 配置密码历史
    if ! grep -q "pam_unix.so.*remember=" /etc/pam.d/common-password; then
        sed -i 's/pam_unix.so obscure sha512/pam_unix.so obscure sha512 remember=24/' /etc/pam.d/common-password
    fi
    
    log_info "PAM 密码策略已配置"
fi

# 配置 login.defs 密码有效期
backup_file /etc/login.defs
sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS   90/' /etc/login.defs
sed -i 's/^PASS_MIN_DAYS.*/PASS_MIN_DAYS   1/' /etc/login.defs
sed -i 's/^PASS_MIN_LEN.*/PASS_MIN_LEN    14/' /etc/login.defs
sed -i 's/^PASS_WARN_AGE.*/PASS_WARN_AGE   7/' /etc/login.defs
log_info "密码有效期已配置（最长 90 天，最短 1 天，提前 7 天警告）"

# 2.2 账户锁定策略
log_info "正在配置账户锁定策略..."

if [ "$OS" = "centos" ]; then
    backup_file /etc/pam.d/system-auth
    backup_file /etc/pam.d/password-auth
    
    # 在 system-auth 中添加 pam_faillock
    if ! grep -q "pam_faillock.so" /etc/pam.d/system-auth; then
        # 在 auth 部分添加 faillock
        sed -i '/^auth        required      pam_env.so/a auth        required      pam_faillock.so preauth silent deny=5 unlock_time=1800 fail_interval=900' /etc/pam.d/system-auth
        sed -i '/^auth        sufficient    pam_unix.so/a auth        [default=die] pam_faillock.so authfail deny=5 unlock_time=1800 fail_interval=900' /etc/pam.d/system-auth
        sed -i '/^account     required      pam_unix.so/i account     required      pam_faillock.so' /etc/pam.d/system-auth
        
        # 在 password-auth 中添加 faillock
        sed -i '/^auth        required      pam_env.so/a auth        required      pam_faillock.so preauth silent deny=5 unlock_time=1800 fail_interval=900' /etc/pam.d/password-auth
        sed -i '/^auth        sufficient    pam_unix.so/a auth        [default=die] pam_faillock.so authfail deny=5 unlock_time=1800 fail_interval=900' /etc/pam.d/password-auth
        sed -i '/^account     required      pam_unix.so/i account     required      pam_faillock.so' /etc/pam.d/password-auth
    fi
    log_info "账户锁定策略已配置（5 次失败锁定 30 分钟）"
    
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    backup_file /etc/pam.d/common-auth
    
    # 使用 pam_tally2 或 pam_faillock
    if ! grep -q "pam_tally2.so" /etc/pam.d/common-auth; then
        sed -i '1i auth    required    pam_tally2.so deny=5 unlock_time=1800 onerr=fail' /etc/pam.d/common-auth
    fi
    log_info "账户锁定策略已配置（5 次失败锁定 30 分钟）"
fi

# 2.3 禁用不必要的系统账户
log_info "正在禁用不必要的系统账户..."

# 列出需要禁用的账户（根据实际情况调整）
disable_users=("games" "gopher" "ftp" "nobody" "uucp" "operator" "news" "lp" "sync" "shutdown" "halt")

for user in "${disable_users[@]}"; do
    if id "$user" &>/dev/null; then
        # 检查用户是否有进程在运行
        if pgrep -u "$user" &>/dev/null; then
            log_warn "用户 $user 有进程运行，跳过禁用"
        else
            usermod -s /sbin/nologin "$user" 2>/dev/null
            passwd -l "$user" 2>/dev/null
            log_info "已禁用账户：$user"
        fi
    else
        log_skip "账户不存在：$user"
    fi
done

# 2.4 检查空密码账户
log_info "正在检查空密码账户..."
empty_pass_users=$(awk -F: '($2 == "" ) { print $1 }' /etc/shadow)
if [ -n "$empty_pass_users" ]; then
    log_warn "发现空密码账户：$empty_pass_users"
    for user in $empty_pass_users; do
        passwd -l "$user" 2>/dev/null
        log_info "已锁定空密码账户：$user"
    done
else
    log_info "未发现空密码账户"
fi

# 2.5 检查 UID 为 0 的账户
log_info "正在检查 UID 为 0 的账户..."
uid0_users=$(awk -F: '($3 == 0) { print $1 }' /etc/passwd)
if [ "$uid0_users" != "root" ]; then
    log_warn "发现多个 UID=0 的账户：$uid0_users"
else
    log_info "只有 root 用户的 UID 为 0，正常"
fi

# ============================================================
# 三、SSH 安全配置
# ============================================================

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}三、SSH 安全配置${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

log_info "正在配置 SSH 安全..."

# 检查 SSH 服务是否安装
if ! command -v sshd &> /dev/null; then
    log_warn "SSH 服务未安装，跳过 SSH 安全配置"
else
    backup_file /etc/ssh/sshd_config
    
    # 3.1 禁止 root 直接登录
    sed -i 's/^#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    log_info "已禁止 root 用户直接 SSH 登录"
    
    # 3.2 禁用空密码
    sed -i 's/^#PermitEmptyPasswords.*/PermitEmptyPasswords no/' /etc/ssh/sshd_config
    sed -i 's/^PermitEmptyPasswords.*/PermitEmptyPasswords no/' /etc/ssh/sshd_config
    log_info "已禁用空密码登录"
    
    # 3.3 禁用密码认证（启用密钥认证后建议开启）
    # 注意：确保已配置密钥登录后再启用此选项
    # sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
    # sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
    # log_info "已禁用密码认证（仅允许密钥认证）"
    log_warn "密码认证保持启用（请配置密钥登录后手动禁用）"
    
    # 3.4 禁用 Challenge-Response 认证
    sed -i 's/^#ChallengeResponseAuthentication.*/ChallengeResponseAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/^ChallengeResponseAuthentication.*/ChallengeResponseAuthentication no/' /etc/ssh/sshd_config
    log_info "已禁用 Challenge-Response 认证"
    
    # 3.5 禁用 GSSAPI 认证（如不需要）
    sed -i 's/^#GSSAPIAuthentication.*/GSSAPIAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/^GSSAPIAuthentication.*/GSSAPIAuthentication no/' /etc/ssh/sshd_config
    log_info "已禁用 GSSAPI 认证"
    
    # 3.6 禁用 X11 转发
    sed -i 's/^#X11Forwarding.*/X11Forwarding no/' /etc/ssh/sshd_config
    sed -i 's/^X11Forwarding.*/X11Forwarding no/' /etc/ssh/sshd_config
    log_info "已禁用 X11 转发"
    
    # 3.7 配置最大认证尝试次数
    sed -i 's/^#MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config
    sed -i 's/^MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config
    log_info "最大认证尝试次数设置为 3"
    
    # 3.8 配置最大会话数
    sed -i 's/^#MaxSessions.*/MaxSessions 5/' /etc/ssh/sshd_config
    sed -i 's/^MaxSessions.*/MaxSessions 5/' /etc/ssh/sshd_config
    log_info "最大会话数设置为 5"
    
    # 3.9 客户端存活配置
    sed -i 's/^#ClientAliveInterval.*/ClientAliveInterval 300/' /etc/ssh/sshd_config
    sed -i 's/^ClientAliveInterval.*/ClientAliveInterval 300/' /etc/ssh/sshd_config
    sed -i 's/^#ClientAliveCountMax.*/ClientAliveCountMax 2/' /etc/ssh/sshd_config
    sed -i 's/^ClientAliveCountMax.*/ClientAliveCountMax 2/' /etc/ssh/sshd_config
    log_info "客户端存活配置已设置（300秒间隔，2次后断开）"
    
    # 3.10 禁用 TCP 转发（如不需要）
    sed -i 's/^#AllowTcpForwarding.*/AllowTcpForwarding no/' /etc/ssh/sshd_config
    sed -i 's/^AllowTcpForwarding.*/AllowTcpForwarding no/' /etc/ssh/sshd_config
    log_info "已禁用 TCP 转发"
    
    # 3.11 禁用代理转发
    sed -i 's/^#AllowAgentForwarding.*/AllowAgentForwarding no/' /etc/ssh/sshd_config
    sed -i 's/^AllowAgentForwarding.*/AllowAgentForwarding no/' /etc/ssh/sshd_config
    log_info "已禁用代理转发"
    
    # 3.12 设置登录横幅（可选）
    echo "*********************************************************" > /etc/ssh/banner
    echo "*  本系统为授权用户使用，未经授权禁止访问。             *" >> /etc/ssh/banner
    echo "*  所有操作将被记录和监控。                             *" >> /etc/ssh/banner
    echo "*********************************************************" >> /etc/ssh/banner
    sed -i 's/^#Banner.*/Banner \/etc\/ssh\/banner/' /etc/ssh/sshd_config
    sed -i 's/^Banner.*/Banner \/etc\/ssh\/banner/' /etc/ssh/sshd_config
    log_info "已配置 SSH 登录横幅"
    
    # 3.13 限制 SSH 用户（可选，取消注释启用，按需修改用户名）
    # echo "AllowUsers admin user1 user2" >> /etc/ssh/sshd_config
    # log_info "已限制允许 SSH 登录的用户"
    
    # 验证 SSH 配置
    if sshd -t >> "$LOG_FILE" 2>&1; then
        log_info "SSH 配置文件语法验证通过"
    else
        log_error "SSH 配置文件语法错误，请检查配置"
    fi
    
    # 重启 SSH 服务
    if [ "$OS" = "centos" ]; then
        systemctl restart sshd
    else
        systemctl restart ssh
    fi
    log_info "SSH 服务已重启，新配置已生效"
fi

# ============================================================
# 四、防火墙配置
# ============================================================

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}四、防火墙配置${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

configure_firewall() {
    log_info "正在配置防火墙..."
    
    if [ "$OS" = "centos" ]; then
        # CentOS/RHEL 使用 firewalld
        if systemctl is-active --quiet firewalld; then
            log_info "firewalld 已在运行，进行配置..."
            
            # 设置默认区域
            firewall-cmd --set-default-zone=public --permanent >> "$LOG_FILE" 2>&1
            
            # 允许 SSH（确保远程连接不中断）
            firewall-cmd --permanent --add-service=ssh >> "$LOG_FILE" 2>&1
            log_info "已允许 SSH 服务"
            
            # 允许 HTTP/HTTPS（根据需要启用）
            # firewall-cmd --permanent --add-service=http
            # firewall-cmd --permanent --add-service=https
            # log_info "已允许 HTTP/HTTPS 服务"
            
            # 阻止 ICMP（Ping）- 可选
            # firewall-cmd --permanent --add-icmp-block=echo-request
            # log_info "已阻止 ICMP Echo 请求"
            
            # 重载规则
            firewall-cmd --reload >> "$LOG_FILE" 2>&1
            log_info "firewalld 规则已重载"
            
            # 显示当前配置
            log_info "当前防火墙配置："
            firewall-cmd --list-all >> "$LOG_FILE" 2>&1
            
        else
            log_warn "firewalld 未运行，正在启动..."
            systemctl start firewalld
            systemctl enable firewalld
            log_info "firewalld 已启动并设置为开机自启"
            # 递归调用进行配置
            configure_firewall
        fi
        
    elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # Ubuntu/Debian 使用 ufw
        if command -v ufw &> /dev/null; then
            log_info "正在配置 ufw 防火墙..."
            
            # 重置 ufw 规则
            ufw --force reset >> "$LOG_FILE" 2>&1
            
            # 默认策略
            ufw default deny incoming >> "$LOG_FILE" 2>&1
            ufw default allow outgoing >> "$LOG_FILE" 2>&1
            log_info "已设置默认策略：入站拒绝，出站允许"
            
            # 允许 SSH
            ufw allow ssh >> "$LOG_FILE" 2>&1
            log_info "已允许 SSH 服务"
            
            # 限制 SSH 连接频率（防暴力破解）
            ufw limit ssh/tcp >> "$LOG_FILE" 2>&1
            log_info "已启用 SSH 速率限制（防暴力破解）"
            
            # 允许 HTTP/HTTPS（根据需要启用）
            # ufw allow http
            # ufw allow https
            # log_info "已允许 HTTP/HTTPS 服务"
            
            # 启用 ufw
            ufw --force enable >> "$LOG_FILE" 2>&1
            log_info "ufw 防火墙已启用"
            
            # 显示状态
            ufw status verbose >> "$LOG_FILE" 2>&1
            
        else
            log_warn "ufw 未安装，正在安装..."
            apt-get install -y ufw >> "$LOG_FILE" 2>&1
            configure_firewall
        fi
    fi
    
    log_info "防火墙配置完成"
}

configure_firewall

# ============================================================
# 五、文件权限加固
# ============================================================

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}五、文件权限加固${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

log_info "正在加固文件权限..."

# 5.1 设置关键配置文件权限
log_info "正在设置关键配置文件权限..."

# /etc/passwd - 所有用户可读，仅 root 可写
chmod 644 /etc/passwd
chown root:root /etc/passwd
log_info "已设置 /etc/passwd 权限为 644"

# /etc/shadow - 仅 root 可读写
chmod 600 /etc/shadow
chown root:root /etc/shadow
log_info "已设置 /etc/shadow 权限为 600"

# /etc/group - 所有用户可读，仅 root 可写
chmod 644 /etc/group
chown root:root /etc/group
log_info "已设置 /etc/group 权限为 644"

# /etc/gshadow - 仅 root 可读写
chmod 600 /etc/gshadow
chown root:root /etc/gshadow
log_info "已设置 /etc/gshadow 权限为 600"

# /etc/sudoers - 仅 root 可读写
chmod 440 /etc/sudoers
chown root:root /etc/sudoers
log_info "已设置 /etc/sudoers 权限为 440"

# SSH 配置文件
chmod 644 /etc/ssh/sshd_config
chown root:root /etc/ssh/sshd_config
log_info "已设置 /etc/ssh/sshd_config 权限为 644"

# /etc/crontab
chmod 600 /etc/crontab
chown root:root /etc/crontab
log_info "已设置 /etc/crontab 权限为 600"

# cron 目录
chmod 700 /etc/cron.d
chmod 700 /etc/cron.hourly
chmod 700 /etc/cron.daily
chmod 700 /etc/cron.weekly
chmod 700 /etc/cron.monthly
chown -R root:root /etc/cron.*
log_info "已设置 cron 目录权限为 700"

# 5.2 设置 umask
log_info "正在配置全局 umask..."

backup_file /etc/profile
if ! grep -q "umask 027" /etc/profile; then
    echo "umask 027" >> /etc/profile
    log_info "已在 /etc/profile 中设置 umask 为 027"
else
    log_info "umask 027 已在 /etc/profile 中设置"
fi

# 也在 bashrc 中设置
if [ -f /etc/bashrc ]; then
    backup_file /etc/bashrc
    if ! grep -q "umask 027" /etc/bashrc; then
        echo "umask 027" >> /etc/bashrc
        log_info "已在 /etc/bashrc 中设置 umask 为 027"
    fi
fi

# 5.3 查找危险的 SUID/SGID 文件
log_info "正在查找危险的 SUID/SGID 文件..."

# 查找所有 SUID 文件
suid_files=$(find / -perm -4000 -type f 2>/dev/null)
log_info "SUID 文件列表（共 $(echo "$suid_files" | wc -l) 个）："
echo "$suid_files" >> "$LOG_FILE"

# 查找所有 SGID 文件
sgid_files=$(find / -perm -2000 -type f 2>/dev/null)
log_info "SGID 文件列表（共 $(echo "$sgid_files" | wc -l) 个）："
echo "$sgid_files" >> "$LOG_FILE"

# 查找可写的 SUID 文件（高危）
writable_suid=$(find / -perm -4000 -writable -type f 2>/dev/null)
if [ -n "$writable_suid" ]; then
    log_warn "发现可写的 SUID 文件（高危）：$writable_suid"
else
    log_info "未发现可写的 SUID 文件"
fi

# 5.4 查找无属主的文件
log_info "正在查找无属主的文件..."
nouser_files=$(find / -xdev -nouser 2>/dev/null | head -20)
nogroup_files=$(find / -xdev -nogroup 2>/dev/null | head -20)

if [ -n "$nouser_files" ]; then
    log_warn "发现无属主的文件（前20个）："
    echo "$nouser_files" >> "$LOG_FILE"
else
    log_info "未发现无属主的文件"
fi

# ============================================================
# 六、审计规则配置
# ============================================================

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}六、审计规则配置${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

log_info "正在配置系统审计..."

# 安装 auditd
if ! command -v auditd &> /dev/null; then
    log_info "正在安装 auditd..."
    if [ "$OS" = "centos" ]; then
        yum install -y audit >> "$LOG_FILE" 2>&1
    else
        apt-get install -y auditd >> "$LOG_FILE" 2>&1
    fi
    log_info "auditd 安装完成"
fi

# 启动并启用 auditd
systemctl start auditd
systemctl enable auditd
log_info "auditd 服务已启动并设置为开机自启"

# 配置审计规则
backup_file /etc/audit/rules.d/audit.rules

cat > /etc/audit/rules.d/audit.rules << 'EOF'
# ============================================================
# 系统审计规则配置
# 参考：CIS Benchmarks、STIG 等安全标准
# ============================================================

# 1. 身份管理 - 用户/组/密码变更
-w /etc/passwd -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/gshadow -p wa -k identity
-w /etc/sudoers -p wa -k sudo_changes
-w /etc/sudoers.d/ -p wa -k sudo_changes

# 2. 登录和认证
-w /var/log/faillog -p wa -k logins
-w /var/log/lastlog -p wa -k logins
-w /var/log/tallylog -p wa -k logins

# 3. 系统时间修改
-a always,exit -F arch=b64 -S adjtimex -S settimeofday -k time_change
-a always,exit -F arch=b32 -S adjtimex -S settimeofday -S stime -k time_change
-a always,exit -F arch=b64 -S clock_settime -k time_change
-a always,exit -F arch=b32 -S clock_settime -k time_change

# 4. 网络配置修改
-a always,exit -F arch=b64 -S sethostname -S setdomainname -k network_config
-w /etc/issue -p wa -k system_language
-w /etc/issue.net -p wa -k system_language
-w /etc/hosts -p wa -k hosts_file
-w /etc/sysconfig/network -p wa -k network_config
-w /etc/network/ -p wa -k network_config

# 5. 防火墙配置变更
-w /etc/sysconfig/iptables -p wa -k firewall_changes
-w /etc/firewalld/ -p wa -k firewall_changes
-w /etc/ufw/ -p wa -k firewall_changes

# 6. PAM 配置变更
-w /etc/pam.d/ -p wa -k pam_changes
-w /etc/security/ -p wa -k security_config

# 7. SSH 配置变更
-w /etc/ssh/sshd_config -p wa -k ssh_config
-w /etc/ssh/ssh_config -p wa -k ssh_config

# 8. 计划任务变更
-w /etc/crontab -p wa -k cron_changes
-w /etc/cron.d/ -p wa -k cron_changes
-w /etc/cron.hourly/ -p wa -k cron_changes
-w /etc/cron.daily/ -p wa -k cron_changes
-w /etc/cron.weekly -p wa -k cron_changes
-w /etc/cron.monthly/ -p wa -k cron_changes
-w /var/spool/cron/ -p wa -k cron_changes
-w /var/spool/cron/crontabs/ -p wa -k cron_changes

# 9. 系统可执行文件变更
-w /bin/ -p wa -k bin_changes
-w /sbin/ -p wa -k sbin_changes
-w /usr/bin/ -p wa -k usr_bin_changes
-w /usr/sbin/ -p wa -k usr_sbin_changes
-w /usr/local/bin/ -p wa -k usr_local_bin_changes
-w /usr/local/sbin/ -p wa -k usr_local_sbin_changes

# 10. 重要配置文件
-w /etc/profile -p wa -k profile_changes
-w /etc/bashrc -p wa -k profile_changes
-w /etc/profile.d/ -p wa -k profile_changes
-w /etc/rc.d/init.d/ -p wa -k init_changes
-w /etc/init.d/ -p wa -k init_changes
-w /etc/systemd/ -p wa -k systemd_changes

# 11. 内核模块加载/卸载
-w /sbin/insmod -p x -k module_load
-w /sbin/modprobe -p x -k module_load
-w /sbin/rmmod -p x -k module_load
-a always,exit -F arch=b64 -S init_module -S delete_module -k module_changes
-a always,exit -F arch=b32 -S init_module -S delete_module -k module_changes

# 12. 文件系统挂载
-a always,exit -F arch=b64 -S mount -S umount2 -k mount_changes
-a always,exit -F arch=b32 -S mount -S umount2 -k mount_changes

# 13. 敏感访问 - root 用户执行
-a always,exit -F arch=b64 -S execve -F uid=0 -F auid>=1000 -F auid!=4294967295 -k root_exec
-a always,exit -F arch=b32 -S execve -F uid=0 -F auid>=1000 -F auid!=4294967295 -k root_exec

# 14. 进程创建（大量日志，按需启用）
# -a always,exit -F arch=b64 -S execve -k exec
# -a always,exit -F arch=b32 -S execve -k exec

# 15. 失败的文件访问
-a always,exit -F arch=b64 -S open -F exit=-EACCES -k access_denied
-a always,exit -F arch=b64 -S open -F exit=-EPERM -k access_denied
-a always,exit -F arch=b32 -S open -F exit=-EACCES -k access_denied
-a always,exit -F arch=b32 -S open -F exit=-EPERM -k access_denied

# ============================================================
# 缓冲区和失败处理配置
# ============================================================

# 设置缓冲区大小
-b 8192

# 失败时的处理方式（0=忽略 1=printk 2=panic）
-f 1

# 忽略错误（继续加载规则）
-i
EOF

log_info "审计规则已配置（/etc/audit/rules.d/audit.rules）"

# 重启 auditd 加载规则
systemctl restart auditd
log_info "auditd 已重启，新规则已加载"

# 配置日志轮转
if [ -f /etc/audit/auditd.conf ]; then
    backup_file /etc/audit/auditd.conf
    sed -i 's/^num_logs.*/num_logs = 5/' /etc/audit/auditd.conf
    sed -i 's/^max_log_file.*/max_log_file = 100/' /etc/audit/auditd.conf
    sed -i 's/^max_log_file_action.*/max_log_file_action = ROTATE/' /etc/audit/auditd.conf
    log_info "审计日志轮转已配置（保留 5 份，每份 100MB）"
fi

# ============================================================
# 七、内核参数加固
# ============================================================

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}七、内核参数加固${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

log_info "正在加固内核参数..."

backup_file /etc/sysctl.conf

# 配置 sysctl.conf
cat > /etc/sysctl.d/99-security.conf << 'EOF'
# ============================================================
# 内核安全加固参数
# 参考：CIS Benchmarks、KMP、STIG 等安全标准
# ============================================================

# ============================================================
# 网络安全参数
# ============================================================

# 1. IP 欺骗防护 - 启用反向路径过滤
# 防止 IP 欺骗攻击，验证数据包的源地址是否可达
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# 2. 禁用 ICMP 重定向接受
# 防止 ICMP 重定向攻击
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0

# 3. 禁用安全 ICMP 重定向
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0

# 4. 禁用 ICMP 重定向发送
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# 5. 忽略 ICMP 广播请求（防止 Smurf 攻击）
net.ipv4.icmp_echo_ignore_broadcasts = 1

# 6. 忽略 bogus ICMP 错误响应
net.ipv4.icmp_ignore_bogus_error_responses = 1

# 7. 启用 SYN Cookie（防止 SYN Flood 攻击）
net.ipv4.tcp_syncookies = 1

# 8. 增大 SYN 队列长度
net.ipv4.tcp_max_syn_backlog = 2048

# 9. 减少 SYN-ACK 重试次数
net.ipv4.tcp_synack_retries = 2

# 10. 减少 SYN 重试次数
net.ipv4.tcp_syn_retries = 2

# 11. 禁用源路由
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv6.conf.default.accept_source_route = 0

# 12. 启用 TCP RFC1337 防护（防止 time-wait 暗杀攻击）
net.ipv4.tcp_rfc1337 = 1

# 13. 禁用 IP 转发（如不需要路由功能）
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# 14. 启用 TCP SYN 洪水保护
net.ipv4.tcp_syncookies = 1

# 15. 增加本地端口范围
net.ipv4.ip_local_port_range = 1024 65535

# 16. 减少 TCP keepalive 时间
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 3

# 17. 启用 timestamps（防止序列号预测攻击）
net.ipv4.tcp_timestamps = 1

# ============================================================
# 文件系统安全参数
# ============================================================

# 18. 禁止硬链接到非所有者的文件
fs.protected_hardlinks = 1

# 19. 禁止软链接到非所有者的文件
fs.protected_symlinks = 1

# 20. 限制核心转储
fs.suid_dumpable = 0
kernel.core_uses_pid = 1

# ============================================================
# 内核安全参数
# ============================================================

# 21. 启用地址空间随机化（ASLR）
kernel.randomize_va_space = 2

# 22. 禁用 Magic SysRq 键
kernel.sysrq = 0

# 23. 禁用 kptr_restrict（隐藏内核指针）
kernel.kptr_restrict = 2

# 24. 限制 dmesg 访问
kernel.dmesg_restrict = 1

# 25. 禁用 ftrace 调试
# kernel.ftrace_enabled = 0

# 26. 限制 ptrace 调试
kernel.yama.ptrace_scope = 1

# ============================================================
# 内存管理参数
# ============================================================

# 27. 启用内存超额使用（合理配置）
vm.overcommit_memory = 1

# 28. 减少 swappiness（减少使用交换分区）
vm.swappiness = 10

# 29. 增加文件描述符限制
fs.file-max = 65535

# ============================================================
# IPv6 安全（如不需要 IPv6，建议禁用）
# ============================================================

# 30. 禁用 IPv6（如不需要）
# net.ipv6.conf.all.disable_ipv6 = 1
# net.ipv6.conf.default.disable_ipv6 = 1
# net.ipv6.conf.lo.disable_ipv6 = 1
EOF

log_info "内核安全参数已配置（/etc/sysctl.d/99-security.conf）"

# 应用内核参数
sysctl -p /etc/sysctl.d/99-security.conf >> "$LOG_FILE" 2>&1
log_info "内核参数已应用"

# ============================================================
# 八、服务加固
# ============================================================

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}八、服务加固${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

log_info "正在加固系统服务..."

# 定义需要禁用的服务
disable_services=(
    "avahi-daemon"        # 零配置网络发现
    "cups"                # 打印服务
    "bluetooth"           # 蓝牙
    "rpcbind"             # RPC 绑定服务
    "nfs"                 # NFS 服务
    "nfs-server"          # NFS 服务器
    "vsftpd"              # FTP 服务
    "telnet"              # Telnet 服务
    "rsh"                 # RSH 服务
    "rexec"               # Rexec 服务
    "autofs"              # 自动挂载
    "abrtd"               # 自动 bug 报告
    "rhnsd"               # Red Hat 网络服务
    "kdump"               # 内核崩溃转储
    "pcscd"               # 智能卡服务
    "gpm"                 # 鼠标服务（文本模式）
    "postfix"             # 邮件服务（如不需要）
    "sendmail"            # 邮件服务（如不需要）
)

for svc in "${disable_services[@]}"; do
    if systemctl list-unit-files | grep -q "^$svc.service"; then
        if systemctl is-active --quiet "$svc"; then
            systemctl stop "$svc" 2>/dev/null
            log_info "已停止服务：$svc"
        fi
        systemctl disable "$svc" 2>/dev/null
        log_info "已禁用服务：$svc"
    else
        log_skip "服务不存在：$svc"
    fi
done

log_info "服务加固完成"

# ============================================================
# 九、安全工具安装
# ============================================================

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}九、安全工具安装${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

log_info "正在安装安全工具..."

# 9.1 安装 fail2ban（防止暴力破解）
log_info "正在安装 fail2ban..."

if [ "$OS" = "centos" ]; then
    yum install -y fail2ban fail2ban-systemd >> "$LOG_FILE" 2>&1
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get install -y fail2ban >> "$LOG_FILE" 2>&1
fi

# 配置 fail2ban SSH 防护
cat > /etc/fail2ban/jail.local << 'EOF'
# Fail2Ban 本地配置
[DEFAULT]
# 封禁时间（秒）- 1小时
bantime = 3600

# 查找时间窗口（秒）- 10分钟
findtime = 600

# 最大尝试次数
maxretry = 3

# 忽略的 IP（白名单）
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

# 调整日志路径（CentOS 不同）
if [ "$OS" = "centos" ]; then
    sed -i 's|/var/log/auth.log|/var/log/secure|' /etc/fail2ban/jail.local
fi

# 启动 fail2ban
systemctl start fail2ban
systemctl enable fail2ban
log_info "fail2ban 已安装并启动（SSH 防护：3 次失败封禁 1 小时）"

# 9.2 安装 rkhunter（Rootkit 检测）
log_info "正在安装 rkhunter..."

if [ "$OS" = "centos" ]; then
    yum install -y rkhunter >> "$LOG_FILE" 2>&1
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get install -y rkhunter >> "$LOG_FILE" 2>&1
fi

# 更新 rkhunter 数据库
rkhunter --update >> "$LOG_FILE" 2>&1
rkhunter --propupd >> "$LOG_FILE" 2>&1
log_info "rkhunter 已安装（Rootkit 检测工具）"

# 9.3 安装 chkrootkit
log_info "正在安装 chkrootkit..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get install -y chkrootkit >> "$LOG_FILE" 2>&1
    log_info "chkrootkit 已安装"
else
    log_info "CentOS 请手动安装 chkrootkit（EPEL 源）"
fi

# 9.4 安装 AIDE（文件完整性检查）
log_info "正在安装 AIDE..."
if [ "$OS" = "centos" ]; then
    yum install -y aide >> "$LOG_FILE" 2>&1
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get install -y aide >> "$LOG_FILE" 2>&1
fi

# 初始化 AIDE 数据库（首次运行时间较长）
# aide --init >> "$LOG_FILE" 2>&1
# mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
log_info "AIDE 已安装（文件完整性检查工具）"
log_warn "请手动运行 aide --init 初始化数据库"

log_info "安全工具安装完成"

# ============================================================
# 十、其他安全加固
# ============================================================

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}十、其他安全加固${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# 10.1 限制 su 命令使用
log_info "正在限制 su 命令使用..."
if ! grep -q "pam_wheel.so" /etc/pam.d/su; then
    backup_file /etc/pam.d/su
    sed -i 's/#auth\s*required\s*pam_wheel.so/auth            required        pam_wheel.so use_uid/' /etc/pam.d/su
    log_info "已限制 su 命令仅 wheel 组成员可使用"
else
    log_info "su 限制已配置"
fi

# 10.2 配置 sudo 日志
log_info "正在配置 sudo 日志..."
backup_file /etc/sudoers
if ! grep -q "logfile" /etc/sudoers; then
    echo "Defaults logfile=\"/var/log/sudo.log\"" >> /etc/sudoers
    echo "Defaults log_input, log_output" >> /etc/sudoers
    log_info "sudo 日志已配置（/var/log/sudo.log）"
fi

# 10.3 禁用 USB 存储（可选，根据需要启用）
# 默认禁用，如需启用请取消下面的注释
# log_info "正在禁用 USB 存储设备..."
# echo "install usb-storage /bin/true" > /etc/modprobe.d/disable-usb-storage.conf
# log_info "USB 存储设备已禁用"
log_warn "USB 存储禁用默认关闭（如需启用请取消 10.3 段的注释）"

# 10.4 配置历史命令记录和时间戳
log_info "正在配置命令历史记录..."
backup_file /etc/profile

if ! grep -q "HISTTIMEFORMAT" /etc/profile; then
    cat >> /etc/profile << 'EOF'

# 命令历史配置
HISTTIMEFORMAT="%F %T "
export HISTTIMEFORMAT
HISTSIZE=10000
HISTFILESIZE=10000
# 记录到 syslog
export PROMPT_COMMAND='history -a; logger -t bash -p local1.info "$USER: $(history 1 | { read x cmd; echo "$cmd"; })"'
EOF
    log_info "命令历史记录已配置（含时间戳，记录到 syslog）"
fi

# 10.5 限制核心转储
log_info "正在限制核心转储..."
backup_file /etc/security/limits.conf
if ! grep -q "* hard core 0" /etc/security/limits.conf; then
    echo "* hard core 0" >> /etc/security/limits.conf
    echo "* soft core 0" >> /etc/security/limits.conf
    log_info "已禁用核心转储"
fi

# 10.6 配置日志轮转
log_info "正在配置日志轮转..."
if [ -f /etc/logrotate.conf ]; then
    backup_file /etc/logrotate.conf
    # 确保日志保留 4 周
    sed -i 's/^rotate.*/rotate 4/' /etc/logrotate.conf
    log_info "日志轮转已配置（保留 4 周）"
fi

# 10.7 禁用不必要的文件系统
log_info "正在禁用不必要的文件系统模块..."

cat > /etc/modprobe.d/disable-fs.conf << 'EOF'
# 禁用不必要的文件系统
install cramfs /bin/true
install freevxfs /bin/true
install jffs2 /bin/true
install hfs /bin/true
install hfsplus /bin/true
install squashfs /bin/true
install udf /bin/true
install vfat /bin/true
EOF
log_info "已禁用不必要的文件系统模块"

# 10.8 配置系统资源限制
log_info "正在配置系统资源限制..."
backup_file /etc/security/limits.conf

# 添加资源限制（防止 fork bomb 等）
if ! grep -q "nproc" /etc/security/limits.conf; then
    cat >> /etc/security/limits.conf << 'EOF'

# 系统资源限制
* soft nproc 2048
* hard nproc 4096
* soft nofile 65535
* hard nofile 65535
* soft memlock 64
* hard memlock 64
EOF
    log_info "系统资源限制已配置"
fi

# ============================================================
# 十一、加固完成
# ============================================================

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}加固完成${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

log_info "脚本执行完毕"
log_info "详细日志已保存到：$LOG_FILE"

echo ""
echo -e "${YELLOW}[!] 重要提示：${NC}"
echo -e "${YELLOW}    1. 建议重启系统以确保所有设置生效${NC}"
echo -e "${YELLOW}    2. 请仔细检查各功能是否正常工作，特别是业务相关服务${NC}"
echo -e "${YELLOW}    3. 加固前请确保已创建系统备份或快照${NC}"
echo -e "${YELLOW}    4. 部分设置可能需要根据实际业务需求调整${NC}"
echo -e "${YELLOW}    5. 日志文件位置：$LOG_FILE${NC}"
echo -e "${YELLOW}    6. 建议运行以下命令检查系统安全状态：${NC}"
echo -e "${YELLOW}       - rkhunter --check  （Rootkit 检测）${NC}"
echo -e "${YELLOW}       - aide --check      （文件完整性检查，需先初始化）${NC}"
echo -e "${YELLOW}       - fail2ban-client status  （fail2ban 状态）${NC}"
echo ""

# 询问是否重启
read -p "是否立即重启系统？(y/N): " restart_confirm
if [ "$restart_confirm" = "y" ] || [ "$restart_confirm" = "Y" ]; then
    echo "[*] 系统将在 10 秒后重启..."
    shutdown -r +1 "Linux 安全加固完成，系统重启以应用所有设置"
else
    echo -e "${GREEN}[*] 请稍后手动重启系统以应用所有设置。${NC}"
fi

exit 0
