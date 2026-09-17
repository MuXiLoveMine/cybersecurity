# FIDO2/WebAuthn 标准详解

### 2.1 FIDO2 技术架构

FIDO2 是 FIDO 联盟和 W3C 联合制定的开放标准，由两个核心规范组成：

```
FIDO2 标准体系
  ├── W3C WebAuthn（Web Authentication）
  │     └── 浏览器/平台 JavaScript API
  │           ├── navigator.credentials.create()  ← 注册
  │           └── navigator.credentials.get()    ← 认证
  │
  └── FIDO CTAP（Client to Authenticator Protocol）
        └── 客户端与认证器之间的通信协议
              ├── CTAP1（即FIDO U2F协议，USB HID）
              ├── CTAP2（CBOR编码，支持平台/漫游认证器）
              └── CTAP 2.1（增强版，支持混合_transport）
```

**FIDO2 三大角色：**

| 角色 | 英文 | 说明 | 示例 |
|------|------|------|------|
| 依赖方 | Relying Party (RP) | 需要验证用户身份的Web服务 | 网站/应用服务器 |
| 客户端 | Client | 用户浏览器或应用 | Chrome、Safari、Edge |
| 认证器 | Authenticator | 生成和存储密钥的硬件/软件 | YubiKey、Touch ID |

**FIDO2 架构图：**

```
┌─────────────────────────────────────────────────────┐
│                  依赖方 (RP Server)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  注册逻辑     │  │  认证逻辑     │  │ 凭据数据库  │  │
│  │  (Challenge) │  │  (Verify)    │  │ (Credential)│  │
│  └──────┬──────┘  └──────┬───────┘  └──────┬─────┘  │
└─────────┼──────────────────┼─────────────────┼────────┘
          │ HTTPS            │ HTTPS           │
          ▼                  ▼                 │
┌─────────────────────────────────────────────────┐    │
│              客户端 (Browser/App)                 │    │
│  ┌──────────────────────────────────────────┐   │    │
│  │  WebAuthn API                              │   │    │
│  │  navigator.credentials.create() / .get()   │   │    │
│  └──────────────────┬───────────────────────┘   │    │
└─────────────────────┼──────────────────────────┘    │
                      │ CTAP2协议                       │
                      ▼                                 │
┌─────────────────────────────────────────────┐        │
│           认证器 (Authenticator)              │        │
│  ┌──────────┐  ┌─────────────┐              │        │
│  │ 私钥存储  │  │ 用户验证     │              │        │
│  │ (Secure) │  │(Bio/PIN)    │              │        │
│  └──────────┘  └─────────────┘              │        │
│  ┌──────────────────────────────┐            │        │
│  │  公私钥对（按RP ID分别存储）  │ ←────────┘
│  └──────────────────────────────┘            │
└─────────────────────────────────────────────┘
```

### 2.2 WebAuthn API 工作原理

#### 2.2.1 注册流程（navigator.credentials.create）

注册阶段的目标是在认证器中为特定 RP 生成一对公私钥，并将公钥注册到服务器。

**注册流程时序：**

```
用户                浏览器(Client)           RP服务器           认证器
 │                      │                      │                  │
 │  1.发起注册           │                      │                  │
 │─────────────────────→│                      │                  │
 │                      │  2.请求注册Challenge  │                  │
 │                      │─────────────────────→│                  │
 │                      │  3.返回Challenge+选项  │                  │
 │                      │←─────────────────────│                  │
 │                      │                      │                  │
 │                      │  4.调用WebAuthn API    │                  │
 │                      │  navigator.credentials│                  │
 │                      │   .create(publicKey)  │                  │
 │                      │                      │                  │
 │                      │  5.CTAP命令→认证器     │                  │
 │                      │─────────────────────────────────────────→│
 │                      │                      │                  │
 │  6.生物验证/触控      │                      │                  │
 │←──────────────────────────────────────────────────────────────│
 │  7.用户同意           │                      │                  │
 │─────────────────────────────────────────────────────────────→│
 │                      │                      │                  │
 │                      │  8.认证器生成密钥对    │                  │
 │                      │     私钥安全存储       │                  │
 │                      │     签名Challenge     │                  │
 │                      │  9.返回Attestation    │                  │
 │                      │←─────────────────────────────────────────│
 │                      │                      │                  │
 │                      │ 10.发送注册数据        │                  │
 │                      │   (公钥+签名)         │                  │
 │                      │─────────────────────→│                  │
 │                      │                      │ 11.验证签名      │
 │                      │                      │     存储公钥      │
 │                      │  12.注册成功          │                  │
 │                      │←─────────────────────│                  │
 │  13.提示完成           │                      │                  │
 │←─────────────────────│                      │                  │
```

