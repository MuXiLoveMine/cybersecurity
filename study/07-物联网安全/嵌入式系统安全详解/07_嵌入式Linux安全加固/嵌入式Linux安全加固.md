# 嵌入式Linux安全加固

### 7.1 内核安全配置

```bash
# 嵌入式Linux内核安全配置 (.config)

# === 内存保护 ===
CONFIG_ARM64_SW_TTBR0_PAN=y      # 用户态内核访问防护
CONFIG_STRICT_KERNEL_RWX=y        # 内核代码段不可写
CONFIG_STRICT_MODULE_RWX=y        # 模块代码段不可写
CONFIG_RANDOMIZE_BASE=y           # KASLR (内核地址随机化)
CONFIG_RANDOMIZE_MODULE_REGION=y # 模块地址随机化

# === 权限控制 ===
CONFIG_SECURITY=y                 # Linux安全模块框架
CONFIG_SECURITY_YAMA=y            # YAMA (进程限制)
# CONFIG_SECURITY_SELINUX=y       # SELinux (可能资源受限)
# CONFIG_SECURITY_APPARMOR=y     # AppArmor
CONFIG_SECCOMP=y                  # 安全计算模式
CONFIG_SECCOMP_FILTER=y           # seccomp BPF过滤

# === 加密支持 ===
CONFIG_CRYPTO=y                   # 加密框架
CONFIG_CRYPTO_AEAD=y              # AEAD加密
CONFIG_CRYPTO_AES=y              # AES
CONFIG_CRYPTO_GCM=y              # GCM模式
CONFIG_CRYPTO_SHA256=y           # SHA-256
CONFIG_CRYPTO_RSA=y              # RSA
CONFIG_CRYPTO_ECDH=y             # ECDH密钥交换

# === 安全启动 ===
CONFIG_EFI=y                      # EFI支持
CONFIG_EFI_STUB=y                 # EFI引导存根
# CONFIG_MODULE_SIG=y             # 模块签名
# CONFIG_MODULE_SIG_FORCE=y       # 强制模块签名

# === 审计 ===
CONFIG_AUDIT=y                    # 审计子系统
CONFIG_AUDITSYSCALL=y             # 系统调用审计

# === 网络安全 ===
CONFIG_NETFILTER=y                # Netfilter框架
CONFIG_NF_CONNTRACK=y            # 连接跟踪
CONFIG_NETFILTER_XTABLES=y       # xtables
CONFIG_NETFILTER_XT_MATCH_STATE=y # 状态匹配
```

### 7.2 用户空间安全加固

```bash
# === 用户空间安全加固 ===

# 1. 文件系统安全
# 挂载选项加固
mount -o remount,ro /             # 根文件系统只读
mount -o remount,nodev,nosuid /tmp # /tmp: 无设备文件, 无suid
mount -o remount,nodev,nosuid,noexec /tmp  # /tmp不可执行
mount -o remount,nodev,nosuid /var/tmp
mount -o remount,nodev,nosuid /dev/shm

# 2. 内核参数加固
# 禁用核心转储
echo 0 > /proc/sys/kernel/core_uses_pid
echo 0 > /proc/sys/kernel/core_pattern
ulimit -c 0

# 禁用魔术SysRq键
echo 0 > /proc/sys/kernel/sysrq

# 网络参数加固
echo 1 > /proc/sys/net/ipv4/tcp_syncookies
echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts
echo 0 > /proc/sys/net/ipv4/ip_forward
echo 1 > /proc/sys/net/ipv4/conf/all/accept_redirects
echo 0 > /proc/sys/net/ipv4/conf/all/accept_source_route

# ASLR
echo 2 > /proc/sys/kernel/randomize_va_space

# 3. 文件权限加固
# 查找SUID/SGID文件
find / -perm -4000 -type f -exec ls -la {} \; 2>/dev/null
find / -perm -2000 -type f -exec ls -la {} \; 2>/dev/null

# 移除不必要的SUID
chmod u-s /usr/bin/passwd
chmod u-s /bin/mount
chmod u-s /bin/umount
chmod u-s /bin/su
chmod u-s /usr/bin/sudo

# 4. 用户管理
# 禁用root登录
passwd -l root

# 设置密码策略
echo "minlen=12" >> /etc/security/pwquality.conf
echo "minclass=3" >> /etc/security/pwquality.conf
echo "maxrepeat=3" >> /etc/security/pwquality.conf

# 5. 服务加固
# 禁用不必要的服务
systemctl disable telnet
systemctl disable rsh
systemctl disable rexec
systemctl disable ftp
systemctl disable rlogin

# SSH加固
cat >> /etc/ssh/sshd_config << 'EOF'
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers admin
Port 22022
Protocol 2
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 0
PermitEmptyPasswords no
X11Forwarding no
AllowTcpForwarding no
EOF

# 6. 防火墙配置
iptables -F
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 22022 -j ACCEPT  # SSH
iptables -A INPUT -p tcp --dport 80 -j ACCEPT     # HTTP (如需)
iptables -A INPUT -j LOG --log-prefix "IPTABLES: "
iptables -A INPUT -j DROP
```

### 7.3 嵌入式Linux安全工具

```bash
# === 安全扫描工具 ===

# 1. Lynis - 安全审计
wget https://cisofy.com/files/lynis-3.0.0.tar.gz
tar xzf lynis-3.0.0.tar.gz
cd lynis
./lynis audit system --quick

# 2. chkrootkit - Rootkit检测
apt-get install chkrootkit
chkrootkit | grep -i "infected\|not found\|not tested"

# 3. rkhunter - Rootkit Hunter
apt-get install rkhunter
rkhunter --update
rkhunter --check

# 4. AIDE - 文件完整性监控
apt-get install aide
aide --init
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
aide --check

# 5. auditd - 审计守护进程
apt-get install auditd
# 配置审计规则
cat >> /etc/audit/rules.d/audit.rules << 'EOF'
# 监控二进制文件修改
-w /bin/ -p wa -k bin_modify
-w /sbin/ -p wa -k bin_modify
-w /usr/bin/ -p wa -k bin_modify
-w /usr/sbin/ -p wa -k bin_modify

# 监控配置文件
-w /etc/ -p wa -k etc_modify

# 监控用户/组变更
-w /etc/passwd -p wa -k passwd_modify
-w /etc/shadow -p wa -k shadow_modify
-w /etc/group -p wa -k group_modify

# 监控登录事件
-w /var/log/faillog -p wa -k logins
-w /var/log/lastlog -p wa -k logins
EOF
systemctl restart auditd
```

---

---

