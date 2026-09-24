# Enterprise WiFi攻击

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

---

