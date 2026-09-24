# WiFi密码学深入

### 7.1 WPA2/WPA3密钥派生完整流程

#### 7.1.1 密钥体系总览

WPA2/WPA3的密钥体系是一个多层次的派生结构：

```
密码 (Password) / 主会话密钥 (MSK)
    |
    v
PMK (Pairwise Master Key) - 成对主密钥
    |
    v
PTK (Pairwise Transient Key) - 成对临时密钥
    |
    +-- KCK (Key Confirmation Key) - 密钥确认密钥
    +-- KEK (Key Encryption Key) - 密钥加密密钥
    +-- TK (Temporal Key) - 临时密钥（数据加密）
    +-- MIC Key (用于管理帧保护)
    |
GTK (Group Temporal Key) - 组临时密钥
    |
    +-- GTK (组播/广播数据加密)
    +-- IGTK (完整性组临时密钥 - 管理帧保护)
```

#### 7.1.2 PMK派生

**WPA2-PSK模式**：
```
PMK = PBKDF2-HMAC-SHA1(Password, SSID, 4096, 256)
```

参数说明：
- **Password**：用户输入的WiFi密码（8-63个ASCII字符）
- **SSID**：网络名称（作为盐值）
- **4096**：迭代次数
- **256**：输出位数（32字节）

**WPA3-SAE模式**：
```
PMK = KDF-HMAC-SHA256(密钥材料, "SAE KDK", ...)
```

SAE模式下PMK通过Dragonfly密钥交换派生，不从密码直接计算，因此更安全。

**Enterprise模式**：
```
PMK = MSK的前256位
```

MSK（Master Session Key）由EAP认证过程生成，长度至少64字节。PMK取MSK的前32字节。

#### 7.1.3 PTK派生

PTK通过PRF（Pseudo-Random Function）从PMK派生：

```
PTK = PRF(PMK, "Pairwise key expansion", 
          Min(MAC_AP, MAC_STA) || Max(MAC_AP, MAC_STA) ||
          Min(ANonce, SNonce) || Max(ANonce, SNonce))
```

**PRF函数（WPA2）**：基于HMAC-SHA1的迭代构造
- 输入：密钥、标签、数据
- 输出：根据需要的长度决定迭代次数

**PTK的组成部分**（按顺序拼接）：

| 部分 | 长度 | 用途 |
|------|------|------|
| KCK | 16字节 | EAPOL消息的MIC计算 |
| KEK | 16字节 | 加密GTK等密钥材料 |
| TK | 16字节（CCMP）/ 32字节（TKIP） | 数据帧加密 |
| MIC Key | 8字节（可选） | 管理帧MIC（TKIP时代） |

总长度：通常是384位（48字节）或512位（64字节）

#### 7.1.4 GTK派生

GTK（Group Temporal Key）用于组播和广播流量的加密：

```
GTK = PRF(GMK, "Group key expansion", MAC_AP || GNonce)
```

其中：
- **GMK**（Group Master Key）：组主密钥，由AP生成
- **GNonce**：组随机数
- GTK在AP上生成，然后通过四次握手的M3消息加密分发给客户端

---

### 7.2 PMK、PTK、GTK、TK计算详解

#### 7.2.1 PMK计算深入

**PBKDF2函数详解**：

PBKDF2（Password-Based Key Derivation Function 2）是RFC 2898定义的密钥派生函数：

```
DK = T1 || T2 || ... || Tdklen/hlen
Ti = F(Password, Salt, c, i)
F(Password, Salt, c, i) = U1 ^ U2 ^ ... ^ Uc
U1 = PRF(Password, Salt || INT(i))
U2 = PRF(Password, U1)
...
Uc = PRF(Password, Uc-1)
```

对于WPA2-PSK：
- PRF = HMAC-SHA1
- c = 4096次迭代
- Salt = SSID
- dklen = 256位（32字节）
- hlen = 160位（20字节）

**为什么PBKDF2让破解变慢**：
- 每次密码猜测都需要执行4096次HMAC-SHA1
- 相比直接哈希，破解速度慢4096倍
- 但GPU仍然可以每秒处理数十万次

**Python实现示例**：

```python
import hashlib
import hmac

def pbkdf2(password, salt, iterations, dklen):
    dk = b''
    block_index = 1
    while len(dk) < dklen:
        u = hmac.new(password.encode(), salt.encode() + block_index.to_bytes(4, 'big'), hashlib.sha1).digest()
        result = u
        for _ in range(iterations - 1):
            u = hmac.new(password.encode(), u, hashlib.sha1).digest()
            result = bytes(a ^ b for a, b in zip(result, u))
        dk += result
        block_index += 1
    return dk[:dklen]

pmk = pbkdf2("password123", "MyWiFi", 4096, 32)
print(f"PMK: {pmk.hex()}")
```

