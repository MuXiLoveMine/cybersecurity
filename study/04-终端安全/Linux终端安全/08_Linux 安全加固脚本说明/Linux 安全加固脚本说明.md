# Linux 安全加固脚本说明

> 详细的加固脚本请参考 `linux_hardening.sh` 文件。以下是脚本的主要功能说明。

### 脚本功能概述

**1. 系统更新**
- 更新系统软件包
- 配置自动安全更新

**2. 账户安全**
- 配置密码策略（长度、复杂度、有效期）
- 配置账户锁定策略
- 禁用不必要的系统账户
- 禁用 root SSH 登录

**3. SSH 安全**
- 禁用 root 远程登录
- 禁用密码认证（建议启用密钥后）
- 修改默认 SSH 端口（可选）
- 配置空闲超时
- 限制最大认证尝试次数

**4. 防火墙配置**
- 配置 iptables/ufw 防火墙
- 默认入站拒绝
- 允许必要的服务端口
- 防止常见攻击（SYN Flood 等）

**5. 文件权限加固**
- 设置关键配置文件权限
- 查找并修复危险的 SUID/SGID 文件
- 设置 umask

**6. 审计配置**
- 安装和配置 auditd
- 配置关键文件和操作的审计规则
- 配置日志轮转

**7. 内核参数加固**
- 网络安全参数（防止 IP 欺骗、SYN Flood）
- 内存安全参数
- 禁用不必要的内核模块
- 启用 ASLR

**8. 服务加固**
- 禁用不必要的服务
- 配置服务最小权限

**9. 安全工具安装**
- 安装 fail2ban（防止暴力破解）
- 安装 rkhunter/chkrootkit（Rootkit 检测）
- 安装 AIDE（文件完整性检查）

---

> 💡 **Linux 安全是一个持续的过程。定期审计、持续监控、及时更新补丁，才能有效保障系统安全。**

---

## 📋 内容审核与补充建议

> 针对「Linux 安全加固脚本说明」部分的内容审核结果：

### 💻 代码示例
- ⚠️ 缺少code相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客

---

## 🛠️ 补充：实战拓展

### 一、Linux 安全加固命令速查表

#### 系统更新与补丁管理

```bash
# ===== Debian/Ubuntu 系列 =====
# 更新软件包列表
apt update
# 升级已安装的软件包
apt upgrade -y
# 完整升级（包括内核等）
apt full-upgrade -y
# 只安装安全更新
apt-get install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades

# ===== RHEL/CentOS 系列 =====
# 更新所有软件包
yum update -y
# 或使用 dnf（新版）
dnf update -y
# 安装安全更新
yum update --security -y
# 安装yum-cron实现自动更新
yum install yum-cron -y
systemctl enable --now yum-cron

# ===== 查看已安装的安全补丁 =====
# Debian/Ubuntu
apt list --installed | grep -i security
# RHEL/CentOS
yum updateinfo list security installed

# ===== 查看内核版本 =====
uname -r
# 检查是否有可用内核更新
apt list --upgradable 2>/dev/null | grep linux-image
```

#### 用户与账户安全

