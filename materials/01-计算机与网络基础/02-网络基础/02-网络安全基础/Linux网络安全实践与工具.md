# Linux 网络安全实践与工具

> 本文系统介绍 Linux 网络安全实践与常用工具：网络配置与排查、防火墙工具、安全加固（SSH/PAM/SELinux/AppArmor）、入侵检测（Snort/Suricata/OSSEC/AIDE）、加密与证书、日志与审计、安全基线检查与自动化。所有命令均标注权限和风险提示，面向运维工程师和安全工程师，仅限授权环境使用。

---

## 目录

- [一、网络配置与排查](#一网络配置与排查)
- [二、防火墙工具](#二防火墙工具)
- [三、安全加固](#三安全加固)
- [四、入侵检测与完整性](#四入侵检测与完整性)
- [五、加密与证书](#五加密与证书)
- [六、日志与审计](#六日志与审计)
- [七、安全基线检查与自动化](#七安全基线检查与自动化)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、网络配置与排查

### 1.1 ip 命令（iproute2 工具集）

`ip` 是现代 Linux 网络配置的核心工具，替代了传统的 ifconfig/route/arp 等。

```bash
# ===== 接口管理 =====
ip link show                    # 查看所有接口
ip link show eth0               # 查看指定接口
ip -s link show eth0            # 查看接口统计（收发包、错误、丢弃）
ip link set eth0 up             # 启用接口🔑
ip link set eth0 down           # 关闭接口🔑
ip link set eth0 mtu 1500       # 设置 MTU🔑
ip link set eth0 address 00:11:22:33:44:55  # 修改 MAC 地址🔑

# ===== 地址管理 =====
ip addr show                    # 查看所有地址
ip addr show eth0               # 查看指定接口地址
ip addr add 192.168.1.100/24 dev eth0    # 添加地址🔑
ip addr del 192.168.1.100/24 dev eth0    # 删除地址🔑
ip addr flush dev eth0          # 清空接口地址🔑

# ===== 路由管理 =====
ip route show                   # 查看路由表
ip route show table main        # 指定路由表
ip route add default via 192.168.1.1     # 添加默认路由🔑
ip route add 10.0.0.0/8 via 192.168.1.2  # 添加静态路由🔑
ip route del 10.0.0.0/8         # 删除路由🔑
ip route get 8.8.8.8            # 查看某个地址走哪条路由

# ===== 邻居（ARP）管理 =====
ip neigh show                   # 查看 ARP 表
ip neigh add 192.168.1.1 lladdr 00:11:22:33:44:55 dev eth0  # 静态 ARP🔑
ip neigh del 192.168.1.1 dev eth0       # 删除 ARP 条目🔑
ip neigh flush all              # 清空 ARP 表🔑
```

> ⚠️ **远程操作警告**：`ip link set down`、`ip addr flush`、修改路由等操作可能导致网络中断，远程操作务必小心。建议配合 `at now + 5 min` 做定时回滚。

### 1.2 ss 命令（socket 统计）

`ss` 是 netstat 的替代工具，速度更快，功能更强。

```bash
# ===== 基础查看 =====
ss -t -a                        # 所有 TCP 连接
ss -u -a                        # 所有 UDP 连接
ss -tlnp                        # TCP 监听端口 + 进程（最常用）🔑
ss -ulnp                        # UDP 监听端口 + 进程🔑
ss -s                           # 连接统计汇总
ss -ta state established        # 已建立的 TCP 连接

# ===== 过滤 =====
ss dst 192.168.1.100            # 目的地址
ss src 192.168.1.100            # 源地址
ss dport = :80                  # 目的端口
ss sport = :22                  # 源端口
ss -t state time-wait           # 指定状态
ss -t state established '( dport = :443 or dport = :80 )'  # 组合过滤

# ===== 详细信息 =====
ss -t -e                        # 显示扩展信息（uid、inode 等）
ss -t -o                        # 显示定时器信息（重传等）
ss -t -i                        # 显示内部 TCP 信息
ss -t -m                        # 显示内存使用
```

### 1.3 tcpdump 抓包

```bash
# ⚠️ 抓包需要 root 权限，且涉及隐私和合规问题，仅限授权环境使用

# ===== 基本抓包 =====
tcpdump -i eth0                 # 指定接口抓包
tcpdump -i any                  # 所有接口
tcpdump -D                      # 列出可用接口
tcpdump -n                      # 不解析域名和端口（数字显示，更快）
tcpdump -nn                     # IP 和端口都不解析
tcpdump -v                      # 详细输出
tcpdump -vv                     # 更详细
tcpdump -c 100                  # 抓 100 个包就停
tcpdump -w capture.pcap         # 保存到文件
tcpdump -r capture.pcap         # 读取保存的文件

# ===== 常用过滤表达式 =====
# 主机过滤
tcpdump host 192.168.1.1
tcpdump src host 192.168.1.1
tcpdump dst host 192.168.1.1

# 端口过滤
tcpdump port 80
tcpdump port 80 or 443
tcpdump portrange 1-1024
tcpdump src port 22
tcpdump dst port 443

# 协议过滤
tcpdump tcp
tcpdump udp
tcpdump icmp
tcpdump arp
tcpdump ip
tcpdump ip6

# 组合过滤（and / or / not）
tcpdump 'tcp port 443 and host 192.168.1.100'
tcpdump 'port 80 or port 443'
tcpdump 'not port 22'
tcpdump 'icmp and src host 192.168.1.1'

# TCP 标志位过滤
tcpdump 'tcp[tcpflags] & tcp-syn != 0'      # 只有 SYN 位
tcpdump 'tcp[tcpflags] & tcp-rst != 0'      # RST 包
tcpdump 'tcp[tcpflags] == tcp-syn'          # 只有 SYN（连接请求）

# ===== 高级用法 =====
tcpdump -i eth0 -s 0 -w capture.pcap       # 抓完整包（-s 0 = 不截断）
tcpdump -i eth0 -G 3600 -w capture_%Y%m%d_%H%M.pcap  # 每小时生成一个文件
tcpdump -r capture.pcap -nn -tttt          # 读取文件，显示绝对时间
tcpdump -r capture.pcap -c 10 -A           # ASCII 方式显示（看 HTTP 内容）
tcpdump -r capture.pcap -c 10 -X           # 十六进制 + ASCII

# ===== 过滤 HTTP =====
tcpdump -i eth0 -A -s 0 'tcp port 80'      # HTTP 明文
tcpdump -i eth0 'tcp port 443'             # HTTPS（只能看到握手，内容是加密的）
```

> ⚠️ **安全警告**：
> - 抓包可能包含敏感信息（密码、数据内容等），需遵守隐私和合规要求
> - 抓包文件要妥善保管，使用后安全删除
> - 仅限授权的网络范围内抓包

### 1.4 nmap 网络扫描

> ⚠️ **重要警告**：端口扫描可能被视为攻击行为，**仅限对自己管理的、有明确授权的系统进行扫描**。未经授权扫描他人系统可能违法。

```bash
# ===== 基础扫描 =====
nmap 192.168.1.1                 # 扫描单个 IP
nmap 192.168.1.0/24              # 扫描网段
nmap 192.168.1.1-100             # 扫描地址范围
nmap -iL targets.txt             # 从文件读取目标

# ===== 主机发现 =====
nmap -sn 192.168.1.0/24          # 只做存活扫描（不扫端口）
nmap -Pn 192.168.1.1             # 跳过主机发现，假设主机存活（禁 ping 时用）
nmap -PS 192.168.1.1             # TCP SYN 发现
nmap -PA 80,443 192.168.1.1      # TCP ACK 发现
nmap -PU 192.168.1.1             # UDP 发现

# ===== 端口扫描技术 =====
nmap -sS 192.168.1.1             # SYN 半开放扫描（默认，需要 root🔑）
nmap -sT 192.168.1.1             # TCP 全连接扫描（不需要 root）
nmap -sU 192.168.1.1             # UDP 扫描🔑
nmap -sA 192.168.1.1             # ACK 扫描（探测防火墙规则）🔑
nmap -sF 192.168.1.1             # FIN 扫描（隐蔽扫描）🔑
nmap -sN 192.168.1.1             # Null 扫描🔑
nmap -sX 192.168.1.1             # Xmas 扫描🔑

# ===== 端口指定 =====
nmap -p 22 192.168.1.1           # 指定单个端口
nmap -p 22,80,443 192.168.1.1    # 多个端口
nmap -p 1-1000 192.168.1.1       # 端口范围
nmap -p- 192.168.1.1             # 全端口扫描（1-65535）
nmap --top-ports 100 192.168.1.1 # 最常用的 100 个端口
nmap -F 192.168.1.1              # 快速扫描（100 个知名端口）

# ===== 服务与版本检测 =====
nmap -sV 192.168.1.1             # 服务版本检测
nmap -sV --version-intensity 5 192.168.1.1  # 检测强度（0-9，越高越详细越慢）
nmap -O 192.168.1.1              # 操作系统检测🔑

# ===== 脚本扫描（NSE） =====
nmap --script=default 192.168.1.1     # 默认脚本
nmap --script=safe 192.168.1.1        # 安全脚本（不破坏）
nmap --script=auth 192.168.1.1        # 认证相关脚本
nmap --script=vuln 192.168.1.1        # 漏洞检测脚本（⚠️ 可能有风险）
nmap --script=http-enum 192.168.1.1   # HTTP 目录枚举
nmap --script=ssl-enum-ciphers 192.168.1.1 -p 443  # SSL 密码套件枚举
nmap --script=banner 192.168.1.1      # 服务 banner 抓取

# ===== 输出 =====
nmap -oN result.txt 192.168.1.1       # 普通文本输出
nmap -oX result.xml 192.168.1.1       # XML 输出
nmap -oG result.gnmap 192.168.1.1     # Grep 友好格式
nmap -oA result 192.168.1.1           # 所有格式都输出

# ===== 性能与计时 =====
nmap -T0 192.168.1.1             # 最慢（躲避检测）
nmap -T1 192.168.1.1             # 慢
nmap -T2 192.168.1.1             # 礼貌
nmap -T3 192.168.1.1             # 正常（默认）
nmap -T4 192.168.1.1             # 快（推荐在可靠网络用）
nmap -T5 192.168.1.1             # 最快（可能漏报）

# ===== 常用组合 =====
nmap -sV -sC -O 192.168.1.1      # 版本检测 + 默认脚本 + 系统检测🔑
nmap -sn 192.168.1.0/24          # 存活主机发现
nmap -p- -sV -T4 192.168.1.1     # 全端口 + 版本检测（慢但全）🔑
```

> ⚠️ **使用警告**：
> - 扫描前确保有明确的书面授权
> - 生产环境使用低强度模式（避免影响业务）
> - `-T4` 及以上可能导致网络拥塞或目标系统异常
> - 漏洞扫描脚本（`--script=vuln`）可能对目标造成影响，谨慎使用

---

## 二、防火墙工具

本节给出核心要点和速查表，详细用法请参考《边界防护、检测与响应》文档。

### 2.1 四大防火墙工具对比

| 工具 | 底层 | 默认系统 | 特点 | 适用场景 |
|------|------|---------|------|---------|
| **iptables** | netfilter | 旧版系统 | 经典、灵活、功能强大 | 需要精细控制 |
| **nftables** | nf_tables | 新系统（Debian 11+/RHEL 8+） | 新一代、语法简洁、性能好 | 新系统推荐 |
| **firewalld** | iptables/nftables | RHEL/CentOS/Fedora | 动态管理、zone 概念 | RHEL 系服务器 |
| **ufw** | iptables | Ubuntu | 简单易用 | 桌面/简单服务器 |

### 2.2 快速参考

```bash
# ===== iptables 速查 =====
# 查看
iptables -L -n -v --line-numbers
iptables -t nat -L -n -v

# 默认策略
iptables -P INPUT DROP

# 常用规则
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# NAT
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth0 -j MASQUERADE
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 8080 -j DNAT --to 192.168.1.10:80

# ===== firewalld 速查 =====
firewall-cmd --add-service=ssh --permanent
firewall-cmd --add-port=8080/tcp --permanent
firewall-cmd --add-source=192.168.1.0/24 --zone=trusted --permanent
firewall-cmd --reload

# ===== ufw 速查 =====
ufw allow 22/tcp
ufw allow from 192.168.1.0/24 to any port 22
ufw limit 22/tcp
ufw enable
```

> ⚠️ **防火墙操作警告**：
> - 远程修改防火墙前，先开一个备用连接或设置定时回滚
> - 先加允许规则再改默认拒绝策略，避免把自己关在外面
> - 修改前备份配置

---

## 三、安全加固

### 3.1 SSH 安全加固

```bash
# ===== 配置文件 =====
# /etc/ssh/sshd_config
# ⚠️ 修改前备份：cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# ===== 核心加固项 =====
# 1. 禁止 root 直接登录
PermitRootLogin no
# 或允许密钥不允许密码
PermitRootLogin prohibit-password

# 2. 禁用密码认证（确认密钥登录可用后再改！）
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM yes  # 配合 PAM 做额外的认证和审计

# 3. 只允许特定用户/组
AllowUsers alice bob
AllowGroups sshusers ops
DenyUsers baduser
DenyGroups badgroup

# 4. 更改默认端口（隐蔽性辅助，不是主要安全手段）
Port 2222

# 5. 登录防护
MaxAuthTries 3            # 最大尝试次数
LoginGraceTime 30         # 登录宽限时间（秒）
MaxSessions 5             # 最大并发会话
ClientAliveInterval 300   # 空闲超时检测间隔
ClientAliveCountMax 2     # 最大无响应次数（300*2=600秒后断开）

# 6. 密钥相关
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no

# 7. 禁用不安全的特性
X11Forwarding no
AllowTcpForwarding no     # 不需要端口转发就关
AllowAgentForwarding no   # 不需要 agent 转发就关
PermitTunnel no

# 8. 协议和算法（只使用安全的算法）
Protocol 2
KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# ===== 重启服务 =====
# ⚠️ 保持一个会话不关闭，新开会话测试通过再关！
systemctl restart sshd

# ===== 配置检查 =====
sshd -t                       # 检查配置语法🔑
sshd -T                       # 显示生效的配置🔑

# ===== fail2ban 防护 =====
# 防止 SSH 暴力破解
apt install fail2ban / yum install fail2ban
# 在 /etc/fail2ban/jail.local 中启用 sshd
fail2ban-client status sshd
```

### 3.2 PAM 加固

详见《身份认证与访问控制》文档，以下为核心要点：

```bash
# ===== 密码复杂度 =====
# Debian/Ubuntu
apt install libpam-pwquality
# 配置：/etc/security/pwquality.conf

# RHEL/CentOS
yum install libpwquality
# 配置文件同上

# ===== 登录失败锁定 =====
# pam_faillock（RHEL 8+、新系统）
# 配置：/etc/security/faillock.conf
# deny = 5
# unlock_time = 300
# even_deny_root

faillock --user alice          # 查看失败记录
faillock --user alice --reset  # 解锁用户🔑

# ===== 密码历史 =====
# password required pam_pwhistory.so remember=5
# 不能重复最近 5 次密码
```

### 3.3 SELinux

**SELinux（Security-Enhanced Linux）**：强制访问控制（MAC）安全模块，由 NSA 开发，已合入 Linux 内核。RHEL/CentOS/Fedora 默认启用。

```bash
# ===== 状态查看 =====
getenforce                     # 查看模式（Enforcing/Permissive/Disabled）
sestatus                       # 详细状态
ps -eZ                         # 查看进程的安全上下文
ls -Z                          # 查看文件的安全上下文
id -Z                          # 查看当前用户的安全上下文

# ===== 模式切换 =====
# 临时切换（重启失效）🔑
setenforce 0                   # Permissive（只告警不阻止）
setenforce 1                   # Enforcing（强制模式）

# 永久切换（修改 /etc/selinux/config）
# SELINUX=enforcing
# SELINUX=permissive
# SELINUX=disabled
# ⚠️ 从 disabled 切到 enforcing 需要重启并重新打标签

# ===== 常见操作 =====
# 查看布尔值
getsebool -a | grep httpd
getsebool httpd_can_network_connect

# 修改布尔值🔑
setsebool httpd_can_network_connect on
setsebool -P httpd_can_network_connect on    # -P 永久生效

# 查看和修改文件上下文
ls -Z /var/www/html/
chcon -R -t httpd_sys_content_t /var/www/html/   # 修改上下文🔑
restorecon -Rv /var/www/html/                    # 恢复默认上下文🔑

# 添加端口上下文🔑
semanage port -l | grep http
semanage port -a -t http_port_t -p tcp 8080

# ===== 日志与排错 =====
# SELinux 拒绝日志在 /var/log/audit/audit.log
grep "denied" /var/log/audit/audit.log

# sealert 工具分析告警（setroubleshoot-server）
sealert -a /var/log/audit/audit.log

# 生成允许规则模块（解决某个拒绝问题）
ausearch -m avc -ts recent | audit2allow -M mypolicy
semodule -i mypolicy.pp

# ⚠️ 警告：不要一上来就关 SELinux！先分析为什么被阻止，通常是标签错了
```

### 3.4 AppArmor

**AppArmor**：另一个 MAC 系统，比 SELinux 简单，Ubuntu/SUSE 默认使用。基于路径配置，比 SELinux 的标签模型更容易理解。

```bash
# ===== 状态查看 =====
apparmor_status                # 查看状态
aa-status                      # 同上
aa-unconfined                  # 查看没有被限制的进程

# ===== 配置文件位置 =====
# /etc/apparmor.d/   每个程序一个配置文件
# /etc/apparmor.d/usr.sbin.apache2 示例

# ===== 模式 =====
# enforce 模式：强制，违反就阻止
# complain 模式：只记录不阻止（学习/调试用）

# 切换模式🔑
aa-complain /usr/sbin/apache2   # 改成 complain 模式
aa-enforce /usr/sbin/apache2    # 改成 enforce 模式

# ===== 创建/更新配置 =====
# 1. 生成基本配置
aa-genprof /usr/bin/program     # 生成配置文件🔑

# 2. 让程序运行一段时间，收集日志
aa-logprof                     # 根据日志更新规则🔑

# ===== 禁用/启用 =====
aa-disable /usr/sbin/apache2    # 禁用某个配置🔑
aa-enable /usr/sbin/apache2     # 启用🔑
```

---

## 四、入侵检测与完整性

### 4.1 Snort / Suricata

详见《边界防护、检测与响应》文档，以下为快速参考：

```bash
# ===== Snort =====
# 安装
apt install snort / yum install snort

# IDS 模式
snort -c /etc/snort/snort.conf -i eth0 -q

# ===== Suricata =====
# 安装
apt install suricata / yum install suricata

# 测试配置
suricata -T -c /etc/suricata/suricata.yaml

# IDS 模式
suricata -c /etc/suricata/suricata.yaml -i eth0

# 规则管理
suricata-update list-sources
suricata-update enable-source et/open
suricata-update
```

### 4.2 OSSEC（主机入侵检测）

**OSSEC**：开源的主机入侵检测系统（HIDS），支持日志分析、文件完整性监控、rootkit 检测、主动响应等。

```bash
# ===== 安装 =====
# 服务端/客户端模式，或单机模式
# 下载源码编译安装或用包管理器

# ===== 主要功能 =====
# 1. 日志分析 - 分析系统日志和应用日志
# 2. 文件完整性监控 - 监控文件变化
# 3. Rootkit 检测 - 检测 rootkit 和后门
# 4. 主动响应 - 发现攻击后自动响应（封禁 IP 等）

# ===== 常用命令 =====
/var/ossec/bin/ossec-control start    # 启动
/var/ossec/bin/ossec-control status   # 状态

# 完整性检查
/var/ossec/bin/syscheck_control -l            # 列出监控的文件
/var/ossec/bin/syscheck_control -u 001        # 运行完整性扫描

# 告警查看
tail -f /var/ossec/logs/alerts/alerts.log

# Rootkit 检测
/var/ossec/bin/rootcheck_control -u 001       # 运行 rootkit 检测

# ===== 配置文件 =====
# /var/ossec/etc/ossec.conf
# 主要配置项：
#   <global>        全局配置
#   <syscheck>      文件完整性监控
#   <rootcheck>     Rootkit 检测
#   <localfile>     监控的日志文件
#   <rules>         规则配置
```

### 4.3 AIDE（文件完整性检查）

**AIDE（Advanced Intrusion Detection Environment）**：文件完整性检查工具，通过对比基线检测文件变化。

```bash
# ===== 安装 =====
apt install aide
yum install aide

# ===== 初始化 =====
# 生成初始数据库（基线）🔑
aide --init
# 输出文件在 /var/lib/aide/aide.db.new.gz
# 需要把它移到正式位置
cp /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
# ⚠️ 基线数据库要妥善保管，最好离线存储！

# ===== 检查 =====
# 运行完整性检查
aide --check
aide -C                        # 简写

# 只检查特定文件
aide --check --limit /etc/passwd

# ===== 更新数据库 =====
# 检查后更新数据库（确认变化是正常的）🔑
aide --update
# 会生成新的数据库，需要手动替换
cp /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz

# ===== 配置文件 =====
# /etc/aide.conf
# /etc/aide.conf.d/

# 配置示例：
# # 规则定义
# Normal = p+u+g+s+m+c+acl+selinux+xattrs+sha256
# 
# # 监控的路径（前面加 / 表示监控）
# /bin Normal
# /sbin Normal
# /usr/sbin Normal
# /usr/bin Normal
# /etc Normal
# 
# # 不监控的（前面加 ! 表示排除）
# !/etc/mtab
# !/etc/adjtime
# !/var/log
# !/var/tmp

# ===== 自动化 =====
# 可以加到 cron 里每天运行，有变化就发邮件
# 0 2 * * * /usr/sbin/aide --check | mail -s "AIDE report" admin@example.com
```

> ⚠️ **AIDE 使用要点**：
> - 基线数据库必须在系统干净的时候建立
> - 基线数据库要存放在安全的地方（离线/只读）
> - 每次系统变更（安装软件、改配置）后要更新基线
> - 检查出变化要分析是正常变更还是入侵导致的

### 4.4 rkhunter（Rootkit 检测）

```bash
# ===== 安装 =====
apt install rkhunter
yum install rkhunter

# ===== 基本用法 =====
# 更新数据文件
rkhunter --update

# 系统基准线（干净系统时运行）🔑
rkhunter --propupd

# 扫描系统
rkhunter --check
rkhunter -c --sk             # --sk 不按键继续

# 详细模式
rkhunter -c -l /var/log/rkhunter.log

# ===== 配置 =====
# /etc/rkhunter.conf
# 主要配置项：
#   ENABLE_TESTS   启用哪些检测
#   DISABLE_TESTS  禁用哪些检测
#   ALLOW_SSH_ROOT_USER  允许 SSH root 登录（避免误报）
#   SCRIPTWHITELIST 脚本白名单

# ===== 自动化 =====
# 加入 cron 定时扫描
```

---

## 五、加密与证书

详见《密码学与安全协议》文档，以下为核心工具速查：

### 5.1 openssl

```bash
# ===== 哈希 =====
openssl sha256 file.txt
openssl md5 file.txt

# ===== 对称加密 =====
openssl enc -aes-256-cbc -salt -in file.txt -out file.enc    # 加密
openssl enc -aes-256-cbc -d -in file.enc -out file.txt       # 解密

# ===== 非对称加密（RSA） =====
openssl genrsa -out private.key 2048                          # 生成私钥
openssl rsa -in private.key -pubout -out public.key          # 提取公钥

# ===== 数字签名 =====
openssl dgst -sha256 -sign private.key -out file.sig file.txt  # 签名
openssl dgst -sha256 -verify public.key -signature file.sig file.txt  # 验证

# ===== 证书 =====
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes  # 自签名证书
openssl x509 -in cert.pem -text -noout                            # 查看证书
openssl s_client -connect example.com:443 -servername example.com # 测试 TLS 连接

# ===== HMAC =====
openssl dgst -sha256 -hmac "secret" file.txt
```

### 5.2 ssh-keygen

```bash
# 生成 Ed25519 密钥对（推荐）
ssh-keygen -t ed25519 -C "alice@example.com"

# 生成 RSA 4096 位
ssh-keygen -t rsa -b 4096 -C "alice@example.com"

# 查看指纹
ssh-keygen -lf ~/.ssh/id_ed25519.pub

# 分发公钥
ssh-copy-id user@server

# 删除 known_hosts 条目
ssh-keygen -R hostname
```

### 5.3 gpg

```bash
# 生成密钥对
gpg --full-gen-key

# 加密文件
gpg -e -r alice@example.com file.txt

# 解密文件
gpg -d file.txt.gpg

# 签名
gpg -s file.txt
gpg -b file.txt   # 分离签名

# 验证签名
gpg --verify file.txt.sig file.txt

# 导入/导出公钥
gpg --export -a alice@example.com > public.key
gpg --import public.key
```

---

## 六、日志与审计

### 6.1 journalctl（systemd 日志）

```bash
# ===== 基本查看 =====
journalctl                       # 所有日志
journalctl -b                    # 本次启动的日志
journalctl -b -1                 # 上次启动的日志
journalctl -k                    # 内核日志（dmesg 风格）
journalctl -u sshd.service       # 指定服务
journalctl -u nginx.service -u php-fpm.service  # 多个服务

# ===== 时间过滤 =====
journalctl --since "2024-01-01"
journalctl --since "2024-01-01 10:00" --until "2024-01-01 12:00"
journalctl --since "1 hour ago"
journalctl --since yesterday
journalctl --since today --until "1 hour ago"

# ===== 优先级过滤 =====
journalctl -p err               # error 及以上
journalctl -p warning           # warning 及以上
# 级别：0=emerg 1=alert 2=crit 3=err 4=warning 5=notice 6=info 7=debug

# ===== 实时跟踪 =====
journalctl -f                    # 实时跟踪（类似 tail -f）
journalctl -u sshd -f            # 跟踪某个服务

# ===== 输出格式 =====
journalctl -o short              # 默认格式
journalctl -o verbose            # 详细格式
journalctl -o json               # JSON 格式
journalctl -o json-pretty        # 格式化 JSON
journalctl --no-pager            # 不分页（适合脚本）

# ===== 字段过滤 =====
journalctl _PID=1234             # 按 PID
journalctl _UID=1000             # 按 UID
journalctl _HOSTNAME=server1     # 按主机名
journalctl SYSLOG_IDENTIFIER=sshd  # 按标识

# ===== 日志管理 =====
journalctl --disk-usage          # 日志占用空间
journalctl --vacuum-size=500M    # 清理到 500M 以内🔑
journalctl --vacuum-time=30d     # 清理 30 天前的🔑

# ===== 配置 =====
# /etc/systemd/journald.conf
# SystemMaxUse=500M      # 最大占用空间
# SystemMaxFileSize=50M  # 单个文件最大
# MaxRetentionSec=1month # 最长保留时间
```

### 6.2 auditd（审计守护进程）

**auditd** 是 Linux 内核级审计系统，可以记录非常详细的系统操作，是合规审计的重要工具。

```bash
# ===== 安装 =====
apt install auditd
yum install audit

# ===== 服务管理 =====
systemctl start auditd
systemctl enable auditd

# ===== 查看审计日志 =====
# 日志文件：/var/log/audit/audit.log

# aureport - 生成报告
aureport                       # 总览报告
aureport -a                    # 认证事件报告
aureport -l                    # 登录报告
aureport -f                    # 文件访问报告
aureport -x                    # 可执行文件报告
aureport -k --key password-file  # 按 key 过滤

# ausearch - 搜索审计日志
ausearch -m SYSCALL            # 按消息类型搜索
ausearch -f /etc/passwd        # 按文件搜索
ausearch -k password-file      # 按规则 key 搜索
ausearch -ua alice             # 按用户搜索
ausearch -ts today -m USER_AUTH  # 时间 + 类型
ausearch -p 1234               # 按 PID 搜索

# ===== 审计规则管理 =====
auditctl -l                    # 列出当前规则🔑

# 文件系统审计（监控文件/目录访问）🔑
auditctl -w /etc/passwd -p wa -k password-file
# -w 监控路径
# -p 权限（r=读 w=写 x=执行 a=属性变更）
# -k 关键字，方便搜索过滤

# 监控目录
auditctl -w /etc/ -p wa -k etc-changes

# 系统调用审计🔑
auditctl -a always,exit -F arch=b64 -S execve -k command-execution
# 监控所有 execve 系统调用（命令执行）

# 删除规则🔑
auditctl -W /etc/passwd -p wa -k password-file
auditctl -D                    # 删除所有规则

# ===== 永久规则 =====
# /etc/audit/rules.d/audit.rules
# 写入文件后重启 auditd 或用 augenrules --load 加载

# ===== 常见审计规则示例 =====
# 1. 监控密码相关文件
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity

# 2. 监控 sudo 和 su
-w /usr/bin/sudo -p x -k privileged
-w /usr/bin/su -p x -k privileged

# 3. 监控登录和认证
-w /var/log/faillog -p wa -k logins
-w /var/log/lastlog -p wa -k logins
-w /var/log/tallylog -p wa -k logins

# 4. 监控审计配置本身
-w /etc/audit/ -p wa -k audit-config
-w /etc/audit/rules.d/ -p wa -k audit-config
```

> ⚠️ **auditd 注意事项**：
> - 审计规则太多会产生大量日志，影响性能
> - 要合理规划监控范围，只监控重要的内容
> - 审计日志本身要保护好，防止被篡改
> - 日志量要规划好存储空间
> - 日志留存期按合规要求配置

### 6.3 rsyslog

```bash
# ===== 配置文件 =====
# /etc/rsyslog.conf
# /etc/rsyslog.d/*.conf

# ===== 日志设施和级别 =====
# 设施（Facility）：
#   auth, authpriv, cron, daemon, kern, lpr, mail,
#   news, syslog, user, uucp, local0~local7
#
# 级别（Priority，从低到高）：
#   debug, info, notice, warning, err, crit, alert, emerg

# ===== 常见配置 =====
# 认证日志到单独文件
auth,authpriv.*                 /var/log/auth.log

# 所有 info 级以上到 messages
*.=info;*.=notice;*.=warn;\
    auth,authpriv.none;\
    cron,daemon.none;\
    mail.none                   /var/log/messages

# 远程日志发送（客户端）
*.* @@remote-log-server:514     # TCP 发送
*.* @remote-log-server:514      # UDP 发送

# 远程日志接收（服务端）
module(load="imtcp")
input(type="imtcp" port="514")

# ===== 日志轮转 =====
# /etc/logrotate.conf
# /etc/logrotate.d/

# 常用配置项：
#   daily / weekly / monthly   轮转频率
#   rotate 4                   保留 4 份
#   compress                   压缩旧日志
#   delaycompress              延迟压缩（最近一份不压缩）
#   missingok                  文件不存在也不报错
#   notifempty                 空文件不轮转
#   size 100M                  超过 100M 就轮转
#   postrotate/endscript       轮转后执行的脚本
```

---

## 七、安全基线检查与自动化

### 7.1 Lynis（安全审计工具）

**Lynis**：开源的系统安全审计工具，能对 Linux 系统进行全面的安全扫描和合规检查。

```bash
# ===== 安装 =====
apt install lynis
yum install lynis
# 或下载源码运行（不需要安装）

# ===== 基本用法 =====
lynis audit system               # 系统审计（最常用）🔑
lynis audit system --quick       # 快速模式（不等待用户输入）
lynis audit system --no-colors   # 无颜色输出

# ===== 输出 =====
# 默认输出到屏幕和日志文件
# 日志：/var/log/lynis.log
# 报告：/var/log/lynis-report.dat

# ===== 扫描分类 =====
# 测试组（test group）：
#   authentication, filesystems, kernel, networking,
#   services, software, storage, users, etc.

# 只扫描特定组
lynis --tests-from-group authentication
lynis --tests-from-group "networking storage"

# 跳过某些测试
lynis --skip-test=KRL-0290

# ===== 配置文件 =====
# /etc/lynis/default.prf  默认配置
# /etc/lynis/custom.prf   自定义配置

# ===== 常用检查项 =====
# Lynis 会检查几百项，包括：
#   - 系统信息和分区
#   - 引导和服务
#   - 内核和内存
#   - 用户、组和认证
#   - 权限和文件完整性
#   - 密码和密钥
#   - 防火墙和网络
#   - 服务和软件
#   - 日志和审计
#   - 等等...

# ===== 结果解读 =====
# Hardening Index：加固指数（越高越好）
# Suggestions：改进建议列表
# Warnings：警告项
```

### 7.2 安全基线自动化

#### （1）常见基线检查工具

| 工具 | 说明 | 特点 |
|------|------|------|
| **Lynis** | 系统安全审计 | 开源、全面、可扩展 |
| **OpenSCAP** | 合规扫描工具 | 支持 SCAP 标准、CIS Benchmark |
| **Ansible + 加固 role** | 配置管理工具做加固 | 自动化、幂等、可重复 |
| **自定义脚本** | Shell/Python 脚本 | 灵活、定制化 |

#### （2）Linux 安全基线核心检查项

```
Linux 安全基线检查清单（核心 50 项）：

一、账号与认证
  □ 禁止空密码账号
  □ 禁用不需要的默认账号
  □ UID 为 0 的账号只有 root
  □ 密码策略符合要求（长度、复杂度、历史）
  □ 登录失败锁定策略
  □ SSH 禁用 root 直接登录
  □ SSH 禁用密码认证（用密钥）
  □ 重要账号启用 MFA

二、文件权限
  □ /etc/passwd 权限 644，属主 root
  □ /etc/shadow 权限 600，属主 root
  □ /etc/gshadow 权限 600
  □ 全局可写文件检查
  □ SUID/SGID 文件审计
  □ 没有不属于任何用户/组的文件
  □ 敏感目录权限（如 /root 700）

三、服务最小化
  □ 关闭不必要的服务
  □ 禁用不必要的开机自启项
  □ 每个服务都有业务理由
  □ 服务使用最小权限账号运行

四、网络安全
  □ 防火墙已启用并配置
  □ 默认策略拒绝入站
  □ 只开放必要的端口
  □ 禁用不必要的网络服务
  □ 禁用 IP 源路由
  □ 开启 SYN Cookies
  □ ICMP 重定向禁用
  □ 广播 ping 禁用

五、日志与审计
  □ 系统日志已配置
  □ 日志集中收集
  □ 日志保留期符合要求
  □ auditd 已启用并配置
  □ 登录审计
  □ 关键文件变更审计
  □ 时间同步（NTP）

六、内核参数
  □ /proc/sys 安全参数配置
  □ 地址空间随机化（ASLR）开启
  □ 禁用不需要的内核模块
  □ 内存保护机制开启

七、软件与补丁
  □ 系统已更新最新安全补丁
  □ 启用自动安全更新
  □ 删除不需要的软件包
  □ YUM/APT 源配置安全
  □ GPG 密钥验证

八、物理安全
  □ BIOS/GRUB 设置密码
  □ 禁用不需要的启动项
  □ Ctrl+Alt+Del 禁用
  □ 单用户模式需要密码

九、监控与告警
  □ 系统监控已部署
  □ 安全事件告警
  □ 异常登录告警
  □ 磁盘/CPU/内存监控

十、备份与恢复
  □ 数据备份已配置
  □ 备份定期验证可恢复
  □ 备份异地存储
  □ 有灾难恢复计划
```

#### （3）基线检查脚本示例

```bash
#!/bin/bash
# 简单的安全基线检查脚本示例
# 实际使用请根据环境定制

echo "=== Linux 安全基线检查 ==="
echo ""

# 1. 检查空密码账号
echo "[1] 空密码账号检查："
empty_pass=$(awk -F: '($2 == "") {print $1}' /etc/shadow)
if [ -z "$empty_pass" ]; then
  echo "  ✅ 无空密码账号"
else
  echo "  ❌ 存在空密码账号: $empty_pass"
fi

# 2. 检查 UID 为 0 的账号
echo "[2] UID=0 账号检查："
uid0=$(awk -F: '($3 == 0) {print $1}' /etc/passwd)
echo "  UID=0 的账号: $uid0"

# 3. 检查 SSH 配置
echo "[3] SSH 安全配置检查："
if grep -q "^PermitRootLogin no" /etc/ssh/sshd_config; then
  echo "  ✅ root 登录已禁用"
else
  echo "  ⚠️  root 登录未禁用"
fi

# 4. 检查防火墙状态
echo "[4] 防火墙状态："
if systemctl is-active --quiet firewalld 2>/dev/null; then
  echo "  ✅ firewalld 正在运行"
elif systemctl is-active --quiet iptables 2>/dev/null; then
  echo "  ✅ iptables 服务正在运行"
elif ufw status 2>/dev/null | grep -q "Status: active"; then
  echo "  ✅ ufw 已启用"
else
  echo "  ❌ 防火墙未启用"
fi

# 5. 检查 SELinux/AppArmor
echo "[5] 强制访问控制："
if command -v getenforce &>/dev/null; then
  selinux=$(getenforce)
  echo "  SELinux 状态: $selinux"
elif command -v aa-status &>/dev/null; then
  echo "  AppArmor 已安装"
  aa-status --profiled 2>/dev/null | head -1
else
  echo "  ⚠️  未启用 MAC（SELinux/AppArmor）"
fi

# 6. 检查审计服务
echo "[6] 审计服务："
if systemctl is-active --quiet auditd; then
  echo "  ✅ auditd 正在运行"
else
  echo "  ❌ auditd 未运行"
fi

echo ""
echo "=== 检查完成 ==="
```

### 7.3 自动化加固的思路

```
安全基线自动化三步走：

1. 检查（Assess）
   → 用 Lynis/OpenSCAP/脚本 扫描
   → 生成报告，找出不符合项
   → 评估风险，确定优先级

2. 加固（Harden）
   → 用 Ansible / Puppet / Chef 等配置管理工具
   → 把加固步骤写成可重复的代码
   → 在测试环境验证
   → 逐步在生产环境推行

3. 监控（Monitor）
   → 持续监控配置漂移
   → 定期自动扫描
   → 不合规及时告警
   → 形成闭环
```

---

## 附：优化后的提示词模板

以下是可复用的 Linux 安全实践类提示词模板：

```markdown
# 角色
你是一名资深 Linux 与网络安全专家，精通 Linux 网络配置、
安全加固与工具链。

# 任务
请系统介绍 Linux【主题】实践与工具，包括：
1. 基本概念与原理
2. 核心工具/命令详解
   - 语法
   - 核心参数
   - 实用示例
3. 配置与加固
   - 关键配置项
   - 最佳实践
   - 常见陷阱
4. 自动化与脚本
   - 检查脚本
   - 基线检查
5. 常见问题与故障排查

# 输出要求
- Markdown 格式，按大类小类组织
- 表格对比，命令附完整示例
- 重要术语中英文对照
- 面向运维工程师、安全工程师
- 深度：操作实践 + 安全加固

# 约束
- 命令标注所需权限（root/普通用户）
- 高风险命令和操作给出警告
- 修改配置前提示备份
- 远程操作警告可能失联
- 仅限授权环境使用
- 最后附"优化后的提示词模板"
```

**使用说明**：将【主题】替换为"系统加固""网络排查""入侵检测""日志审计""容器安全""Web 服务器安全"等，即可生成同等深度和结构的 Linux 安全实践专题文档。

---

> **总结**：Linux 网络安全是一个系统工程——从基础的网络配置和排查（ip/ss/tcpdump/nmap），到防火墙（iptables/nftables/firewalld/ufw），再到系统加固（SSH/PAM/SELinux/AppArmor）、入侵检测（Snort/Suricata/OSSEC/AIDE）、加密与证书（openssl/gpg/ssh-keygen）、日志与审计（journalctl/auditd/rsyslog），最后通过自动化基线检查和持续监控形成闭环。每个工具都有它的定位和价值，关键是要组合起来使用，形成纵深防御。记住：安全是一个持续的过程，不是一次性的配置——加固完了就不管了，要定期检查、持续监控、不断改进。