#### 7.2.2 PTK计算深入

**PRF函数实现**：

WPA2使用自定义的PRF函数（称为PRF-512、PRF-384等，取决于输出长度）：

```python
def prf(key, label, data, length):
    result = b''
    i = 0
    while len(result) < length:
        msg = bytes([i]) + label.encode() + data
        h = hmac.new(key, msg, hashlib.sha1).digest()
        result += h
        i += 1
    return result[:length]
```

**完整PTK计算示例**：

```python
def compute_ptk(pmk, aa, spa, anonce, snonce):
    if aa < spa:
        mac_min, mac_max = aa, spa
    else:
        mac_min, mac_max = spa, aa
    
    if anonce < snonce:
        nonce_min, nonce_max = anonce, snonce
    else:
        nonce_min, nonce_max = snonce, anonce
    
    data = mac_min + mac_max + nonce_min + nonce_max
    ptk = prf(pmk, "Pairwise key expansion", data, 48)
    return ptk

kck = ptk[0:16]
kek = ptk[16:32]
tk = ptk[32:48]
```

#### 7.2.3 TK（Temporal Key）与数据加密

TK是实际用于加密数据帧的密钥，但并不是直接用来加密。每个数据帧还会派生一个新的密钥：

**CCMP模式下的密钥派生**：
```
Temporal Key (TK) = 128位

对于每个数据帧：
    PN (Packet Number) = 48位序列号
    Nonce = Priority || MAC_SA || PN
    CCMP uses AES-CTR with Nonce and TK
    MIC Key: 使用同样的TK和AES-CMAC计算
```

#### 7.2.4 GTK计算与分发

**GTK生成**：

```python
def compute_gtk(gmk, aa, gnonce):
    data = aa + gnonce
    gtk = prf(gmk, "Group key expansion", data, 32)
    return gtk
```

**GTK分发**：
- GTK由AP生成
- 在四次握手的M3消息中发送给客户端
- 使用KEK加密保护
- 使用KCK计算MIC验证完整性

**GTK更新**：
- 客户端离开网络时，AP应更新GTK
- 定期更新GTK可提升安全性
- 更新通过Group Key Handshake完成

---

### 7.3 消息完整性校验（MIC）原理

#### 7.3.1 MIC的作用

MIC（Message Integrity Check）用于验证消息的完整性和真实性：
- 防止数据被篡改
- 防止数据被伪造
- 防止重放攻击（配合序列号）

#### 7.3.2 EAPOL消息的MIC

四次握手中的EAPOL消息使用MIC来验证完整性：

**MIC计算**：
```
MIC = HMAC-MD5(KCK, EAPOL消息体)
或
MIC = HMAC-SHA1(KCK, EAPOL消息体)
或
MIC = AES-CMAC-128(KCK, EAPOL消息体)  # WPA2/AES
```

**MIC位置**：
- EAPOL-Key帧的Key Information字段指明是否有MIC
- MIC位于Key Data字段之前
- 计算MIC时，MIC字段本身先填充为0

#### 7.3.3 数据帧的MIC

**CCMP的MIC**：
- CCMP使用CBC-MAC模式计算MIC
- MIC长度为64位（8字节）
- 同时保护帧头（部分字段）和数据载荷
- 加密和MIC使用同一个TK，但不同的处理模式

**CCMP封装过程**：
1. 构造CCM Nonce（PN + MAC + Priority）
2. 使用AES-CBC计算MIC（覆盖帧头和数据）
3. 使用AES-CTR加密数据和MIC
4. 结果：加密的数据 + 加密的MIC

**验证过程**：
1. 解密数据和MIC
2. 重新计算MIC
3. 比较计算的MIC和接收到的MIC
4. 不一致则丢弃帧

#### 7.3.4 Michael MIC（TKIP）

TKIP使用Michael算法计算MIC：
- Michael是一个64位的MIC算法
- 比CRC32强，但不如CCMP的CMAC
- 设计上有已知弱点
- TKIP已被弃用，仅作历史了解

---

### 7.4 CCMP与GCMP加密模式对比

#### 7.4.1 CCMP（Counter Mode with CBC-MAC Protocol）

CCMP是WPA2的默认加密协议，基于AES算法：

