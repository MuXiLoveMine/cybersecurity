# 无线IDS/IPS部署与实战

## 目录

- [1. 无线IDS/WIPS概述](#1-无线idswips概述)
- [2. WIDS/WIPS系统架构](#2-widswips系统架构)
- [3. 无线入侵检测技术](#3-无线入侵检测技术)
- [4. 攻击识别与分类](#4-攻击识别与分类)
- [5. 802.11协议安全分析](#5-80211协议安全分析)
- [6. 商业WIDS方案对比](#6-商业wids方案对比)
- [7. 开源WIDS方案](#7-开源wids方案)
- [8. 无线取证技术](#8-无线取证技术)
- [9. 部署最佳实践](#9-部署最佳实践)
- [10. 实战案例](#10-实战案例)
- [11. 配置示例](#11-配置示例)

---

## 1. 无线IDS/WIPS概述

### 1.1 什么是无线入侵检测系统

无线入侵检测系统（Wireless Intrusion Detection System，WIDS）是专门用于监控无线网络频谱和协议流量、识别非法无线设备和无线攻击行为的安全系统。与传统有线网络的IDS不同，WIDS需要处理802.11协议栈的各个层次，包括物理层信号、管理帧、控制帧和数据帧。

无线入侵防御系统（Wireless Intrusion Prevention System，WIPS）在WIDS的基础上增加了主动防御能力，不仅能检测无线攻击，还能自动采取阻断、隔离、告警等响应措施。

### 1.2 为什么需要WIDS/WIPS

传统网络安全防护（防火墙、NIDS）无法覆盖无线攻击面：

- **非法AP接入**：员工私自接入 Rogue AP，绕过有线网络安全策略
- **Evil Twin攻击**：攻击者伪造合法AP进行中间人攻击
- **无线DoS攻击**：Deauth/Disassociate洪水攻击导致服务中断
- **无线嗅探**：攻击者被动监听无线流量窃取数据
- **MAC欺骗**：伪造已授权客户端MAC地址绕过MAC过滤
- **VPN绕过**：通过无线侧绕过企业VPN安全隧道

### 1.3 WIDS与有线IDS的区别

| 特性 | 有线IDS | WIDS |
|------|---------|------|
| 监控介质 | 网线/光纤 | 空中电磁波 |
| 协议栈 | TCP/IP | 802.11 + TCP/IP |
| 信号范围 | 物理端口 | 物理空间（3D） |
| 设备识别 | IP/MAC | MAC + 信号指纹 + Probe |
| 攻击类型 | 网络层以上 | 物理层到应用层 |
| 部署方式 | 旁路/串联 | 分布式传感器 |
| 防御方式 | 丢包/重置 | 反制帧/功率调整 |

### 1.4 WIDS核心能力

1. **无线电频谱监控**：扫描2.4GHz/5GHz/6GHz频段，检测异常信号
2. **设备发现与分类**：自动发现所有无线设备，分类为合法/非法/未知
3. **协议分析**：解析802.11管理帧/控制帧/数据帧，检测协议层攻击
4. **攻击检测**：识别Deauth、Evil Twin、Rogue AP、MAC欺骗等攻击
5. **取证记录**：保存完整无线流量pcap，支持事后取证分析
6. **合规报告**：满足PCI DSS、HIPAA等合规要求

---

## 2. WIDS/WIPS系统架构

### 2.1 系统组件

一个完整的WIDS/WIPS系统包含以下核心组件：

#### 2.1.1 无线传感器（Sensor）

传感器是WIDS的前端数据采集设备，负责：
- 持续扫描所有802.11频段（2.4GHz: 1-14信道, 5GHz: 36-165信道, 6GHz: 2-233信道）
- 捕获所有802.11帧（管理帧、控制帧、数据帧）
- 执行频谱分析，检测非WiFi干扰（蓝牙、微波炉、无绳电话）
- 发送反制帧（WIPS功能）

传感器类型：
- **专用传感器**：独立硬件设备，仅用于监控（如Aruba AP-318, Cisco AIR-AP1562）
- **混合传感器**：兼顾AP和监控功能（如Cisco AP在Off-channel扫描模式）
- **软件传感器**：基于USB无线网卡 + 主机软件（如Kismet + Alfa网卡）

#### 2.1.2 分析引擎（Analysis Engine）

分析引擎是WIDS的核心处理中心，负责：
- 对传感器上报的原始帧进行协议解析
- 执行攻击检测规则引擎
- 设备分类与指纹识别
- 关联分析多传感器数据
- 生成告警事件

#### 2.1.3 管理控制台（Management Console）

- 实时告警展示
- 设备清单管理
- 检测规则配置
- 传感器状态监控
- 报表与合规报告生成
- 取证数据检索

#### 2.1.4 响应执行器（Response Executor）

- 发送Deauth反制帧隔离Rogue AP
- 调整AP发射功率压制攻击信号
- 交换机端口关闭阻断有线连接
- SNMP Trap通知上游系统
- 集成SOAR平台自动化响应

### 2.2 部署模式

#### 模式一：分布式传感器部署

```
[传感器1] ---WiFi--- [传感器2] ---WiFi--- [传感器3]
    |                    |                    |
    +----------+---------+---------+----------+
               |
        [分析引擎 / 管理控制台]
               |
        [企业有线网络]
```

适用场景：大型企业园区，需要全覆盖无线监控。

#### 模式二：混合AP模式

```
[混合AP1] ---+--- [混合AP2] ---+--- [混合AP3]
  AP+监控     |    AP+监控       |    AP+监控
             [WIDS/WIPS引擎]
```

适用场景：中小型企业，AP兼顾业务和监控。

#### 模式三：移动巡查模式

```
[移动传感器(笔记本+USB网卡)]
         |
    [离线分析工具]
```

适用场景：临时安全评估、渗透测试、事件响应。

### 2.3 传感器覆盖规划

传感器覆盖范围受以下因素影响：

| 因素 | 影响 | 建议密度 |
|------|------|----------|
| 2.4GHz | 穿墙能力强，覆盖远 | 每500-800平方米1个 |
| 5GHz | 穿墙弱，覆盖近 | 每300-500平方米1个 |
| 6GHz | 覆盖最短 | 每200-300平方米1个 |
| 混凝墙 | 信号衰减20-30dB | 增加密度 |
| 玻璃隔断 | 信号衰减5-10dB | 正常密度 |
| 金属货架 | 多径干扰严重 | 增加传感器 |
| 开放区域 | 覆盖范围最大 | 正常密度 |

传感器部署位置建议：
- 天花板中央，覆盖最大
- 避免金属遮挡物附近
- 每层楼至少1个传感器
- 高密度区域（会议室/食堂）增加传感器
- 边界区域（外墙/窗户）部署传感器检测外部攻击

---

## 3. 无线入侵检测技术

### 3.1 非法AP检测

#### 3.1.1 授权AP白名单

WIDS维护已授权AP的指纹信息：
- MAC地址（BSSID）
- SSID
- 信道
- 安全配置（WPA2/WPA3/802.1X）
- 厂商OUI
- 发射功率范围

任何不在白名单中发射Beacon的AP被标记为Rogue AP。

#### 3.1.2 有线侧关联

通过交换机CAM表和ARP表，确认Rogue AP是否连接到企业有线网络：
- 查询交换机MAC地址表，定位Rogue AP物理端口
- 发送SNMP查询到交换机获取端口信息
- 自动关闭对应交换机端口（WIPS功能）

#### 3.1.3 无线侧定位

使用多个传感器的RSSI值进行三角定位：
- 至少3个传感器接收到Rogue AP信号
- 通过RSSI差异计算距离
- 三角交点确定物理位置
- 精度约3-5米

### 3.2 Ad-hoc网络检测

Ad-hoc网络（IBSS）允许两台设备直接通信，绕过企业AP：
- 检测Beacon帧中IBSS标志位
- 识别未授权的Ad-hoc BSSID
- 告警并记录参与设备MAC

### 3.3 Misconfigured AP检测

检测配置不当的授权AP：
- 使用WEP加密（已知不安全）
- 使用默认密码（admin/admin）
- 开启WPS（WPS PIN可暴力破解）
- 管理界面暴露在无线网络
- 默认SSID未修改（如TP-LINK_1234）
- 使用TKIP加密（已淘汰）

### 3.4 无线桥接检测

检测通过无线桥接连接两个网络：
- 识别WDS模式通信
- 检测非授权的无线回程链路
- 监控Mesh网络节点异常

---

## 4. 攻击识别与分类

### 4.1 Deauth Flood攻击

#### 4.1.1 攻击原理

攻击者发送大量伪造的Deauth帧，强制断开客户端与AP的连接：

```text
攻击者 -> [伪造AP MAC] Deauth Frame -> 客户端
         [伪造客户端MAC] Deauth Frame -> AP
```

#### 4.1.2 WIDS检测方法

- 检测短时间内大量Deauth帧（阈值：100帧/秒）
- 检测源MAC不在已连接客户端列表中的Deauth帧
- 检测Deauth帧的接收地址为广播（FF:FF:FF:FF:FF:FF）
- 关联分析多个传感器同时检测Deauth

#### 4.1.3 WIPS防御

- 发送反制Deauth帧断开攻击设备
- 调整AP到受影响信道以外
- 启用802.11w管理帧保护（PMF）

### 4.2 Evil Twin攻击

#### 4.2.1 攻击原理

攻击者创建一个与合法AP相同SSID和相近BSSID的AP，诱使客户端连接：

```
合法AP: BSSID=AA:BB:CC:DD:EE:01, 信道6, SSID=CorpWiFi
恶意AP: BSSID=AA:BB:CC:DD:EE:F1, 信道6, SSID=CorpWiFi
```

#### 4.2.2 WIDS检测方法

- 同一SSID出现多个BSSID
- BSSID的OUI与授权AP不匹配
- 相同信道出现多个Beacon
- 信号强度异常变化（客户端突然出现更强信号源）
- 安全配置不一致（合法AP用WPA3-Enterprise，恶意AP用Open/WPA2-PSK）
- DHCP指纹不一致（DHCP Server IP不同）
- 无线帧时间戳异常

#### 4.2.3 WIPS防御

- 发送反制帧阻止客户端连接恶意AP
- 降低合法AP功率，避免信号泄漏到建筑外
- 启用802.1X认证确保客户端只连接合法AP
- 部署VPN over WiFi，即使连接恶意AP也无法解密

### 4.3 MAC Spoofing攻击

#### 4.3.1 攻击原理

攻击者修改自己的MAC地址为已授权客户端的MAC地址，绕过MAC过滤：

```bash
# Linux MAC修改
ifconfig wlan0 down
ifconfig wlan0 hw ether AA:BB:CC:DD:EE:FF
ifconfig wlan0 up

# Mac OS MAC修改
sudo ifconfig en0 ether AA:BB:CC:DD:EE:FF
```

#### 4.3.2 WIDS检测方法

MAC Spoofing检测是WIDS的核心能力之一：
- **信号指纹**：相同MAC但RSSI签名突变（不同位置）
- **序列号跳变**：802.11帧的Sequence Number不连续
- **时间差异常**：同一MAC在两个位置同时出现
- **厂商OUI不匹配**：MAC地址OUI与设备类型不符
- **帧时序异常**：同一MAC的帧间隔不符合正常通信模式
- **Probe请求指纹**：不同设备的Probe Request参数集不同

#### 4.3.3 检测算法

```
序列号检测算法:
1. 跟踪每个MAC的序列号基址
2. 新帧序列号 = (基址 + 偏移) mod 4096
3. 如果偏移 > 100 且不在合理窗口内 -> 告警
4. 如果检测到序列号回退 -> 告警

RSSI指纹检测:
1. 为每个MAC建立RSSI基线 (均值, 方差)
2. 新帧RSSI偏差 > 3σ -> 可能Spoofing
3. 多传感器RSSI指纹不匹配 -> 确认Spoofing
```

### 4.4 Beacon Flood攻击

#### 4.4.1 攻击原理

攻击者发送大量伪造Beacon帧，创建数百个虚拟AP，导致客户端无法发现真实AP：

#### 4.4.2 WIDS检测

- 检测短时间内出现大量新BSSID
- 所有Beacon的发射功率/信号指纹相似
- Beacon帧间隔不符合102.4ms标准
- 检测到Beacon帧来源MAC不在授权列表

### 4.5 Authentication/Association Flood

- 检测大量未完成的Authentication/Association请求
- 检测Auth帧后无Assoc帧的异常模式
- 监控AP关联表溢出

### 4.6 干扰攻击

- 非WiFi干扰源检测（微波炉、蓝牙、无绳电话）
- 持续性窄带干扰
- 频谱分析异常模式
- 检测RF Jamming设备

---

## 5. 802.11协议安全分析

### 5.1 管理帧安全

802.11管理帧（Beacon/Probe/Auth/Assoc/Deauth/Disassoc）在传统802.11中不加密，是无线安全的最大弱点。

#### 802.11w (PMF) 管理帧保护

802.11w（Protected Management Frames）通过加密单播管理帧来解决此问题：

```
PMF能力协商:
  1. AP在Beacon/Probe Response中包含RSN信息元素，PMF=Required/Capable
  2. 客户端在Association Request中携带PMF能力
  3. AP和客户端协商管理帧加密密钥
  4. 后续单播管理帧使用BIP（Broadcast/Multicast Integrity Protocol）保护

保护的管理帧:
  - Disassociation
  - Deauthentication
  - Action (部分子类型)
```

WIDS需要检测PMF是否正确启用，以及是否存在降级攻击。

### 5.2 控制帧安全

控制帧（RTS/CTS/ACK）不加密且不可保护：
- 攻击者可伪造CTS帧触发AP延迟
- 可伪造ACK帧导致帧丢失
- 检测方法：异常RTS/CTS频率、RTS/CTS比率异常

### 5.3 数据帧安全

#### WPA3分析

WPA3相比WPA2的关键改进：
- SAE（Simultaneous Authentication of Equals）替代PSK
- 抗离线字典攻击
- 前向保密
- 192位安全套件（WPA3-Enterprise 192-bit模式）

WIDS检测项：
- 检测WPA3降级到WPA2攻击
- 检测SAE握手异常
- 检测OWE（Opportunistic Wireless Encryption）配置

### 5.4 802.1X/EAP安全

检测EAP认证过程中的异常：
- EAP方法降级攻击（EAP-TLS -> EAP-PEAP -> EAP-MSCHAPv2）
- 伪造RADIUS服务器（检查服务器证书）
- EAP-Response/Identity泄露用户身份
- EAP-Logoff帧导致认证状态异常

---

## 6. 商业WIDS方案对比

### 6.1 Cisco Adaptive Wireless IPS

**架构**：Cisco WLC（Wireless LAN Controller）+ lightweight AP

**核心功能**：
- Rogue AP检测与自动遏制
- 自无线干扰检测（wIPS功能需要额外许可证）
- 集成ISE进行身份关联
- 频谱分析（CleanAir技术）
- 支持分布式部署

**优势**：
- 与Cisco网络设备深度集成
- CleanAir频谱分析业界领先
- 支持跨控制器Rogue AP关联

**劣势**：
- 许可证成本高
- 仅支持Cisco AP作为传感器
- 配置复杂

**配置示例**：

```bash
# Cisco WLC CLI配置wIPS
config wips ap enable all
config wips rogue-ap contain 7  # 遏制Rogue AP，发送7个反制客户端
config wips rogue-client contain 3
config wips rogue-report interval 60
show wips summary
show wips rogue-ap detailed <mac>
```

### 6.2 Aruba (HPE) RFProtect

**架构**：Aruba Mobility Controller + AP + RFProtect许可证

**核心功能**：
- WIDS/WIPS一体化
- 频谱分析
- 无线设备分类
- Rogue AP自动遏制
- 集成ClearPass进行策略控制

**优势**：
- AP混合模式（业务+监控）
- 与ClearPass深度集成
- 支持多厂商AP监控

**配置示例**：

```
# Aruba Mobility Controller配置
wids-profile "Corp-WIDS"
  rogue-ap-detection enable
  rogue-ap-contain enable
  spoof-detection enable
  deauth-flood-detection enable
  valid-ap-list "Corp-APs"  # 授权AP列表
ap-group "Corp-APs"
  wids-profile "Corp-WIDS"
  ap-mode air-monitor  # 部分AP专用监控模式
```

### 6.3 Fortinet FortiGate WiFi

**优势**：
- 集成在FortiGate防火墙中
- 有线无线一体化安全策略
- 支持FortiLink自动管理

### 6.4 方案对比表

| 特性 | Cisco wIPS | Aruba RFProtect | Fortinet |
|------|-----------|-----------------|----------|
| 架构 | 专用控制器 | 混合AP | 集成防火墙 |
| 传感器 | Cisco AP | Aruba AP | FortiAP |
| 频谱分析 | CleanAir | 集成 | 基础 |
| Rogue AP遏制 | 支持 | 支持 | 支持 |
| 三角定位 | 支持 | 支持 | 支持 |
| 身份关联 | ISE | ClearPass | FSSO |
| 价格 | 高 | 中高 | 中 |
| 多厂商支持 | 不支持 | 部分 | 不支持 |

---

## 7. 开源WIDS方案

### 7.1 Kismet

Kismet是最流行的开源无线监控工具：

#### 核心能力
- 被动扫描所有802.11频段
- 设备发现与分类
- 隐藏SSID探测
- 数据包捕获（pcap格式）
- 基础攻击检测
- Web UI实时监控
- 插件系统扩展

#### 部署配置

```bash
# 安装Kismet
sudo apt-get install kismet

# 配置kismet.conf
source=rt8187:wifi0  # 指定无线网卡和驱动
channel=1,6,11,36,40,44  # 扫描信道
alertbackdoor=all  # 启用所有告警
logtitle=Kismet-Log  # 日志标题
logtypes=pcap  # 日志格式

# 启动Kismet
kismet -c wlan0 -t "WIDS-Monitor" --daemonize

# Web UI
http://localhost:2501
```

#### Kismet告警规则

```lua
# kismet_alerts.conf
alert DEAUTHFLOOD 100 1  # 100秒内超过1个Deauth -> 告警
alert DISASSOCFLOOD 100 1
alert AUTHFLOOD 60 10  # 60秒内超过10个Auth请求
alert APCHANGE  # AP信道或ESSID变化
alert PROBEREQUEST  # 异常Probe Request
alert BROADCASTPROBE  # 广播Probe
alert WEPFAIL  # WEP认证失败
alert WPA2DOWNGRADE  # WPA2降级攻击
alert TKIPREUSE  # TKIP重用
alert CHRSTOP  # 信道停止扫描
```

#### Kismet REST API

```python
import requests

# 获取所有设备
resp = requests.get('http://localhost:2501/devices/all_devices.json')
devices = resp.json()

# 获取告警
resp = requests.get('http://localhost:2501/alerts/alerts.json')
alerts = resp.json()

# 获取信道占用
resp = requests.get('http://localhost:2501/channels/channels.json')
channels = resp.json()
```

### 7.2 Horde

Horde是分布式Kismet部署框架：

```
[传感器1 - Kismet] ---+
[传感器2 - Kismet] ---+--> [Horde服务器]
[传感器3 - Kismet] ---+      [Web仪表盘]
```

### 7.3 其他开源工具

- **Aircrack-ng**：无线安全审计套件，支持抓包、注入、破解
- **PixieWPS**：WPS PIXIE攻击工具
- **Wifite**：自动化无线攻击框架
- **Fern WiFi Cracker**：GUI无线攻击工具

---

## 8. 无线取证技术

### 8.1 抓包分析

#### 全频段抓包

使用Monitor模式无线网卡进行全频段抓包：

```bash
# 启用Monitor模式
airmon-ng start wlan0

# 设置信道
iwconfig wlan0mon channel 6

# 抓包（保存pcap）
airodump-ng wlan0mon -w capture --channel 1,6,11,36,40,44 -w /tmp/wids_capture

# 使用tshark进行实时分析
tshark -i wlan0mon -f "type mgt" -T fields -e wlan.fc.type -e wlan.fc.subtype -e wlan.sa -e wlan.da -e wlan.bssid
```

#### 管理帧分析

```python
from scapy.all import *

def analyze_mgmt_frame(pkt):
    if pkt.haslayer(Dot11):
        # 检测Deauth帧
        if pkt.type == 0 and pkt.subtype == 12:
            src = pkt.addr2
            dst = pkt.addr1
            bssid = pkt.addr3
            print(f"[ALERT] Deauth: {src} -> {dst} (BSSID: {bssid})")
            log_event("DEAUTH", src, dst, bssid, pkt)
        
        # 检测Disassoc帧
        elif pkt.type == 0 and pkt.subtype == 10:
            src = pkt.addr2
            dst = pkt.addr1
            print(f"[ALERT] Disassoc: {src} -> {dst}")
            log_event("DISASSOC", src, dst, pkt.addr3, pkt)
        
        # 检测Beacon帧
        elif pkt.type == 0 and pkt.subtype == 8:
            ssid = pkt.info.decode('utf-8', errors='ignore')
            bssid = pkt.addr3
            channel = get_channel_from_beacon(pkt)
            print(f"[INFO] Beacon: SSID={ssid} BSSID={bssid} CH={channel}")

def get_channel_from_beacon(pkt):
    if pkt.haslayer(Dot11Elt):
        elt = pkt[Dot11Elt]
        while elt:
            if elt.ID == 3:  # DS Parameter Set
                return elt.info[0]
            elt = elt.payload
    return None

sniff(iface="wlan0mon", prn=analyze_mgmt_frame, store=0)
```

### 8.2 信道扫描

```python
import subprocess
import json

def scan_all_channels(interface="wlan0mon"):
    channels_24ghz = list(range(1, 15))
    channels_5ghz = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165]
    all_channels = channels_24ghz + channels_5ghz
    
    results = {}
    for ch in all_channels:
        subprocess.run(["iwconfig", interface, "channel", str(ch)],
                       capture_output=True)
        import time
        time.sleep(0.5)  # 等待信道切换
        
        output = subprocess.run(
            ["iwlist", interface, "scan"],
            capture_output=True, text=True
        )
        aps = parse_iwlist(output.stdout)
        if aps:
            results[ch] = aps
    
    return results

def parse_iwlist(output):
    aps = []
    current_ap = {}
    for line in output.split('\n'):
        line = line.strip()
        if 'Address:' in line:
            current_ap['bssid'] = line.split('Address: ')[1]
        elif 'ESSID:' in line:
            current_ap['ssid'] = line.split('ESSID:"')[1].rstrip('"')
        elif 'Channel:' in line:
            current_ap['channel'] = line.split('Channel:')[1].strip()
        elif 'Quality=' in line:
            current_ap['quality'] = line.split('Quality=')[1].split(' ')[0]
        if 'Cell' in line and current_ap:
            aps.append(current_ap)
            current_ap = {}
    return aps
```

### 8.3 设备指纹

```python
def generate_device_fingerprint(pkt):
    """生成设备指纹用于追踪"""
    fingerprint = {
        'mac': pkt.addr2,
        'oui': pkt.addr2[:8],
        'frame_types': set(),
        'channels': set(),
        'signal_range': [100, 0],
        'ssid_list': set(),
        'security_modes': set(),
        'first_seen': time.time(),
        'last_seen': time.time(),
    }
    
    if pkt.haslayer(Dot11):
        fingerprint['frame_types'].add(f"{pkt.type}/{pkt.subtype}")
        if pkt.type == 0 and pkt.subtype == 8:  # Beacon
            if pkt.haslayer(Dot11Elt):
                elt = pkt[Dot11Elt]
                while elt:
                    if elt.ID == 0:  # SSID
                        fingerprint['ssids'].add(elt.info)
                    elif elt.ID == 48:  # RSN
                        fingerprint['security_modes'].add('WPA2')
                    elt = elt.payload
    
    # RSSI信息
    if hasattr(pkt, 'dBm_AntSignal'):
        rssi = pkt.dBm_AntSignal
        fingerprint['signal_range'][0] = min(fingerprint['signal_range'][0], rssi)
        fingerprint['signal_range'][1] = max(fingerprint['signal_range'][1], rssi)
    
    return fingerprint
```

### 8.4 取证报告生成

```python
import json
from datetime import datetime

class WirelessForensicsReport:
    def __init__(self):
        self.devices = {}
        self.alerts = []
        self.pcap_path = None
        self.start_time = datetime.now()
    
    def add_device(self, mac, device_info):
        self.devices[mac] = device_info
    
    def add_alert(self, alert_type, details):
        self.alerts.append({
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'details': details
        })
    
    def generate_report(self, output_path):
        report = {
            'title': '无线安全取证报告',
            'scan_start': self.start_time.isoformat(),
            'scan_end': datetime.now().isoformat(),
            'summary': {
                'total_devices': len(self.devices),
                'authorized_aps': sum(1 for d in self.devices.values() if d.get('authorized')),
                'rogue_aps': sum(1 for d in self.devices.values() if d.get('type') == 'rogue_ap'),
                'total_alerts': len(self.alerts),
                'critical_alerts': sum(1 for a in self.alerts if a['type'] in ['DEAUTH_FLOOD', 'EVIL_TWIN']),
            },
            'devices': list(self.devices.values()),
            'alerts': self.alerts,
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
```

---

## 9. 部署最佳实践

### 9.1 传感器覆盖最佳实践

1. **覆盖率目标**：所有企业物理区域100%覆盖
2. **冗余覆盖**：每个位置至少2个传感器可接收信号
3. **边界覆盖**：建筑外墙和窗户附近部署传感器
4. **高密度区域**：会议室、大厅增加传感器密度
5. **频段覆盖**：同时覆盖2.4GHz、5GHz、6GHz
6. **定期巡检**：每季度验证传感器覆盖效果

### 9.2 告警规则配置

```
告警分级:
  紧急:
    - Rogue AP连接到企业有线网络
    - Evil Twin检测（同SSID多BSSID+安全降级）
    - Deauth Flood攻击
    - WPA3降级攻击
  
  重要:
    - 未授权Ad-hoc网络
    - MAC Spoofing检测
    - 未授权无线桥接
    - 认证洪水攻击
  
  一般:
    - 新设备发现
    - Misconfigured AP
    - 非WiFi干扰检测
    - 信号强度异常波动
  
  信息:
    - 设备类型变化
    - SSID广播变化
    - 信道变更
```

### 9.3 响应策略

| 攻击类型 | 自动响应 | 人工响应 |
|---------|---------|---------|
| Rogue AP | 交换机端口关闭 | 物理定位并移除 |
| Evil Twin | 反制Deauth + 告警 | 安全团队介入 |
| Deauth Flood | 信道切换 + PMF启用 | 定位攻击者 |
| MAC Spoofing | 阻断Spoofed MAC | 审查授权设备 |
| Ad-hoc | 告警 | 安全策略宣贯 |
| 干扰 | 频谱分析告警 | 排查干扰源 |

### 9.4 集成企业安全架构

```
WIDS/WIPS
    |
    +---> SIEM (Splunk/ELK)
    |       告警关联分析
    |       跨域攻击链可视化
    |
    +---> SOAR (Cortex XSOAR/Ansible)
    |       自动化响应
    |       工单创建
    |
    +---> NAC (Cisco ISE/Aruba ClearPass)
    |       终端合规性检查
    |       有线侧隔离
    |
    +--→ CMDB
    |       资产关联
    |       设备指纹库
    |
    +--> 威胁情报
            IOC匹配
            APT关联
```

---

## 10. 实战案例

### 10.1 Evil Twin检测案例

**场景**：企业发现部分员工报告WiFi连接不稳定，怀疑遭受Evil Twin攻击。

**调查过程**：

1. 检查WIDS告警日志，发现同一SSID出现两个BSSID
2. 合法AP: BSSID=AA:BB:CC:00:01:01, 信道=6, WPA3-Enterprise
3. 恶意AP: BSSID=00:11:22:33:44:55, 信道=6, WPA2-PSK
4. 恶意AP使用默认密码，安全配置降级
5. 通过三角定位确定恶意AP位置在停车场
6. WIPS发送反制帧阻止客户端连接
7. 安全团队前往停车场发现便携式AP设备

**关键检测点**：
- 同一SSID两个BSSID
- 安全配置降级（WPA3 → WPA2-PSK）
- OUI不匹配（企业AP是Cisco，恶意AP是Realtek）
- 位置异常（合法AP在室内，恶意AP在停车场）

### 10.2 Rogue AP隔离案例

**场景**：员工私自接入个人便携AP到企业网络。

**调查过程**：

1. WIDS检测到新BSSID，不在授权列表
2. 传感器捕获该AP的Beacon帧
3. 分析引擎确定Rogue AP连接在企业有线网络
4. 查询交换机MAC地址表，定位物理端口
5. WIPS自动关闭交换机端口
6. 安全团队定位到员工工位

**自动化响应脚本**：

```python
import subprocess
import re

def locate_rogue_ap_on_switch(bssid, switch_ip, community="public"):
    """在交换机上定位Rogue AP"""
    # SNMP查询MAC地址表
    cmd = f"snmpwalk -v2c -c {community} {switch_ip} .1.3.6.1.2.1.17.4.3.1.1"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # 解析MAC地址表
    for line in result.stdout.split('\n'):
        if bssid.lower().replace(':', '') in line.lower():
            port_oid = line.split('=')[0].strip()
            port_cmd = f"snmpwalk -v2c -c {community} {switch_ip} .1.3.6.1.2.1.17.1.4.3.1.1"
            port_result = subprocess.run(port_cmd, shell=True, capture_output=True, text=True)
            
            # 匹配端口号
            for port_line in port_result.stdout.split('\n'):
                if port_oid.split('.')[-1] in port_line:
                    port_num = re.search(r'(\d+)$', port_line)
                    if port_num:
                        return int(port_num.group(1))
    return None

def block_switch_port(switch_ip, port_num):
    """关闭交换机端口隔离Rogue AP"""
    commands = [
        f"interface GigabitEthernet{port_num}",
        "shutdown",
        "description Blocked by WIDS - Rogue AP detected"
    ]
    # 通过SSH发送配置命令
    # ssh admin@switch_ip -> configure terminal -> interface -> shutdown
    print(f"[BLOCKED] Port {port_num} on {switch_ip} has been shut down")
```

### 10.3 MAC Spoofing检测案例

**场景**：检测到已授权MAC地址的异常行为。

**检测过程**：

1. 传感器A在3楼报告MAC=AA:BB:CC:DD:EE:01，RSSI=-45dBm
2. 传感器B在1楼报告同一MAC=AA:BB:CC:DD:EE:01，RSSI=-50dBm
3. 物理距离超过200米，不可能同时出现如此强信号
4. 序列号分析发现跳变：传感器A收到seq=1000，传感器B收到seq=2000
5. 判定为MAC Spoofing攻击
6. 触发告警并通知安全团队

---

## 11. 配置示例

### 11.1 Kismet企业部署配置

```bash
# /etc/kismet/kismet.conf

# 基本配置
servername=Enterprise-WIDS
serversecret=CHANGE_ME_TO_RANDOM_STRING

# 数据源配置（多网卡）
source=nl80211:wlan0:name=Sensor-2.4G
source=nl80211:wlan1:name=Sensor-5G

# 信道跳跃配置
channelhop=true
channelsplit=true
channelhop=1,6,11,36,40,44,48,52,56,60,64,100,104,108,112,116,120,124,128,132,136,140,144,149,153,157,161,165

# 日志配置
logtypes=pcap
logprefix=/var/log/kismet
logrotate=true

# 告警配置
alertbackdoor=all

# Web UI
httpd=true
httpdport=2501
httpdallow=10.0.0.0/8

# Tracker配置
tracker_devices=true
tracker_devices_time=60

# 加密告警
alert CRYPTODOWN  # 加密降级告警
alert TKIPREUSE    # TKIP重用
alert WEPFAIL      # WEP认证失败
```

### 11.2 Cisco WLC WIDS配置

```bash
# 启用wIPS
config wips ap enable all

# 配置Rogue AP遏制
config wips rogue-ap contain 7  # 使用7个客户端遏制

# 配置Rogue客户端遏制
config wips rogue-client contain 3

# 配置检测间隔
config wips rogue-report interval 60

# 配置告警阈值
config wips alert interval 30

# 查看wIPS状态
show wips summary

# 查看Rogue AP详情
show wips rogue-ap detailed <mac-address>

# 查看所有Rogue设备
show wips rogue-device all

# 导出Rogue报告
show wips rogue-report export
```

### 11.3 集成Splunk SIEM

```python
# 将Kismet告警转发到Splunk
import requests
import json
from splunk_hec_handler import SplunkHEC

class KismetSplunkIntegration:
    def __init__(self, kismet_url, splunk_url, splunk_token):
        self.kismet_url = kismet_url
        self.splunk = SplunkHEC(splunk_url, splunk_token)
    
    def forward_alerts(self):
        """转发Kismet告警到Splunk"""
        resp = requests.get(f"{self.kismet_url}/alerts/alerts.json")
        alerts = resp.json()
        
        for alert in alerts:
            event = {
                'time': alert.get('timestamp'),
                'source': 'kismet-wids',
                'sourcetype': 'wireless:alert',
                'event': {
                    'alert_type': alert.get('type'),
                    'severity': self._map_severity(alert.get('type')),
                    'source_mac': alert.get('source'),
                    'dest_mac': alert.get('dest'),
                    'bssid': alert.get('bssid'),
                    'channel': alert.get('channel'),
                    'description': alert.get('text'),
                    'sensor': alert.get('sensor'),
                }
            }
            self.splunk.send(event)
    
    def _map_severity(self, alert_type):
        severity_map = {
            'DEAUTHFLOOD': 'critical',
            'DISASSOCFLOOD': 'critical',
            'AUTHFLOOD': 'high',
            'PROBEREQUEST': 'medium',
            'BROADCASTPROBE': 'low',
            'APCHANGE': 'info',
            'TKIPREUSE': 'high',
            'WEPFAIL': 'medium',
        }
        return severity_map.get(alert_type, 'info')
    
    def forward_devices(self):
        """转发设备列表到Splunk"""
        resp = requests.get(f"{self.kismet_url}/devices/all_devices.json")
        devices = resp.json()
        
        for dev in devices:
            event = {
                'source': 'kismet-wids',
                'sourcetype': 'wireless:device',
                'event': {
                    'mac': dev.get('kismet.device.base.macaddr'),
                    'type': dev.get('kismet.device.base.type'),
                    'channel': dev.get('kismet.channel.frequency'),
                    'signal': dev.get('kismet.device.base.signal'),
                    'first_seen': dev.get('kismet.device.base.first_time'),
                    'last_seen': dev.get('kismet.device.base.last_time'),
                }
            }
            self.splunk.send(event)
```

### 11.4 Sigma规则 - 无线攻击检测

```yaml
title: 检测无线Deauth Flood攻击
id: 5a3b2c1d-9e8f-7a6b-5c4d-3e2f1a0b9c8d
status: experimental
description: 检测短时间内大量Deauth帧，可能表示Deauth Flood DoS攻击
author: Security Team
date: 2026/09/15
logsource:
    product: kismet
    service: alerts
detection:
    selection:
        alert_type: DEAUTHFLOOD
    timeframe: 60s
    condition: selection | count() > 5
falsepositives:
    - 合法AP重启
    - 网络维护操作
level: critical
tags:
    - attack.disruption
    - attack.t1498
    - attack.t1498.001
```

---

## 12. 合规要求

### 12.1 PCI DSS无线安全要求

PCI DSS对无线网络安全有明确要求：
- 定期扫描所有无线设备
- 检测未授权无线设备
- 事件响应计划包含无线安全
- 季度无线渗透测试

### 12.2 HIPAA无线安全要求

- 加密无线通信（WPA2/WPA3）
- 定期审计无线访问
- 无线安全风险评估
- 无线安全事件记录

### 12.3 等保2.0无线安全要求

- 三级以上系统需无线安全审计
- 无线网络边界防护
- 无线接入认证
- 无线安全监控与告警

---

## 13. 未来发展趋势

### 13.1 AI驱动的无线安全

- 机器学习检测异常无线行为模式
- RF指纹识别替代MAC地址认证
- 自适应频谱管理
- 预测性威胁检测

### 13.2 6GHz频段安全

- 802.11be (Wi-Fi 7) 新特性
- 6GHz频段管理帧保护
- AFC（Automated Frequency Coordination）
- 6GHz传感器部署

### 13.3 物联网无线安全

- 低功耗无线协议安全（BLE/Zigbee/Thread）
- 大规模设备识别
- 自动化分类与隔离
- 与NAC深度集成

---

## 总结

无线IDS/IPS是网络安全防护体系中不可或缺的一环。传统有线网络安全设备无法覆盖无线攻击面，而无线攻击（Rogue AP、Evil Twin、Deauth Flood等）对企业数据安全构成严重威胁。

企业应建立分层防御体系：
1. 部署WIDS/WIPS实现全天候无线监控
2. 启用802.11w管理帧保护（PMF）
3. 使用WPA3-Enterprise + 802.1X认证
4. 定期进行无线渗透测试
5. 集成SIEM/SOAR实现自动化响应
6. 建立无线安全事件响应流程
7. 对员工进行无线安全意识培训

通过商业WIDS方案（Cisco/Aruba）或开源方案（Kismet）的合理部署，企业可以有效检测和防御无线安全威胁，满足PCI DSS、HIPAA和等保2.0合规要求。
