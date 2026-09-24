# WPA3安全分析

### 1.1 WPA3新特性概述

WPA3（Wi-Fi Protected Access 3）是Wi-Fi联盟于2018年发布的第三代Wi-Fi安全标准，旨在解决WPA2中暴露的诸多安全问题。与WPA2相比，WPA3引入了以下核心改进：

#### 1.1.1 SAE（Simultaneous Authentication of Equals）

SAE是WPA3-Personal的核心认证协议，替代了WPA2中的PSK（Pre-Shared Key）认证方式。SAE基于Dragonfly密钥交换协议（RFC 7664），具有以下关键特性：

- **对等认证**：通信双方地位平等，不存在客户端/服务端的角色差异
- **前向保密**：即使长期密钥（密码）泄露，之前的会话密钥仍然安全
- **抗离线字典攻击**：攻击者无法通过捕获的握手包进行离线暴力破解
- **抗主动攻击**：攻击者无法通过交互来加速密码猜测

#### 1.1.2 OWE（Opportunistic Wireless Encryption）

OWE（RFC 8110）提供了"机会主义加密"，用于开放网络（无密码WiFi）。它允许客户端和AP在不预先共享密钥的情况下建立加密连接，防止被动窃听。

- 类似HTTPS对HTTP的升级，但无需证书
- 基于Diffie-Hellman密钥交换
- 不提供身份认证，仅加密数据传输

#### 1.1.3 管理帧保护增强

WPA3要求支持**管理帧保护（Management Frame Protection, MFP）**，即802.11w标准的强制实施：

- 取消认证（Deauthentication）和解除关联（Disassociation）帧受到保护
- 防止简单的取消认证洪泛攻击
- Robust Management Frames (RMF) 包括：Deauthentication、Disassociation、Spectrum Management、QoS、Radio Measurement等

#### 1.1.4 其他增强特性

- **192位加密套件**：WPA3-Enterprise提供可选的192位安全模式，使用GCMP-256、SHA-384、ECDH-P-384、ECDSA-P-384
- **更强大的密钥派生**：使用更安全的密钥派生函数
- **Easy Connect**：简化IoT设备的安全配置流程

---

### 1.2 SAE协议原理深度解析

#### 1.2.1 Dragonfly密钥交换协议

SAE基于Dragonfly协议，这是一种基于密码的认证密钥交换（Password Authenticated Key Exchange, PAKE）协议。其核心思想是：

1. 双方共享一个密码（Password）
2. 通过密码派生一个椭圆曲线上的点（Password Element, PE）
3. 执行类似Diffie-Hellman的密钥交换
4. 最终生成共享密钥PMK（Pairwise Master Key）

#### 1.2.2 SAE握手流程

SAE握手分为两个阶段：**Commit阶段**和**Confirm阶段**。

**Commit消息交换：**

```
客户端 -> AP: Commit(Scalar, Element)
AP -> 客户端: Commit(Scalar, Element)
```

双方各自生成：
- 私钥标量（Scalar）：随机数
- 元素（Element）：对密码派生点进行标量乘法的结果

**Confirm消息交换：**

```
客户端 -> AP: Confirm(Send-Confirm)
AP -> 客户端: Confirm(Send-Confirm)
```

双方验证对方的身份并确认密钥一致性。

#### 1.2.3 密码元素（Password Element）派生

密码元素的派生是SAE安全性的关键。密码被确定性地映射到椭圆曲线上的一个点：

```
PE = KDF(Password, SSID, MAC_AP, MAC_STA)
```

其中KDF是密钥派生函数，使用HMAC和计数器模式。这个过程被称为"hunting and pecking"，因为需要不断尝试直到找到有效的曲线点。

**关键安全特性**：由于PE的派生与双方MAC地址绑定，攻击者即使捕获了Commit消息，也无法离线验证密码猜测——因为每次连接的PE都不同。

---