**组成部分**：
- **CTR模式**：用于加密数据（提供机密性）
- **CBC-MAC**：用于完整性校验（提供认证）
- 两者结合称为CCM模式

**CCMP数据封装**：
```
802.11头部 | CCMP头部 | 加密数据 | MIC | FCS
                |
                +-- PN (48位包序号)
                +-- KeyID
                +-- ExtIV
```

**安全特性**：
- 每个帧使用唯一的PN（Packet Number）
- PN递增，防止重放攻击
- PN + MAC地址构成CTR模式的nonce
- MIC保护帧头和数据的完整性

**CCMP的安全性**：
- 基于AES，安全性高
- 只要nonce不重复，就是安全的
- KRACK攻击利用了密钥重装导致nonce重复的问题

#### 7.4.2 GCMP（Galois/Counter Mode Protocol）

GCMP是WPA3支持的加密协议，基于GCM模式：

**组成部分**：
- **CTR模式**：加密数据
- **GMAC（Galois MAC）**：完整性校验
- 两者结合称为GCM模式

**与CCMP的区别**：
- 使用GCM而非CCM
- 计算效率更高（可并行计算）
- 适用于高速无线网络（802.11ac/ax）

#### 7.4.3 CCMP vs GCMP详细对比

| 特性 | CCMP | GCMP |
|------|------|------|
| 基础算法 | AES | AES |
| 模式 | CCM (CTR + CBC-MAC) | GCM (CTR + GMAC) |
| MIC长度 | 64位 (8字节) | 128位 (16字节) |
| 密钥长度 | 128位 | 128位 / 256位 |
| 计算效率 | 中等（串行） | 高（可并行） |
| 引入标准 | 802.11i (WPA2) | 802.11ac/ad (WPA3支持) |
| nonce重用后果 | 可解密明文 | 可解密明文 + 伪造认证 |
| KRACK影响 | 中等 | 严重 |

#### 7.4.4 为什么GCMP在KRACK下更危险

GCM模式的特点：
- 是一种流密码模式（CTR）
- 相同key+nonce会产生相同的密钥流
- 密钥流泄露可导致明文泄露
- 更严重的是，GMAC的认证密钥也会泄露

**GCMP下的KRACK利用**：
1. 密钥重装导致nonce重置
2. 相同key+nonce加密两个不同的明文P1和P2
3. 得到C1 = P1 XOR Keystream，C2 = P2 XOR Keystream
4. C1 XOR C2 = P1 XOR P2
5. 如果知道其中一个明文，可求出另一个
6. 更严重的是，可以恢复出GHASH密钥，从而伪造任意数据包

---

### 7.5 密钥重装与重放攻击

#### 7.5.1 重放攻击基础

**什么是重放攻击**：
- 攻击者捕获合法的加密数据包
- 在稍后的时间重新发送这个数据包
- 接收方无法区分是原始包还是重放包

**防御重放攻击的机制**：
- **序列号**：每个帧有递增的序列号
- **重放计数器**：接收方记录期望的下一个序列号
- **丢弃旧帧**：序列号小于当前值的帧被丢弃

#### 7.5.2 密钥重装如何导致重放攻击

**正常情况**：
- 密钥安装时，重放计数器初始化为0
- 每发送/接收一个帧，计数器递增
- 旧的帧因为序列号低而被丢弃

**密钥重装后**：
- 计数器被重置为初始值
- 之前的旧帧的序列号又"有效"了
- 攻击者可以重放之前捕获的帧
- 接收方会接受这些重放的帧

#### 7.5.3 重放攻击的危害

**组播重放**：
- 重装GTK后可以重放组播/广播帧
- 例如重放ARP请求、DHCP消息等
- 可能导致网络混乱或信息泄露

**单播重放**：
- 重装PTK后可以重放单播帧
- 重放TCP数据包可能干扰连接
- 重放应用层数据可能导致业务逻辑问题

#### 7.5.4 nonce重用与明文恢复

在CTR模式下，nonce重用是致命的：

```
C1 = P1 XOR Keystream(key, nonce)
C2 = P2 XOR Keystream(key, nonce)

C1 XOR C2 = P1 XOR P2
```

如果攻击者知道P1（例如一个HTTP请求，结构已知），就可以推导出P2。

**实际利用场景**：
1. 捕获正常通信中的加密数据包
2. 触发密钥重装（KRACK）
3. 诱导客户端发送新的数据
4. 新数据用相同的key+nonce加密
5. 通过XOR操作恢复明文

---

