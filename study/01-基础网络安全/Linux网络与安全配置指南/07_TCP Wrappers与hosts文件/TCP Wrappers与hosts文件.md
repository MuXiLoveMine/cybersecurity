# TCP Wrappers与hosts文件

```bash
# /etc/hosts.allow - 允许规则
# 格式: 服务: 客户端 [: 命令]

# 允许SSH特定IP
sshd: 192.168.1.0/24 192.168.2.100
sshd: .example.com

# 允许所有服务给localhost
ALL: 127.0.0.1 [::1]

# 允许特定服务
vsftpd: 192.168.1.0/24
nginx: ALL

# 带动作的规则
sshd: 192.168.1.100: spawn echo "%h attempted access" >> /var/log/sshd_access.log

# /etc/hosts.deny - 拒绝规则
# 拒绝所有（默认拒绝策略）
ALL: ALL

# 拒绝特定IP
ALL: 10.0.0.0/8
sshd: ALL EXCEPT 192.168.1.0/24

# 带日志的拒绝
ALL: ALL: spawn echo "%h connect to %d" >> /var/log/tcpd.log

# 注意：hosts.allow优先于hosts.deny
# 检查tcpd是否编译到服务中
ldd /usr/sbin/sshd | grep wrap
```

---

---

