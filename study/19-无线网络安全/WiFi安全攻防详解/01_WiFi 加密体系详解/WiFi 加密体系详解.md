# WiFi 加密体系详解

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

---

## 📋 内容审核与补充建议

> 针对「WiFi 加密体系详解」部分的内容审核结果：

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