```bash
# ===== 查看用户列表 =====
cat /etc/passwd
# 查看可登录的用户
grep -v '/usr/sbin/nologin\|/bin/false' /etc/passwd

# ===== 查看UID为0的账户（root权限）=====
awk -F: '($3 == "0") {print $1}' /etc/passwd
# 应该只有root

# ===== 查看空密码账户 =====
awk -F: '($2 == "") {print $1}' /etc/shadow

# ===== 禁用不需要的系统账户 =====
usermod -s /usr/sbin/nologin daemon
usermod -s /usr/sbin/nologin nobody
# 将不需要登录的账户shell改为nologin

# ===== 密码策略配置（PAM）=====
# 编辑 /etc/pam.d/common-password（Debian）或 /etc/pam.d/system-auth（RHEL）
# 密码复杂度：安装 libpam-pwquality
apt install libpam-pwquality -y   # Debian
yum install pam_pwquality -y      # RHEL

# 配置 /etc/security/pwquality.conf
cat > /etc/security/pwquality.conf << 'EOF'
minlen = 14           # 最小长度14位
dcredit = -1          # 至少1个数字
ucredit = -1          # 至少1个大写字母
lcredit = -1          # 至少1个小写字母
ocredit = -1          # 至少1个特殊字符
maxrepeat = 3         # 最多3个重复字符
dictcheck = 1         # 检查字典
EOF

# ===== 密码有效期配置 =====
# 编辑 /etc/login.defs
PASS_MAX_DAYS   90    # 密码最长使用90天
PASS_MIN_DAYS   1     # 密码最短使用1天
PASS_WARN_AGE   7     # 过期前7天提醒

# ===== 账户锁定策略 =====
# 编辑 /etc/pam.d/common-auth（Debian）添加：
auth required pam_tally2.so deny=5 unlock_time=1800 even_deny_root root_unlock_time=60
# 5次失败锁定30分钟，root也锁定，root锁定60秒

# 查看锁定状态
pam_tally2 -u username
# 解锁账户
pam_tally2 -u username -r --reset
```

#### SSH 安全加固

```bash
# ===== 备份SSH配置 =====
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# ===== 编辑 SSH 配置 =====
vim /etc/ssh/sshd_config

# 关键配置项：
Protocol 2                      # 只使用SSH协议2
PermitRootLogin no              # 禁止root直接登录
PasswordAuthentication no       # 禁用密码认证（启用密钥后）
PubkeyAuthentication yes        # 启用公钥认证
PermitEmptyPasswords no         # 禁止空密码
MaxAuthTries 3                  # 最大认证尝试次数
LoginGraceTime 30               # 登录宽限时间（秒）
ClientAliveInterval 300         # 客户端空闲超时检查
ClientAliveCountMax 2           # 最多2次无响应后断开
AllowUsers user1 user2          # 只允许特定用户SSH登录
AllowGroups sshusers            # 只允许特定组
Port 2222                       # 修改默认端口（可选，安全收益有限）
X11Forwarding no                # 禁用X11转发
AllowTcpForwarding no           # 禁用TCP转发（如不需要）
PermitTunnel no                 # 禁用隧道

# ===== 配置密钥登录 =====
# 客户端生成密钥对
ssh-keygen -t ed25519 -C "your_email@example.com"
# 或RSA
ssh-keygen -t rsa -b 4096

# 将公钥上传到服务器
ssh-copy-id user@server
# 或手动添加到 ~/.ssh/authorized_keys

# 设置正确的权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# ===== 重启SSH服务 =====
systemctl restart sshd
# 或
service sshd restart

# ===== 验证配置语法 =====
sshd -t
```

#### 防火墙配置

```bash
# ===== UFW（Ubuntu/Debian推荐）=====
# 安装
apt install ufw -y

# 默认策略
ufw default deny incoming       # 默认拒绝入站
ufw default allow outgoing      # 默认允许出站

# 允许SSH
ufw allow 22/tcp
# 或限制来源IP
ufw allow from 192.168.1.0/24 to any port 22

# 允许HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# 启用防火墙
ufw enable

# 查看状态
ufw status verbose
ufw status numbered

# 删除规则
ufw delete allow 80/tcp
# 或按编号删除
ufw delete 2

# ===== iptables（通用，底层）=====
# 查看当前规则
iptables -L -n -v
iptables -L -n --line-numbers

# 清空规则
iptables -F
iptables -X

# 设置默认策略
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 允许已建立的连接
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# 允许回环接口
iptables -A INPUT -i lo -j ACCEPT

# 允许SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 防止SYN Flood
iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 5 -j ACCEPT

# 保存规则（Debian）
iptables-save > /etc/iptables/rules.v4
# 安装持久化工具：apt install iptables-persistent

# ===== firewalld（RHEL/CentOS 7+）=====
# 查看状态
firewall-cmd --state
firewall-cmd --list-all

# 开放端口
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https

# 富规则（限制来源IP）
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" port port="22" protocol="tcp" accept'

# 重新加载配置
firewall-cmd --reload
```