**注册请求选项结构：**

```javascript
// 服务端生成注册选项
const publicKeyCredentialCreationOptions = {
    challenge: new Uint8Array(32),  // 服务端生成的随机挑战，至少16字节
    rp: {
        name: "安全学习平台",
        id: "security.example.com"   // RP ID，必须等于或为域名后缀
    },
    user: {
        id: new Uint8Array(16),      // 用户唯一ID（不含可读信息）
        name: "learner@example.com",  // 用于显示
        displayName: "安全学习者"
    },
    pubKeyCredParams: [
        { type: "public-key", alg: -7 },   // ES256 (ECDSA P-256)
        { type: "public-key", alg: -257 }, // RS256 (RSASSA-PKCS1-v1.5)
        { type: "public-key", alg: -8 }   // EdDSA (Ed25519)
    ],
    authenticatorSelection: {
        authenticatorAttachment: "platform",  // platform=内置, cross-platform=外接
        userVerification: "required",         // required/preferred/discouraged
        residentKey: "preferred",             // 是否存储可发现凭据
        requireResidentKey: false
    },
    timeout: 60000,
    excludeCredentials: [
        // 排除已注册的凭据，防止重复注册
        {
            type: "public-key",
            id: existingCredentialId
        }
    ],
    attestation: "none"  // none/indirect/direct，隐私与信任权衡
};

// 调用浏览器API
const credential = await navigator.credentials.create({
    publicKey: publicKeyCredentialCreationOptions
});
```

**认证器返回的 Attestation 对象结构：**

```
AttestationObject (CBOR编码)
  ├── fmt: "packed" / "tpm" / "android-key" / "none" / ...
  ├── authData:
  │     ├── rpIdHash: SHA-256(rp.id)
  │     ├── flags:
  │     │     ├── UP (User Present)
  │     │     ├── UV (User Verified)
  │     │     ├── BE (Backup Eligible)
  │     │     └── BS (Backup State)
  │     ├── signCount: 签名计数器（防克隆）
  │     └── attestedCredentialData:
  │           ├── aaguid: 认证器型号标识
  │           ├── credentialId: 凭据ID
  │           └── credentialPublicKey: COSE格式公钥
  └── attStmt: 签名证据（用于验证认证器真实性）
```

#### 2.2.2 认证流程（navigator.credentials.get）

认证阶段通过私钥对服务端挑战进行签名来证明身份。

**认证流程时序：**

```
用户                浏览器(Client)           RP服务器           认证器
 │                      │                      │                  │
 │  1.发起登录           │                      │                  │
 │─────────────────────→│                      │                  │
 │                      │  2.请求认证Challenge  │                  │
 │                      │─────────────────────→│                  │
 │                      │  3.返回Challenge      │                  │
 │                      │←─────────────────────│                  │
 │                      │                      │                  │
 │                      │  4.调用WebAuthn API    │                  │
 │                      │  navigator.credentials│                  │
 │                      │   .get(publicKey)     │                  │
 │                      │                      │                  │
 │                      │  5.CTAP命令→认证器     │                  │
 │                      │─────────────────────────────────────────→│
 │  6.生物验证/触控      │                      │                  │
 │←──────────────────────────────────────────────────────────────│
 │                      │  7.认证器查找私钥      │                  │
 │                      │     签名Challenge     │                  │
 │                      │  8.返回Assertion      │                  │
 │                      │←─────────────────────────────────────────│
 │                      │                      │                  │
 │                      │  9.发送认证数据        │                  │
 │                      │   (credentialId+签名) │                  │
 │                      │─────────────────────→│                  │
 │                      │                      │ 10.查找公钥      │
 │                      │                      │     验证签名      │
 │                      │                      │     检查signCount│
 │                      │  11.认证成功+Token    │                  │
 │                      │←─────────────────────│                  │
 │  12.登录完成           │                      │                  │
 │←─────────────────────│                      │                  │
```