### 1.3 WPA3-SAE攻击面分析

尽管SAE在设计上比PSK更安全，但它并非完美无缺。以下是已发现的攻击面：

#### 1.3.1 侧信道攻击（Side-Channel Attacks）

**时间侧信道攻击**：
- 密码元素派生过程中的"hunting and pecking"循环次数取决于密码值
- 攻击者可以通过测量响应时间来推断密码信息
- 2019年Dragonblood漏洞披露了此类攻击

**缓存侧信道攻击**：
- 利用CPU缓存泄漏的信息
- 例如Flush+Reload攻击可提取密钥信息

#### 1.3.2 降级攻击

WPA3与WPA2混合模式下的降级攻击是重要攻击面：
- 大多数WPA3 AP同时支持WPA2（过渡模式）
- 攻击者可迫使客户端使用WPA2连接
- 然后使用传统WPA2攻击手段

#### 1.3.3 实现漏洞

不同厂商的SAE实现可能存在漏洞：
- 标量（Scalar）生成的随机性不足
- 密码元素派生的实现缺陷
- Confirm消息验证逻辑错误

#### 1.3.4 主动在线猜测攻击

虽然SAE防止离线字典攻击，但在线猜测仍然可行：
- 攻击者可以尝试不同的密码进行连接
- 每次尝试都需要与AP进行完整的SAE握手
- 速率限制是主要防御手段
- 某些AP实现中速率限制存在绕过可能

---

### 1.4 Dragonblood攻击详解

Dragonblood是2019年由Mathy Vanhoef（KRACK发现者）和Eyal Ronen公开的针对WPA3的系列攻击，共包含5个漏洞。

#### 1.4.1 Dragonblood漏洞概述

| 漏洞编号 | 名称 | 类型 | 影响 |
|---------|------|------|------|
| CVE-2019-9494 | Dragonblood SAE timing attack | 侧信道 | 可恢复密码 |
| CVE-2019-9495 | Dragonblood SAE cache attack | 缓存侧信道 | 可恢复密码 |
| CVE-2019-9496 | Dragonblood SAE downgrade | 降级攻击 | 降级到WPA2 |
| CVE-2019-9497 | Dragonblood EAP-pwd reflection | 反射攻击 | 绕过认证 |
| CVE-2019-9498/9499 | Dragonblood EAP-pwd | 侧信道 | 可恢复密码 |

#### 1.4.2 SAE时间侧信道攻击（CVE-2019-9494）

**攻击原理**：

SAE的密码元素派生使用"hunting and pecking"方法：

```python
def derive_password_element(password, ssid, mac_ap, mac_sta):
    k = 0
    while True:
        pwd_seed = HMAC-SHA256(password, ssid || mac_ap || mac_sta || k)
        x = pwd_seed mod p  # p是椭圆曲线的模数
        # 尝试计算 y^2 = x^3 + ax + b
        if is_quadratic_residue(x):
            return Point(x, y)
        k += 1
```

**攻击方法**：
1. 攻击者作为合法客户端连接AP
2. 尝试不同的密码，测量AP响应Commit消息的时间
3. 密码正确时，派生PE的循环次数不同，导致响应时间有差异
4. 通过大量测量和统计分析，逐步推断密码

**攻击复杂度**：
- 每次密码猜测约需10ms
- 对一个8字符密码，平均需要约350次尝试可区分正确与错误密码
- 实际破解仍需结合字典攻击，但大大减少了尝试次数

#### 1.4.3 SAE缓存侧信道攻击（CVE-2019-9495）

**攻击原理**：

如果攻击者与目标AP共享同一CPU（例如虚拟化环境），可以通过缓存侧信道获取更精确的信息：

1. 使用Flush+Reload技术监控密码派生函数的执行
2. 精确测量循环迭代次数
3. 直接获取密码元素派生过程中的中间值

