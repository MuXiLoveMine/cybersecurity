# Linux 安全配置基线

### 2.1 账户安全

**密码策略**

编辑 /etc/login.defs：

```bash
# 密码最长使用期限（天）
PASS_MAX_DAYS   90

# 密码最短使用期限（天）
PASS_MIN_DAYS   1

# 密码最短长度
PASS_MIN_LEN    14

# 密码过期前警告天数
PASS_WARN_AGE   7
```

**PAM 密码复杂度**

```bash
# CentOS/RHEL - 安装 pam_pwquality
yum install libpwquality
# 编辑 /etc/security/pwquality.conf
minlen = 14           # 最小长度
dcredit = -1          # 至少一个数字
ucredit = -1          # 至少一个大写字母
lcredit = -1          # 至少一个小写字母
ocredit = -1          # 至少一个特殊字符
maxrepeat = 3         # 最多连续相同字符数
maxclassrepeat = 4    # 最多同类字符连续数

# Ubuntu/Debian
# 编辑 /etc/pam.d/common-password
password requisite pam_pwquality.so retry=3 minlen=14 dcredit=-1 ucredit=-1 lcredit=-1 ocredit=-1
```

**账户锁定策略**

```bash
# CentOS/RHEL - 编辑 /etc/pam.d/system-auth 和 /etc/pam.d/password-auth
auth required pam_faillock.so preauth silent deny=5 unlock_time=1800
auth [default=die] pam_faillock.so authfail deny=5 unlock_time=1800
account required pam_faillock.so

# Ubuntu/Debian - 编辑 /etc/pam.d/common-auth
auth required pam_tally2.so deny=5 unlock_time=1800 onerr=fail

# 查看账户锁定状态
faillock --user username
pam_tally2 --user username

# 解锁账户
faillock --user username --reset
pam_tally2 --user username --reset
```

**禁用不必要的账户**

```bash
# 查看所有用户账户
cat /etc/passwd | grep -v nologin | grep -v false

# 禁用用户（不删除）
usermod -s /sbin/nologin username
passwd -l username  # 锁定密码

# 启用用户
passwd -u username
usermod -s /bin/bash username

# 删除用户
userdel -r username  # -r 同时删除主目录
```

**检查空密码账户**

```bash
# 查找空密码用户
awk -F: '($2 == "" ) { print $1 }' /etc/shadow

# 锁定空密码账户
passwd -l username
```

### 2.2 SSH 安全配置

**SSH 配置文件**

```bash
# 配置文件路径
/etc/ssh/sshd_config
```

**推荐安全配置**

```bash
# /etc/ssh/sshd_config 安全配置示例

# 禁止 root 直接登录
PermitRootLogin no

# 禁止空密码
PermitEmptyPasswords no

# 使用密钥认证（推荐）
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# 禁用密码认证（启用密钥后建议关闭）
PasswordAuthentication no

# 禁用 Challenge-Response 认证
ChallengeResponseAuthentication no

# 禁用 Kerberos 认证（如不需要）
KerberosAuthentication no
GSSAPIAuthentication no

# 禁用 X11 转发（如不需要）
X11Forwarding no

# 禁用 TCP 转发（如不需要）
AllowTcpForwarding no

# 客户端存活配置（防止空闲连接）
ClientAliveInterval 300
ClientAliveCountMax 2

# 最大认证尝试次数
MaxAuthTries 3

# 最大会话数
MaxSessions 5

# 限制登录用户（白名单方式，推荐）
AllowUsers alice bob
AllowGroups sshusers

# 修改默认端口（减少扫描噪音，非核心安全措施）
Port 2222

# 使用协议版本 2（默认已是）
Protocol 2

# 允许的认证方式
AuthenticationMethods publickey

# 登录横幅（可选）
Banner /etc/ssh/banner
```

**SSH 密钥管理**

```bash
# 生成 SSH 密钥对（推荐 ED25519 算法）
ssh-keygen -t ed25519 -C "user@example.com"

# 或者使用 RSA（至少 4096 位）
ssh-keygen -t rsa -b 4096 -C "user@example.com"

# 复制公钥到服务器
ssh-copy-id user@server
# 或手动添加
cat ~/.ssh/id_ed25519.pub | ssh user@server 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'

# 正确的权限设置
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# 验证配置并重启 SSH
sshd -t  # 测试配置文件语法
systemctl restart sshd  # 或 ssh
```

### 2.3 防火墙配置

**iptables 基础**

```bash
# 查看当前规则
iptables -L -n -v
iptables -L -n --line-numbers

# 查看 NAT 表
iptables -t nat -L -n -v

# 清空所有规则
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# 设置默认策略
iptables -P INPUT DROP       # 默认入站拒绝
iptables -P FORWARD DROP     # 默认转发拒绝
iptables -P OUTPUT ACCEPT    # 默认出站允许
```

**iptables 常用规则**

```bash
# 允许回环接口
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# 允许已建立和相关的连接
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 允许 SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
# 限制 SSH 源地址
iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 22 -j ACCEPT

# 允许 HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 允许 ICMP（Ping）
iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT

# 防止 SYN Flood
iptables -N synflood
iptables -A synflood -m limit --limit 1/s --limit-burst 3 -j RETURN
iptables -A synflood -j DROP
iptables -A INPUT -p tcp --syn -j synflood

# 防止端口扫描
iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP
iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP
iptables -A INPUT -p tcp --tcp-flags ALL FIN,URG,PSH -j DROP
```