**认证请求与调用：**

```javascript
// 服务端生成认证选项
const publicKeyCredentialRequestOptions = {
    challenge: new Uint8Array(32),
    rpId: "security.example.com",
    allowCredentials: [
        {
            type: "public-key",
            id: credentialId  // 之前注册时返回的凭据ID
        }
    ],
    userVerification: "required",
    timeout: 60000
};

// 客户端调用
const assertion = await navigator.credentials.get({
    publicKey: publicKeyCredentialRequestOptions
});

// assertion 包含:
// - credentialId: 使用的凭据ID
// - authenticatorData: RP ID Hash + Flags + signCount
// - clientDataJSON: origin + challenge + type
// - signature: 认证器私钥对 authenticatorData || SHA256(clientDataJSON) 的签名
```

**服务端验证逻辑（Python示例）：**

```python
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec, ed25519
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
import cbor2
import json

def verify_webauthn_assertion(assertion_response, stored_credential):
    """
    验证WebAuthn认证断言
    assertion_response: 前端传来的认证数据
    stored_credential: 数据库中存储的凭据信息
    """
    # 1. 解析clientDataJSON
    client_data = json.loads(assertion_response['clientDataJSON'])
    
    # 2. 验证type
    if client_data['type'] != 'webauthn.get':
        raise ValueError("Invalid type")
    
    # 3. 验证origin
    if client_data['origin'] != 'https://security.example.com':
        raise ValueError("Invalid origin")
    
    # 4. 验证challenge
    if client_data['challenge'] != stored_credential['current_challenge']:
        raise ValueError("Challenge mismatch")
    
    # 5. 解析authenticatorData
    auth_data = assertion_response['authenticatorData']
    rp_id_hash = auth_data[:32]
    
    # 6. 验证RP ID Hash
    expected_rp_hash = hashlib.sha256(b'security.example.com').digest()
    if rp_id_hash != expected_rp_hash:
        raise ValueError("RP ID mismatch")
    
    # 7. 验证User Verification Flag
    flags = auth_data[32]
    uv_flag = (flags & 0x04) != 0  # UV bit
    if not uv_flag:
        raise ValueError("User verification required but not performed")
    
    # 8. 检查signCount（防克隆重放）
    sign_count = int.from_bytes(auth_data[33:37], 'big')
    if sign_count <= stored_credential['sign_count'] and sign_count != 0:
        raise ValueError("Possible cloned authenticator detected")
    
    # 9. 验证签名
    client_data_hash = hashlib.sha256(
        assertion_response['clientDataJSON'].encode()
    ).digest()
    
    signed_data = auth_data + client_data_hash
    
    # 根据公钥算法验证签名
    public_key = stored_credential['public_key']
    signature = assertion_response['signature']
    
    if stored_credential['alg'] == -7:  # ES256
        public_key.verify(signature, signed_data, ec.ECDSA(
            hashlib.sha256()
        ))
    elif stored_credential['alg'] == -257:  # RS256
        from cryptography.hazmat.primitives.asymmetric import padding
        public_key.verify(signature, signed_data, 
            padding.PKCS1v15(), hashlib.sha256())
    
    # 更新sign count
    stored_credential['sign_count'] = sign_count
    return True
```

### 2.3 公钥挑战-响应认证流程

FIDO2 的核心安全原理是**公钥挑战-响应机制**，整个过程不传输任何密码或密钥。

