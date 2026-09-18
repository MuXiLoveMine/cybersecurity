# KotH防御策略

### 4.1 系统加固

#### 4.1.1 SSH安全加固

```bash
# 修改SSH配置文件 /etc/ssh/sshd_config

# 禁止root密码登录
PermitRootLogin prohibit-password

# 禁用密码认证（只允许密钥登录）
PasswordAuthentication no

# 更改SSH端口（安全通过隐蔽）
Port 2222

# 限制登录尝试次数
MaxAuthTries 2

# 禁用空密码
PermitEmptyPasswords no

# 禁用X11转发
X11Forwarding no

# 设置登录横幅（威慑作用）
Banner /etc/ssh/banner

# 重启SSH服务
systemctl restart sshd
```

#### 4.1.2 防火墙配置

**使用iptables：**
```bash
# 清空现有规则
iptables -F
iptables -X

# 默认策略
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 允许已建立的连接
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 允许本地回环
iptables -A INPUT -i lo -j ACCEPT

# 允许SSH（只允许自己的IP）
iptables -A INPUT -p tcp --dport 22 -s <your_ip> -j ACCEPT

# 允许HTTP/HTTPS（如果需要）
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 保存规则
iptables-save > /etc/iptables/rules.v4
```

**使用ufw（更简单）：**
```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow from <your_ip> to any port 22
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

#### 4.1.3 文件权限加固

```bash
# 修复敏感文件权限
chmod 700 /root
chmod 600 /etc/shadow
chmod 644 /etc/passwd
chmod 600 /etc/gshadow

# 移除危险的SUID文件
chmod u-s /usr/bin/find
chmod u-s /usr/bin/vim
chmod u-s /bin/nmap

# 限制/tmp目录
mount -o remount,noexec,nosuid /tmp
```

#### 4.1.4 服务最小化

```bash
# 查看所有运行的服务
systemctl list-units --type=service --state=running

# 停止并禁用不需要的服务
systemctl stop <service_name>
systemctl disable <service_name>

# 常见可关闭服务：
# - avahi-daemon（如果不需要网络发现）
# - cups（打印服务）
# - bluetooth（蓝牙）
# - rpcbind（RPC服务）
```

### 4.2 后门检测与清除

#### 4.2.1 快速检测脚本

```bash
#!/bin/bash
# 快速后门检测脚本

echo "=== SSH密钥检查 ==="
cat ~/.ssh/authorized_keys 2>/dev/null
cat /root/.ssh/authorized_keys 2>/dev/null

echo -e "\n=== 定时任务检查 ==="
crontab -l 2>/dev/null
ls -la /etc/cron.d/ 2>/dev/null
cat /etc/crontab 2>/dev/null

echo -e "\n=== SUID文件检查 ==="
find / -perm -4000 -type f 2>/dev/null | head -20

echo -e "\n=== 可疑进程检查 ==="
ps aux | grep -E "(bash|sh|nc|ncat|socat|python|perl|php)" | grep -v grep

echo -e "\n=== 网络连接检查 ==="
netstat -tulnp 2>/dev/null || ss -tulnp

echo -e "\n=== 系统服务检查 ==="
systemctl list-unit-files --type=service --state=enabled 2>/dev/null | grep -v "@" | head -30

echo -e "\n=== 最近修改的文件 ==="
find /etc -mmin -60 -type f 2>/dev/null
find /tmp -mmin -60 -type f 2>/dev/null
```

#### 4.2.2 Rootkit检测

```bash
# 使用rkhunter检测
apt install rkhunter
rkhunter --update
rkhunter --check

# 使用chkrootkit检测
apt install chkrootkit
chkrootkit
```

#### 4.2.3 完整性检查

```bash
# 使用AIDE（高级入侵检测环境）
apt install aide
aideinit
# 生成基线数据库后，定期运行检查
aide --check
```

### 4.3 监控与告警

#### 4.3.1 文件监控

**使用inotifywait监控关键文件：**
```bash
#!/bin/bash
# 监控king.txt文件变化

inotifywait -m /root/king.txt -e modify -e create -e delete |
while read path action file; do
    echo "$(date): $action on $file"
    # 可以在这里添加告警逻辑
    # 比如发送邮件、调用webhook等
done
```

#### 4.3.2 登录监控

```bash
# 监控SSH登录
# 在.bashrc或/etc/profile中添加
echo "$(date): $USER logged in from $SSH_CLIENT" >> /var/log/login_monitor.log

# 实时监控日志
tail -f /var/log/auth.log | grep --line-buffered "Accepted" | while read line; do
    echo "ALERT: New SSH login: $line"
    # 发送告警
done
```

#### 4.3.3 进程监控

```bash
# 监控可疑进程
#!/bin/bash
while true; do
    # 检查是否有新的bash进程
    bash_count=$(ps aux | grep -c "[b]ash")
    if [ $bash_count -gt 2 ]; then
        echo "$(date): ALERT - Unexpected bash processes detected"
        ps aux | grep "[b]ash"
    fi
    sleep 5
done
```

### 4.4 反击对手技术

防御不仅是守住自己的阵地，还可以主动出击，反击对手。

#### 4.4.1 溯源反制

**1. 收集攻击者信息**
```bash
# 查看登录日志
grep "Failed password" /var/log/auth.log | tail -20
grep "Accepted" /var/log/auth.log | tail -20

# 查看攻击者IP
last -i

# 查看Web访问日志
tail -100 /var/log/apache2/access.log
tail -100 /var/log/nginx/access.log
```

**2. 分析攻击手段**
- 查看攻击者留下的文件和工具
- 分析攻击流量的特征
- 了解对手的技术水平和习惯

#### 4.4.2 主动反击

**1. 反向渗透**
- 如果攻击者上传了WebShell，分析其代码，找到可利用的信息
- 利用攻击者留下的工具反制攻击者
- 注意：反击的合法性取决于比赛规则

**2. 蜜罐技术**
```bash
# 创建假的flag文件，监控访问
inotifywait -m /fake_flag.txt -e access |
while read path action file; do
    echo "Someone accessed the fake flag!"
    # 记录攻击者信息
    who | grep -v `whoami`
done
```

**3. 日志伪造与欺骗**
- 在日志中植入假的漏洞信息
- 创建假的管理后台，诱导攻击者尝试
- 制造系统已崩溃的假象，让对手转向其他目标

---

---

## 📋 内容审核与补充建议

> 针对「KotH防御策略」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
