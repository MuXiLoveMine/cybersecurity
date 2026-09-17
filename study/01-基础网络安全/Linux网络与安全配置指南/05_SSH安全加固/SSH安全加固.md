# SSH安全加固

### 4.1 SSH配置加固

```bash
# /etc/ssh/sshd_config 安全配置

# 基本设置
Port 2222                          # 修改默认端口
Protocol 2                         # 仅使用SSH v2
AddressFamily inet                 # 仅IPv4
ListenAddress 0.0.0.0              # 监听地址

# 主机密钥
HostKey /etc/ssh/ssh_host_ed25519_key
HostKey /etc/ssh/ssh_host_rsa_key
# 禁用DSA和ECDSA
# HostKey /etc/ssh/ssh_host_dsa_key     # 禁用
# HostKey /etc/ssh/ssh_host_ecdsa_key   # 禁用

# 密钥交换算法（使用最安全的算法）
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512

# 密码套件
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr

# MAC算法
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512,hmac-sha2-256

# 认证设置
PermitRootLogin no                 # 禁止root直接登录
PermitEmptyPasswords no            # 禁止空密码
PasswordAuthentication no         # 禁用密码认证（仅密钥）
PubkeyAuthentication yes          # 启用密钥认证
ChallengeResponseAuthentication no
UsePAM yes

# 授权密钥文件
AuthorizedKeysFile .ssh/authorized_keys

# 登录限制
MaxAuthTries 3                     # 最大认证尝试次数
MaxSessions 10                     # 最大会话数
MaxStartups 10:30:60              # 最大并发未认证连接

# 登录超时
LoginGraceTime 30                  # 登录宽限时间（秒）
ClientAliveInterval 300           # 客户端存活检查间隔
ClientAliveCountMax 2              # 客户端存活检查次数

# 用户/组限制
AllowUsers admin deploy            # 仅允许指定用户
# 或
AllowGroups sshusers              # 仅允许指定组
DenyUsers nobody
DenyGroups nogroup

# 其他安全选项
X11Forwarding no                  # 禁用X11转发
AllowTcpForwarding no             # 禁用TCP转发
AllowAgentForwarding no           # 禁用Agent转发
PermitTunnel no                   # 禁用隧道
PrintMotd no                      # 不打印MOTD
PrintLastLog yes                  # 打印最后登录信息
StrictModes yes                   # 严格模式

# 日志
SyslogFacility AUTH
LogLevel VERBOSE                  # 详细日志

# 超时设置
TCPKeepAlive no
ClientAliveInterval 300
ClientAliveCountMax 0             # 0表示不保持连接

# 限制访问来源
Match Address 192.168.1.0/24
    PasswordAuthentication yes    # 内网允许密码
    MaxAuthTries 5

Match User deploy
    AllowTcpForwarding yes
    X11Forwarding no
    PermitTunnel yes
    ForceCommand internal-sftp    # SFTP only

# 重启SSH服务
systemctl restart sshd
```

### 4.2 密钥管理与轮换

```bash
# 生成安全的SSH密钥对
# Ed25519（推荐）
ssh-keygen -t ed25519 -a 100 -C "user@hostname" -f ~/.ssh/id_ed25519

# RSA（兼容性好）
ssh-keygen -t rsa -b 4096 -a 100 -C "user@hostname" -f ~/.ssh/id_rsa

# ECDSA
ssh-keygen -t ecdsa -b 521 -C "user@hostname"

# 设置密钥密码
ssh-keygen -p -f ~/.ssh/id_ed25519

# 密钥权限设置
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# 配置SSH客户端
cat > ~/.ssh/config << 'EOF'
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive no
    Compression yes
    HashKnownHosts yes

Host prod-server
    HostName 192.168.1.100
    Port 2222
    User admin
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ProxyJump jump-host  # 通过跳板机

Host jump-host
    HostName 10.0.0.1
    Port 2222
    User jump
    IdentityFile ~/.ssh/jump_ed25519
EOF

chmod 600 ~/.ssh/config

# 密钥轮换策略
# 建议：每90天轮换一次SSH密钥
# 使用脚本自动化轮换
```

### 4.3 SSH跳板机配置

```bash
# 跳板机（Jump Host）配置
# /etc/ssh/sshd_config on jump host

# 限制跳板机功能
AllowTcpForwarding yes
PermitTunnel no
X11Forwarding no
AllowAgentForwarding no

# 强制使用受限Shell
Match Group jumpers
    ForceCommand /usr/bin/limited-shell
    AllowTcpForwarding yes
    PermitOpen 192.168.1.100:2222 192.168.1.101:2222
    # 仅允许连接到指定目标

# bastion主机加固脚本
#!/bin/bash
# 加固跳板机

# 1. 禁用不需要的服务
systemctl disable avahi-daemon
systemctl disable cups
systemctl disable bluetooth
systemctl disable modemmanager

# 2. 限制用户Shell
echo '/bin/rbash' >> /etc/shells
usermod -s /bin/rbash jumpuser

# 3. 限制可用命令
mkdir -p /home/jumpuser/bin
ln -s /usr/bin/ssh /home/jumpuser/bin/ssh
ln -s /bin/clear /home/jumpuser/bin/clear
echo 'export PATH=/home/jumpuser/bin' >> /home/jumpuser/.bashrc

# 4. 审计配置
echo 'export PROMPT_COMMAND="history -a; logger -t ssh-cmd -p local5.info \"USER=$USER CMD=$(history 1 | sed \"s/^[ ]*[0-9]\\+ //\")\""' >> /etc/profile.d/audit.sh
```

### 4.4 SSH审计与监控

```bash
# 查看SSH登录日志
journalctl -u sshd                # systemd日志
grep sshd /var/log/auth.log        # 认证日志
grep "Failed password" /var/log/auth.log | head

# 统计SSH暴力破解
grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -20
grep "Invalid user" /var/log/auth.log | awk '{print $NF}' | sort | uniq -c | sort -rn | head -20

# SSH登录成功记录
grep "Accepted" /var/log/auth.log | tail -20

# 使用last命令查看登录历史
last -n 50                         # 最近50次登录
last -f /var/log/wtmp              # 从指定文件查看
lastb                              # 失败登录尝试

# fail2ban配置
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
banaction = iptables-multiport

[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200
findtime = 300
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# 查看fail2ban状态
fail2ban-client status
fail2ban-client status sshd
fail2ban-client set sshd unbanip 192.168.1.100
```

---

---

## 📋 内容审核与补充建议

> 针对「SSH安全加固」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
