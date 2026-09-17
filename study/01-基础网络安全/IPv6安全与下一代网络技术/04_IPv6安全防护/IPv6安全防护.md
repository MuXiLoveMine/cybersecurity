# IPv6安全防护

### 3.1 SEND/CGA

SEND（SEcure Neighbor Discovery）是对NDP的安全增强，使用CGA（Cryptographically Generated Addresses）防止地址欺骗。

**CGA原理：**

```
CGA生成过程：
1. 选择Modifier（随机数，16字节）
2. 计算Hash：Hash1 = SHA1(Modifier || SubnetPrefix || Public Key)
3. 取Hash1的左59位（或更多）作为Interface ID
4. 设置U/L位为1（本地管理）
5. CGA地址 = SubnetPrefix || Interface ID

验证过程：
1. 接收者获取发送者的公钥和Modifier
2. 重新计算Hash1
3. 验证地址是否匹配
4. 验证NDP消息签名
```

**SEND配置（Cisco设备示例）：**

```
! 启用SEND/CGA
ipv6 cga rsakeypair key-name

! 配置CGA参数
ipv6 cga modifier rsakeypair key-name sec-level 1

! 接口配置
interface GigabitEthernet0/0/0
  ipv6 address 2001:db8::/64 cga key-name
  ipv6 nd secured
  ipv6 nd sec-level 1
  ipv6 nd cga rsakeypair key-name
!
```

> 注意：SEND在实际部署中非常少见，主要原因是配置复杂且性能开销大。多数环境使用RA Guard等其他防护措施替代。

### 3.2 RA Guard

RA Guard（Router Advertisement Guard）是交换机层面的防护机制，阻止非信任端口发送RA消息。

**Cisco RA Guard配置：**

```
! 定义RA Guard策略
ipv6 nd raguard policy RAGUARD_POLICY
  device-role host
  trusted-port no
  hop-limit maximum 64
  managed-config-flag off
  other-config-flag off
  router-preference maximum medium
!

! 应用到接入端口
interface GigabitEthernet0/1
  switchport mode access
  ipv6 nd raguard attach-policy RAGUARD_POLICY
!

! 信任上联端口
interface GigabitEthernet0/24
  switchport mode trunk
  ipv6 nd raguard attach-policy RAGUARD_POLICY
!
```

**华为设备RA Guard配置：**

```
# 使能RA Guard功能
ipv6 nd raguard enable

# 配置接口角色
interface GigabitEthernet0/0/1
  ipv6 nd raguard role access-port
#
interface GigabitEthernet0/0/24
  ipv6 nd raguard role trusted
#
```

**Linux主机RA Guard（使用ip6tables）：**

```bash
# 只允许来自路由器的RA
ip6tables -A INPUT -p icmpv6 --icmpv6-type router-advertisement \
  -m mac --mac-source 00:aa:bb:cc:dd:ee -j ACCEPT

# 拒绝其他所有RA
ip6tables -A INPUT -p icmpv6 --icmpv6-type router-advertisement \
  -j DROP

# 使用ndppd守护进程保护
# 安装并配置ndppd
apt install ndppd
```

### 3.3 DHCPv6-Shield

DHCPv6-Shield防止非授权DHCPv6服务器响应客户端请求。

```
! Cisco DHCPv6 Guard配置
ipv6 dhcp guard policy DHCPV6_POLICY
  device-role client
  trusted-port no
!

interface GigabitEthernet0/1
  ipv6 dhcp guard attach-policy DHCPV6_POLICY
!

interface GigabitEthernet0/24
  ipv6 nd raguard attach-policy RAGUARD_POLICY
  ipv6 dhcp guard attach-policy DHCPV6_POLICY
  ipv6 dhcp guard trusted-port
!
```

### 3.4 IPv6防火墙规则

**ip6tables防火墙规则集：**

```bash
#!/bin/bash
# IPv6防火墙基础规则

# 清除现有规则
ip6tables -F
ip6tables -X

# 默认策略
ip6tables -P INPUT DROP
ip6tables -P FORWARD DROP
ip6tables -P OUTPUT ACCEPT

# 1. 允许回环
ip6tables -A INPUT -i lo -j ACCEPT
ip6tables -A OUTPUT -o lo -j ACCEPT

# 2. 允许已建立连接
ip6tables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 3. 允许ICMPv6（必须！IPv6依赖ICMPv6运行）
ip6tables -A INPUT -p icmpv6 -j ACCEPT

# 4. 限制ICMPv6速率（防洪水攻击）
ip6tables -A INPUT -p icmpv6 -m limit --limit 10/sec --limit-burst 20 -j ACCEPT
ip6tables -A INPUT -p icmpv6 -j DROP

# 5. 阻止扩展报头滥用
# 阻止没有上层协议头且非分片的包
ip6tables -A INPUT -m u32 --u32 "0x4&0xff=0xff" -j DROP  # Next Header = No Next Header

# 6. 丢弃有Routing扩展头的包（源路由攻击）
ip6tables -A INPUT -m rt --rt-type 0 -j DROP

# 7. 限制分片包速率
ip6tables -A INPUT -m frag --fragmore -j DROP  # 阻止重叠分片
ip6tables -A INPUT -p tcp --fragment -m limit --limit 10/sec -j ACCEPT
ip6tables -A INPUT --fragment -j DROP

# 8. 允许SSH
ip6tables -A INPUT -p tcp --dport 22 -j ACCEPT

# 9. 允许HTTP/HTTPS
ip6tables -A INPUT -p tcp --dport 80 -j ACCEPT
ip6tables -A INPUT -p tcp --dport 443 -j ACCEPT

# 10. 记录被拒绝的连接
ip6tables -A INPUT -j LOG --log-prefix "IP6_DROP: " --log-level 6
ip6tables -A INPUT -j DROP

# 保存规则
ip6tables-save > /etc/iptables/rules.v6
```

**pfSense/OPNsense IPv6防火墙规则：**

```
# WAN入站规则
# 1. 允许ICMPv6（必须）
pass in on WAN inet6 proto ipv6-icmp all

# 2. 允许已建立连接
pass in on WAN inet6 proto {tcp,udp} from any to (WAN) \
  port {80,443} keep state

# 3. 阻止RA注入
block in on WAN inet6 proto ipv6-icmp \
  from any to ff02::1 ipv6-icmp-type router-advertisement

# LAN规则
# 4. 允许SLAAC和DHCPv6
pass in on LAN inet6 proto udp from any to fe80::/10 port {546,547}
```

---

---

## 📋 内容审核与补充建议

> 针对「IPv6安全防护」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