#### 文件系统与权限加固

```bash
# ===== 查找SUID文件 =====
find / -perm -4000 -type f 2>/dev/null
# 查找SGID文件
find / -perm -2000 -type f 2>/dev/null
# 查找世界可写文件
find / -perm -0002 -type f 2>/dev/null
find / -perm -0002 -type d 2>/dev/null

# ===== 移除不必要的SUID位 =====
chmod u-s /usr/bin/不必要的程序
# 例：如果不使用wall命令
chmod u-s /usr/bin/wall

# ===== 检查关键文件权限 =====
# /etc/shadow 应该只有root可读
ls -la /etc/shadow    # 应为 -rw-r----- root shadow
chmod 640 /etc/shadow
chown root:shadow /etc/shadow

# /etc/passwd 权限
ls -la /etc/passwd    # 应为 -rw-r--r-- root root
chmod 644 /etc/passwd

# /etc/sudoers 权限
chmod 440 /etc/sudoers
chown root:root /etc/sudoers

# ===== 查找无属主文件 =====
find / -nouser -o -nogroup 2>/dev/null
# 这些文件可能是安全隐患

# ===== 设置umask =====
# 编辑 /etc/profile 或 /etc/bash.bashrc
umask 027    # 新文件权限 640，新目录 750
# 或更严格
umask 077    # 新文件权限 600，新目录 700
```

#### 内核参数加固（sysctl）

```bash
# ===== 编辑 /etc/sysctl.conf 或 /etc/sysctl.d/99-security.conf =====

# 网络安全参数
# 防止IP欺骗
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# 禁用ICMP重定向
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0

# 禁用源路由
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# SYN Flood防护
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2

# 启用ASLR（地址空间随机化）
kernel.randomize_va_space = 2

# 禁止使用dmesg
kernel.dmesg_restrict = 1

# 限制核心转储（防止敏感信息泄露）
fs.suid_dumpable = 0

# 禁用Magic SysRq键
kernel.sysrq = 0

# 保护符号链接（防止TOCTOU攻击）
fs.protected_symlinks = 1
fs.protected_hardlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2

# ===== 应用配置 =====
sysctl -p
# 或指定文件
sysctl -p /etc/sysctl.d/99-security.conf

# ===== 查看当前值 =====
sysctl net.ipv4.tcp_syncookies
```

#### 日志与审计配置

```bash
# ===== 安装 auditd =====
apt install auditd -y    # Debian
yum install audit -y     # RHEL

# 启用并启动
systemctl enable --now auditd

# ===== 配置审计规则 =====
# 编辑 /etc/audit/rules.d/audit.rules
# 或直接使用 auditctl 命令

# 监控/etc/passwd和/etc/shadow的修改
auditctl -w /etc/passwd -p wa -k identity
auditctl -w /etc/shadow -p wa -k identity
auditctl -w /etc/gshadow -p wa -k identity
auditctl -w /etc/group -p wa -k identity

# 监控sudo使用
auditctl -w /usr/bin/sudo -p x -k sudo

# 监控登录相关
auditctl -w /var/log/faillog -p wa -k logins
auditctl -w /var/log/lastlog -p wa -k logins

# 监控重要系统调用
auditctl -a always,exit -F arch=b64 -S execve -k exec
auditctl -a always,exit -F arch=b32 -S execve -k exec

# ===== 查看审计日志 =====
ausearch -k identity      # 搜索identity相关事件
ausearch -m USER_LOGIN    # 搜索登录事件
aureport -au              # 认证报告
aureport -l               # 登录报告

# ===== 日志轮转 =====
# 编辑 /etc/logrotate.conf 或 /etc/logrotate.d/ 下的文件
# 确保日志定期轮转、压缩、保留足够时间
```