```
挑战-响应流程：
  
  服务端                         认证器
    │                              │
    │  1. 生成随机Challenge(≥16B)  │
    │─────────────────────────────→│  (通过浏览器中转)
    │                              │
    │  2. 认证器内部操作：           │
    │     - 查找对应RP的私钥         │
    │     - 用户验证(生物/PIN)       │
    │     - 签名：sig = Sign(SK,   │
    │         Challenge||context)  │
    │                              │
    │  3. 返回签名+credentialId     │
    │←─────────────────────────────│
    │                              │
    │  4. 服务端验证：              │
    │     - 查找credentialId→公钥   │
    │     - Verify(PK, Challenge,  │
    │         sig) == True?        │
    │                              │
    │  每次认证使用不同Challenge     │
    │  → 防止重放攻击               │
    │  → 私钥永远不离开认证器        │
```

**关键安全属性：**

- **私钥不出认证器**：私钥在认证器安全区域（SE/TPM）生成和存储，永不导出
- **每RP独立密钥**：不同网站使用不同密钥，认证器按 `rpId` 区分
- **挑战随机性**：每次认证的 Challenge 不同，防止重放
- **来源绑定**：`clientDataJSON` 包含 `origin`，认证器和服务端均可验证

### 2.4 设备绑定认证器 vs 漫游认证器

| 特性 | 平台认证器（Platform Authenticator） | 漫游认证器（Roaming Authenticator） |
|------|--------------------------------------|--------------------------------------|
| 存储位置 | 内置于设备 | 独立硬件设备 |
| 传输方式 | 直接API调用 | USB/NFC/BLE |
| 示例 | Touch ID、Windows Hello、Android Biometric | YubiKey、Google Titan、Feitian ePass |
| 便携性 | 不可移动 | 可在多设备间移动 |
| 安全边界 | 设备SE/TEE | 独立安全芯片 |
| 用户体验 | 无需额外设备 | 需携带物理令牌 |
| 恢复性 | 设备丢失则凭据丢失 | 可备份多枚令牌 |
| 适用场景 | 日常消费级应用 | 高安全需求场景 |

**混合传输认证器（Hybrid Transport）：**

CTAP 2.1 引入了 hybrid transport，允许手机作为漫游认证器为电脑上的浏览器认证：

```
┌───────────┐    BLE广播+二维码      ┌───────────┐
│   电脑      │←──────────────────→│   手机      │
│ (浏览器)   │    BLE建立连接         │(认证器App) │
│           │←──────QR扫码配对──────→│           │
│           │    WLAN/TLS数据传输     │           │
└───────────┘                      └───────────┘

流程：
1. 电脑浏览器显示二维码
2. 手机扫描二维码建立BLE连接
3. 通过WLAN建立TLS隧道传输CTAP消息
4. 手机完成生物验证并签名
5. 签名通过隧道返回电脑浏览器
```

### 2.5 多设备凭据管理

FIDO2 的一个重要演进是从单设备凭据转向多设备凭据同步（Multi-Device Credentials），即 Passkey 的基础。

**可发现凭据（Discoverable Credentials / Resident Keys）：**

```
非可发现凭据（Non-Resident Key）：
  - 认证器不存储credentialId→用户映射
  - 服务端需在allowCredentials中提供credentialId
  - 认证器只是"无状态签名器"
  - 适合无存储限制的硬件令牌

可发现凭据（Resident Key / Discoverable Credential）：
  - 认证器内部存储credentialId→用户→私钥映射
  - 认证器可"发现"已注册用户
  - 支持用户名-less 登录（只需输入域名）
  - 受认证器存储空间限制
```

**多设备凭据同步机制：**

```
Passkey 同步架构：

┌─────────┐    ┌─────────┐    ┌─────────┐
│ iPhone   │    │  iPad   │    │ MacBook │
│ Touch ID │    │ Face ID │    │ Touch ID│
└────┬─────┘    └────┬────┘    └────┬────┘
     │               │               │
     └───────┬───────┘               │
             │   iCloud Keychain      │
             ▼                        │
     ┌───────────────┐                │
     │ Apple 同步服务 │←───────────────┘
     │ (E2E加密同步)  │
     └───────────────┘
```

---

---

## 📋 内容审核与补充建议

> 针对「FIDO2/WebAuthn 标准详解」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
