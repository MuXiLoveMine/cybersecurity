# Linux日志系统

### 5.1 journalctl日志管理

```bash
# 查看所有日志
journalctl                          # 所有日志
journalctl --no-pager              # 不分页
journalctl -n 50                    # 最近50条
journalctl -f                       # 实时跟踪

# 按服务查看
journalctl -u sshd                  # SSH服务日志
journalctl -u nginx                 # Nginx日志
journalctl -u docker                # Docker日志

# 按时间过滤
journalctl --since today
journalctl --since "2024-01-01" --until "2024-01-31"
journalctl --since "1 hour ago"
journalctl --since "2024-01-01 12:00:00"

# 按优先级过滤
journalctl -p err                   # 错误及以上
journalctl -p warning              # 警告及以上
journalctl -p crit                  # 严重及以上
journalctl -p alert                 # 警报及以上
journalctl -p emerg                # 紧急

# 按进程查看
journalctl _PID=1234
journalctl _UID=1000
journalctl _GID=1000

# 按可执行文件
journalctl /usr/bin/sshd
journalctl /usr/sbin/nginx

# 按启动会话
journalctl --list-boots            # 列出所有启动会话
journalctl -b 0                   # 当前启动会话
journalctl -b -1                   # 上一次启动

# 日志磁盘使用
journalctl --disk-usage

# 限制日志大小
journalctl --vacuum-size=500M      # 限制日志500MB
journalctl --vacuum-time=30d       # 保留30天

# 配置日志持久化
# /etc/systemd/journald.conf
[Journal]
Storage=persistent                 # 持久化存储
Compress=yes                       # 压缩
SystemMaxUse=1G                    # 最大使用1GB
SystemMaxFileSize=100M             # 单个文件最大100MB
MaxRetentionSec=30day             # 保留30天
RateLimitInterval=30s              # 速率限制
RateLimitBurst=1000                # 突发限制
```

### 5.2 rsyslog配置

```bash
# /etc/rsyslog.conf 或 /etc/rsyslog.d/*.conf

# 模块加载
module(load="imuxsock")            # Unix套接字
module(load="imklog")              # 内核日志
module(load="imudp")              # UDP输入
module(load="imtcp")              # TCP输入

# UDP输入配置
input(type="imudp" port="514")
input(type="imtcp" port="514")

# 规则配置
# 设施.级别 动作
auth,authpriv.*        /var/log/auth.log
mail.*                 /var/log/mail.log
cron.*                 /var/log/cron.log
*.emerg                :omusrmsg:*
local5.*               /var/log/custom.log

# 远程日志服务器
*.* @@logserver.example.com:514    # TCP发送
*.* @logserver.example.com:514     # UDP发送

# 模板配置
template(name="RemoteLogs" type="string"
    string="/var/log/remote/%HOSTNAME%/%PROGRAMNAME%.log"
)

# 使用模板
*.* ?RemoteLogs

# 安全加固
$FileCreateMode 0640               # 日志文件权限
$DirCreateMode 0750                # 目录权限
$umask 0037                        # umask设置
$PrivDropToGroup syslog            # 降权到syslog组
```

### 5.3 auditd审计系统

```bash
# 安装和启动
apt install auditd
systemctl enable auditd
systemctl start auditd

# 审计规则配置 /etc/audit/audit.rules
# 监控文件访问
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/sudoers -p wa -k sudo_changes
-w /etc/ssh/sshd_config -p wa -k ssh_config

# 监控命令执行
-w /bin/su -p x -k privileged
-w /bin/sudo -p x -k privileged
-w /usr/bin/passwd -p x -k privileged
-w /bin/mount -p x -k privileged
-w /bin/umount -p x -k privileged

# 监控系统调用
-a always,exit -F arch=b64 -S open -S openat -F auid>=1000 -F auid!=4294967295 -k file_access
-a always,exit -F arch=b64 -S chmod -S fchmod -S chown -S fchown -F auid>=1000 -k perm_change

# 监控网络配置
-w /etc/network/ -p wa -k network_config
-w /etc/resolv.conf -p wa -k network_config
-w /etc/hosts -p wa -k network_config

# 监控cron
-w /etc/crontab -p wa -k cron
-w /etc/cron.d/ -p wa -k cron
-w /etc/cron.daily/ -p wa -k cron
-w /var/spool/cron/ -p wa -k cron

# 监控模块加载
-w /sbin/insmod -p x -k modules
-w /sbin/rmmod -p x -k modules
-w /sbin/modprobe -p x -k modules
-a always,exit -F arch=b64 -S init_module -S delete_module -k modules

# 查看审计日志
ausearch -k identity                # 按关键词搜索
ausearch -k ssh_config
ausearch -ts today                  # 今天的日志
ausearch -ts "2024-01-01" -te "2024-01-31"
ausearch -m USER_LOGIN              # 按消息类型
ausearch -ui 1000                   # 按用户ID
ausearch -f /etc/passwd              # 按文件

# 生成审计报告
aureport --summary                  # 摘要报告
aureport --file                     # 文件访问报告
aureport --user                     # 用户活动报告
aureport --failed                   # 失败事件
aureport --start today              # 今天的报告
```

### 5.4 日志集中管理

```bash
# 使用rsyslog转发到集中服务器
cat > /etc/rsyslog.d/forward.conf << 'EOF'
# 使用TCP转发（更可靠）
*.* action(type="omfwd"
    target="logserver.example.com"
    port="6514"
    protocol="tcp"
    StreamDriver="gtls"
    StreamDriverMode="1"
    StreamDriverAuthMode="x509/name"
    StreamDriverPermittedPeers="logserver.example.com")

# 本地保留副本
*.* /var/log/local-backup.log
& stop
EOF

systemctl restart rsyslog
```

---

---

