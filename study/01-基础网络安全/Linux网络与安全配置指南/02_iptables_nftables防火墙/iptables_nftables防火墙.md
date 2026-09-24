# iptables/nftables防火墙

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

---