**iptables 保存和恢复**

```bash
# CentOS/RHEL
iptables-save > /etc/sysconfig/iptables
iptables-restore < /etc/sysconfig/iptables

# Debian/Ubuntu
iptables-save > /etc/iptables/rules.v4
iptables-restore < /etc/iptables/rules.v4

# 安装 iptables-persistent（Debian/Ubuntu）
apt install iptables-persistent
```

**firewalld 配置（CentOS/RHEL 7+）**

```bash
# 查看状态
firewall-cmd --state
firewall-cmd --list-all

# 查看默认区域
firewall-cmd --get-default-zone

# 启用/禁用服务
firewall-cmd --add-service=http --permanent
firewall-cmd --add-service=https --permanent
firewall-cmd --add-port=2222/tcp --permanent

# 限制源地址
firewall-cmd --permanent --zone=public --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" service name="ssh" accept'

# 重载规则
firewall-cmd --reload

# 移除规则
firewall-cmd --remove-service=telnet --permanent
```

**ufw 配置（Ubuntu/Debian）**

```bash
# 启用/禁用 ufw
ufw enable
ufw disable

# 默认策略
ufw default deny incoming
ufw default allow outgoing

# 允许服务
ufw allow ssh
ufw allow http
ufw allow https
ufw allow 2222/tcp

# 限制源地址
ufw allow from 192.168.1.0/24 to any port 22

# 查看状态
ufw status verbose
ufw status numbered

# 删除规则
ufw delete allow http
ufw delete 3  # 按编号删除

# 启用日志
ufw logging on
```

### 2.4 审计配置

**auditd 安装与配置**

```bash
# CentOS/RHEL
yum install audit
systemctl enable auditd
systemctl start auditd

# Ubuntu/Debian
apt install auditd
systemctl enable auditd
systemctl start auditd
```

**auditd 配置文件**

```bash
# 主配置文件
/etc/audit/auditd.conf

# 规则文件
/etc/audit/rules.d/audit.rules
```

**常用审计规则**

```bash
# /etc/audit/rules.d/audit.rules

# 监控系统时间修改
-a always,exit -F arch=b64 -S adjtimex -S settimeofday -k time_change
-a always,exit -F arch=b32 -S adjtimex -S settimeofday -S stime -k time_change

# 监控用户/组修改
-w /etc/passwd -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/gshadow -p wa -k identity
-w /etc/sudoers -p wa -k sudo_changes

# 监控登录和认证
-w /var/log/faillog -p wa -k logins
-w /var/log/lastlog -p wa -k logins
-w /var/log/tallylog -p wa -k logins

# 监控网络配置修改
-a always,exit -F arch=b64 -S sethostname -S setdomainname -k system_language
-w /etc/issue -p wa -k system_language
-w /etc/issue.net -p wa -k system_language
-w /etc/hosts -p wa -k system_language
-w /etc/sysconfig/network -p wa -k system_language

# 监控防火墙修改
-w /etc/sysconfig/iptables -p wa -k firewall_changes
-w /etc/firewalld/ -p wa -k firewall_changes

# 监控关键系统文件
-w /etc/pam.d/ -p wa -k pam_changes
-w /etc/ssh/sshd_config -p wa -k ssh_changes
-w /etc/cron.d/ -p wa -k cron_changes
-w /etc/crontab -p wa -k cron_changes

# 监控可执行文件修改
-w /bin/ -p wa -k bin_changes
-w /sbin/ -p wa -k sbin_changes
-w /usr/bin/ -p wa -k usr_bin_changes
-w /usr/sbin/ -p wa -k usr_sbin_changes

# 监控 root 用户操作
-a always,exit -F arch=b64 -S execve -F uid=0 -F auid>=1000 -F auid!=4294967295 -k root_exec

# 监控文件系统挂载
-a always,exit -F arch=b64 -S mount -S umount2 -k mount_changes

# 监控内核模块加载/卸载
-w /sbin/insmod -p x -k module_load
-w /sbin/modprobe -p x -k module_load
-w /sbin/rmmod -p x -k module_load
-a always,exit -F arch=b64 -S init_module -S delete_module -k module_changes

# 监控敏感文件访问
-w /root/.ssh/ -p rw -k root_ssh_access
-w /home/*/.ssh/ -p rw -k user_ssh_access

# 结束标记（必须是最后一条）
-D
-b 8192
-f 1
```

**审计日志查看**

```bash
# 查看所有审计日志
ausearch -m all

# 按关键字搜索
ausearch -k identity  # 搜索身份相关事件
ausearch -k time_change  # 搜索时间修改事件

# 按时间搜索
ausearch -ts today -k ssh_changes
ausearch -ts "09/11/2024 00:00:00" -te "09/11/2024 23:59:59"

# 生成审计报告
aureport -au  # 认证报告
aureport -l   # 登录报告
aureport -p   # 进程报告
aureport -f   # 文件报告
aureport -e   # 事件报告
aureport --summary  # 摘要报告

# 实时监控审计日志
auditctl -s  # 查看审计状态
tail -f /var/log/audit/audit.log
```

---

---

