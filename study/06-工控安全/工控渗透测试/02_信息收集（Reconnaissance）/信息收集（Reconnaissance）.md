# 信息收集（Reconnaissance）

### 2.1 开源情报收集（OSINT）

#### 2.1.1 网络空间搜索引擎

利用网络空间搜索引擎发现暴露在互联网上的工控设备：

| 平台 | 网址 | 特点 |
|------|------|------|
| Shodan | shodan.io | 最著名的物联网/工控设备搜索引擎 |
| FOFA | fofa.info | 国内常用，支持中文语法 |
| ZoomEye | zoomeye.org | 知道创宇出品 |
| Censys | censys.io | 证书和设备搜索 |
| Onyphe | onyphe.io | 多源数据聚合 |

**常用搜索语法：**

**Shodan 搜索语法：**
```
# 搜索 Modbus TCP 设备
port:502

# 搜索 S7 协议设备
port:102

# 搜索西门子 S7 PLC
s7

# 搜索 DNP3 设备
port:20000 dnp3

# 搜索 IEC 104 设备
port:2404

# 搜索 HMI 设备
port:5900 hmi

# 搜索特定厂商设备
product:"Siemens"
product:"Schneider Electric"
product:"Allen-Bradley"

# 按国家/地区过滤
port:502 country:CN
port:102 city:"Shanghai"

# 搜索 VNC（HMI 远程访问）
port:5900 "HMI"
```

**FOFA 搜索语法：**
```
# 搜索 Modbus 设备
port="502" && protocol="modbus"

# 搜索 S7 设备
port="102" && protocol="s7"

# 搜索工业路由器
title="Industrial Router"

# 搜索 SCADA 系统
body="SCADA"

# 搜索特定厂商
banner="Siemens SIMATIC"
```

#### 2.1.2 公开信息源

- **厂商官网**：产品文档、固件下载、漏洞公告
- **漏洞库**：CVE、CNVD、CNNVD、ICS-CERT
- **技术论坛**：工控相关的技术讨论
- **招聘信息**：了解目标单位的技术栈
- **招标文件**：了解设备型号和网络架构
- **新闻报道**：项目建设信息

### 2.2 资产发现

#### 2.2.1 主机发现

**注意事项：**
- 工控网络中谨慎使用扫描
- 控制扫描速率，避免影响生产
- 优先使用 ARP 扫描（二层），对设备影响小
- 大规模扫描前需甲方确认

**常用工具：**

**Nmap 主机发现（轻量级）：**
```bash
# ARP 扫描（最安全，仅二层，不影响设备）
nmap -sn -PR 192.168.1.0/24

# ICMP 扫描（轻量）
nmap -sn -PE 192.168.1.0/24

# 慢速扫描（降低影响）
nmap -sn -T2 192.168.1.0/24
```

**Masscan（高速扫描，谨慎使用）：**
```bash
# 快速扫描指定端口
masscan 192.168.1.0/24 -p502,102,2404 --rate=100
```

#### 2.2.2 端口扫描

**常见工控端口：**

| 端口 | 协议 | 说明 |
|------|------|------|
| 21 | FTP | 固件升级、文件传输 |
| 22 | SSH | 远程管理 |
| 23 | Telnet | 远程管理（明文） |
| 80/443 | HTTP/HTTPS | Web 管理界面 |
| 102 | S7comm | 西门子 S7 协议 |
| 502 | Modbus TCP | Modbus TCP 协议 |
| 20000 | DNP3 | DNP3 协议 |
| 2404 | IEC 104 | 电力 IEC 104 协议 |
| 4840 | OPC UA | OPC UA TCP |
| 4843 | OPC UA TLS | OPC UA HTTPS |
| 5900 | VNC | HMI 远程桌面 |
| 789 | FINS | 欧姆龙 FINS 协议 |
| 9600 | FINS TCP | 欧姆龙 FINS TCP |
| 44818 | EtherNet/IP | 罗克韦尔 CIP 协议 |
| 34962-34964 | Profinet | 西门子 Profinet |
| 5006/5007 | MELSEC | 三菱 MC 协议 |

**Nmap 端口扫描：**
```bash
# 工控常用端口扫描（慢速）
nmap -p21,22,23,80,443,102,502,2404,4840,5900,44818 -T3 192.168.1.100

# 全端口扫描（更慢，更全）
nmap -p- -T2 192.168.1.100

# 服务版本探测
nmap -sV -p102,502 192.168.1.100
```

### 2.3 协议识别与设备探测

#### 2.3.1 Nmap NSE 脚本

Nmap 自带一些工控相关的 NSE 脚本：

```bash
# 列出所有工控相关脚本
ls /usr/share/nmap/scripts/ | grep -iE "modbus|s7|enip|bacnet|knx"

# Modbus 设备信息探测
nmap --script modbus-discover -p502 192.168.1.100

# 读取 Modbus 设备信息
nmap --script modbus-info -p502 192.168.1.100

# S7 设备信息探测
nmap --script s7-info -p102 192.168.1.100

# EtherNet/IP 设备探测
nmap --script enip-enumerate -p44818 192.168.1.100
```

#### 2.3.2 专用工控扫描工具

| 工具 | 说明 | 类型 |
|------|------|------|
| Nmap + NSE | 通用扫描器 + 工控脚本 | 开源 |
| Masscan | 高速端口扫描 | 开源 |
| ZMap | 互联网规模扫描 | 开源 |
| ISF (Industrial Control System Exploitation Framework) | 工控渗透框架 | 开源 |
| 360 工业安全大脑扫描器 | 工控漏洞扫描 | 商业 |
| 启明星辰工控扫描器 | 工控漏洞扫描 | 商业 |
| 绿盟工控扫描器 | 工控漏洞扫描 | 商业 |

#### 2.3.3 手动协议探测

**Modbus TCP 设备探测（Python 示例）：**
```python
# 使用 Modbus 功能码 0x11 (报告从站ID) 探测设备
# 向目标发送读设备信息请求，根据响应判断是否为 Modbus 设备
# 详见 modbus_tool.py 中的设备信息探测功能
```

**S7 设备探测：**
```
# 发送 S7 通信设置请求（功能码 0xF0）
# 或发送 CPU 状态查询请求
# 根据响应判断设备型号和版本
```

### 2.4 信息收集阶段输出

**应收集的信息：**
- 网络拓扑结构
- 设备清单（IP、MAC、厂商、型号、版本）
- 开放端口和服务
- 使用的协议类型
- 操作系统和软件版本
- 网络分区和边界设备
- 安全防护设备部署情况

---

---