### 二、Linux 安全检查 Shell 脚本

```bash
#!/bin/bash
# Linux 安全配置审计脚本
# 用法: sudo bash linux_security_audit.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0
INFO=0

echo -e "${BLUE}===== Linux 安全审计脚本 =====${NC}"
echo ""

# ===== 1. 系统信息 =====
echo -e "${YELLOW}[1/10] 系统信息收集...${NC}"
echo -e "  主机名: $(hostname)"
echo -e "  系统版本: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo -e "  内核版本: $(uname -r)"
echo -e "  运行时间: $(uptime -p)"
INFO=$((INFO + 4))

# ===== 2. 系统更新 =====
echo -e "${YELLOW}[2/10] 系统更新检查...${NC}"
if command -v apt &> /dev/null; then
    updates=$(apt list --upgradable 2>/dev/null | grep -c 'upgradable')
    echo -e "  可更新包数量: $updates"
elif command -v yum &> /dev/null; then
    updates=$(yum check-update 2>/dev/null | grep -c '^[a-zA-Z]')
    echo -e "  可更新包数量: $updates"
fi
if [ "$updates" -gt 0 ]; then
    echo -e "  ${YELLOW}[警告] 有可用的安全更新${NC}"
    WARN=$((WARN + 1))
else
    echo -e "  ${GREEN}[通过] 系统已是最新${NC}"
    PASS=$((PASS + 1))
fi

# ===== 3. 账户安全 =====
echo -e "${YELLOW}[3/10] 账户安全检查...${NC}"

# UID为0的用户
uid0=$(awk -F: '($3 == 0) {print $1}' /etc/passwd)
uid0_count=$(echo "$uid0" | wc -l)
if [ "$uid0_count" -gt 1 ]; then
    echo -e "  ${RED}[失败] 发现多个UID=0的账户: $uid0${NC}"
    FAIL=$((FAIL + 1))
else
    echo -e "  ${GREEN}[通过] 只有root拥有UID=0${NC}"
    PASS=$((PASS + 1))
fi

# 空密码账户
empty_pw=$(awk -F: '($2 == "") {print $1}' /etc/shadow 2>/dev/null)
if [ -n "$empty_pw" ]; then
    echo -e "  ${RED}[失败] 发现空密码账户: $empty_pw${NC}"
    FAIL=$((FAIL + 1))
else
    echo -e "  ${GREEN}[通过] 无空密码账户${NC}"
    PASS=$((PASS + 1))
fi

# root SSH登录
if grep -qi "^PermitRootLogin no" /etc/ssh/sshd_config 2>/dev/null; then
    echo -e "  ${GREEN}[通过] 已禁止root SSH登录${NC}"
    PASS=$((PASS + 1))
else
    echo -e "  ${RED}[失败] root可以通过SSH登录${NC}"
    FAIL=$((FAIL + 1))
fi

# ===== 4. 密码策略 =====
echo -e "${YELLOW}[4/10] 密码策略检查...${NC}"
if grep -q "minlen" /etc/security/pwquality.conf 2>/dev/null; then
    minlen=$(grep "minlen" /etc/security/pwquality.conf | grep -oP '\d+')
    echo -e "  密码最小长度: $minlen"
    if [ "$minlen" -ge 14 ]; then
        echo -e "  ${GREEN}[通过] 密码长度符合要求${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "  ${YELLOW}[警告] 密码长度小于14位${NC}"
        WARN=$((WARN + 1))
    fi
else
    echo -e "  ${YELLOW}[警告] 未配置密码复杂度策略${NC}"
    WARN=$((WARN + 1))
fi

# ===== 5. SUID/SGID 检查 =====
echo -e "${YELLOW}[5/10] SUID/SGID 文件检查...${NC}"
suid_count=$(find / -perm -4000 -type f 2>/dev/null | wc -l)
sgid_count=$(find / -perm -2000 -type f 2>/dev/null | wc -l)
echo -e "  SUID文件数量: $suid_count"
echo -e "  SGID文件数量: $sgid_count"
if [ "$suid_count" -gt 20 ]; then
    echo -e "  ${YELLOW}[警告] SUID文件较多，建议审计${NC}"
    WARN=$((WARN + 1))
else
    echo -e "  ${GREEN}[信息] SUID文件数量在正常范围${NC}"
    INFO=$((INFO + 1))
fi

# ===== 6. 防火墙状态 =====
echo -e "${YELLOW}[6/10] 防火墙检查...${NC}"
if command -v ufw &> /dev/null && ufw status | grep -q "active"; then
    echo -e "  ${GREEN}[通过] UFW防火墙已启用${NC}"
    PASS=$((PASS + 1))
elif systemctl is-active --quiet firewalld 2>/dev/null; then
    echo -e "  ${GREEN}[通过] firewalld防火墙已启用${NC}"
    PASS=$((PASS + 1))
elif iptables -L INPUT -n | grep -q "DROP\|REJECT"; then
    echo -e "  ${GREEN}[通过] iptables已配置${NC}"
    PASS=$((PASS + 1))
else
    echo -e "  ${RED}[失败] 防火墙未启用或未配置${NC}"
    FAIL=$((FAIL + 1))
fi

# ===== 7. 监听端口 =====
echo -e "${YELLOW}[7/10] 监听端口检查...${NC}"
listen_ports=$(ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null)
echo -e "  监听的TCP端口:"
echo "$listen_ports" | awk 'NR>1 {print "    " $4}' | head -10
INFO=$((INFO + 1))

# ===== 8. 内核参数 =====
echo -e "${YELLOW}[8/10] 内核安全参数检查...${NC}"

# ASLR
aslr=$(sysctl -n kernel.randomize_va_space 2>/dev/null)
if [ "$aslr" -eq 2 ]; then
    echo -e "  ${GREEN}[通过] ASLR已完全启用${NC}"
    PASS=$((PASS + 1))
else
    echo -e "  ${YELLOW}[警告] ASLR未完全启用 (当前值: $aslr)${NC}"
    WARN=$((WARN + 1))
fi

# SYN Cookies
syncookie=$(sysctl -n net.ipv4.tcp_syncookies 2>/dev/null)
if [ "$syncookie" -eq 1 ]; then
    echo -e "  ${GREEN}[通过] SYN Cookies已启用${NC}"
    PASS=$((PASS + 1))
else
    echo -e "  ${RED}[失败] SYN Cookies未启用${NC}"
    FAIL=$((FAIL + 1))
fi

# ===== 9. 审计服务 =====
echo -e "${YELLOW}[9/10] 审计服务检查...${NC}"
if systemctl is-active --quiet auditd 2>/dev/null; then
    echo -e "  ${GREEN}[通过] auditd审计服务运行中${NC}"
    PASS=$((PASS + 1))
else
    echo -e "  ${YELLOW}[警告] auditd未运行${NC}"
    WARN=$((WARN + 1))
fi

# ===== 10. 关键文件权限 =====
echo -e "${YELLOW}[10/10] 关键文件权限检查...${NC}"

# /etc/shadow
shadow_perm=$(stat -c "%a" /etc/shadow 2>/dev/null)
if [ "$shadow_perm" -le 640 ]; then
    echo -e "  ${GREEN}[通过] /etc/shadow 权限正确 ($shadow_perm)${NC}"
    PASS=$((PASS + 1))
else
    echo -e "  ${RED}[失败] /etc/shadow 权限过宽 ($shadow_perm)${NC}"
    FAIL=$((FAIL + 1))
fi

# /etc/sudoers
sudoers_perm=$(stat -c "%a" /etc/sudoers 2>/dev/null)
if [ "$sudoers_perm" -eq 440 ]; then
    echo -e "  ${GREEN}[通过] /etc/sudoers 权限正确${NC}"
    PASS=$((PASS + 1))
else
    echo -e "  ${YELLOW}[警告] /etc/sudoers 权限为 $sudoers_perm${NC}"
    WARN=$((WARN + 1))
fi

# ===== 汇总 =====
echo ""
echo -e "${BLUE}===== 审计结果汇总 =====${NC}"
echo -e "  ${GREEN}通过: $PASS${NC}"
echo -e "  ${RED}失败: $FAIL${NC}"
echo -e "  ${YELLOW}警告: $WARN${NC}"
echo -e "  ${BLUE}信息: $INFO${NC}"
echo ""
echo -e "  总分: $((PASS*100/(PASS+FAIL+WARN))) / 100"
echo ""
echo -e "报告生成时间: $(date)"
echo -e "脚本执行完成。"
```

