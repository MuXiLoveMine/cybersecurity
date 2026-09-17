# Linux网络与安全配置指南

> 本文档全面介绍Linux网络配置、防火墙规则、端口管理、SSH加固、日志系统、服务加固及容器网络安全，提供实战加固检查清单。

---

## 目录

- [1. Linux网络配置](#1-linux网络配置)
  - [1.1 ip命令详解](#11-ip命令详解)
  - [1.2 ifconfig与route](#12-ifconfig与route)
  - [1.3 NetworkManager](#13-networkmanager)
  - [1.4 网络接口绑定与聚合](#14-网络接口绑定与聚合)
- [2. iptables/nftables防火墙](#2-iptablenftables防火墙)
  - [2.1 iptables基础](#21-iptables基础)
  - [2.2 iptables规则编写](#22-iptables规则编写)
  - [2.3 nftables新一代防火墙](#23-nftables新一代防火墙)
  - [2.4 防火墙实战配置](#24-防火墙实战配置)
- [3. 端口管理](#3-端口管理)
  - [3.1 netstat端口检测](#31-netstat端口检测)
  - [3.2 ss命令](#32-ss命令)
  - [3.3 lsof端口分析](#33-lsof端口分析)
  - [3.4 端口安全策略](#34-端口安全策略)
- [4. SSH安全加固](#4-ssh安全加固)
  - [4.1 SSH配置加固](#41-ssh配置加固)
  - [4.2 密钥管理与轮换](#42-密钥管理与轮换)
  - [4.3 SSH跳板机配置](#43-ssh跳板机配置)
  - [4.4 SSH审计与监控](#44-ssh审计与监控)
- [5. Linux日志系统](#5-linux日志系统)
  - [5.1 journalctl日志管理](#51-journalctl日志管理)
  - [5.2 rsyslog配置](#52-rsyslog配置)
  - [5.3 auditd审计系统](#53-auditd审计系统)
  - [5.4 日志集中管理](#54-日志集中管理)
- [6. 网络服务加固](#6-网络服务加固)
  - [6.1 Nginx安全加固](#61-nginx安全加固)
  - [6.2 Apache安全加固](#62-apache安全加固)
  - [6.3 MySQL安全加固](#63-mysql安全加固)
  - [6.4 Redis安全加固](#64-redis安全加固)
- [7. TCP Wrappers与hosts文件](#7-tcp-wrappers与hosts文件)
- [8. 网络命名空间与容器安全](#8-网络命名空间与容器安全)
  - [8.1 网络命名空间](#81-网络命名空间)
  - [8.2 容器网络安全](#82-容器网络安全)
  - [8.3 iptables与容器](#83-iptables与容器)
- [9. 实战加固检查清单](#9-实战加固检查清单)

---

## 1. Linux网络配置

### 1.1 ip命令详解

`ip`命令来自`iproute2`包，是现代Linux网络配置的核心工具，取代了传统的`ifconfig`和`route`。

```bash
# 查看所有网络接口
ip addr show
ip a                    # 简写

# 查看指定接口
ip addr show eth0
ip a show eth0

# 查看链路状态
ip link show
ip link show eth0

# 启用/禁用接口
ip link set eth0 up     # 启用
ip link set eth0 down  # 禁用

# 配置IP地址
ip addr add 192.168.1.100/24 dev eth0
ip addr del 192.168.1.100/24 dev eth0

# 配置IPv6地址
ip addr add 2001:db8::1/64 dev eth0

# 查看路由表
ip route show
ip route get 8.8.8.8   # 查看到指定地址的路由

# 添加/删除路由
ip route add 10.0.0.0/24 via 192.168.1.1
ip route del 10.0.0.0/24 via 192.168.1.1

# 添加默认路由
ip route add default via 192.168.1.1

# 查看ARP表
ip neigh show
ip n show

# 查看多播地址
ip maddr show
```

### 1.2 ifconfig与route

虽然`ip`命令是推荐工具，但`ifconfig`和`route`仍在广泛使用。

```bash
# ifconfig基本用法
ifconfig                    # 查看所有接口
ifconfig eth0               # 查看指定接口
ifconfig eth0 up            # 启用接口
ifconfig eth0 down          # 禁用接口

# 配置IP地址
ifconfig eth0 192.168.1.100 netmask 255.255.255.0
ifconfig eth0 192.168.1.100/24      # CIDR格式

# 配置别名接口
ifconfig eth0:0 192.168.2.100/24

# 修改MAC地址（需root权限，接口需先down）
ifconfig eth0 down
ifconfig eth0 hw ether 00:11:22:33:44:55
ifconfig eth0 up

# route命令
route -n                    # 查看路由表（数字格式）
route add -net 10.0.0.0 netmask 255.255.255.0 gw 192.168.1.1
route add default gw 192.168.1.1
route del -net 10.0.0.0 netmask 255.255.255.0
```

### 1.3 NetworkManager

NetworkManager是现代Linux发行版的默认网络管理工具，提供动态网络配置。

```bash
# nmcli命令行工具
nmcli device status                 # 查看设备状态
nmcli device show eth0              # 查看设备详情
nmcli device connect eth0           # 连接设备
nmcli device disconnect eth0        # 断开设备

# 连接管理
nmcli connection show               # 查看所有连接
nmcli connection show "Wired connection 1"  # 查看连接详情

# 创建新连接
nmcli connection add type ethernet ifname eth0 con-name "eth0-static" ipv4.addresses 192.168.1.100/24 ipv4.gateway 192.168.1.1 ipv4.dns 8.8.8.8 ipv4.method manual

# 修改连接
nmcli connection modify "eth0-static" ipv4.addresses 192.168.1.200/24

# 启用/禁用连接
nmcli connection up "eth0-static"
nmcli connection down "eth0-static"

# WiFi管理
nmcli device wifi list             # 列出可用WiFi
nmcli device wifi connect "SSID" password "password"

# nmtui - 文本用户界面
nmtui                               # 交互式配置工具
```

### 1.4 网络接口绑定与聚合

```bash
# 配置网络绑定（Bonding）
# 模式：active-backup(1), balance-rr(0), 802.3ad(4)
modprobe bonding

# 创建bond接口
ip link add bond0 type bond
ip link set bond0 type bond miimon 100 mode 1
ip link set eth0 master bond0
ip link set eth1 master bond0
ip link set bond0 up

# 配置聚合（Teaming）
teamd -o -f /etc/teamd/team0.conf
# 配置文件示例
cat > /etc/teamd/team0.conf << EOF
{
    "device": "team0",
    "runner": {"name": "activebackup"},
    "link_watch": {"name": "ethtool"},
    "ports": {"eth0": {}, "eth1": {}}
}
EOF
```

---

## 2. iptables/nftables防火墙

### 2.1 iptables基础

iptables是Linux传统的包过滤防火墙，基于Netfilter框架。

```bash
# 查看当前规则
iptables -L                    # 查看所有链
iptables -L -n                # 不解析IP和端口
iptables -L -n -v              # 详细统计
iptables -L -n -v --line-numbers  # 显示行号
iptables -S                    # 查看规则（命令格式）

# 查看NAT表
iptables -t nat -L -n
iptables -t mangle -L -n
iptables -t raw -L -n

# 清除规则
iptables -F                    # 清除所有链的规则
iptables -X                    # 删除自定义链
iptables -Z                    # 清零计数器
iptables -t nat -F             # 清除NAT表规则

# 设置默认策略
iptables -P INPUT DROP         # 默认拒绝输入
iptables -P FORWARD DROP       # 默认拒绝转发
iptables -P OUTPUT ACCEPT      # 默认允许输出
```

**iptables表与链结构：**

| 表 | 链 | 用途 |
|------|------|------|
| raw | PREROUTING, OUTPUT | 数据包跟踪 |
| mangle | PREROUTING, INPUT, FORWARD, OUTPUT, POSTROUTING | 数据包修改 |
| nat | PREROUTING, OUTPUT, POSTROUTING | 地址转换 |
| filter | INPUT, FORWARD, OUTPUT | 包过滤 |

### 2.2 iptables规则编写

```bash
# 基本规则语法
# iptables [-t 表] -A 链 匹配条件 -j 动作

# 允许已建立的连接
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# 允许回环接口
iptables -A INPUT -i lo -j ACCEPT

# 允许SSH（限制速率防止暴力破解）
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --set --name SSH
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --update --seconds 60 --hitcount 5 --name SSH -j DROP
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 允许HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 允许DNS
iptables -A INPUT -p udp --dport 53 -j ACCEPT
iptables -A INPUT -p tcp --dport 53 -j ACCEPT

# 允许NTP
iptables -A INPUT -p udp --dport 123 -j ACCEPT

# 拒绝特定IP
iptables -A INPUT -s 192.168.1.100 -j DROP
iptables -A INPUT -s 10.0.0.0/8 -j DROP

# 允许特定IP访问SSH
iptables -A INPUT -s 192.168.1.0/24 -p tcp --dport 22 -j ACCEPT

# 限制ICMP
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-request -j DROP

# 端口转发（DNAT）
iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 192.168.1.100:80
iptables -t nat -A POSTROUTING -p tcp -d 192.168.1.100 --dport 80 -j SNAT --to-source 192.168.1.1

# 日志记录
iptables -A INPUT -j LOG --log-prefix "DROPPED: " --log-level 4

# 防止SYN洪水攻击
iptables -A INPUT -p tcp --syn -m limit --limit 5/s --limit-burst 10 -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP

# 防止端口扫描
iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP       # NULL扫描
iptables -A INPUT -p tcp --tcp-flags SYN,FIN SYN,FIN -j DROP  # SYN-FIN扫描
iptables -A INPUT -p tcp --tcp-flags SYN,RST SYN,RST -j DROP   # SYN-RST扫描
iptables -A INPUT -p tcp --tcp-flags FIN,RST FIN,RST -j DROP   # FIN-RST扫描
iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP      # XMAS扫描
iptables -A INPUT -p tcp --tcp-flags ACK,FIN FIN -j DROP  # FIN扫描

# 保存和恢复规则
iptables-save > /etc/iptables/rules.v4
iptables-restore < /etc/iptables/rules.v4
ip6tables-save > /etc/iptables/rules.v6
```

### 2.3 nftables新一代防火墙

nftables是iptables的替代品，提供了更强大、更灵活的包过滤框架。

```bash
# 查看当前规则集
nft list ruleset

# 清空规则
nft flush ruleset

# 创建表
nft add table inet filter
nft add table ip nat
nft add table ip6 filter

# 创建链
nft add chain inet filter input '{ type filter hook input priority 0; policy drop; }'
nft add chain inet filter forward '{ type filter hook forward priority 0; policy drop; }'
nft add chain inet filter output '{ type filter hook output priority 0; policy accept; }'

# 添加规则
nft add rule inet filter input iif "lo" accept
nft add rule inet filter input ct state established,related accept
nft add rule inet filter input tcp dport 22 accept
nft add rule inet filter input tcp dport { 80, 443 } accept
nft add rule inet filter input udp dport 53 accept

# 速率限制
nft add rule inet filter input tcp dport 22 ct state new limit rate 5/minute accept
nft add rule inet filter input tcp dport 22 ct state new drop

# 拒绝特定IP
nft add rule inet filter input ip saddr 192.168.1.100 drop

# NAT
nft add table ip nat
nft add chain ip nat prerouting '{ type nat hook prerouting priority 0; }'
nft add chain ip nat postrouting '{ type nat hook postrouting priority 100; }'
nft add rule ip nat prerouting tcp dport 8080 dnat to 192.168.1.100:80
nft add rule ip nat postrouting ip daddr 192.168.1.100 tcp dport 80 snat to 192.168.1.1

# 保存规则
nft list ruleset > /etc/nftables.conf
nft -f /etc/nftables.conf
```

**nftables配置文件示例 `/etc/nftables.conf`：**

```nft
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;

        # 允许回环
        iif "lo" accept

        # 允许已建立连接
        ct state established,related accept

        # 丢弃无效连接
        ct state invalid drop

        # SSH速率限制
        tcp dport 22 ct state new limit rate 5/minute accept
        tcp dport 22 ct state new drop

        # 允许Web服务
        tcp dport { 80, 443 } accept

        # 允许DNS
        udp dport 53 accept
        tcp dport 53 accept

        # ICMP限制
        icmp type echo-request limit rate 1/second accept
        ip6 nexthdr icmpv6 icmpv6 type { echo-request, nd-neighbor-solicit } limit rate 1/second accept

        # 防止扫描
        tcp flags & (fin|syn|rst|psh|ack|urg) == fin|syn|rst|psh|ack|urg drop
        tcp flags & (fin|syn) == fin|syn drop
        tcp flags & (syn|rst) == syn|rst drop

        # 日志
        limit rate 10/minute log prefix "nft-dropped: " level warn
    }

    chain forward {
        type filter hook forward priority 0; policy drop;
    }

    chain output {
        type filter hook output priority 0; policy accept;
    }
}
```

### 2.4 防火墙实战配置

```bash
# Web服务器防火墙配置
#!/bin/bash
# /etc/iptables/web-server.rules

# 清除现有规则
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

# 设置默认策略
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 允许回环
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# 允许已建立连接
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# 丢弃无效数据包
iptables -A INPUT -m conntrack --ctstate INVALID -j DROP

# SSH防护
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --set --name SSH
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --update --seconds 60 --hitcount 5 --name SSH -j LOG --log-prefix "SSH-BRUTEFORCE: "
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --update --seconds 60 --hitcount 5 --name SSH -j DROP
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Web服务
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# DNS（如果运行DNS服务器）
iptables -A INPUT -p udp --dport 53 -j ACCEPT
iptables -A INPUT -p tcp --dport 53 -j ACCEPT

# ICMP限制
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT

# 日志记录被拒绝的包
iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-DENIED: " --log-level 4

# 最终拒绝
iptables -A INPUT -j REJECT --reject-with icmp-host-prohibited

# 保存
iptables-save > /etc/iptables/rules.v4
```

---

## 3. 端口管理

### 3.1 netstat端口检测

```bash
# 查看所有监听端口
netstat -tlnp        # TCP监听端口
netstat -ulnp         # UDP监听端口
netstat -tunlp        # 所有监听端口

# 查看所有连接
netstat -an           # 所有连接
netstat -ant          # 所有TCP连接
netstat -anu          # 所有UDP连接

# 查看特定端口
netstat -tlnp | grep :80
netstat -tlnp | grep :22

# 统计连接状态
netstat -ant | awk '{print $6}' | sort | uniq -c | sort -rn

# 查看每个IP的连接数
netstat -ant | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn

# 查看异常连接
netstat -ant | grep ESTABLISHED | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -20
```

### 3.2 ss命令

`ss`是`netstat`的现代替代品，速度更快，功能更强。

```bash
# 查看监听端口
ss -tlnp              # TCP监听
ss -ulnp              # UDP监听
ss -tunlp             # 所有监听

# 查看所有连接
ss -tan               # 所有TCP
ss -uan               # 所有UDP
ss -an                # 所有

# 查看已建立连接
ss -t state established

# 查看特定端口
ss -tlnp | grep :80
ss -tlnp 'sport = :80'

# 按状态统计
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn

# 查看连接到指定IP的所有连接
ss -t dst 192.168.1.100

# 查看指定进程的连接
ss -tlnp | grep nginx

# 查看socket统计
ss -s
```

### 3.3 lsof端口分析

```bash
# 查看端口占用
lsof -i :80           # 谁在使用80端口
lsof -i :22           # 谁在使用22端口
lsof -i tcp:80        # TCP 80端口
lsof -i udp:53         # UDP 53端口

# 查看所有网络连接
lsof -i                # 所有网络连接
lsof -i tcp            # 所有TCP
lsof -i udp            # 所有UDP

# 按用户查看
lsof -u www-data       # www-data用户的连接
lsof -u root           # root用户的连接

# 按进程查看
lsof -p 1234           # PID 1234的连接
lsof -c nginx          # nginx进程的连接

# 查看监听端口
lsof -i -P -n | grep LISTEN

# 查看Unix域套接字
lsof -U
```

### 3.4 端口安全策略

```bash
# 定期扫描开放端口
#!/bin/bash
# 端口审计脚本
echo "=== 端口审计报告 $(date) ==="
echo ""
echo "TCP监听端口:"
ss -tlnp | awk 'NR>1 {print "  "$4" -> "$7}'
echo ""
echo "UDP监听端口:"
ss -ulnp | awk 'NR>1 {print "  "$4" -> "$7}'
echo ""
echo "已建立连接数: $(ss -t state established | wc -l)"
echo "TIME_WAIT连接数: $(ss -t state time-wait | wc -l)"
echo "CLOSE_WAIT连接数: $(ss -t state close-wait | wc -l)"

# 检查非标准端口
echo ""
echo "非标准端口监听:"
ss -tlnp | grep -vE ':(22|80|443|53|123|25)\b'

# 检查root进程监听的端口
echo ""
echo "root进程监听的端口:"
ss -tlnp | grep 'users:("root'
```

---

## 4. SSH安全加固

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

## 5. Linux日志系统

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

## 6. 网络服务加固

### 6.1 Nginx安全加固

```nginx
# /etc/nginx/nginx.conf 安全配置

user nginx;
worker_processes auto;
pid /run/nginx.pid;

# 安全相关
server_tokens off;                    # 隐藏版本号

events {
    worker_connections 1024;
    multi_accept on;
}

http {
    # 基本安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'" always;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # 隐藏服务器信息
    proxy_hide_header X-Powered-By;
    proxy_hide_header Server;
    fastcgi_hide_header X-Powered-By;

    # 限制请求大小
    client_max_body_size 10m;
    client_body_buffer_size 16k;
    client_header_buffer_size 4k;
    large_client_header_buffers 4 4k;

    # 超时设置
    client_body_timeout 30;
    client_header_timeout 30;
    keepalive_timeout 30 30;
    send_timeout 30;

    # 限制连接数
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
    limit_req_zone $binary_remote_addr zone=req_limit:10m rate=10r/s;

    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    server {
        listen 80;
        server_name example.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name example.com;

        ssl_certificate /etc/nginx/ssl/example.com.crt;
        ssl_certificate_key /etc/nginx/ssl/example.com.key;

        # 应用限制
        limit_conn conn_limit 10;
        limit_req zone=req_limit burst=20 nodelay;

        # 防止目录遍历
        location ~* /\.(git|svn|hg) {
            deny all;
            return 404;
        }

        # 防止访问敏感文件
        location ~* \.(env|sql|bak|old|tmp|log|conf)$ {
            deny all;
            return 404;
        }

        # 防止PHP上传目录执行
        location ~* /uploads/.*\.php$ {
            deny all;
        }

        # 安全的PHP配置
        location ~ \.php$ {
            fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
            fastcgi_index index.php;
            include fastcgi_params;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;

            # 防止零日漏洞
            try_files $uri =404;
        }
    }
}
```

### 6.2 Apache安全加固

```apache
# /etc/apache2/conf-enabled/security.conf

# 隐藏版本信息
ServerTokens Prod
ServerSignature Off

# 添加安全头
<IfModule mod_headers.c>
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains"
    Header unset X-Powered-By
    Header unset Server
</IfModule>

# 限制请求大小
LimitRequestBody 10485760

# 防止目录列表
Options -Indexes

# 禁用TRACE
TraceEnable Off

# 限制方法
<LimitExcept GET POST HEAD OPTIONS>
    Require all denied
</LimitExcept>

# SSL配置
<IfModule mod_ssl.c>
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    SSLCipherSuite ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    SSLHonorCipherOrder on
    SSLCompression off
    SSLSessionTickets off
    SSLUseStapling on
    SSLStaplingCache shmcb:/var/run/ocsp(128000)
</IfModule>

# 防止访问敏感文件
<FilesMatch "(^\.|\.env$|\.sql$|\.bak$|\.log$|\.conf$)">
    Require all denied
</FilesMatch>

# 防止上传执行
<Directory "/var/www/html/uploads">
    php_admin_flag engine off
    <FilesMatch "\.ph(p[345]?|t|tml)$">
        Require all denied
    </FilesMatch>
</Directory>
```

### 6.3 MySQL安全加固

```sql
-- 安全配置 /etc/mysql/mysql.conf.d/mysqld.cnf

[mysqld]
# 基本安全
bind-address = 127.0.0.1          -- 仅本地监听
port = 3306
skip-symbolic-links              -- 禁用符号链接

# 认证安全
default-authentication-plugin = mysql_native_password
default_password_lifetime = 90   -- 密码90天过期
password_history = 5             -- 保留5个历史密码

# SSL/TLS
ssl-ca = /etc/mysql/ssl/ca.pem
ssl-cert = /etc/mysql/ssl/server-cert.pem
ssl-key = /etc/mysql/ssl/server-key.pem
require_secure_transport = ON    -- 强制加密连接

# 日志审计
log_error = /var/log/mysql/error.log
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

# 安全SQL模式
sql_mode = STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION

-- 运行mysql_secure_installation
-- mysql_secure_installation

-- 安全检查SQL
-- 查看用户权限
SELECT user, host, authentication_string FROM mysql.user;

-- 移除匿名用户
DELETE FROM mysql.user WHERE User='';

-- 移除test数据库
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';

-- 限制用户权限
SHOW GRANTS FOR 'user'@'localhost';
REVOKE ALL PRIVILEGES ON *.* FROM 'user'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON mydb.* TO 'user'@'localhost';
```

### 6.4 Redis安全加固

```bash
# /etc/redis/redis.conf 安全配置

# 网络安全
bind 127.0.0.1 ::1                 # 仅本地监听
protected-mode yes                  # 保护模式
port 6379                           # 默认端口（建议修改）

# 认证
requirepass YourStrongPassword123! # 设置密码

# 命令重命名/禁用
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG ""
rename-command KEYS ""
rename-command DEBUG ""
rename-command SHUTDOWN ""
rename-command DEL ""

# 访问控制
# 使用ACL（Redis 6+）
# user default on >password ~* &* +@all -@dangerous

# 限制最大客户端
maxclients 100

# 内存限制
maxmemory 1gb
maxmemory-policy allkeys-lru

# 持久化安全
dir /var/lib/redis
dbfilename dump.rdb
appendonly yes
appendfilename "appendonly.aof"

# 日志
loglevel notice
logfile /var/log/redis/redis-server.log

# 文件权限
# chown redis:redis /etc/redis/redis.conf
# chmod 600 /etc/redis/redis.conf
# chown -R redis:redis /var/lib/redis
# chmod 700 /var/lib/redis
```

---

## 7. TCP Wrappers与hosts文件

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

## 8. 网络命名空间与容器安全

### 8.1 网络命名空间

```bash
# 创建网络命名空间
ip netns add ns1
ip netns add ns2

# 查看命名空间
ip netns list

# 在命名空间中执行命令
ip netns exec ns1 ip addr
ip netns exec ns1 ip link set lo up

# 创建veth对连接命名空间
ip link add veth1 type veth peer name veth2
ip link set veth1 netns ns1
ip link set veth2 netns ns2

# 配置IP地址
ip netns exec ns1 ip addr add 10.0.0.1/24 dev veth1
ip netns exec ns1 ip link set veth1 up
ip netns exec ns2 ip addr add 10.0.0.2/24 dev veth2
ip netns exec ns2 ip link set veth2 up

# 测试连通性
ip netns exec ns1 ping 10.0.0.2

# 删除命名空间
ip netns del ns1
ip netns del ns2
```

### 8.2 容器网络安全

```bash
# Docker网络安全

# 使用自定义网络
docker network create --driver bridge \
    --subnet 172.20.0.0/16 \
    --ip-range 172.20.0.0/24 \
    secure-network

# 限制容器间通信
docker network create --internal isolated-network

# 绑定到localhost
docker run -p 127.0.0.1:8080:80 nginx

# 使用用户定义网络
docker run --network secure-network nginx

# Docker安全选项
docker run \
    --cap-drop ALL \                  # 丢弃所有capabilities
    --cap-add NET_BIND_SERVICE \     # 仅添加必要的
    --security-opt no-new-privileges \  # 防止提权
    --security-opt seccomp=/etc/docker/seccomp.json \  # seccomp策略
    --read-only \                     # 只读文件系统
    --tmpfs /tmp \                    # 临时文件系统
    --memory="512m" \                 # 内存限制
    --cpus="1.0" \                    # CPU限制
    --pids-limit 100 \                # 进程数限制
    --ulimit nofile=1024 \            # 文件描述符限制
    --user 1000:1000 \                # 非root用户
    nginx

# 防止容器逃逸
docker run \
    --security-opt=no-new-privileges \
    --cap-drop ALL \
    --cap-add CHOWN \
    --cap-add SETGID \
    --cap-add SETUID \
    --read-only \
    --mount type=tmpfs,destination=/tmp \
    alpine

# iptables与Docker
# Docker自动创建iptables规则
# 查看Docker iptables规则
iptables -t nat -L DOCKER
iptables -L DOCKER
iptables -L DOCKER-ISOLATION-STAGE-1
iptables -L DOCKER-ISOLATION-STAGE-2

# 限制容器出站流量
iptables -I DOCKER-USER -d 10.0.0.0/8 -j DROP
iptables -I DOCKER-USER -d 172.16.0.0/12 -j DROP
iptables -I DOCKER-USER -d 192.168.0.0/16 -j DROP
```

### 8.3 iptables与容器

```bash
# Docker网络隔离规则

# 阻止容器访问宿主机内网
iptables -I DOCKER-USER -i docker0 -d 192.168.0.0/16 -j DROP
iptables -I DOCKER-USER -i docker0 -d 10.0.0.0/8 -j DROP
iptables -I DOCKER-USER -i docker0 -d 172.16.0.0/12 -j DROP

# 限制容器间通信
iptables -I DOCKER-ISOLATION-STAGE-1 -i br-<network_id> -j DROP

# 审计容器网络
docker network ls
docker network inspect bridge
docker network inspect <network_name>

# 使用网络策略（Kubernetes）
# NetworkPolicy示例
cat << 'EOF' | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
EOF
```

---

## 9. 实战加固检查清单

```bash
#!/bin/bash
# Linux安全加固检查脚本

echo "=========================================="
echo "  Linux安全加固检查清单"
echo "  日期: $(date)"
echo "=========================================="
echo ""

# 1. 系统更新
echo "[1] 系统更新检查"
echo "  待更新包数: $(apt list --upgradable 2>/dev/null | wc -l)"
echo "  内核版本: $(uname -r)"
echo ""

# 2. 用户安全
echo "[2] 用户安全检查"
echo "  UID为0的用户: $(awk -F: '$3==0 {print $1}' /etc/passwd)"
echo "  空密码用户: $(awk -F: '($2=="*" || $2=="!") {print $1}' /etc/shadow | wc -l)"
echo "  可登录用户数: $(grep -v '/nologin\|/false' /etc/passwd | wc -l)"
echo "  sudo组用户: $(getent group sudo | cut -d: -f4)"
echo ""

# 3. SSH安全
echo "[3] SSH安全检查"
echo "  SSH端口: $(grep -E '^Port' /etc/ssh/sshd_config | awk '{print $2}')"
echo "  Root登录: $(grep -E '^PermitRootLogin' /etc/ssh/sshd_config | awk '{print $2}')"
echo "  密码认证: $(grep -E '^PasswordAuthentication' /etc/ssh/sshd_config | awk '{print $2}')"
echo "  最大尝试: $(grep -E '^MaxAuthTries' /etc/ssh/sshd_config | awk '{print $2}')"
echo "  空密码: $(grep -E '^PermitEmptyPasswords' /etc/ssh/sshd_config | awk '{print $2}')"
echo ""

# 4. 防火墙状态
echo "[4] 防火墙检查"
echo "  iptables规则数: $(iptables -L | wc -l)"
echo "  INPUT默认策略: $(iptables -L INPUT | head -1)"
echo "  FORWARD默认策略: $(iptables -L FORWARD | head -1)"
echo "  ufw状态: $(ufw status 2>/dev/null || echo '未安装')"
echo ""

# 5. 端口检查
echo "[5] 端口检查"
echo "  监听TCP端口:"
ss -tlnp | awk 'NR>1 {print "    "$4}' | sort
echo "  监听UDP端口:"
ss -ulnp | awk 'NR>1 {print "    "$4}' | sort
echo ""

# 6. 日志检查
echo "[6] 日志检查"
echo "  日志大小: $(journalctl --disk-usage 2>/dev/null)"
echo "  auth.log存在: $([ -f /var/log/auth.log ] && echo '是' || echo '否')"
echo "  失败登录次数(24h): $(grep "Failed password" /var/log/auth.log 2>/dev/null | grep "$(date +%b\ %e)" | wc -l)"
echo ""

# 7. 文件权限
echo "[7] 关键文件权限检查"
for file in /etc/passwd /etc/shadow /etc/group /etc/sudoers /etc/ssh/sshd_config; do
    echo "  $file: $(stat -c '%a %U:%G' $file 2>/dev/null)"
done
echo ""

# 8. 内核参数
echo "[8] 内核安全参数"
echo "  IP转发: $(cat /proc/sys/net/ipv4/ip_forward)"
echo "  SYN Cookie: $(cat /proc/sys/net/ipv4/tcp_syncookies)"
echo "  反向路径过滤: $(cat /proc/sys/net/ipv4/conf/all/rp_filter)"
echo "  ICMP重定向: $(cat /proc/sys/net/ipv4/conf/all/accept_redirects)"
echo "  源路由: $(cat /proc/sys/net/ipv4/conf/all/accept_source_route)"
echo ""

# 9. 服务检查
echo "[9] 运行中的服务"
systemctl list-units --type=service --state=running | awk '{print "  "$1}' | head -20
echo ""

# 10. 定时任务
echo "[10] 定时任务检查"
echo "  root crontab:"
crontab -l 2>/dev/null | sed 's/^/    /'
echo "  /etc/crontab:"
cat /etc/crontab 2>/dev/null | grep -v '^#' | grep -v '^$' | sed 's/^/    /'
echo ""

echo "=========================================="
echo "  检查完成，请根据结果进行加固"
echo "=========================================="
```

**内核参数加固 `/etc/sysctl.conf`：**

```bash
# IP转发（仅路由器/VPN需要）
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# SYN洪水防护
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 3

# 反向路径过滤
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# 禁用ICMP重定向
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0

# 禁用源路由
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# 禁用ICMP广播
net.ipv4.icmp_echo_ignore_broadcasts = 1

# 记录可疑包
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# 地址伪装检查
net.ipv4.conf.all.rp_filter = 1

# TCP TIME_WAIT优化
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_tw_reuse = 1

# 增加文件描述符限制
fs.file-max = 65535

# 禁用core dump
kernel.core_uses_pid = 1

# 防止缓冲区溢出
kernel.randomize_va_space = 2

# 应用更改
sysctl -p
```

---

## 总结

本文档全面覆盖了Linux网络安全配置的各个方面，包括网络接口配置、防火墙规则编写、端口管理、SSH安全加固、日志系统配置、服务加固、TCP Wrappers、容器网络安全及实战加固检查清单。通过系统性地应用这些安全配置，可以显著提升Linux服务器的安全防护能力。

> **免责声明**：本文档仅用于安全学习和研究目的。在实际操作中请确保获得适当授权。
