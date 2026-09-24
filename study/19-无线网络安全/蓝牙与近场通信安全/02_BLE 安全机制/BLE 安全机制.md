# BLE 安全机制

### 2.1 BLE 配对模式

BLE 配对是设备之间建立安全连接的过程，分为两个阶段：

```
BLE 配对流程：

阶段1: 配对请求交换
├── Initiator -> Responder: Pairing Request
│   ├── IO Capability
│   ├── OOB Data Flag
│   ├── Bonding Flags
│   ├── MITM Flag
│   ├── SC Flag (Secure Connections)
│   └── Max Encryption Key Size
└── Responder -> Initiator: Pairing Response

阶段2: 密钥生成（Legacy 或 Secure Connections）

阶段3: 密钥分发
├── 分发 LTK, IRK, CSRK 等密钥
└── 用于后续连接的加密和签名

配对方法（取决于 IO 能力）：

1. Just Works（无认证）
   ├── 无用户输入/显示
   ├── 无 MITM 保护
   ├── TK = 0（Legacy）/ 使用 ECDH（SC）
   └── 安全性最低

2. Passkey Entry（6位数字）
   ├── 一方显示6位数字，另一方输入
   ├── 提供 MITM 保护
   ├── TK = Passkey（Legacy）
   └── 多轮确认（SC）

3. Numeric Comparison（仅 SC）
   ├── 双方显示6位数字
   ├── 用户确认是否一致
   ├── 提供 MITM 保护
   └── 仅 Secure Connections 支持

4. Out of Band（OOB）
   ├── 通过其他通道（NFC等）交换配对信息
   ├── 最高安全性
   ├── 传递: 随机数、确认值、公钥
   └── 提供 MITM 保护
```

### 2.2 Legacy 配对密钥派生

```
Legacy 配对密钥生成流程：

1. 临时密钥（TK）生成
   ├── Just Works: TK = 0
   ├── Passkey: TK = Passkey (6位数字, 128位表示)
   └── OOB: TK = OOB Data (128位)

2. 短期密钥（STK）生成
   ├── 交换随机数 Srand 和 Irand
   ├── STK = s1(TK, Srand, Irand)
   └── s1: AES-CMAC 生成 128 位 STK

3. 长期密钥（LTK）分发
   ├── EDIV (16位): 加密分集标识
   ├── Rand (64位): 随机数
   └── LTK (128位): 长期加密密钥

Legacy 配对安全弱点：
├── TK 过短（6位数字 = 20位有效空间）
├── Just Works 模式 TK=0
├── STK 可被暴力破解
├── 无前向保密
└── 密钥可能在空中传输
```

### 2.3 Secure Connections（LE SC）

```
BLE 4.2 引入的 Secure Connections：

核心改进：
├── 使用 ECDH (P-256) 密钥交换
├── 前向保密（Forward Secrecy）
├── 不再使用 TK/STK
├── 直接生成 LTK
└── 抵抗被动窃听

配对流程：

1. 公钥交换
   ├── 双方生成 ECDH 密钥对 (PKa, SKa) 和 (PKb, SKb)
   └── 交换公钥 PKa 和 PKb

2. DH 密钥计算
   └── DHKey = ECDH(SKa, PKb) = ECDH(SKb, PKa)

3. 认证阶段（根据配对方法）：
   ├── Just Works: 无额外认证
   ├── Numeric Comparison:
   │   ├── 计算 Na, Nb (32位随机数)
   │   ├── 计算确认值
   │   └── 显示 6 位数字供用户确认
   ├── Passkey:
   │   ├── 20 轮交互（每轮1位Passkey）
   │   └── 每轮交换随机数和确认值
   └── OOB:
       ├── 通过带外通道传递
       └── 交换随机数和确认值

4. 确认阶段
   ├── 交换确认值
   └── 使用 DHKey + 随机数计算

5. LTK 生成
   ├── LTK = f5(DHKey, Na, Nb, IOCap_a, IOCap_b)
   ├── MacKey (用于签名)
   └── Session Key Diversifier

安全分析：
├── ECDH-P256 提供 128 位安全强度
├── 前向保密: 即使 LTK 泄露，过去会话安全
├── MITM 保护: 通过用户确认/输入
└── KNOB 攻击仍可降级密钥长度
```

### 2.4 BLE 密钥类型

```
BLE 密钥体系：

1. LTK (Long Term Key)
   ├── 128 位长期加密密钥
   ├── 存储在设备中用于后续连接
   ├── 用于链路层加密
   └── 每次连接生成会话密钥

2. IRK (Identity Resolving Key)
   ├── 16 字节密钥
   ├── 用于生成可解析私有地址（RPA）
   ├── RPA = hash(IRK, random) || random
   ├── 防止设备被追踪
   └── 已配对设备可用 IRK 解析 RPA

3. CSRK (Connection Signature Resolving Key)
   ├── 16 字节密钥
   ├── 用于数据签名
   ├── 签名 = mac(CSRK, data) || counter
   └── 用于未加密连接的完整性保护

4. STK (Short Term Key) - 仅 Legacy
   ├── 临时加密密钥
   ├── 配对后立即使用
   └── 分发 LTK 后被替换

5. Session Key
   ├── 每次连接动态生成
   ├── Session Key = f5(LTK, ...)
   └── 用于当前会话的数据加密

隐私特性：
├── 可解析私有地址（RPA）
│   ├── 每隔一定时间更换地址
│   ├── 格式: hash(IRK, prand) || prand
│   └── 已配对设备可解析身份
├── 不可解析私有地址
│   └── 随机地址，无法解析
└── 公共地址
    └── 固定地址，可被追踪
```

---

---