### 三、常用安全工具安装与使用

```bash
# ===== fail2ban（防止暴力破解）=====
# 安装
apt install fail2ban -y    # Debian
yum install fail2ban -y    # RHEL（需EPEL源）

# 配置SSH防护
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600      # 封禁1小时
findtime = 600      # 10分钟内
maxretry = 5        # 5次失败
ignoreip = 127.0.0.1 192.168.1.0/24  # 白名单

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
EOF

# 启动服务
systemctl enable --now fail2ban

# 查看状态
fail2ban-client status
fail2ban-client status sshd

# 手动解封
fail2ban-client set sshd unbanip 192.168.1.100

# ===== rkhunter（Rootkit检测）=====
# 安装
apt install rkhunter -y

# 更新特征库
rkhunter --update

# 运行扫描
rkhunter --check
rkhunter --check --skip-keypress  # 无交互模式

# 查看报告
cat /var/log/rkhunter.log

# ===== chkrootkit（Rootkit检测）=====
# 安装
apt install chkrootkit -y

# 运行扫描
chkrootkit

# ===== AIDE（文件完整性检查）=====
# 安装
apt install aide -y

# 初始化数据库
aideinit
# 或
aide --init

# 更新数据库
mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz

# 执行检查
aide --check
aide --check --verbose

# ===== Lynis（系统安全审计）=====
# 安装
apt install lynis -y
# 或下载最新版
# git clone https://github.com/CISOfy/lynis.git

# 运行审计
lynis audit system
# 详细输出
lynis audit system --verbose
# 只看警告
lynis audit system -Q 2>/dev/null | grep -i warning

# 查看报告
cat /var/log/lynis-report.dat
```

