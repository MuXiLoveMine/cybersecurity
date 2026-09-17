# macOS 网络安全

### 8.1 防火墙（Application Firewall, ALF）

ALF（Application Layer Firewall）是 macOS 内置的应用层防火墙，按应用而非端口控制网络访问。

```bash
# 查看 ALF 状态
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
# 输出：Firewall Function Enabled.（或 Disabled.）

# 启用/禁用 ALF
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off

# 设置允许入站连接的应用
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/app
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /path/to/app

# 查看应用列表
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps

# 启用隐身模式（不响应 ping 和端口扫描）
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on

# 查看隐身模式状态
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode

# 配置日志
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setloggingmode on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setloggingopt detail
```

### 8.2 pfctl 包过滤防火墙配置

macOS 内置 OpenBSD 的 PF（Packet Filter）防火墙，提供更细粒度的网络层过滤。

```bash
# pf 配置文件位置
/etc/pf.conf          # 主配置文件
/pf.anchors/          # 锚点规则文件目录

# 查看 pf 状态
sudo pfctl -s info

# 启用/禁用 pf
sudo pfctl -e         # 启用
sudo pfctl -d         # 禁用

# 重新加载规则
sudo pfctl -f /etc/pf.conf

# 查看当前规则
sudo pfctl -s rules

# pf.conf 示例配置

# 宏定义
ext_if = "en0"
web_ports = "{ http, https }"

# 选项
set block-policy drop
set fingerprints "/etc/pf.os"
set state-defaults pflow

# 规范化（清理异常数据包）
scrub in all

# 默认阻止所有入站
block in all

# 允许回环
pass in quick on lo0 all
pass out quick on lo0 all

# 阻止特定国家 IP（示例，需 GeoIP 数据库）
# block in quick from { 10.0.0.0/8, 172.16.0.0/12 } to any

# 允许出站
pass out all keep state

# 允许特定入站
pass in on $ext_if proto tcp from any to any port $web_ports keep state

# 防 SYN Flood
pass in on $ext_if proto tcp to any port $web_ports flags S/SA keep state \
    (max 100, source-track rule, max-src-conn 50, max-src-nodes 50, \
     max-src-conn-rate 10/30, overload flush)
```

### 8.3 VPN 配置与安全

```bash
# 查看网络服务
networksetup -listallnetworkservices

# 配置 L2TP/IPSec VPN（系统偏好设置 GUI 或 networksetup）
sudo networksetup -createl2tpservice "Company VPN" \
    --server vpn.example.com \
    --account username

# 配置 IKEv2 VPN
# 推荐使用 MDM 部署 VPN 配置 Profile
# PayloadType: com.apple.vpn.managed
# PayloadContent:
#   IPv4:
#     Proxies: ...
#   ProxiesType: ...
#   VPNType: IKEv2
#   OnDemand: ...
#   IKEv2:
#     AuthenticationMethod: Certificate
#     ServerCertificateCommonName: vpn.example.com

# 检查 VPN 路由
netstat -rn | grep utun

# Split Tunneling 安全注意：
# 1. 避免 Split Tunneling 导致流量泄露
# 2. 确保所有流量走 VPN 或定义明确的路由
# 3. 监控 DNS 泄露（使用专用 DNS 服务器）
```

### 8.4 网络流量分析工具

```bash
# tcpdump — 命令行抓包
sudo tcpdump -i en0 -w /tmp/capture.pcap
sudo tcpdump -i en0 port 443 -nn -X
sudo tcpdump -i en0 'host malicious.example.com' -nn

# nettop — 实时网络监控
nettop -P -L 1 -x   # 按进程显示网络流量

# lsof — 查看网络连接
sudo lsof -i -P -n | grep LISTEN    # 监听端口
sudo lsof -i -P -n | grep ESTABLISHED  # 已建立连接

# networksetup — 网络配置
networksetup -listallhardwareports
networksetup -getdnsservers Wi-Fi
sudo networksetup -setdnsservers Wi-Fi 1.1.1.1 8.8.8.8

# arp — ARP 表
arp -a              # 查看所有 ARP 表项
arp -a -i en0       # 指定接口

# Wireshark — 图形化抓包分析（需单独安装）
# 安装：brew install --cask wireshark
# 使用专用接口监控模式抓包

# 识别异常 C2 通信
# 1. 周期性固定间隔连接到外部 IP
# 2. DNS 隧道（高频 TXT/A 查询）
# 3. 非标准端口 HTTPS 通信
# 4. DNS over HTTPS (DoH) 绕过本地 DNS 监控
```

---

---

## 📋 内容审核与补充建议

> 针对「macOS 网络安全」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