**攻击场景**：
- 云环境中的虚拟AP
- 共享硬件的多租户环境
- 恶意APP在同一设备上

#### 1.4.4 降级攻击（CVE-2019-9496）

**攻击原理**：

在WPA2/WPA3混合模式下，攻击者可以：

1. 发送伪造的Beacon帧，宣称AP只支持WPA2
2. 或在认证/关联过程中修改RSNE字段，移除WPA3支持
3. 客户端降级到WPA2进行连接
4. 攻击者随后可执行传统WPA2攻击

**实战利用**：

```bash
# 使用hostapd-mana创建降级AP
# 配置文件中只声明WPA2支持
interface=wlan0
ssid=TargetNetwork
wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_passphrase=dummypassword
```

#### 1.4.5 EAP-pwd反射攻击（CVE-2019-9497）

此漏洞影响WPA3-Enterprise使用EAP-pwd认证的场景：

1. 攻击者向客户端发送其自己的Commit消息
2. 客户端返回Confirm消息
3. 攻击者将此Confirm消息原样发回给客户端
4. 由于某些实现中的验证逻辑缺陷，客户端会接受自己的Confirm消息
5. 攻击者成功绕过认证

---

### 1.5 WPA3降级攻击深度分析

#### 1.5.1 降级攻击的分类

**Beacon层降级**：
- 攻击者广播伪造的Beacon，移除WPA3支持标识
- 客户端扫描时发现"目标网络"只支持WPA2
- 适用于被动扫描的客户端

**Probe Response降级**：
- 攻击者响应客户端的Probe Request
- 在Probe Response中只声明WPA2支持
- 适用于主动扫描的客户端

**关联过程降级**：
- 攻击者在AP和客户端之间充当中间人
- 修改Association Request/Response中的RSNE字段
- 需要更复杂的中间人位置

#### 1.5.2 降级攻击的前提条件

1. **混合模式支持**：AP同时支持WPA2和WPA3
2. **客户端兼容性**：客户端同时支持WPA2和WPA3
3. **信号强度优势**：攻击者的信号强于真实AP
4. **无企业级防护**：目标网络未部署WIPS

#### 1.5.3 防御降级攻击的措施

- 禁用WPA2过渡模式，纯WPA3环境
- 客户端配置为仅WPA3模式
- 部署无线入侵防御系统（WIPS）
- 启用管理帧保护（MFP）

---

### 1.6 WPA3与WPA2混合模式攻击

#### 1.6.1 混合模式的安全风险

大多数企业在迁移到WPA3时会采用混合模式（Transition Mode），即AP同时广播WPA2和WPA3支持。这种模式带来了诸多安全问题：

**最弱链接问题**：
- 整体安全性由最弱的连接决定
- 只要有一个客户端使用WPA2连接，网络就存在WPA2级别的漏洞

**攻击面扩大**：
- 同时存在SAE和PSK两个攻击面
- 降级攻击成为可能
- 针对WPA2的所有攻击仍然有效

#### 1.6.2 混合模式下的攻击策略

**策略一：针对WPA2客户端的攻击**
- 识别网络中的WPA2客户端
- 执行传统的WPA2攻击（捕获四次握手、PMKID等）
- 破解密码后，该密码也适用于WPA3连接

**策略二：降级攻击**
- 迫使WPA3客户端降级到WPA2
- 然后执行WPA2攻击

**策略三：SAE侧信道攻击**
- 针对WPA3客户端执行Dragonblood攻击
- 获取密码后可访问整个网络

#### 1.6.3 混合模式的识别

```bash
# 使用airodump-ng识别混合模式AP
airodump-ng wlan0mon --wpa

# 输出中如果同时出现 WPA2 和 WPA3 的RSN信息，则为混合模式
# WPA3标识: RSN: *AKM: 00-0f-ac:8 (SAE)
# WPA2标识: RSN: *AKM: 00-0f-ac:2 (PSK)
```

---

---