### 四、Linux 安全加固检查清单速查

| 检查项 | 命令/文件 | 期望值 |
|--------|-----------|--------|
| 系统更新 | `apt update && apt upgrade` | 定期更新 |
| root SSH登录 | `/etc/ssh/sshd_config` | `PermitRootLogin no` |
| 密码认证 | `/etc/ssh/sshd_config` | `PasswordAuthentication no` |
| 空密码账户 | `awk -F: '($2==""){print $1}' /etc/shadow` | 无结果 |
| UID=0账户 | `awk -F: '($3==0){print $1}' /etc/passwd` | 只有root |
| SUID文件 | `find / -perm -4000 -type f` | 审计每一个 |
| 防火墙 | `ufw status` / `iptables -L` | 已启用 |
| ASLR | `sysctl kernel.randomize_va_space` | 值为2 |
| SYN Cookies | `sysctl net.ipv4.tcp_syncookies` | 值为1 |
| 审计服务 | `systemctl status auditd` | running |
| /etc/shadow权限 | `stat /etc/shadow` | 640或更小 |
| 世界可写文件 | `find / -perm -0002 -type f` | 无异常 |

> **加固原则**：
> - 最小权限原则：只授予必要的权限
> - 最小服务原则：只运行必要的服务
> - 纵深防御：多层防护，不要依赖单一措施
> - 定期审计：配置不是一次性的，需要持续监控
> - 变更管理：所有变更要有记录和回滚方案
